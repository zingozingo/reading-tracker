from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Application
    app_name: str = "BookTracker API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Server
    port: int = 8000
    
    # API
    api_v1_str: str = "/api/v1"
    
    # For backwards compatibility
    @property
    def project_name(self) -> str:
        return self.app_name
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()