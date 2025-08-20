from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = False
    DATABASE_URL: str

    # clerk
    CLERK_ISSUER: str
    CLERK_JWKS_URL: str
    CLERK_SECRET_KEY: str
    CLERK_AUDIENCE: str

    class Config:
        env_file = ".env"


settings = Settings()
