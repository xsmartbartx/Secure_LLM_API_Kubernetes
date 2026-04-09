from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Tenant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    domain: Optional[str] = None
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int
    email: str
    username: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RateLimitProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    requests_per_minute: int = 60
    tokens_per_request: int = 8000
    tokens_per_day: int = 50000
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UsageRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int
    user_id: int
    client_id: Optional[int] = None
    model_name: str
    prompt_tokens: int
    response_tokens: int
    total_tokens: int
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
