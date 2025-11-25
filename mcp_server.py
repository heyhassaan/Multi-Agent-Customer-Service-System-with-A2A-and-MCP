from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime

DB_PATH = "mcp_demo.db"

app = Flask(__name__)

def db_conn(path=DB_PATH):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/mcp/get_customer/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    conn = db_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({'error':'not found'}), 404

@app.route('/mcp/list_customers', methods=['GET'])
def list_customers():
    status = request.args.get('status')
    limit = request.args.get('limit', type=int)
    q = 'SELECT * FROM customers'
    params = []
    if status:
        q += ' WHERE status = ?'
        params.append(status)
    if limit:
        q += ' LIMIT ?'
        params.append(limit)
    conn = db_conn()
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/mcp/update_customer/<int:customer_id>', methods=['POST'])
def update_customer(customer_id):
    data = request.json or {}
    fields = []
    params = []
    allowed = ('name','email','phone','status')
    for k in allowed:
        if k in data:
            fields.append(f"{k} = ?")
            params.append(data[k])
    params.append(datetime.utcnow().isoformat())
    params.append(customer_id)
    if not fields:
        return jsonify({'error':'no valid fields'}), 400
    q = f"UPDATE customers SET {', '.join(fields)}, updated_at = ? WHERE id = ?"
    conn = db_conn()
    c = conn.cursor()
    c.execute(q, params)
    conn.commit()
    conn.close()
    return jsonify({'status':'ok'})

@app.route('/mcp/create_ticket', methods=['POST'])
def create_ticket():
    data = request.json or {}
    customer_id = data.get('customer_id')
    issue = data.get('issue')
    priority = data.get('priority','low')
    if not customer_id or not issue:
        return jsonify({'error':'missing fields'}), 400
    conn = db_conn()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute('INSERT INTO tickets (customer_id, issue, status, priority, created_at) VALUES (?, ?, ?, ?, ?)',
              (customer_id, issue, 'open', priority, now))
    conn.commit()
    ticket_id = c.lastrowid
    conn.close()
    return jsonify({'ticket_id': ticket_id})

@app.route('/mcp/get_customer_history/<int:customer_id>', methods=['GET'])
def get_customer_history(customer_id):
    conn = db_conn()
    rows = conn.execute('SELECT * FROM tickets WHERE customer_id = ? ORDER BY created_at DESC', (customer_id,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

if __name__ == '__main__':
    print('Starting MCP server on http://127.0.0.1:8000')
    app.run(host='127.0.0.1', port=8000, debug=False, use_reloader=False)
