from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Secure LLM API"
    environment: str = "development"
    database_url: str = "sqlite:///./data/db.sqlite"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
