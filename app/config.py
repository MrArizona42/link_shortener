import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ----- Base URL -----
    BASE_URL: str

    # ----- Database settings -----
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # ----- Redis settings -----
    REDIS_HOST: str
    REDIS_PORT: int

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    # ----- FastAPI settings -----
    APP_HOST: str
    APP_PORT: int
    APP_WORKERS: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
