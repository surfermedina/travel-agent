# Banking Agent (MVP)

This is a prototype customer-facing AI agent for answering banking questions using Azure OpenAI and FastAPI.

## Features
- `/ask` endpoint (FastAPI)
- Client-specific system prompts
- Environment-based config loading
- Scalable foundation for future vector search and RAG

## Getting Started

1. Clone the repo
2. Create a `.env` file (use `config/azure.env` as a template)
3. Activate the virtual environment
4. Run the API:
5. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to test

## Project Structure
banking-agent/
├── .gitignore
├── .env                     # Local config (excluded from Git)
├── README.md                # Overview and setup instructions
├── RELEASE_NOTES.md         # Version history and release notes
├── requirements.txt         # Python dependencies
├── index.html               # Demo frontend UI (local only)
├── style.css                # Stylesheet for frontend UI
├── main.py                  # FastAPI entry point
├── app/
│   ├── __init__.py
│   ├── api.py               # FastAPI route definitions
│   ├── main.py              # FastAPI app creation (referenced by uvicorn)
│   └── models.py            # Pydantic models for input/output
├── clients/
│   └── demobank/
│       └── documents/
│           ├── faq.yaml
│           └── prompt.yaml
├── logs/
│   └── session_*.log        # Timestamped log files
├── tests/                   # (Coming soon)
│   └── test_agent.py
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   ├── match_faq.py
│   ├── sanitize.py
│   └── yaml_loader.py