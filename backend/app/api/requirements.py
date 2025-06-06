from fastapi import APIRouter
from app.models.requirements import ConversationRequest, ConversationResponse, Message
from app.core.parsing import chat_with_design_assistant

router = APIRouter()

@router.post("/chat", response_model=ConversationResponse)
def chat_with_assistant(request: ConversationRequest):
    # Get response from the design assistant
    response = chat_with_design_assistant(request.message, request.history)
    
    # Update conversation history
    new_history = request.history.copy() if request.history else []
    new_history.append(Message(role="user", content=request.message))
    new_history.append(Message(role="assistant", content=response))
    
    return ConversationResponse(
        response=response,
        history=new_history
    ) 