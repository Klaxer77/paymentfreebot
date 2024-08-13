from typing import ClassVar, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.dev")

    MODE: Literal["DEV", "TEST", "PROD"]
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    DB_HOST: str
    DB_NAME: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str

    NGROK_TUNNEL_URL: str
    BOT_SECRET_TOKEN: str
    WEB_APP_URL: str

    SECRET_KEY: str
    ALGORITHM: str

    YOOKASSA_SHOPID: int
    YOOKASSA_SECRETKEY: str
    YOOKASSA_SECRETKEY_SHLUZ: str
    YOOKASSA_AGENTID: int

    COMMISION_PERCENTAGE: int
    
    USER_WEBHOOK_URL: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
