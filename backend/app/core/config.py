from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str  # Required environment variable
    model_name: str = "gpt-4o-mini"  # or your specific model

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() 