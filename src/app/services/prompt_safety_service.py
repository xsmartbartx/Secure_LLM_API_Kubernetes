import re
from fastapi import HTTPException, status


BANNED_SUBSTRINGS = [
    "drop table",
    "delete from",
    "insert into",
    "update ",
    "shutdown",
    "curl ",
    "wget ",
    "scp ",
    "ssh ",
    "api_key",
    "secret",
    "password",
    "openai",
    "authorization",
    "bearer ",
    "access token",
    "refresh token",
    "export ",
    "set-cookie",
    "base64",
]

PROMPT_INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"forget (all )?previous instructions",
    r"do not follow previous instructions",
    r"disregard previous instructions",
    r"ignore (this|these) instructions",
    r"don'?t follow",
    r"reveal secret",
    r"exfiltrate",
]

MAX_PROMPT_LENGTH = 4000


def validate_prompt(prompt: str) -> str:
    if not prompt or not prompt.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prompt cannot be empty")

    normalized = prompt.strip()
    if len(normalized) > MAX_PROMPT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Prompt exceeds maximum length of {MAX_PROMPT_LENGTH} characters",
        )

    prompt_lower = normalized.lower()
    for banned in BANNED_SUBSTRINGS:
        if banned in prompt_lower:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt contains forbidden content or sensitive terms",
            )

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, prompt_lower):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt appears to contain prompt injection or conflicting instructions",
            )

    return normalized
