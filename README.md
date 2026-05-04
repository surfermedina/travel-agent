# AI Travel Agent (Lisbon Demo)

An AI-powered travel assistant that delivers personalized itineraries through structured, multi-step dialogue.  

Built with a custom FastAPI backend, real-time streaming responses, and a modular architecture designed for scalable, multi-client deployments.

🔗 Live Demo: https://moreyummy.com/agents/travel-agent/

---

## Key Features

- Personalized itineraries via multi-step dialogue
- Guided planning (asks questions, maintains context)
- Real-time streaming responses (NDJSON)
- Intent-aware behavior (itinerary → flights → recommendations)
- Retrieval-Augmented Generation (RAG) for grounded answers
- Prompt-as-code (YAML-driven behavior control)
- Deterministic routing (flows vs RAG vs fallback)
- Session memory for multi-turn conversations

---

## Tech Stack

- Python + FastAPI backend
- Azure OpenAI (LLM)
- Streaming API responses
- Docker + Azure App Service deployment
- Modular API layer (OpenAPI / Swagger)
- Environment-driven, multi-client architecture

---

## How It Works

Frontend (HTML/JS chat UI)  
↓  
FastAPI `/ask_stream` endpoint  
↓  
Routing Layer:
- Structured flows (e.g., itinerary planning)
- RAG retrieval (custom knowledge base)
- LLM fallback  
↓  
Streaming response to client (real-time UX)

---

## Project Structure

travel-agent/
├── app/ # FastAPI backend
├── clients/ # Client-specific configs (Lisbon demo)
├── utils/ # RAG, routing, preprocessing
├── examples/ # Frontend chat UI (reference)
├── config/ # Environment templates
├── Dockerfile
├── startup.sh

---

## Local Setup

1. Clone repo  
2. Create `.env` from template  
3. Install dependencies:
    pip install -r requirements.txt
4. Run:
    uvicorn app.main:app --reload
5. Open:
http://127.0.0.1:8000/docs

---

## Notes

- Demo frontend included under `/examples`
- Background image excluded due to licensing
- Designed for reuse across multiple travel or business use cases

---

## About

Built by Joel “Ed” Medina  
https://moreyummy.com