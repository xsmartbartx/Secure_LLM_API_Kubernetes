from typing import Optional
from sqlmodel import SQLModel


class LLMRequest(SQLModel):
    prompt: str
    model: Optional[str] = "secure-llm-v1"


class LLMResponse(SQLModel):
    model: str
    output: str
    prompt_tokens: int
    response_tokens: int
    total_tokens: int
