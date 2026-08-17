from fastapi import FastAPI

app = FastAPI(
    title="Neura RAG Chatbot API",
    description="AI chatbot microservice for Neura Solutions Limited",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Neura RAG Chatbot",
    }
