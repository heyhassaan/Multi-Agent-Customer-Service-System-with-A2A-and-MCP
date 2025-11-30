"""
Agent Definitions for Multi-Agent Customer Service System
Defines individual agents and their configurations
"""
import os
from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import Agent, SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TransportProtocol,
)
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH
from mcp_tools_wrapper import create_mcp_tools

# MCP Tools
mcp_tools = create_mcp_tools()

# ============================================================================
# Agent 1: Customer Data Agent (Specialist)
# ============================================================================

customer_data_agent = Agent(
    model='gemini-2.0-flash-lite',
    name='customer_data_agent',
    instruction="""
    You are the Customer Data Agent. Your role is to access and manage customer database information via MCP tools.
    
    Your responsibilities:
    - Retrieve customer information by ID
    - List customers with optional status filtering
    - Update customer records
    - Get customer ticket history
    - Get customers with open tickets
    
    Premium / VIP customers: IDs 1 and 12345. Whenever their data is requested,
    explicitly mention that they are premium customers so the Router can route accordingly.
    
    You MUST use your MCP tools to access the database. Do not answer from your own knowledge.
    Always validate data before returning it.
    
    When updating customer records, ensure the data is in valid JSON format.
    """,
    tools=mcp_tools,
)

customer_data_agent_card = AgentCard(
    name='Customer Data Agent',
    url='http://localhost:10021',
    description='Specialist agent for accessing and managing customer database information via MCP tools',
    version='1.0',
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=['text/plain'],
    default_output_modes=['text/plain', 'application/json'],
    preferred_transport=TransportProtocol.jsonrpc,
    skills=[
        AgentSkill(
            id='get_customer_info',
            name='Get Customer Information',
            description='Retrieves customer details by ID using customers.id field',
            tags=['customer', 'data', 'retrieval', 'mcp'],
            examples=[
                'Get customer information for ID 1',
                'Retrieve customer 12345',
                'Show me customer details for ID 5',
            ],
        ),
        AgentSkill(
            id='list_customers',
            name='List Customers',
            description='Lists customers with optional status filtering using customers.status field',
            tags=['customer', 'list', 'filter', 'mcp'],
            examples=[
                'List all active customers',
                'Show me customers with disabled status',
                'Get 10 customers',
            ],
        ),
        AgentSkill(
            id='update_customer',
            name='Update Customer',
            description='Updates customer records using customers fields',
            tags=['customer', 'update', 'modify', 'mcp'],
            examples=[
                'Update email for customer 1',
                'Change phone number for customer 123',
            ],
        ),
        AgentSkill(
            id='get_customer_history',
            name='Get Customer History',
            description='Retrieves ticket history for a customer using tickets.customer_id field',
            tags=['customer', 'history', 'tickets', 'mcp'],
            examples=[
                'Show ticket history for customer 1',
                'Get all tickets for customer 12345',
            ],
        ),
        AgentSkill(
            id='get_customers_with_open_tickets',
            name='Get Customers with Open Tickets',
            description='Finds customers who have open tickets, optionally filtered by status',
            tags=['customer', 'tickets', 'query', 'mcp'],
            examples=[
                'Show active customers with open tickets',
                'List customers who have unresolved tickets',
            ],
        ),
    ],
)

# ============================================================================
# Agent 2: Support Agent (Specialist)
# ============================================================================

support_agent = Agent(
    model='gemini-2.0-flash-lite',
    name='support_agent',
    instruction="""
    You are the Support Agent. Your role is to handle customer support queries and issues.
    
    Your responsibilities:
    - Handle general customer support queries
    - Create support tickets for customer issues
    - Escalate complex issues when needed
    - Request customer context from Data Agent when needed
    - Provide solutions and recommendations
    
    You have access to customer lookup tools to find customer IDs when needed.
    You can create tickets and check customer history.
    
    When a customer mentions they are "customer X" or provides identifying information,
    use your lookup tools first, then create tickets or check history.
    
    If you cannot proceed (e.g., need billing context), tell the Router exactly what information you require.
    For urgent issues (billing, refunds, critical problems), prioritize them appropriately and escalate if needed.
    """,
    tools=mcp_tools,  # Support agent also needs customer lookup tools
)

support_agent_card = AgentCard(
    name='Support Agent',
    url='http://localhost:10022',
    description='Specialist agent for handling customer support queries, ticket creation, and issue resolution',
    version='1.0',
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=['text/plain'],
    default_output_modes=['text/plain'],
    preferred_transport=TransportProtocol.jsonrpc,
    skills=[
        AgentSkill(
            id='create_ticket',
            name='Create Support Ticket',
            description='Creates a new support ticket using tickets fields',
            tags=['support', 'ticket', 'create', 'mcp'],
            examples=[
                'Create a ticket for customer 1 about account upgrade',
                'Open a high priority ticket for billing issue',
            ],
        ),
        AgentSkill(
            id='handle_support_query',
            name='Handle Support Query',
            description='Processes general customer support queries and provides solutions',
            tags=['support', 'help', 'assistance'],
            examples=[
                'I need help with my account',
                'How do I upgrade my subscription?',
                'I have a billing question',
            ],
        ),
        AgentSkill(
            id='escalate_issue',
            name='Escalate Issue',
            description='Escalates complex or urgent issues appropriately',
            tags=['support', 'escalation', 'urgent'],
            examples=[
                'I\'ve been charged twice, please refund immediately!',
                'My account has been compromised',
            ],
        ),
    ],
)

# ============================================================================
# Agent 3: Router Agent (Orchestrator)
# ============================================================================

# Create remote references to other agents
remote_customer_data_agent = RemoteA2aAgent(
    name='customer_data',
    description='Specialist agent for accessing customer database information',
    agent_card=f'http://localhost:10021{AGENT_CARD_WELL_KNOWN_PATH}',
)

remote_support_agent = RemoteA2aAgent(
    name='support',
    description='Specialist agent for handling customer support queries',
    agent_card=f'http://localhost:10022{AGENT_CARD_WELL_KNOWN_PATH}',
)

# Router agent - uses SequentialAgent which automatically routes through sub-agents
router_agent = SequentialAgent(
    name='router_agent',
    sub_agents=[remote_customer_data_agent, remote_support_agent],
)

router_agent_card = AgentCard(
    name='Router Agent',
    url='http://localhost:10020',
    description='Orchestrator agent that receives queries, analyzes intent, and routes to appropriate specialist agents',
    version='1.0',
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=['text/plain'],
    default_output_modes=['text/plain'],
    preferred_transport=TransportProtocol.jsonrpc,
    skills=[
        AgentSkill(
            id='route_query',
            name='Route Customer Query',
            description='Analyzes query intent and routes to appropriate specialist agent',
            tags=['routing', 'orchestration', 'coordination'],
            examples=[
                'Get customer information for ID 5',
                'I\'m customer 1 and need help upgrading my account',
                'Show me all active customers who have open tickets',
            ],
        ),
        AgentSkill(
            id='coordinate_agents',
            name='Coordinate Multiple Agents',
            description='Coordinates responses from multiple specialist agents for complex queries',
            tags=['coordination', 'multi-agent', 'orchestration'],
            examples=[
                'Update my email and show my ticket history',
                'I want to cancel but have billing issues',
            ],
        ),
        AgentSkill(
            id='analyze_intent',
            name='Analyze Query Intent',
            description='Analyzes customer queries to determine intent and required actions',
            tags=['analysis', 'intent', 'routing'],
            examples=[
                'Determine if query needs data retrieval or support',
                'Identify if multiple agents are needed',
            ],
        ),
    ],
)

# Export all agents and cards
__all__ = [
    'customer_data_agent',
    'customer_data_agent_card',
    'support_agent',
    'support_agent_card',
    'router_agent',
    'router_agent_card',
]

