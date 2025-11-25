# Multi-Agent Customer Service Demo

This repository demonstrates a simple multi-agent customer service system with Agent-to-Agent (A2A) coordination and a Model Context Protocol (MCP) server backed by SQLite.

Contents:
- `database_setup.py` — creates `mcp_demo.db` and seeds sample customers and tickets.
- `mcp_server.py` — Flask MCP server exposing endpoints for data access.
- `agents.py` — `RouterAgent`, `CustomerDataAgent`, and `SupportAgent` with A2A logging.
- `runner.py` — seeds DB, starts MCP server, runs demo scenarios.
- `requirements.txt` — Python dependencies.

Setup (Windows PowerShell):
```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python runner.py
```

What to expect:
- The runner seeds the database, starts the MCP server, creates agents, and executes multiple demo scenarios showing A2A communication and MCP calls.

Notes:
- This is a demo/prototype to showcase coordination patterns. For production, use proper async servers, authentication, and robust parsing.



