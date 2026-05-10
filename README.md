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
├── flows/ # Multi-step dialogue setup
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

---

## Adding a New Flow

Flows are reusable multi-step conversation paths triggered by specific phrases. They can also define post-completion actions such as email sending. New flows should not require api.py changes.

1. Create a new flow file [name]_flow.py, such as ...
   flows/hotel_booking_flow.py

2. Define the flow object
   Include:
   - name
   - default_state
   - triggers
   - fallback_message
   - steps
   - completion

   Example step types:
   - "collect"
   - "email_capture"

   Completion config includes:
   - system_prompt
   - prompt_template
   - response_source
   - email_enabled

3. Register the flow in flows/flow_registry.py

   Example:

   from flows.hotel_booking_flow import HOTEL_BOOKING_FLOW

   FLOW_REGISTRY = {
       ...
       "hotel_booking": HOTEL_BOOKING_FLOW
   }

4. Keep triggers specific
   Avoid overlapping/general phrases between the various flow.py files

5. (Optional, but advisable) Add a starter button in index.html

6. Test

---

# Assistant Discussion Flow & Orchestration Architecture

USER MESSAGE
    │
    ▼
chat.js
(frontend UI + streaming transport)
    │
    ▼
POST /ask_stream
(api.py)
    │
    ▼
sanitize_input()
preprocess_input()
(utils/)
    │
    ├── Greeting only?
    │       └── Return greeting response
    │
    ├── Active flow exists?
    │       │
    │       ▼
    │   get_active_flow()
    │   (flow_engine.py)
    │       │
    │       ▼
    │   handle_flow()
    │   (api.py)
    │       │
    │       ├── collect step
    │       │       │
    │       │       ├── collect_step_input()
    │       │       ├── advance_flow_step()
    │       │       ├── get_next_flow_prompt()
    │       │       └── session_state update
    │       │
    │       │       (flow_engine.py)
    │       │
    │       └── completion step
    │               │
    │               ├── execute_flow_completion()
    │               │   (api.py)
    │               │       │
    │               │       ├── render_completion_prompt()
    │               │       │   (flow_engine.py)
    │               │       │
    │               │       ├── flow config lookup
    │               │       │   (itinerary_flow.py)
    │               │       │
    │               │       ├── Azure OpenAI stream call
    │               │       └── return GPT stream iterator
    │               │
    │               ▼
    │       flow_generator()
    │       (api.py)
    │               │
    │               ├── iterate GPT stream chunks
    │               ├── emit NDJSON delta events
    │               ├── append assistant reply to session_history
    │               ├── clear session_state
    │               └── emit final event
    │
    ├── Flow trigger detected?
    │       │
    │       ├── detect_triggered_flow()
    │       ├── initialize_flow_state()
    │       └── get_initial_flow_prompt()
    │
    │       (flow_engine.py)
    │
    ├── FAQ fuzzy match?
    │       │
    │       ├── load_faq()
    │       │   (yaml_loader.py)
    │       │
    │       ├── faq.yaml
    │       │   (client FAQ knowledge base)
    │       │
    │       ├── find_best_match()
    │       │   (match_faq.py)
    │       │
    │       └── return FAQ response
    │
    └── RAG + GPT fallback
            │
            ├── get_top_chunks()
            │   (rag_retriever.py)
            │
            ├── Chroma vector retrieval
            │
            ├── append RAG context to session_history
            │
            ├── Azure OpenAI stream call
            │
            ├── event_generator()
            │   (api.py)
            │
            ├── emit NDJSON delta events
            └── append assistant response to session_history