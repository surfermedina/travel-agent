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
from pydantic import BaseModel
from agent import get_agent_response
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

app = FastAPI()

class Query(BaseModel):
    message: str

@app.post("/ask")
async def ask_agent(query: Query):
    response = await get_agent_response(query.message)
    return {"response": response}