from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.chat_service import ChatService, get_chat_service


router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    user_message: str


class ChatResponse(BaseModel):
    conversation_id: str
    assistant_message: str
    state: Dict[str, Any]


@router.post("", response_model=ChatResponse)
async def chat_endpoint(
    payload: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """
    HTTP-only endpoint that delegates to ChatService.
    No business logic or LLM calls here.
    """
    result = await service.handle_chat(
        conversation_id=payload.conversation_id,
        user_message=payload.user_message,
    )

    return ChatResponse(
        conversation_id=result["conversation_id"],
        assistant_message=result["assistant_message"],
        state=result["state"],
    )


@router.post("/reload-rag")
async def reload_rag_endpoint(
    service: ChatService = Depends(get_chat_service),
) -> Dict[str, str]:
    """
    Force reload the RAG knowledge base.
    """
    service.reload_retriever()
    return {"status": "success", "message": "RAG data reloaded successfully."}


