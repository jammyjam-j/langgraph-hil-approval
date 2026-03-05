import os
from pathlib import Path

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = Field("langgraph-hil-approval", env="PROJECT_NAME")
    VERSION: str = Field("0.1.0", env="VERSION")

    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SQLALCHEMY_ECHO: bool = Field(False, env="SQLALCHEMY_ECHO")

    FASTAPI_HOST: str = Field("0.0.0.0", env="FASTAPI_HOST")
    FASTAPI_PORT: int = Field(8000, env="FASTAPI_PORT")
    FASTAPI_DEBUG: bool = Field(False, env="FASTAPI_DEBUG")

    LANGGRAPH_ENDPOINT: str = Field(..., env="LANGGRAPH_ENDPOINT")
    LANGGRAPH_API_KEY: str | None = Field(None, env="LANGGRAPH_API_KEY")

    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    @validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith(("postgresql://", "sqlite:///")):
            raise ValueError("DATABASE_URL must start with postgresql:// or sqlite:///")
        return v

    @validator("LANGGRAPH_ENDPOINT")
    def validate_endpoint(cls, v: str) -> str:
        if not v.startswith("http"):
            raise ValueError("LANGGRAPH_ENDPOINT must be a valid URL")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
REPO_URL = "https://github.com/jammyjam-j/langgraph-hil-approval"

if __name__ == "__main__":
    print(settings.json(indent=2))