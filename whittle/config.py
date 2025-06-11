"""
Configuration management for Whittle
"""
from pathlib import Path
from typing import Optional
import os
from dotenv import load_dotenv

def load_config() -> None:
    """
    Load configuration from environment variables and .env files
    Checks in the following order:
    1. Environment variables
    2. .env file in current directory
    3. .env file in user's home directory
    """
    # Try loading from current directory first
    load_dotenv(Path(".env"))
    
    # Then try user's home directory
    home_env = Path.home() / ".env"
    if home_env.exists():
        load_dotenv(home_env)
        
def get_openai_key() -> Optional[str]:
    """Get OpenAI API key from environment"""
    return os.getenv("OPENAI_API_KEY") 