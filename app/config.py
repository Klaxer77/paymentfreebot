from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.dev")
    
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
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 999999999

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    @property    
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
     
settings = Settings()