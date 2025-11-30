"""
MCP Tools Wrapper for ADK Agents
Wraps MCP service functions as callable tools for ADK agents
"""
from mcp_service import (
    get_customer,
    list_customers,
    update_customer,
    create_ticket,
    get_customer_history,
    get_customers_with_open_tickets
)

# ADK agents can use functions directly as tools
# These are simple wrappers that maintain the MCP interface

def tool_get_customer(customer_id: int) -> str:
    """Get customer details by ID. Uses customers.id field."""
    return get_customer(customer_id)

def tool_list_customers(status: str = None, limit: int = 10) -> str:
    """List customers, optionally filtered by status. Uses customers.status field."""
    return list_customers(status, limit)

def tool_update_customer(customer_id: int, data: str) -> str:
    """Update customer details. Data should be a JSON string. Uses customers fields."""
    return update_customer(customer_id, data)

def tool_create_ticket(customer_id: int, issue: str, priority: str = "medium") -> str:
    """Create a new support ticket. Uses tickets fields."""
    return create_ticket(customer_id, issue, priority)

def tool_get_customer_history(customer_id: int) -> str:
    """Get ticket history for a customer. Uses tickets.customer_id field."""
    return get_customer_history(customer_id)

def tool_get_customers_with_open_tickets(status: str = None, limit: int = 50) -> str:
    """Get customers who have open tickets. Optionally filter by customer status."""
    return get_customers_with_open_tickets(status, limit)

def create_mcp_tools():
    """Create list of MCP tools for ADK agents."""
    return [
        tool_get_customer,
        tool_list_customers,
        tool_update_customer,
        tool_create_ticket,
        tool_get_customer_history,
        tool_get_customers_with_open_tickets,
    ]

