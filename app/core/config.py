from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = False
    ENV: Literal["dev", "prod"] = "dev"
    DATABASE_URL: str

    # clerk
    CLERK_ISSUER: str
    CLERK_JWKS_URL: str
    CLERK_SECRET_KEY: str
    CLERK_AUDIENCE: str


settings = Settings()
