import logging

from fastapi import APIRouter, HTTPException

from app.conversations.store import conversation_store
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.gemini_service import GeminiService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Chat"])

gemini_service = GeminiService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    try:
        conversation_id = request.conversation_id

        if not conversation_id:
            conversation_id = conversation_store.create()

        elif not conversation_store.exists(conversation_id):
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            )

        history = conversation_store.get_messages(
            conversation_id
        )

        answer = await gemini_service.generate_response(
            message=request.message,
            history=history,
        )

        conversation_store.add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message,
        )

        conversation_store.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
        )

        return ChatResponse(
            success=True,
            conversation_id=conversation_id,
            message=answer,
            mode="general",
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception("Chat request failed")

        raise HTTPException(
            status_code=503,
            detail="The AI service is temporarily unavailable.",
        )