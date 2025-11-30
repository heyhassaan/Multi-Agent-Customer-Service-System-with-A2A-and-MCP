# Multi-Agent Customer Service (A2A + MCP)

This project implements a customer-support system that strictly follows the Model Context Protocol (MCP) and Google’s Agent-to-Agent (A2A) specifications. Three independent agents (Router, Customer Data, Support) run as separate A2A services, talk to each other via the A2A protocol, and use an MCP server to query/update a SQLite database.

## Architecture Overview

- **Router Agent (Orchestrator)** – Receives user queries, analyzes intent, delegates to specialists, and composes the final response.
- **Customer Data Agent** – Talks to the MCP server to read/update customer records and ticket history.
- **Support Agent** – Handles support workflows, ticket creation, and escalations; requests context from the data agent when needed.
- **FastMCP Server** – Exposes the required tools (get/list/update customers, create tickets, get history, plus helper queries) over the MCP protocol backed by `multi_agent_service.db`.

Each agent publishes an AgentCard at `/.well-known/agent-card.json`, supports JSON-RPC transports, and can be exercised independently (e.g., via MCP Inspector or any A2A client).

## Prerequisites

- Python 3.11+
- `uv` for dependency management
- Google API key (Gemini models) stored in `.env`

## Quick Start

```bash
# 1. Create & activate venv
uv venv .venv
source .venv/bin/activate

# 2. Install project deps
uv pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env   # or create manually
echo "GOOGLE_API_KEY=your_key" >> .env

# 4. Initialize database (creates multi_agent_service.db with seed data)
python db_initialize.py

# 5. (Optional) verify MCP tools
python test_mcp.py
```

## Running the A2A System

Open two terminals (both inside the virtual environment):

1. **Start all A2A agents**:
   ```bash
   python agents_server.py
   ```
   - Router: `http://127.0.0.1:10020`
   - Customer Data: `http://127.0.0.1:10021`
   - Support: `http://127.0.0.1:10022`

2. **Run demo scenarios through the router**:
   ```bash
   python demo_scenarios.py
   ```
   This script uses the simple A2A client (`agent_client.py`) to send five representative queries (simple lookup, upgrade help, open-ticket report, escalation, multi-intent update/history).

> Tip: you can also call individual agents using `call_agent()` from `agent_client.py` or any A2A-compliant client.

## Project Structure

- `agents_definitions.py` – Definitions of Router, Customer Data, and Support agents + AgentCards.
- `agents_server.py` – Spins up each agent as an independent A2A HTTP server.
- `agent_client.py` – Helper for invoking agents via A2A protocol with conversation support.
- `demo_scenarios.py` – Demo driver that exercises all required scenarios with multi-turn support.
- `mcp_service.py` – FastMCP server implementation exposing database tools backed by SQLite.
- `mcp_tools_wrapper.py` – Wrappers exposing MCP functions as callable ADK tools.
- `db_initialize.py` – Creates/initializes `multi_agent_service.db` with seed data.
- `multi_agent_service.db` – SQLite database (usually ignored in git; regenerate via setup script).
- `README_A2A.md`, `REQUIREMENTS_ALIGNMENT.md`, etc. – Development notes (optional to keep).

Legacy LangGraph prototypes (`agents.py`, original `main.py`, labs) are no longer used; you can remove them if you only want the final A2A solution.

## Demo Runner (Jupyter Notebook)

Open `demo_runner.ipynb` in Jupyter to run an interactive demo that will:
1. Spin up all A2A agents in the background.
2. Execute `demo_scenarios.py` (all assignment scenarios).
3. Capture stdout/stderr plus server logs into `demo_output.md`.
4. Shut down the agents automatically.

Commit the generated `demo_output.md` (or regenerate it before submission) as proof of the end-to-end run.

## Testing / Validation

1. `python test_mcp.py` confirms MCP tool calls succeed.
2. `python demo_scenarios.py` (with servers running) demonstrates:
   - Simple info lookup
   - Coordinated “upgrade my account” flow
   - Complex `active customers with open tickets` query
   - Escalation / refund request
   - Multi-intent update + ticket history

Because the agents are independent A2A services, you can also run MCP Inspector or any A2A client against `http://127.0.0.1:1002x` to verify cards and task execution.
