# This file -- api.py -- defines the API routes (also called endpoints) for this FastAPI app. 
# These are the specific HTTP paths that the backend listens to — like /ask — and it handles incoming requests.

# --- FastAPI & typing imports ---
from fastapi import APIRouter, HTTPException           # APIRouter allows modular route organization
from fastapi.responses import StreamingResponse
from app.models import UserQuery, AgentResponse        # Pydantic models for input/output validation

# --- Internal modules for processing ---
from utils.yaml_loader import load_faq, load_system_prompt # Load FAQ and system prompt from YAML files 
from utils.match_faq import find_best_match            # Fuzzy match input to FAQ
from utils.sanitize import sanitize_input              # Sanitize user input for safety
from utils.logger import get_logger                    # Custom logger for structured logging
from utils.rag_retriever import get_top_chunks         # RAG chunk retriever from Chroma DB
from utils.preprocess_input import preprocess_input    # Preprocess: strip greetings, detect risky keywords

# --- Azure OpenAI integration ---
from openai import AzureOpenAI                         # OpenAI client (via Azure)
import os
from dotenv import load_dotenv        

# -- For streaming responses ---
import json                 # Loads .env vars into environment

# --- Set up the route manager ---
router = APIRouter()                                   # Think of this as a "sub-app" for routing
load_dotenv()                                          # Load secrets from .env
logger = get_logger()                                  # Get shared logger instance

# --- Setup globals from .env ---
client_id = os.getenv("CLIENT_ID", "demobank")         # Use .env or default to 'demobank'
faq_data = load_faq(client_id)                         # Load corresponding FAQ YAML
system_prompt = load_system_prompt(client_id)          # Load system instructions from YAML
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")      # Which GPT model deployment to use

# --- Initialize OpenAI client for Azure ---
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# --- In-memory context trackers ---
session_history = {}  # Tracks chat messages per session
session_state = {}    # Tracks structured state like current flow steps

# --- Business Checking Flow Handler ---
def handle_business_checking_flow(user_input: str, session_id: str) -> dict:
    state = session_state[session_id]
    step = state.get("step", 1)

    if step == 1:
        state["business_name"] = user_input
        state["step"] = 2
        return {"source": "multi-step", "answer": "What type of business is it (e.g., LLC, sole proprietorship, partnership)?"}

    elif step == 2:
        state["business_type"] = user_input
        state["step"] = 3
        return {"source": "multi-step", "answer": "Do you already have an EIN (Employer Identification Number)?"}

    elif step == 3:
        state["has_ein"] = user_input
        state["step"] = 4
        return {"source": "multi-step", "answer": "Which state is your business registered in?"}

    elif step == 4:
        state["state"] = user_input
        state["step"] = 5
        return {"source": "multi-step", "answer": "How many people will be authorized to sign on this account?"}

    elif step == 5:
        state["signers"] = user_input
        state["step"] = 6
        summary = (
            f"Business Name: {state['business_name']}\n"
            f"Type: {state['business_type']}\n"
            f"EIN: {state['has_ein']}\n"
            f"State: {state['state']}\n"
            f"Authorized Signers: {state['signers']}"
        )
        return {
            "source": "multi-step",
            "answer": f"Thanks! I have the following info:\n\n{summary}\n\nWould you prefer a secure online link or to schedule an in-branch appointment?"
        }

    elif step == 6:
        session_state[session_id] = {}  # Clear state
        return {
            "source": "multi-step",
            "answer": "Perfect — I've noted your preference. A representative will follow up shortly!"
        }

    else:
        session_state[session_id] = {}
        return {"source": "multi-step", "answer": "Sorry, I lost track of the steps. Let’s start again — what’s the name of your business?"}

# --- API Endpoints ---
@router.post("/ask", response_model=AgentResponse)     # POST /ask — takes in a UserQuery, returns AgentResponse
def ask_question(payload: UserQuery):
    raw_input = payload.question                       # Extract the question from request payload
    session_id = payload.session_id                    # Track conversation session
    current_client = payload.client_id or client_id    # Allow override of client_id per request (optional)

    # Sanitize & Preprocess
    sanitized = sanitize_input(raw_input)
    preprocessed = preprocess_input(sanitized)

    logger.info(f"[API] Client: {current_client} | Session: {session_id} | Raw Input: {raw_input}")
    logger.debug(f"[API] Sanitized Input: {sanitized} | Cleaned Input: {preprocessed['cleaned']}")

    # --- Greeting only ---
    if preprocessed["is_greeting_only"]:
        return {"source": "greeting", "answer": "Hi there! How can I help you today?"}

    # --- Multi-step flow handler ---
    if session_id in session_state and session_state[session_id].get("flow") == "business_checking":
        return handle_business_checking_flow(preprocessed["cleaned"], session_id)

    # --- Smarter Multi-step trigger ---
    lower_input = preprocessed["cleaned"].lower()
    if "business checking" in lower_input and any(keyword in lower_input for keyword in ["open", "start", "apply"]):
        session_state[session_id] = {
            "flow": "business_checking",
            "step": 1
        }
        return {"source": "multi-step", "answer": "Great! What's the name of your business?"}

    # --- FAQ match with suppression toggle ---
    if session_id not in session_state or not session_state[session_id].get("flow"):
        answer = find_best_match(
            preprocessed["cleaned"],
            faq_data,
            suppress_short_matches=preprocessed["contains_sensitive_terms"],
            session_id=session_id  # <-- 🔥 this is the key addition
        )
    if answer:
        logger.info(f"[API] [FAQ MATCH] Answer: {answer[:300]}")
        return {"source": "faq", "answer": answer}

    # --- RAG Chunk Retrieval ---
    rag_chunks = get_top_chunks(preprocessed["cleaned"], k=4)
    rag_context = "\n\n".join([chunk for chunk, _ in rag_chunks])

    # Initialize session history if new session
    if session_id not in session_history:
        session_history[session_id] = [
            {"role": "system", "content": system_prompt}
        ]

    # Append RAG-enhanced user input to chat history
    session_history[session_id].append(
        {"role": "user", "content": f"Context:\n{rag_context}\n\nQuestion:\n{preprocessed['cleaned']}"}
    )

    try:
        # Query Azure OpenAI with session-aware messages
        response = client.chat.completions.create(
            model=deployment,
            messages=session_history[session_id]
        )

        gpt_answer = response.choices[0].message.content

        # Append assistant reply to session history
        session_history[session_id].append(
            {"role": "assistant", "content": gpt_answer}
        )

        logger.info(f"[API] [GPT RESPONSE] Answer: {gpt_answer[:300]}")
        return {"source": "gpt", "answer": gpt_answer}

    except Exception as e:
        logger.exception("Error querying GPT")          # Log full traceback for debugging
        raise HTTPException(status_code=500, detail="Internal error querying GPT.")


@router.post("/ask_stream")
async def ask_stream(payload: dict):
    question = payload.get("question", "")
    session_id = payload.get("session_id", "")

    if not session_id:
        session_id = "default"

    # reuse your existing logic
    sanitized = sanitize_input(question)
    preprocessed = preprocess_input(sanitized)

    rag_chunks = get_top_chunks(preprocessed["cleaned"], k=4)
    rag_context = "\n\n".join([chunk for chunk, _ in rag_chunks])

    if session_id not in session_history:
        session_history[session_id] = [
            {"role": "system", "content": system_prompt}
        ]
    session_history[session_id].append(
        {
            "role": "user",
            "content": f"Context:\n{rag_context}\n\nQuestion:\n{preprocessed['cleaned']}"
        }
    )
    messages = session_history[session_id]

    def event_generator():
        stream = client.chat.completions.create(
            model=deployment,  # keep your deployment name for now
            messages=messages,
            stream=True,
        )

        full_answer = ""

        for chunk in stream:
            try:
                text = chunk.choices[0].delta.content
            except Exception:
                continue

            if not text:
                continue

            full_answer += text

            yield json.dumps({
                "type": "delta",
                "text": text
            }) + "\n"

        # save to history (critical)
        session_history[session_id].append(
            {"role": "assistant", "content": full_answer}
        )

        yield json.dumps({"type": "final"}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")