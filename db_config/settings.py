
from pydantic import BaseModel
from decouple import config


class Settings(BaseModel):
    PROJECT_TITLE: str = "Starlette ALL auth"
    PROJECT_VERSION: str = "1.0.0"

    USE_SQLITE_DB: str = config("USE_SQLITE_DB")

    POSTGRES_USER: str = config("POSTGRES_USER")
    POSTGRES_PASSWORD = config("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = config("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = config("POSTGRES_PORT")
    POSTGRES_DB: str = config("POSTGRES_DB")

    DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    FROM: str = config("FROM")
    MAIL_PASSWORD: str = config("MAIL_PASSWORD")
    TO_MAIL: str = config("TO_MAIL")

    SECRET_KEY: str = config("SECRET")
    ALGORITHM = "HS256"

    DEBUG: str = config("DEBUG")
    ALLOWED_HOSTS: str = config("ALLOWED_HOSTS")
    JWT_PREFIX: str = config("JWT_PREFIX")

    JWT_ALGORITHM = config("JWT_ALGORITHM")

    EMAIL_TOKEN_EXPIRY_MINUTES: int = 120

    UPLOAD_FOLDER: str = config("UPLOAD_FOLDER")

    TIME_FORMAT: int = "%H:%M:%S"
    DATETIME_FORMAT: int = "%Y-%m-%d%H:%M:%S"
    DATE_TIME: int = "%Y-%m-%d%H:%M"
    DATETIME: int = "%Y-%m-%d"
    DATE: int = "%d.%m.%Y"


settings = Settings()
