from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.gemini_service import GeminiService


router = APIRouter(prefix="/api/v1", tags=["Chat"])

gemini_service = GeminiService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        answer = await gemini_service.generate_response(request.message)

        return ChatResponse(
            success=True,
            message=answer,
            mode="general",
        )

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="The AI service is temporarily unavailable.",
        )
