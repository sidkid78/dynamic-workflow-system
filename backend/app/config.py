"""
Configuration Module

This module defines application-wide configuration settings using Pydantic's BaseSettings.
It loads environment variables from a .env file and provides a centralized place for
managing application configuration.

The Settings class includes:
- Basic application information (name, version)
- Debug settings
- CORS configuration
- File paths for agent workspace and response storage
- Azure OpenAI API configuration
- Workflow behavior settings

The module also ensures required directories exist on startup.

Usage:
    from app.config import settings
    
    # Access configuration values
    api_key = settings.AZURE_OPENAI_API_KEY
    is_configured = settings.is_azure_openai_configured
"""

import os
from typing import List, Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "Dynamic Workflow System"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    # GOOGLE_API_KEY: str = "YOUR_GOOGLE_API_KEY" # Keep for web search
    # GOOGLE_CSE_ID: str = "YOUR_GOOGLE_CSE_ID" # Keep for web search
    # GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY") # Remove Gemini Key
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001"]
    AGENT_WORKSPACE_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "agent_workspace"))
    
    # Response saving settings
    SAVE_RESPONSES: bool = True
    RESPONSES_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "responses"))
    
    # Context File Setting
    CONTEXT_FILE_PATH: Optional[str] = os.getenv("CONTEXT_FILE_PATH", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", r"C:\Users\sidki\source\repos\effective\context.md")))

    # Azure OpenAI Settings (Restored)
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1") # Example default
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview") # Example default

    # Workflow Settings
    DEFAULT_WORKFLOW: str = "orchestrator_workers"
    MAX_RETRIES: int = 3
    TIMEOUT_SECONDS: int = 120

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from environment variables

    @property
    def is_azure_openai_configured(self) -> bool:
        """Check if Azure OpenAI is properly configured"""
        return bool(self.AZURE_OPENAI_API_KEY and self.AZURE_OPENAI_ENDPOINT and self.AZURE_OPENAI_DEPLOYMENT_NAME)

# Create settings instance
settings = Settings()

# Ensure agent workspace exists
if not os.path.exists(settings.AGENT_WORKSPACE_PATH):
    try:
        os.makedirs(settings.AGENT_WORKSPACE_PATH)
        print(f"Created agent workspace directory: {settings.AGENT_WORKSPACE_PATH}")
    except Exception as e:
        print(f"Error creating agent workspace directory: {e}")

# Ensure responses directory exists if response saving is enabled
if settings.SAVE_RESPONSES and not os.path.exists(settings.RESPONSES_DIR):
    try:
        os.makedirs(settings.RESPONSES_DIR)
        print(f"Created responses directory: {settings.RESPONSES_DIR}")
    except Exception as e:
        print(f"Error creating responses directory: {e}")































# # Load environment variables from .env file
# load_dotenv()

# def get_cors_origins() -> List[str]:
#     """Get CORS origins from environment or return defaults"""
#     cors_origins = os.getenv("CORS_ORIGINS")
#     if cors_origins:
#         try:
#             # Try to parse as JSON array
#             return json.loads(cors_origins)
#         except json.JSONDecodeError:
#             # Fallback to comma-separated string
#             return [origin.strip() for origin in cors_origins.split(",")]
#     return [
#         "http://localhost:3000",     # React development server
#         "http://localhost:8000",     # FastAPI development server
#         "http://127.0.0.1:3000",
#         "http://127.0.0.1:8000",
#         "http://192.168.18.3:3000"   # IP address access
#     ]

# class Settings(BaseSettings):
#     # Application Settings
#     APP_NAME: str = "Dynamic Workflow API"
#     APP_VERSION: str = "1.0.0"
#     DEBUG: bool = False
    
#     # CORS Settings
#     CORS_ORIGINS: List[str] = get_cors_origins()
    
#     # Azure OpenAI Settings
#     AZURE_OPENAI_O3_KEY: str
#     AZURE_OPENAI_O3_RESOURCE_NAME: str
#     AZURE_OPENAI_O3_DEPLOYMENT_NAME: str
#     AZURE_OPENAI_API_VERSION: str = "2024-12-01-preview"
    
#     # Workflow Settings
#     DEFAULT_WORKFLOW: str = "prompt_chaining"
#     MAX_RETRIES: int = 3
#     TIMEOUT_SECONDS: int = 60
    
#     model_config = {
#         "env_file": ".env",
#         "env_file_encoding": "utf-8",
#         "case_sensitive": True,
#         "extra": "allow"  # Allow extra fields from environment variables
#     }

#     @property
#     def azure_openai_endpoint(self) -> str:
#         """Generate the Azure OpenAI endpoint URL"""
#         if not self.AZURE_OPENAI_O3_RESOURCE_NAME:
#             raise ValueError("AZURE_OPENAI_O3_RESOURCE_NAME is not configured")
#         return f"https://{self.AZURE_OPENAI_O3_RESOURCE_NAME}.openai.azure.com"

#     @property
#     def is_azure_openai_configured(self) -> bool:
#         """Check if Azure OpenAI is properly configured"""
#         return all([
#             self.AZURE_OPENAI_O3_KEY,
#             self.AZURE_OPENAI_O3_RESOURCE_NAME,
#             self.AZURE_OPENAI_O3_DEPLOYMENT_NAME
#         ])

#     def get_azure_client(self) -> AzureOpenAI:
#         """Get an initialized Azure OpenAI client"""
#         if not self.is_azure_openai_configured:
#             raise ValueError("Azure OpenAI is not properly configured")
        
#         return AzureOpenAI(
#             api_key=self.AZURE_OPENAI_O3_KEY,
#             api_version=self.AZURE_OPENAI_API_VERSION,
#             azure_endpoint=self.azure_openai_endpoint,
#         )

#     def get_chat_completion_params(self, **kwargs) -> dict:
#         """Get standardized parameters for chat completion"""
#         params = {
#             "model": self.AZURE_OPENAI_O3_DEPLOYMENT_NAME,
#             "max_completion_tokens": kwargs.pop("max_tokens", 2048),  # Convert max_tokens to max_completion_tokens
#             **kwargs
#         }
#         return params

# # Create settings instance
# settings = Settings()

# # Initialize Azure OpenAI client
# try:
#     azure_client = settings.get_azure_client()
#     print("Azure OpenAI client initialized successfully")
# except ValueError as e:
#     print(f"Failed to initialize Azure OpenAI client: {e}")