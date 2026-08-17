from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Message sent by the website visitor",
    )


class ChatResponse(BaseModel):
    success: bool
    message: str
    mode: str = "general"
