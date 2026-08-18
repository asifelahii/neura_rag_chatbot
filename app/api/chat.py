import logging

from fastapi import APIRouter, HTTPException, Request

from app.conversations.store import conversation_store
from app.rag.retriever import get_knowledge_retriever
from app.schemas.chat import ChatRequest, ChatResponse
from app.security.rate_limiter import rate_limiter
from app.services.ai_exceptions import AIServiceUnavailableError
from app.services.gemini_service import GeminiService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Chat"])

gemini_service = GeminiService()
knowledge_retriever = get_knowledge_retriever()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    http_request: Request,
):
    try:
        client_host = (
            http_request.client.host
            if http_request.client
            else "unknown"
        )

        rate_limiter.check(client_host)

        conversation_id = request.conversation_id

        if not conversation_id:
            conversation_id = await conversation_store.create()

        elif not await conversation_store.exists(
            conversation_id
        ):
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            )

        history = await conversation_store.get_messages(
            conversation_id
        )

        context = await knowledge_retriever.retrieve(
            request.message
        )

        answer = await gemini_service.generate_response(
            message=request.message,
            history=history,
            context=context,
        )

        await conversation_store.add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message,
        )

        await conversation_store.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
        )

        mode = "rag" if context else "general"

        return ChatResponse(
            success=True,
            conversation_id=conversation_id,
            message=answer,
            mode=mode,
        )

    except HTTPException:
        raise

    except AIServiceUnavailableError:
        logger.warning(
            "AI provider unavailable request_id=%s",
            getattr(
                http_request.state,
                "request_id",
                "unknown",
            ),
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "The AI service is temporarily busy. "
                "Please try again shortly."
            ),
        )

    except Exception:
        logger.exception(
            "Chat request failed request_id=%s",
            getattr(
                http_request.state,
                "request_id",
                "unknown",
            ),
        )

        raise HTTPException(
            status_code=503,
            detail="The AI service is temporarily unavailable.",
        )
