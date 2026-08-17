from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Neura RAG Chatbot API"
    app_version: str = "0.1.0"
    app_env: str = "development"

    gemini_api_key: str
    gemini_model: str = "gemini-3.6-flash"

    rag_enabled: bool = False

    max_history_messages: int = 12
    conversation_ttl_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    allowed_origins: list[str] = [
    "https://neura-solutions.vercel.app",
    ]


settings = Settings()
