"""
agent.py

Handles prompt construction and interaction with Azure OpenAI.

- Loads the system prompt for the active client
- Sends a chat request to Azure OpenAI
- Returns the agent's response text
"""

import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
client_id = os.getenv("CLIENT_ID")

# Load system prompt from client folder
def load_system_prompt():
    prompt_path = f"clients/{client_id}/system_prompt.txt"
    if os.path.exists(prompt_path):
        with open(prompt_path, "r") as f:
            return f.read()
    return "You are a helpful banking assistant."

system_prompt = load_system_prompt()

# Main function used by main.py
async def get_agent_response(user_input: str) -> str:
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content