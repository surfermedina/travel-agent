# This file -- api.py -- defines the API routes (also called endpoints) for this FastAPI app. 
# These are the specific HTTP paths that the backend listens to — like /ask — and it handles incoming requests.

# --- FastAPI & typing imports ---
from fastapi import APIRouter, HTTPException, BackgroundTasks   # APIRouter allows modular route organization
from fastapi.responses import StreamingResponse
from app.models import UserQuery, AgentResponse        # Pydantic models for input/output validation

# --- Internal modules for processing ---
from utils.yaml_loader import load_faq, load_system_prompt # Load FAQ and system prompt from YAML files 
from utils.match_faq import find_best_match            # Fuzzy match input to FAQ
from utils.sanitize import sanitize_input              # Sanitize user input for safety
from utils.logger import get_logger                    # Custom logger for structured logging
from utils.rag_retriever import get_top_chunks         # RAG chunk retriever from Chroma DB
from utils.preprocess_input import preprocess_input    # Preprocess: strip greetings, detect risky keywords
from utils.email_sender import send_itinerary_email    # Function to send itinerary emails via Resend API
from flows.flow_registry import FLOW_REGISTRY          # Central registry for multi-step flows
from flows.flow_engine import *                        # Flow execution engine functions for multi-step interactions

# --- Azure OpenAI integration ---
from openai import AzureOpenAI                         # OpenAI client (via Azure)
import os
from dotenv import load_dotenv        

# -- For streaming responses ---
import json                 # Loads .env vars into environment
import asyncio              # For async handling of streaming responses    

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

# --- Execute the final completion step for a flow (e.g. GPT itinerary generation) ---
def execute_flow_completion(flow,state,stream=False):

    """
    Execute the configured completion behavior
    for a flow.
    Args:
        flow (dict):
            Flow definition object.
        state (dict):
            Current collected session state.
        stream (bool):
            Whether to stream GPT output progressively.
    Returns:
        str:
            Completion output text.
    """

    completion_type = get_completion_type(flow)

    if completion_type == "gpt_generation":

        prompt = render_completion_prompt(flow, state)

        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {
                    "role": "system",
                    "content": get_completion_config(flow).get("system_prompt", "")
                },
                {"role": "user", "content": prompt}
            ],
            stream=stream
        )

        if stream:
            return response

        return response.choices[0].message.content

    return "Unsupported completion type."

# --- Flow Handler ---
def handle_flow(flow, user_input: str, session_id: str, background_tasks: BackgroundTasks = None) -> dict:
    state = session_state[session_id]
    step = state.get("step", 1)

    # --- Standard input collection steps ---
    if get_step_type(flow, step) == "collect":

        collect_step_input(flow, state, step, user_input)

        advance_flow_step(state)

        return build_flow_response(
            "multi-step",
            get_next_flow_prompt(flow, state["step"])
        )

    elif get_step_type(flow, step) == "email_capture":

        email_input = user_input.strip()

        if email_input and email_input.lower() != "skip":

            if "@" in email_input and "." in email_input:
                state["email"] = email_input
                email_confirmation = f"\n\n(I'll also email this response to {email_input}.)"

            else:
                email_confirmation = "\n\n(No valid email detected, so I won't send an email copy.)"

        else:
            email_confirmation = ""

        # Stream live GPT output for /ask_stream, return full text for /ask
        #   If background_tasks is None, we're in the /ask_stream endpoint and should stream; 
        #   otherwise, execute the /ask endpoint normally
        completion_output = execute_flow_completion(flow,state,stream=background_tasks is None)

        # Streaming endpoint returns the live GPT stream immediately
        # /ask_stream → return live GPT stream immediately
        # /ask → continue normal completion + email handling
        if background_tasks is None: 
            return build_flow_response(
                get_completion_response_source(flow),
                completion_output,
                stream=True
            )

        email_handler_name = get_completion_email_handler(flow)

        if is_completion_email_enabled(flow) and state.get("email"):

            email_handler = globals().get(email_handler_name)

            if email_handler:

                if background_tasks:

                    background_tasks.add_task(
                        email_handler,
                        state["email"],
                        completion_output
                    )

                else:

                    email_handler(
                        state["email"],
                        completion_output
                    )

        session_history.setdefault(session_id, []).append(
            {"role": "assistant", "content": completion_output}
        )

        session_state[session_id] = {}

        return build_flow_response(
            get_completion_response_source(flow),
            completion_output + email_confirmation
        )

    else:
        session_state[session_id] = {}

        return build_flow_response(
            "multi-step",
            get_flow_fallback_message(flow)
        )

# --- API Endpoints ---
@router.post("/ask", response_model=AgentResponse)     # POST /ask — takes in a UserQuery, returns AgentResponse
def ask_question(payload: UserQuery, background_tasks: BackgroundTasks):
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

    # --- Active multi-step flow handler ---
    active_flow = get_active_flow(
        session_id,
        session_state,
        FLOW_REGISTRY
    )

    if active_flow:

        return handle_flow(
            active_flow,
            preprocessed["cleaned"],
            session_id,
            background_tasks
        )
    
    # --- Multi-step triggers ---
    lower_input = preprocessed["cleaned"].lower()

    # --- Generic multi-step flow trigger detection ---
    triggered_flow = detect_triggered_flow(
        lower_input,
        FLOW_REGISTRY
    )

    if triggered_flow:

        session_state[session_id] = initialize_flow_state(triggered_flow)

        return {
            "source": "multi-step",
            "answer": get_initial_flow_prompt(triggered_flow)
        }

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

    # --- Active multi-step flow handler ---
    active_flow = get_active_flow(
        session_id,
        session_state,
        FLOW_REGISTRY
    )

    if active_flow:

        flow_response = handle_flow(
            active_flow,
            preprocessed["cleaned"],
            session_id,
            None
        )

        is_streaming_response = flow_response.get("stream", False)

        # Handle live GPT streaming separately from normal full-text flow responses
        async def flow_generator():
            if is_streaming_response:

                full_answer = ""

                for chunk in flow_response.get("answer"):

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

                    await asyncio.sleep(0)

                session_history.setdefault(session_id, []).append(
                    {"role": "assistant", "content": full_answer}
                )

                if active_flow.get("completion", {}).get("email_enabled") and session_state[session_id].get("email"):

                    send_itinerary_email(
                        session_state[session_id]["email"],
                        full_answer
                    )

                session_state[session_id] = {}

            else:

                yield json.dumps({
                    "type": "delta",
                    "text": flow_response.get("answer", "")
                }) + "\n"

            yield json.dumps({"type": "final"}) + "\n"

        return StreamingResponse(
            flow_generator(),
            media_type="application/x-ndjson"
        )
    
    # --- Multi-step triggers ---
    lower_input = preprocessed["cleaned"].lower()

    # --- Generic multi-step flow trigger detection ---
    triggered_flow = detect_triggered_flow(
        lower_input,
        FLOW_REGISTRY
    )

    if triggered_flow:

        session_state[session_id] = initialize_flow_state(triggered_flow)

        async def trigger_generator():
            yield json.dumps({
                "type": "delta",
                "text": build_flow_response(
                    "multi-step",
                    get_initial_flow_prompt(triggered_flow)
                ).get("answer", "")
            }) + "\n"

            yield json.dumps({"type": "final"}) + "\n"

        return StreamingResponse(
            trigger_generator(),
            media_type="application/x-ndjson"
        )

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