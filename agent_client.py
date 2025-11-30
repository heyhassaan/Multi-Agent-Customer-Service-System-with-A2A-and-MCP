"""
Agent Client Helper
Simplifies calling A2A agents with multi-turn conversation support
"""
import httpx
from typing import Optional, Dict, Any
from a2a.client import ClientConfig, ClientFactory, create_text_message_object
from a2a.types import TransportProtocol
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH


class A2ASimpleClient:
    """A2A Simple Client to call A2A servers."""
    
    def __init__(self, default_timeout: float = 240.0):
        self._agent_info_cache: dict[str, dict | None] = {}  # Cache for agent metadata
        self.default_timeout = default_timeout
    
    async def create_task(self, agent_url: str, message: str) -> str:
        """Send a message following the official A2A SDK pattern."""
        # Configure httpx client with timeout
        timeout_config = httpx.Timeout(
            timeout=self.default_timeout,
            connect=10.0,
            read=self.default_timeout,
            write=10.0,
            pool=5.0,
        )
        
        async with httpx.AsyncClient(timeout=timeout_config) as httpx_client:
            # Check if we have cached agent card data
            if (
                agent_url in self._agent_info_cache
                and self._agent_info_cache[agent_url] is not None
            ):
                agent_card_data = self._agent_info_cache[agent_url]
            else:
                # Fetch the agent card
                agent_card_response = await httpx_client.get(
                    f'{agent_url}{AGENT_CARD_WELL_KNOWN_PATH}'
                )
                agent_card_data = self._agent_info_cache[agent_url] = (
                    agent_card_response.json()
                )
            
            # Create AgentCard from data
            from a2a.types import AgentCard
            agent_card = AgentCard(**agent_card_data)
            
            # Create A2A client with the agent card
            config = ClientConfig(
                httpx_client=httpx_client,
                supported_transports=[
                    TransportProtocol.jsonrpc,
                    TransportProtocol.http_json,
                ],
                use_client_preference=True,
            )
            factory = ClientFactory(config)
            client = factory.create(agent_card)
            
            # Create the message object
            message_obj = create_text_message_object(content=message)
            
            # Send the message and collect responses
            responses = []
            async for response in client.send_message(message_obj):
                responses.append(response)
            
            # The response is a tuple - get the first element (Task object)
            if (
                responses
                and isinstance(responses[0], tuple)
                and len(responses[0]) > 0
            ):
                task = responses[0][0]  # First element of the tuple
                
                # Extract text: task.artifacts[0].parts[0].root.text
                try:
                    return task.artifacts[0].parts[0].root.text
                except (AttributeError, IndexError):
                    return str(task)
            
            return 'No response received'


# Enhanced convenience function with context support
async def call_agent(
    agent_url: str, 
    message: str,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Call an A2A agent with a message and optional conversation context.
    
    Args:
        agent_url: The agent's URL
        message: The user's message
        context: Optional conversation context including:
            - history: Previous conversation turns
            - customer_id: Known customer ID
            - session_id: Session identifier
    
    Returns:
        The agent's response as a string
    """
    # Build enhanced message with context embedded
    full_message = message
    
    if context:
        context_parts = []
        
        # Add customer ID if known
        if context.get('customer_id'):
            context_parts.append(f"[CONTEXT: Customer ID is {context['customer_id']}]")
        
        # Add recent conversation history
        if context.get('history'):
            recent = context['history'][-2:]  # Last 2 turns
            if recent:
                context_parts.append("\n[RECENT CONVERSATION:")
                for i, turn in enumerate(recent, 1):
                    user_msg = turn.get('user', '')[:100]
                    agent_msg = turn.get('assistant', '')[:100]
                    context_parts.append(f"  Turn {i}:")
                    context_parts.append(f"    User: {user_msg}")
                    context_parts.append(f"    Agent: {agent_msg}")
                context_parts.append("]\n")
        
        # Prepend context to message
        if context_parts:
            full_message = "\n".join(context_parts) + "\n\nCURRENT MESSAGE: " + message
    
    # Use the original client to send the enhanced message
    client = A2ASimpleClient()
    return await client.create_task(agent_url, full_message)