from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Message sent by the website visitor",
    )

    conversation_id: Optional[str] = Field(
        default=None,
        description="Existing conversation token. Leave empty for a new conversation.",
    )


class ChatResponse(BaseModel):
    success: bool
    conversation_id: str
    message: str
    mode: str = "general"
