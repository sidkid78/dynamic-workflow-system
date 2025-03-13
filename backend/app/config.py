import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

# Simple settings class without using pydantic-settings
class Settings:
    # Application settings
    APP_NAME: str = "Dynamic Workflow System"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]  # Frontend URL
    
    # Azure OpenAI settings
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_RESOURCE_NAME: str = os.getenv("AZURE_OPENAI_RESOURCE_NAME", "")
    AZURE_OPENAI_DEPLOYMENT_ID: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_ID", "gpt-4o")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2023-08-01-preview")
    
    # Workflow settings
    DEFAULT_WORKFLOW: str = "prompt_chaining"
    MAX_RETRIES: int = 3
    TIMEOUT_SECONDS: int = 60

# Create a singleton settings instance
settings = Settings()