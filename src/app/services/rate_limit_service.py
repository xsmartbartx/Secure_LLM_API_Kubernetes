from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlmodel import Session, select
from app.db.models import UsageRecord, RateLimitProfile
from app.db.repository import get_rate_limit_profile, create_usage_record, get_daily_token_usage, get_recent_request_count


def estimate_prompt_tokens(prompt: str) -> int:
    return max(1, len(prompt) // 4)


def enforce_rate_limit(session: Session, user, prompt: str):
    profile = get_rate_limit_profile(session)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rate limit profile not configured",
        )

    prompt_tokens = estimate_prompt_tokens(prompt)
    recent_requests = get_recent_request_count(session, user.id, minutes=1)
    daily_tokens = get_daily_token_usage(session, user.id)

    if recent_requests >= profile.requests_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Request rate limit exceeded",
        )

    if prompt_tokens > profile.tokens_per_request:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Prompt exceeds maximum {profile.tokens_per_request} tokens",
        )

    if daily_tokens + prompt_tokens > profile.tokens_per_day:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily token limit exceeded",
        )

    return prompt_tokens


def record_usage(session: Session, user, prompt_tokens: int, model_name: str, response_tokens: int = 50):
    total_tokens = prompt_tokens + response_tokens
    return create_usage_record(
        session=session,
        tenant_id=user.tenant_id,
        user_id=user.id,
        model_name=model_name,
        prompt_tokens=prompt_tokens,
        response_tokens=response_tokens,
        total_tokens=total_tokens,
        status="ok",
    )
