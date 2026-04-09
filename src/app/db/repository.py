from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.db.models import User, Tenant, RateLimitProfile, UsageRecord


def get_user_by_username(session: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()


def get_user_by_email(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def create_user(session: Session, username: str, email: str, hashed_password: str, tenant_id: int = 1) -> User:
    user = User(username=username, email=email, hashed_password=hashed_password, tenant_id=tenant_id)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_default_tenant(session: Session) -> Tenant | None:
    statement = select(Tenant).where(Tenant.name == "default")
    return session.exec(statement).first()


def create_default_tenant(session: Session) -> Tenant:
    tenant = Tenant(name="default", domain=None)
    session.add(tenant)
    session.commit()
    session.refresh(tenant)
    return tenant


def get_rate_limit_profile(session: Session, name: str = "default") -> RateLimitProfile:
    statement = select(RateLimitProfile).where(RateLimitProfile.name == name)
    profile = session.exec(statement).first()
    if profile is None:
        profile = create_rate_limit_profile(session, name)
    return profile


def create_rate_limit_profile(session: Session, name: str = "default") -> RateLimitProfile:
    profile = RateLimitProfile(name=name)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def get_recent_request_count(session: Session, user_id: int, minutes: int = 1) -> int:
    cutoff = datetime.utcnow() - timedelta(minutes=minutes)
    statement = select(UsageRecord).where(
        UsageRecord.user_id == user_id,
        UsageRecord.created_at >= cutoff,
    )
    return len(session.exec(statement).all())


def get_daily_token_usage(session: Session, user_id: int) -> int:
    start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    statement = select(UsageRecord).where(
        UsageRecord.user_id == user_id,
        UsageRecord.created_at >= start_of_day,
    )
    return sum(record.total_tokens for record in session.exec(statement).all())


def create_usage_record(
    session: Session,
    tenant_id: int,
    user_id: int,
    model_name: str,
    prompt_tokens: int,
    response_tokens: int,
    total_tokens: int,
    status: str = "ok",
    client_id: int | None = None,
) -> UsageRecord:
    record = UsageRecord(
        tenant_id=tenant_id,
        user_id=user_id,
        client_id=client_id,
        model_name=model_name,
        prompt_tokens=prompt_tokens,
        response_tokens=response_tokens,
        total_tokens=total_tokens,
        status=status,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record
