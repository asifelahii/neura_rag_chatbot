import os


os.environ["GEMINI_API_KEY"] = "test-gemini-api-key"
os.environ["CONVERSATION_STORE"] = "memory"
os.environ["RAG_ENABLED"] = "false"
os.environ["RATE_LIMIT_ENABLED"] = "true"
os.environ["APP_SECRET_KEY"] = (
    "test-secret-key-for-neura-chatbot-only"
)
