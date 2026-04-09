from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.db.repository import create_default_tenant, create_user, get_default_tenant
from app.db.session import get_session
from app.schemas.auth import TokenRequest, TokenResponse, UserCreate
from app.services.auth_service import authenticate_user, create_access_token, get_password_hash

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register_user(payload: UserCreate, session: Session = Depends(get_session)):
    tenant = get_default_tenant(session)
    if tenant is None:
        tenant = create_default_tenant(session)

    hashed_password = get_password_hash(payload.password)
    user = create_user(session, payload.username, payload.email, hashed_password, tenant_id=tenant.id)
    access_token = create_access_token(subject=user.username)

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=TokenResponse)
async def issue_token(payload: TokenRequest, session: Session = Depends(get_session)):
    user = authenticate_user(session, payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}
