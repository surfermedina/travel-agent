# Banking Agent – Version 1.1 Release Notes

**Release Date:** July 9, 2025  
**Version Tag:** v1.1.0  
**Project:** banking-agent  
**Author:** Joel “Ed” Medina  
**Website:** https://moreyummy.com

---

## Overview

Version 1.1 delivers the first **publicly deployed**, Azure-hosted release of the Banking Agent with full **frontend integration**, secure CORS configuration, and end-to-end query resolution via both FAQ matching and Azure OpenAI fallback. This version is stable, web-accessible, and ready for client demos and further modular expansion.

---

## What’s New in v1.1

### Frontend Web Chat (Public UI)
- Integrated a minimalist HTML/JS chat frontend (`index.html`) for direct user interaction.
- Supports message submission, real-time feedback, and live query resolution via `/ask` endpoint.

### FastAPI Web Server and Azure Hosting
- Application served via `gunicorn` using a custom `startup.sh` script.
- Deployed using Azure App Services (Python/Linux) with GitHub-integrated CI/CD.

### Secure CORS Configuration
- Locked down CORS policy to allow only approved domains:
  - `https://bankagent.moreyummy.com`
  - `https://moreyummy.com`
- Temporary support for `localhost:5500` allowed during development and removed post-deploy.

### GitHub-Centered Deployment Pipeline
- Full source-controlled pipeline, eliminating manual edits in Kudu.
- Startup script (`startup.sh`) defines app entrypoint and Python environment activation.

---

## Core Features (Unchanged from v1.0)

- **FAQ Matching with RapidFuzz**
- **LLM Fallback via Azure OpenAI**
- **Client-Specific Knowledge Bases**
- **Per-Session Logging**
- **Secure Input Sanitization**
- **YAML File Handling with Safety Checks**

---

## Deployment Architecture

Frontend → JavaScript Fetch
https://bankagent.moreyummy.com/ask
↓
Backend → FastAPI Router
|-> FAQ Matcher
|-> Azure OpenAI GPT-4 Fallback
↓
Logging → /logs/session_<timestamp>.log

---

## Directory Structure (Updated)

banking-agent/
├── app/
│ ├── api.py
│ ├── models.py
│ └── main.py
├── clients/
│ └── demobank/
│ └── documents/
│ └── faq.yaml
├── static/
│ └── index.html
├── requirements.txt
├── startup.sh
├── .env.example
├── logs/
│ └── session_*.log
├── .gitignore
└── README.md


---

## Known Limitations

- Frontend styling is minimal and will be updated in a future release.
- No RAG (Retrieval-Augmented Generation) yet — FAQ-only responses.
- Logging is local only (not yet integrated with Azure Monitoring or Application Insights).

---

## Planned Enhancements

- CSS/UI polish to match the main moreyummy.com site.
- YAML expansion and full RAG support for long-form documents.
- Add redeployment documentation for consistent multi-client rollout.
- Docker containerization and optional Azure Container Apps migration.
- Add API key authentication layer for frontend calls.

---

## Contact and Attribution

This release is intended for client demonstration, internal documentation, and early-stage partner onboarding.

© 2025 Joel “Ed” Medina. All rights reserved.  
All software and documentation are the intellectual property of Joel Medina and MoreYummy.com. Unauthorized use, reproduction, or distribution is prohibited without written permission.

**Website:** [https://moreyummy.com](https://moreyummy.com)  
**Email:** eddie.medina@gmail.com
