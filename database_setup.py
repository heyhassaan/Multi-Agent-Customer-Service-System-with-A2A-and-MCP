import sqlite3
from datetime import datetime

DB_PATH = "mcp_demo.db"

def create_db(path=DB_PATH):
    conn = sqlite3.connect(path)
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        status TEXT CHECK(status IN ('active','disabled')) DEFAULT 'active',
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        issue TEXT NOT NULL,
        status TEXT CHECK(status IN ('open','in_progress','resolved')) DEFAULT 'open',
        priority TEXT CHECK(priority IN ('low','medium','high')) DEFAULT 'low',
        created_at DATETIME,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    )
    ''')

    conn.commit()

    # Insert sample customers
    now = datetime.utcnow().isoformat()
    sample_customers = [
        (1, 'Alice Smith', 'alice@example.com', '555-0101', 'active', now, now),
        (2, 'Bob Jones', 'bob@example.com', '555-0102', 'active', now, now),
        (3, 'Carol Lee', 'carol@example.com', '555-0103', 'disabled', now, now),
        (4, 'David Kim', 'david@example.com', '555-0104', 'active', now, now),
        (5, 'Eve Turner', 'eve@example.com', '555-0105', 'active', now, now),
        (12345, 'Premium Customer', 'premium@example.com', '555-9999', 'active', now, now),
    ]

    c.executemany('''
    INSERT OR REPLACE INTO customers (id, name, email, phone, status, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', sample_customers)

    # Insert sample tickets
    sample_tickets = [
        (1, 1, 'Cannot login', 'open', 'high', now),
        (2, 2, 'Billing discrepancy', 'in_progress', 'medium', now),
        (3, 5, 'Feature request', 'resolved', 'low', now),
        (4, 12345, 'Payment failed twice', 'open', 'high', now),
        (5, 12345, 'Upgrade inquiry', 'open', 'medium', now),
    ]

    c.executemany('''
    INSERT OR REPLACE INTO tickets (id, customer_id, issue, status, priority, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_tickets)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    print(f"Creating database at {DB_PATH} and inserting sample data...")
    create_db()
    print("Done.")
