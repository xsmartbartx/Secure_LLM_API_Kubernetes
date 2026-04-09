from sqlmodel import SQLModel


class TokenRequest(SQLModel):
    username: str
    password: str


class TokenResponse(SQLModel):
    access_token: str
    token_type: str


class UserCreate(SQLModel):
    username: str
    email: str
    password: str
