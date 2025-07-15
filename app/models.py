from pydantic import BaseModel

# Input model: what the user sends to /ask
class UserQuery(BaseModel):
    session_id: str     # Unique identifier for the chat session
    client_id: str      # Identifies the bank/client requesting
    question: str       # The actual user input

# Output model: what the API returns
class AgentResponse(BaseModel):
    source: str         # 'faq' or 'gpt'
    answer: str         # Agent response text