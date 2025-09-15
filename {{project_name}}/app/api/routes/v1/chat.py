from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.deps import get_initialized_agent


router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    error: str | None= None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, agent=Depends(get_initialized_agent)):
    """Simple chat endpoint for the agent"""
    try:
        response = await agent.handle_message(request.message, verbose=False)
        return ChatResponse(response=response)
        
    except Exception as e:
        return ChatResponse(
            response="",
            error=f"An error occurred: {str(e)}"
        )