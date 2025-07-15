# This file -- api.py -- defines the API routes (also called endpoints) for this FastAPI app. 
# These are the specific HTTP paths that the backend listens to — like /ask — and it handles incoming requests.

# --- FastAPI & typing imports ---
from fastapi import APIRouter, HTTPException           # APIRouter allows modular route organization
from app.models import UserQuery, AgentResponse        # Pydantic models for input/output validation

# --- Internal modules for processing ---
from utils.yaml_loader import load_faq, load_system_prompt # Load FAQ and system prompt from YAML files 
from utils.match_faq import find_best_match            # Fuzzy match input to FAQ
from utils.sanitize import sanitize_input              # Sanitize user input for safety
from utils.logger import get_logger                    # Custom logger for structured logging

# --- Azure OpenAI integration ---
from openai import AzureOpenAI                         # OpenAI client (via Azure)
import os
from dotenv import load_dotenv                         # Loads .env vars into environment

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

# --- In-memory context tracker ---
# This dictionary stores conversation history for each session.
# Example: { "session_id_123": [{"role": "user", "content": "..."}, ...] }
session_history = {}

# --- API Endpoints ---
# This endpoint handles user queries and returns answers from either the FAQ or GPT.
# It also tracks message history per session, enabling future multi-turn dialogue.
@router.post("/ask", response_model=AgentResponse)     # POST /ask — takes in a UserQuery, returns AgentResponse
def ask_question(payload: UserQuery):
    raw_input = payload.question                       # Extract the question from request payload
    user_question = sanitize_input(raw_input)          # Sanitize any dangerous characters
    session_id = payload.session_id                    # Track conversation session
    current_client = payload.client_id or client_id    # Allow override of client_id per request (optional)

    logger.info(f"[API] Client: {current_client} | Session: {session_id} | Raw Input: {raw_input}")
    logger.debug(f"[API] Sanitized Input: {user_question}")

    # First, try to match the question to the FAQ
    answer = find_best_match(user_question, faq_data)

    if answer:
        logger.info("[API] [FAQ MATCH] Answer returned from FAQ.")
        return {"source": "faq", "answer": answer}

    logger.info("[API] [NO FAQ MATCH] Querying GPT...")

    # Initialize session history if new session
    if session_id not in session_history:
        session_history[session_id] = [
            {"role": "system", "content": system_prompt}
        ]

    # Append current user input to chat history
    session_history[session_id].append(
        {"role": "user", "content": user_question}
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

        return {"source": "gpt", "answer": gpt_answer}

    except Exception as e:
        logger.exception("Error querying GPT")          # Log full traceback for debugging
        raise HTTPException(status_code=500, detail="Internal error querying GPT.")
