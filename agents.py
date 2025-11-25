import requests
import threading
import time

class Message:
    def __init__(self, sender, intent, payload=None):
        self.sender = sender
        self.intent = intent
        self.payload = payload or {}

class Agent:
    def __init__(self, name):
        self.name = name

    def log(self, msg):
        print(f"[{self.name}] {msg}")

    def receive(self, msg: Message):
        self.log(f"Received message from {msg.sender}: intent={msg.intent}, payload={msg.payload}")

class CustomerDataAgent(Agent):
    def __init__(self, name, mcp_base='http://127.0.0.1:8000/mcp'):
        super().__init__(name)
        self.mcp = mcp_base

    def get_customer(self, customer_id):
        self.log(f"Fetching customer {customer_id} via MCP")
        r = requests.get(f"{self.mcp}/get_customer/{customer_id}")
        if r.status_code == 200:
            return r.json()
        return None

    def list_customers(self, status=None, limit=None):
        params = {}
        if status: params['status'] = status
        if limit: params['limit'] = limit
        r = requests.get(f"{self.mcp}/list_customers", params=params)
        return r.json()

    def update_customer(self, customer_id, data):
        r = requests.post(f"{self.mcp}/update_customer/{customer_id}", json=data)
        return r.json()

    def get_history(self, customer_id):
        r = requests.get(f"{self.mcp}/get_customer_history/{customer_id}")
        return r.json()

class SupportAgent(Agent):
    def __init__(self, name, data_agent: CustomerDataAgent):
        super().__init__(name)
        self.data_agent = data_agent

    def handle_support(self, context):
        self.log(f"Handling support with context: {context}")
        # naive handling: if billing related -> escalate for billing context
        text = context.get('text','').lower()
        if 'billing' in text or 'charge' in text or 'refund' in text:
            self.log('Need billing context')
            return {'status':'need_billing_context'}
        # If request contains update email
        if 'update my email' in text or 'update email' in text:
            cust = context.get('customer')
            new_email = context.get('new_email')
            if cust and new_email:
                self.log(f"Updating email for {cust.get('id')} to {new_email}")
                self.data_agent.update_customer(cust.get('id'), {'email': new_email})
                return {'status':'email_updated'}
        # Default resolution
        return {'status':'resolved', 'message':'Support provided: please see instructions.'}

class RouterAgent(Agent):
    def __init__(self, name, data_agent: CustomerDataAgent, support_agent: SupportAgent):
        super().__init__(name)
        self.data_agent = data_agent
        self.support_agent = support_agent

    def analyze_intent(self, text):
        text_l = text.lower()
        intents = []
        if 'cancel' in text_l or 'unsubscribe' in text_l:
            intents.append('cancellation')
        if 'billing' in text_l or 'charged' in text_l or 'refund' in text_l or 'bill' in text_l:
            intents.append('billing')
        if 'upgrade' in text_l or 'upgrade my account' in text_l:
            intents.append('upgrade')
        if 'get customer information' in text_l or 'get customer' in text_l or 'customer information' in text_l:
            intents.append('get_customer')
        if 'ticket' in text_l or 'tickets' in text_l:
            intents.append('tickets')
        if not intents:
            intents.append('support')
        return intents

    def route(self, text):
        self.log(f"Routing query: {text}")
        intents = self.analyze_intent(text)
        self.log(f"Detected intents: {intents}")
        # Extract customer id naively
        cid = None
        words = text.split()
        for w in words:
            if w.isdigit():
                cid = int(w)
                break

        # Example flows
        if 'get customer information' in text.lower() or 'get customer' in text.lower():
            if cid:
                self.log(f"A2A: Router -> DataAgent: fetch customer {cid}")
                cust = self.data_agent.get_customer(cid)
                self.log(f"A2A: DataAgent -> Router: returned customer data")
                return {'reply': f"Customer {cid}: {cust}"}
        
        # Multi-intent: cancellation + billing
        if 'cancel' in text.lower() and 'billing' in text.lower():
            self.log('A2A: Router negotiating with SupportAgent on cancellation+billing')
            resp = self.support_agent.handle_support({'text': text})
            if resp.get('status') == 'need_billing_context':
                self.log('A2A: SupportAgent -> Router: need billing context')
                self.log('A2A: Router -> DataAgent: fetch billing history')
                billing = None
                if cid:
                    billing = self.data_agent.get_history(cid)
                self.log('A2A: DataAgent -> Router: returned billing history')
                return {'reply': 'Escalation: billing context fetched', 'billing': billing}
        
        # Multi-step: query for high-priority tickets for premium customers
        if 'high-priority tickets' in text.lower() or 'high priority tickets' in text.lower():
            self.log('A2A: Router decomposing multi-step query')
            self.log('A2A: Router -> DataAgent: get all active customers')
            custs = self.data_agent.list_customers(status='active')
            self.log(f'A2A: DataAgent -> Router: returned {len(custs)} customers')
            premium_ids = [c['id'] for c in custs if 'premium' in (c.get('name') or '').lower()]
            self.log(f'A2A: Router identified {len(premium_ids)} premium customers')
            tickets = []
            for pid in premium_ids:
                self.log(f'A2A: Router -> DataAgent: get history for customer {pid}')
                hist = self.data_agent.get_history(pid)
                for t in hist:
                    if t.get('priority') == 'high' and t.get('status') in ('open','in_progress'):
                        tickets.append(t)
            self.log(f'A2A: Router synthesized {len(tickets)} high-priority open tickets')
            return {'reply': f'Found {len(tickets)} high-priority tickets', 'tickets': tickets}
        
        # Complex query: all active customers with open tickets
        if 'all active customers' in text.lower() and 'open tickets' in text.lower():
            self.log('A2A: Router decomposing complex query')
            self.log('A2A: Router -> DataAgent: get all active customers')
            custs = self.data_agent.list_customers(status='active')
            self.log(f'A2A: DataAgent -> Router: returned {len(custs)} active customers')
            result = []
            for c in custs:
                self.log(f'A2A: Router -> DataAgent: check tickets for customer {c["id"]}')
                hist = self.data_agent.get_history(c['id'])
                open_tickets = [t for t in hist if t.get('status') == 'open']
                if open_tickets:
                    result.append({'customer': c['name'], 'customer_id': c['id'], 'open_tickets_count': len(open_tickets)})
            self.log(f'A2A: Router synthesized report for {len(result)} customers with open tickets')
            return {'reply': f'Found {len(result)} active customers with open tickets', 'details': result}

        # Default: send to support
        self.log('A2A: Router -> SupportAgent: forward to support')
        support_resp = self.support_agent.handle_support({'text': text, 'customer_id': cid})
        return {'reply': support_resp}
