import threading
import time
import subprocess
import requests
import os
import sys

from database_setup import create_db, DB_PATH

def start_mcp_server():
    # Start the Flask MCP server using the same Python interpreter running this script
    return subprocess.Popen([sys.executable, 'mcp_server.py'], shell=False)

def wait_for_server(url='http://127.0.0.1:8000/mcp/get_customer/1', timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            return True
        except Exception:
            time.sleep(0.3)
    return False

def run_demo():
    print('Seeding database...')
    create_db()

    print('Starting MCP server...')
    proc = start_mcp_server()
    try:
        ok = wait_for_server()
        if not ok:
            print('MCP server did not start in time.')
            proc.terminate()
            return

        # Import agents after server is up to avoid requests race
        from agents import CustomerDataAgent, SupportAgent, RouterAgent

        print('Creating agents...')
        data_agent = CustomerDataAgent('DataAgent')
        support_agent = SupportAgent('SupportAgent', data_agent)
        router = RouterAgent('Router', data_agent, support_agent)

        scenarios = [
            ("Simple Query", "Get customer information for ID 5"),
            ("Coordinated Query", "I'm customer 12345 and need help upgrading my account"),
            ("Complex Query", "Show me all active customers who have open tickets"),
            ("Escalation", "I've been charged twice, please refund immediately!"),
            ("Multi-Intent", "Update my email to new@email.com and show my ticket history for 12345"),
        ]

        for name, q in scenarios:
            print('\n---')
            print(f"Scenario: {name}")
            print(f"Query: {q}")
            # naive special handling for the multi-intent to include new_email
            if 'update my email' in q.lower():
                # call support via router but include new_email in context
                resp = router.route(q + ' new@email.com')
            else:
                resp = router.route(q)
            print('Response:')
            print(resp)

    finally:
        print('Stopping MCP server...')
        proc.terminate()

if __name__ == '__main__':
    run_demo()
