# langgraph-hil-approval  
Human‑in‑the‑loop approval workflow powered by LangGraph and FastAPI

## Overview
langgraph-hil-approval is a lightweight framework for building AI agents that require explicit human approval before proceeding to the next step in a workflow. It leverages **LangGraph** for stateful agent orchestration and **FastAPI** for exposing a stateless REST API, enabling easy integration into existing infrastructures.

The project demonstrates how to:
* Create multi‑step approval chains
* Persist conversation state in a database
* Expose endpoints for agents, workers, and end users
* Run the entire stack in Docker

## Features
- **Human‑in‑the‑loop (HITL)** integration with LangGraph  
- Stateless FastAPI service with JWT authentication  
- Persistent workflow state via SQLite / PostgreSQL  
- Automated testing (unit tests + API contract)  
- CI/CD pipeline on GitHub Actions  
- Docker support for local and production deployments  

## Tech Stack
| Layer | Technology |
|-------|------------|
| Agent orchestration | LangGraph |
| Backend framework | FastAPI |
| Database | SQLite (dev), PostgreSQL (prod) |
| Authentication | JWT |
| Testing | pytest, httpx |
| CI/CD | GitHub Actions |
| Containerization | Docker / docker‑compose |

## Installation

```bash
# Clone the repository
git clone https://github.com/jammyjam-j/langgraph-hil-approval

cd langgraph-hil-approval

# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate   # On Windows use `.venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

### Docker

```bash
docker compose up --build
```

The service will be available at `http://localhost:8000`.

## Usage Examples

### Starting the FastAPI server (dev)

```bash
uvicorn app.main:app --reload
```

### Creating a new approval request

```python
import httpx

client = httpx.Client()

payload = {
    "title": "Budget Increase",
    "description": "Requesting additional funds for Q4 marketing.",
    "initiator_id": 42
}

response = client.post("http://localhost:8000/api/requests", json=payload)
print(response.json())
```

### Approving a step

```bash
curl -X POST http://localhost:8000/api/requests/<request_id>/approve \
     -H "Authorization: Bearer <JWT_TOKEN>"
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST /api/requests` | Create a new approval request |
| `GET /api/requests/{id}` | Retrieve request details |
| `POST /api/requests/{id}/approve` | Approve the current step |
| `POST /api/requests/{id}/reject` | Reject the current step |
| `GET /api/requests` | List all requests (admin only) |

All endpoints require a valid JWT token. See `app/dependencies.py` for authentication details.

## References and Resources
- [Human-in-the-loop - Docs by LangChain](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop)
- [LangGraph Human in the Loop: Multi-Step Approval Workflows ...](https://langchain-tutorials.github.io/langgraph-human-loop-multi-step-approval-checkpoints/)
- [Don’t Let Your AI Agents Run Wild: Building a Human-in-the‑Loop System with LangGraph](https://shubhamvora.medium.com/dont-let-your-ai-agents-run-wild-building-a-human-in-the-loop-system-with-langgraph-0189bf0c8e20)
- [Human-in-the-Loop LangGraph Demo (FastAPI + React)](https://github.com/esurovtsev/langgraph-hitl-fastapi-demo)
- [Implementing Human-in-the-Loop in a stateless REST API with ...](https://www.evanlivelo.com/blog/2025/10/13/stateless-api-hitl-langgraph)

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository  
2. Create a feature branch (`git checkout -b feature-xyz`)  
3. Commit your changes (`git commit -m "Add feature xyz"`)  
4. Push to the fork (`git push origin feature-xyz`)  
5. Open a pull request against https://github.com/jammyjam-j/langgraph-hil-approval

Please ensure tests pass and linting is satisfied before submitting.

## License
MIT ©