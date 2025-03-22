import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    # Database settings
    DB_USER: str
    DB_PASSWORD: str
    # DB_HOST: str = "db"  # same as service name in docker-compose.yml
    DB_PORT: int
    DB_NAME: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Redis settings
    # REDIS_HOST: str = "redis"  # same as service name in docker-compose.yml
    REDIS_PORT: int

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_WORKERS: int = 1

    # SQL Queries Paths
    BASE_DIR = os.path.dirname(__file__)
    SQL_QUERIES: dict = {
        "auth": {
            "create_user": os.path.join(BASE_DIR, "auth/sql/create_user.sql"),
            "get_user_by_email": os.path.join(
                BASE_DIR, "auth/sql/get_user_by_email.sql"
            ),
        },
        "links": {
            "insert_link": os.path.join(BASE_DIR, "links/sql/insert_link.sql"),
            "get_link_by_short_code": os.path.join(
                BASE_DIR, "links/sql/get_link_by_short_code.sql"
            ),
        },
    }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
