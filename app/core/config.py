import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEBUG: bool = False
    DATABASE_URL: str

    # clerk
    CLERK_ISSUER: str
    CLERK_JWKS_URL: str
    CLERK_SECRET_KEY: str
    CLERK_AUDIENCE: str

    model_config = SettingsConfigDict(
        # 本番環境では環境変数のみを使用し、.envファイルは読み込まない
        env_file=".env" if os.getenv("APP_ENV") != "prod" else None,
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_prefix="",
        extra="ignore",
    )


settings = Settings()
