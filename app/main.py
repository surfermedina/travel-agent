"""
main.py

This is the entry point for the Banking Agent FastAPI server.

It sets up the FastAPI application, middleware, and routing.

The application:
- Loads environment variables from the `.env` file
- Adds CORS middleware to allow frontend access
- Includes API routes defined in `app/api.py`
- Provides a root endpoint for basic health checks

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
    allow_origins=[
        # your local test page (commented out for live deployment)
        "*",
        "http://localhost:5000",
        "http://localhost:5500",          
        "http://127.0.0.1:5500",
        "https://app.moreyummy.com",
        "https://bankagent.moreyummy.com",
        "https://moreyummy.com",
        "https://www.moreyummy.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Banking Assistant API is running."}

app.include_router(router)