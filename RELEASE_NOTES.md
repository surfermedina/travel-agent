# Release Notes

## v1.0.0 — Travel Agent Demo Launch

Initial public release of the AI Travel Agent, featuring a Lisbon-focused demo with multi-step itinerary planning and real-time streaming responses.

🔗 Demo: https://moreyummy.com/agents/travel-agent/

---

## Highlights

- Deployed FastAPI backend on Azure App Service
- Integrated web-based chat UI with streaming responses
- Implemented multi-step guided itinerary planning
- Added session-based memory for multi-turn conversations
- Enabled intent switching (itinerary → flights → recommendations)

---

## Core Capabilities

- Structured dialogue flows (guided planning)
- Retrieval-Augmented Generation (custom knowledge base)
- LLM fallback (Azure OpenAI)
- Deterministic routing between flows, RAG, and fallback
- Real-time streaming UX (NDJSON)

---

## Architecture

Frontend → FastAPI → Routing Layer → RAG / LLM → Streaming Response

---

## Known Limitations

- UI is intentionally minimal (demo-focused)
- Limited destination scope (Lisbon only)
- No persistent user accounts or saved trips

---

## Next Steps

- Expand destinations beyond Lisbon
- Enhance UI/UX (mobile + interaction design)
- Add persistent user sessions / saved itineraries
- Improve RAG coverage and content depth
- Add analytics and usage tracking

---

## Author

Joel “Ed” Medina  
https://moreyummy.com