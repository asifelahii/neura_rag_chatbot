from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Neura RAG Chatbot API"
    app_version: str = "0.1.0"
    app_env: str = "development"

    gemini_api_key: str
    gemini_model: str = "gemini-3.6-flash"

    gemini_max_output_tokens: int = 800
    gemini_request_timeout_seconds: float = 30.0

    rag_enabled: bool = False

    max_history_messages: int = 12
    conversation_ttl_minutes: int = 30

    rate_limit_enabled: bool = True
    rate_limit_requests: int = 10
    rate_limit_window_seconds: int = 60

    conversation_store: str = "memory"

    redis_url: str = "redis://localhost:6379/0"
    redis_key_prefix: str = "neura:conversation:"

    allowed_origins: list[str] = [
        "https://neura-solutions.vercel.app",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()