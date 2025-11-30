"""
Database Initialization
Sets up multi_agent_service.db with tables and seed data
"""
import sqlite3
import datetime

def create_database():
    conn = sqlite3.connect('multi_agent_service.db')
    cursor = conn.cursor()

    # Initialize multi-agent service database with deterministic test data
    cursor.execute("PRAGMA foreign_keys = OFF;")
    cursor.execute("DROP TABLE IF EXISTS tickets;")
    cursor.execute("DROP TABLE IF EXISTS customers;")
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create Customers Table
    cursor.execute('''
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        status TEXT CHECK(status IN ('active', 'disabled')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create Tickets Table
    cursor.execute('''
    CREATE TABLE tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        issue TEXT NOT NULL,
        status TEXT CHECK(status IN ('open', 'in_progress', 'resolved')),
        priority TEXT CHECK(priority IN ('low', 'medium', 'high')),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
    ''')

    # Insert Test Data
    customers = [
        (1, 'Alice Smith', 'alice@example.com', '555-0101', 'active'),
        (2, 'Bob Jones', 'bob@example.com', '555-0102', 'active'),
        (3, 'Charlie Brown', 'charlie@example.com', '555-0103', 'disabled'),
        (4, 'Diana Prince', 'diana@example.com', '555-0104', 'active'),
        (5, 'Evan Wright', 'evan@example.com', '555-0105', 'active'),
        (12345, 'Priya Patel (Premium)', 'priya@example.com', '555-0999', 'active')
    ]

    cursor.executemany('''
    INSERT INTO customers (id, name, email, phone, status) VALUES (?, ?, ?, ?, ?)
    ''', customers)

    tickets = [
        (1, 'Cannot login to account', 'open', 'high'),
        (1, 'Billing inquiry', 'resolved', 'medium'),
        (2, 'Feature request: Dark mode', 'open', 'low'),
        (4, 'Payment failed', 'in_progress', 'high'),
        (5, 'Update profile picture', 'resolved', 'low'),
        (5, 'Follow-up: profile picture rendering issue', 'open', 'medium'),
        (12345, 'Account upgrade assistance', 'open', 'medium'),
        (12345, 'High priority refund review', 'open', 'high')
    ]

    cursor.executemany('''
    INSERT INTO tickets (customer_id, issue, status, priority) VALUES (?, ?, ?, ?)
    ''', tickets)

    conn.commit()
    conn.close()
    print("Database created and initialized with deterministic test data.")

if __name__ == '__main__':
    create_database()
