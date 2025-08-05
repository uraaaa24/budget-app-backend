from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Budget App"
    DEBUG: bool = False
    DATABASE_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
