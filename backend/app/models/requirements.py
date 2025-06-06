from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ConversationRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []

class ConversationResponse(BaseModel):
    response: str
    history: List[Message] 