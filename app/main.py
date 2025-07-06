"""
main.py

This is the entry point for the Banking Agent FastAPI server.

It defines a RESTful API with a single `/ask` endpoint that receives
questions from users and routes them to the agent logic for response generation.

The application:
- Loads environment variables from the `.env` file
- Accepts POST requests containing a user message
- Passes the message to the agent for processing
- Returns the agent's response as JSON

To run the server locally:
    uvicorn main:app --reload

You can test the API at:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router

# Load environment variables from .env file
app = FastAPI(
    title="Banking Assistant API",
    description="LLM-powered banking assistant by MoreYummy.com",
    version="1.1"
)

# CORS middleware for frontend/backend separation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domains in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Banking Assistant API is running."}

app.include_router(router)