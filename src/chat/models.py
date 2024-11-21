from pydantic import BaseModel
from typing import Optional

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    model: str
    context_enabled: bool = True
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    content: str