from pydantic import BaseModel

class UserQuery(BaseModel):
    question: str

class AgentResponse(BaseModel):
    source: str  # 'faq' or 'gpt'
    answer: str
