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

## Folder Structure
banking-agent/
│
├── main.py
├── agent.py
├── .env
├── .gitignore
├── clients/
├── config/
├── prompts/
├── tests/
├── vector-index/
└── README.md