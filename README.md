# Banking Agent (MVP)

This is a prototype customer-facing AI agent for answering banking questions using Azure OpenAI and FastAPI.
The live, working demo is at:  
👉 https://www.moreyummy.com/bankagent-demo/

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

All dependencies are pinned in `requirements.txt` for reproducibility. A future update may split runtime and development requirements.

## Project Structure

banking-agent/
├── app/                    # Core FastAPI app
│   ├── api.py              # Route definitions
│   ├── main.py             # FastAPI app creation
│   └── models.py           # Pydantic request/response models
├── clients/                # Client-specific configs
│   └── demobank/           # Example client (others handled in branches)
│       └── documents/
│           ├── faq.yaml
│           └── prompt.yaml
├── config/                 # Example environment configs
│   └── azure.env.example   # Template (copy to azure.env locally)
├── examples/               # Demo frontend (reference only)
│   ├── README.md
│   ├── index.html          # The index file mentioned above in the live example on moreyummy.com
│   ├── chat.js
│   └── style.css
├── utils/                  # Helper modules
│   ├── README.md
│   ├── logger.py           # Centralized logging
│   ├── match_faq.py        # FAQ fuzzy matching
│   ├── pdf_cleaner.py      # Clean PDF text for ingestion
│   ├── preprocess_input.py # Normalize/sanitize input
│   ├── rag_ingest.py       # Ingest PDFs into Chroma
│   ├── rag_retriever.py    # RAG document retrieval
│   ├── sanitize.py         # Input sanitization
│   └── yaml_loader.py      # Safe YAML loader
├── prompts/                # Prompt templates (.gitkeep placeholder)
├── tests/                  # Unit tests (.gitkeep placeholder)
├── archives/               # Archived files and prototypes
│   ├── agent.py
│   └── ROADMAP_v1.md
├── Dockerfile              # Container build definition
├── requirements.txt        # Python dependencies
├── startup.sh              # Container entrypoint (gunicorn/uvicorn)
├── README.md               # Project overview (this file)
└── RELEASE_NOTES.md        # Version history
