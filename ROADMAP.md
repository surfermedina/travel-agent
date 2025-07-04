# Banking Agent Roadmap

## ✅ Stage 0: Setup & Structure
- [x] Create folder structure
- [x] Create and activate virtual environment
- [x] Install dependencies
- [x] Configure .env and .gitignore
- [x] Initialize GitHub repo

## 🔨 Stage 1: MVP Agent
- [ ] Build main.py FastAPI endpoint
- [ ] Build agent.py logic using Azure OpenAI
- [ ] Add basic system prompt support
- [ ] Test via Swagger UI

## 🔐 Stage 2: Client Data Privacy & Auth
- [ ] Multi-client separation (config, prompts, logs)
- [ ] Discuss session-based access tokens (if needed)

## 🧠 Stage 3: Vector Search (Azure AI Search)
- [ ] Ingest docs and metadata
- [ ] Retrieve context to augment chat
- [ ] Include RAG response flow

## 📦 Stage 4: Docker & Deployment
- [ ] Create Dockerfile
- [ ] Test container locally
- [ ] Deploy via Azure or Render

## 📈 Stretch Goals
- [ ] Multi-turn history
- [ ] Integrate with frontend UI
- [ ] Client onboarding automation