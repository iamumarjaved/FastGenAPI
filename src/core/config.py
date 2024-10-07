from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str = "fsdwk4rn23r2lkm23k4n23km324kj34kj" 
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    app_name: str = "REST API Boilerplate"
    version: str = "1.0.0"
    docs_url: str = "/swagger"
    redoc_url: str = "/redoc"
    
    class Config:
        env_file = ".env"

settings = Settings()
