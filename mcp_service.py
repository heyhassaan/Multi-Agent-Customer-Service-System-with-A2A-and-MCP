"""
MCP Service Implementation
FastMCP server exposing database tools
"""
from mcp.server.fastmcp import FastMCP
import sqlite3
import json
from typing import List, Optional

# Initialize FastMCP server
mcp = FastMCP("Multi-Agent Service MCP")

DB_PATH = "multi_agent_service.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@mcp.tool()
def get_customer(customer_id: int) -> str:
    """Get customer details by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    customer = cursor.fetchone()
    conn.close()
    
    if customer:
        return json.dumps(dict(customer))
    return "Customer not found"

@mcp.tool()
def list_customers(status: Optional[str] = None, limit: int = 10) -> str:
    """List customers, optionally filtered by status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM customers"
    params = []
    
    if status:
        query += " WHERE status = ?"
        params.append(status)
        
    query += " LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    customers = cursor.fetchall()
    conn.close()
    
    return json.dumps([dict(c) for c in customers])

@mcp.tool()
def update_customer(customer_id: int, data: str) -> str:
    """Update customer details. Data should be a JSON string of fields to update."""
    try:
        updates = json.loads(data)
    except json.JSONDecodeError:
        return "Invalid JSON data"
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if customer exists
    cursor.execute("SELECT id FROM customers WHERE id = ?", (customer_id,))
    if not cursor.fetchone():
        conn.close()
        return "Customer not found"
    
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values())
    values.append(customer_id)
    
    query = f"UPDATE customers SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    
    try:
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        return f"Customer {customer_id} updated successfully"
    except Exception as e:
        conn.close()
        return f"Error updating customer: {str(e)}"

@mcp.tool()
def create_ticket(customer_id: int, issue: str, priority: str = "medium") -> str:
    """Create a new support ticket."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if customer exists
    cursor.execute("SELECT id FROM customers WHERE id = ?", (customer_id,))
    if not cursor.fetchone():
        conn.close()
        return "Customer not found"
        
    try:
        cursor.execute(
            "INSERT INTO tickets (customer_id, issue, priority, status) VALUES (?, ?, ?, 'open')",
            (customer_id, issue, priority)
        )
        ticket_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return f"Ticket created with ID {ticket_id}"
    except Exception as e:
        conn.close()
        return f"Error creating ticket: {str(e)}"

@mcp.tool()
def get_customer_history(customer_id: int) -> str:
    """Get ticket history for a customer."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tickets WHERE customer_id = ?", (customer_id,))
    tickets = cursor.fetchall()
    conn.close()
    
    if tickets:
        return json.dumps([dict(t) for t in tickets])
    return "No tickets found for this customer"

@mcp.tool()
def get_customers_with_open_tickets(status: Optional[str] = None, limit: int = 50) -> str:
    """Get customers who have open tickets. Optionally filter by customer status (active/disabled)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT DISTINCT c.* 
        FROM customers c
        INNER JOIN tickets t ON c.id = t.customer_id
        WHERE t.status = 'open'
    """
    params = []
    
    if status:
        query += " AND c.status = ?"
        params.append(status)
    
    query += " LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    customers = cursor.fetchall()
    conn.close()
    
    if customers:
        return json.dumps([dict(c) for c in customers])
    return "No customers found with open tickets"

if __name__ == "__main__":
    mcp.run()
