"""
Demo Scenarios Runner
Executes multi-agent test scenarios with conversation support
"""
import asyncio
from typing import Optional
from agent_client import call_agent

ROUTER_AGENT_URL = "http://localhost:10020"

class ConversationSession:
    """Manages a multi-turn conversation session."""
    
    def __init__(self, agent_url: str):
        self.agent_url = agent_url
        self.conversation_history = []
        self.session_id = None
        self.customer_id = None
        
    async def send_message(self, message: str) -> str:
        """Send a message and maintain conversation context."""
        try:
            # Build context from history
            context = {
                "message": message,
                "history": self.conversation_history[-5:],  # Last 5 turns
                "session_id": self.session_id,
                "customer_id": self.customer_id
            }
            
            response = await call_agent(self.agent_url, message, context=context)
            
            # Update conversation history
            self.conversation_history.append({
                "user": message,
                "assistant": response
            })
            
            # Extract customer_id if mentioned in the conversation
            if not self.customer_id and "customer" in message.lower():
                # Simple extraction - you might want to make this more robust
                words = message.split()
                for i, word in enumerate(words):
                    if word.lower() in ["id", "customer"] and i + 1 < len(words):
                        try:
                            self.customer_id = int(words[i + 1])
                        except ValueError:
                            pass
            
            return response
        except Exception as e:
            return f"Error: {e}"
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        self.customer_id = None


async def run_interactive_mode():
    """Run in interactive mode for testing multi-turn conversations."""
    print("=" * 60)
    print("Multi-Agent Customer Service System (A2A)")
    print("Interactive Mode - Multi-Turn Conversations")
    print("=" * 60)
    print("\nCommands:")
    print("  /quit or /exit  - Exit the system")
    print("  /clear          - Clear conversation history")
    print("  /history        - Show conversation history")
    print("  /new            - Start new conversation session")
    print("=" * 60)
    
    session = ConversationSession(ROUTER_AGENT_URL)
    
    while True:
        print("\n" + "-" * 60)
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
            
        # Handle commands
        if user_input.lower() in ['/quit', '/exit']:
            print("\nGoodbye! 👋")
            break
        elif user_input.lower() == '/clear':
            session.clear_history()
            print("✅ Conversation history cleared")
            continue
        elif user_input.lower() == '/new':
            session = ConversationSession(ROUTER_AGENT_URL)
            print("✅ New conversation session started")
            continue
        elif user_input.lower() == '/history':
            if session.conversation_history:
                print("\nConversation History:")
                for i, turn in enumerate(session.conversation_history, 1):
                    print(f"\n[Turn {i}]")
                    print(f"You: {turn['user']}")
                    print(f"Agent: {turn['assistant']}")
            else:
                print("No conversation history yet")
            continue
        
        # Send message
        print("\nAgent: ", end="", flush=True)
        response = await session.send_message(user_input)
        print(response)


async def run_test_scenarios():
    """Run predefined test scenarios with multi-turn conversations."""
    print("=" * 60)
    print("Multi-Agent Customer Service System (A2A)")
    print("Test Scenarios - Multi-Turn Conversations")
    print("=" * 60)
    print("\nStarting test scenarios...\n")
    
    # Scenario 1: Customer needs help, provides ID in follow-up
    print("\n" + "=" * 60)
    print("SCENARIO 1: Multi-turn customer support with ID follow-up")
    print("=" * 60)
    
    session1 = ConversationSession(ROUTER_AGENT_URL)
    
    print("\n[User]: I need help upgrading my account")
    response = await session1.send_message("I need help upgrading my account")
    print(f"[Agent]: {response}\n")
    await asyncio.sleep(1)
    
    print("[User]: My customer ID is 12345")
    response = await session1.send_message("My customer ID is 12345")
    print(f"[Agent]: {response}\n")
    await asyncio.sleep(1)
    
    print("[User]: What options do I have?")
    response = await session1.send_message("What options do I have?")
    print(f"[Agent]: {response}\n")
    
    # Scenario 2: Billing issue with escalation
    print("\n" + "=" * 60)
    print("SCENARIO 2: Billing issue with multiple follow-ups")
    print("=" * 60)
    
    session2 = ConversationSession(ROUTER_AGENT_URL)
    
    print("\n[User]: I have a billing problem")
    response = await session2.send_message("I have a billing problem")
    print(f"[Agent]: {response}\n")
    await asyncio.sleep(1)
    
    print("[User]: I was charged twice for my subscription")
    response = await session2.send_message("I was charged twice for my subscription")
    print(f"[Agent]: {response}\n")
    await asyncio.sleep(1)
    
    print("[User]: My customer ID is 5")
    response = await session2.send_message("My customer ID is 5")
    print(f"[Agent]: {response}\n")
    await asyncio.sleep(1)
    
    print("[User]: Can you issue a refund?")
    response = await session2.send_message("Can you issue a refund?")
    print(f"[Agent]: {response}\n")
    
    # Scenario 3: Email update with verification
    print("\n" + "=" * 60)
    print("SCENARIO 3: Email update with verification")
    print("=" * 60)
    
    session3 = ConversationSession(ROUTER_AGENT_URL)
    
    print("\n[User]: I want to update my contact information")
    response = await session3.send_message("I want to update my contact information")
    print(f"[Agent]: {response}\n")
    await asyncio.sleep(1)
    
    print("[User]: Customer ID 5, please update my email")
    response = await session3.send_message("Customer ID 5, please update my email")
    print(f"[Agent]: {response}\n")
    await asyncio.sleep(1)
    
    print("[User]: New email is evan.new@example.com")
    response = await session3.send_message("New email is evan.new@example.com")
    print(f"[Agent]: {response}\n")
    await asyncio.sleep(1)
    
    print("[User]: Can you show me my updated information?")
    response = await session3.send_message("Can you show me my updated information?")
    print(f"[Agent]: {response}\n")
    
    print("\n" + "=" * 60)
    print("All test scenarios completed!")
    print("=" * 60)


async def main():
    """Main entry point - choose mode."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        await run_interactive_mode()
    else:
        await run_test_scenarios()


if __name__ == "__main__":
    asyncio.run(main())