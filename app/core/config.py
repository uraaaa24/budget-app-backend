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
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        # 環境変数を.envファイルより優先させる（これがデフォルトだが明示的に設定）
        env_prefix="",
        extra="ignore",
    )


settings = Settings()
