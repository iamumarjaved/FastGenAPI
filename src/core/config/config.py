import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from src.core.config.env_configurations import DevelopmentConfig, TestingConfig, ProductionConfig


class Settings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    
    # OAuth2 Credentials
    google_client_id: str
    google_client_secret: str
    google_authorize_url: str
    google_token_url: str
    google_userinfo_url: str
    
    # GitHub OAuth2 credentials
    github_client_id: str
    github_client_secret: str
    github_authorize_url: str
    github_token_url: str
    github_userinfo_url: str
    
    # Facebook OAuth2 credentials
    facebook_client_id: str
    facebook_client_secret: str
    facebook_authorize_url: str
    facebook_token_url: str
    facebook_userinfo_url: str
        
    # App details
    app_name: str
    version: str
    docs_url: str
    redoc_url: str
    session_secret_key: str
    redis_host: str
    redis_port: int
    
    # Database
    database_url: str
    
    # Limiter
    rate_limit: str
    
    # HyperDX
    hyperdx_api_key: str

    class Config:
        env_file = ".env"
        extra = "allow"  

env = os.getenv("ENVIRONMENT", "development")

if env == "development":
    load_dotenv(".env.dev")
    app_config = DevelopmentConfig()
elif env == "testing":
    load_dotenv(".env.test")
    app_config = TestingConfig()
else:
    load_dotenv(".env.prod")
    app_config = ProductionConfig()

settings = Settings()
