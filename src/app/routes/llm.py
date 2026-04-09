from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.db.session import get_session
from app.schemas.llm import LLMRequest, LLMResponse
from app.services.prompt_safety_service import validate_prompt
from app.services.token_service import get_current_user
from app.services.rate_limit_service import enforce_rate_limit, record_usage

router = APIRouter()

@router.post("/generate", response_model=LLMResponse)
async def generate_text(
    request: LLMRequest,
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
):
    prompt = validate_prompt(request.prompt)

    prompt_tokens = enforce_rate_limit(session, user, prompt)
    response_tokens = 50
    record_usage(session, user, prompt_tokens, request.model, response_tokens)

    return LLMResponse(
        model=request.model,
        output="This is a placeholder response.",
        prompt_tokens=prompt_tokens,
        response_tokens=response_tokens,
        total_tokens=prompt_tokens + response_tokens,
    )
