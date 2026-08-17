from fastapi import FastAPI

from app.api.chat import router as chat_router


app = FastAPI(
    title="Neura RAG Chatbot API",
    description="AI chatbot microservice for Neura Solutions Limited",
    version="0.1.0",
)


app.include_router(chat_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "Neura RAG Chatbot",
    }
