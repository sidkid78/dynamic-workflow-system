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
- Google Gemini API configuration (migrated from Azure OpenAI)
- Workflow behavior settings

The module also ensures required directories exist on startup.

Usage:
    from app.config import settings
    
    # Access configuration values
    api_key = settings.GOOGLE_API_KEY
    is_configured = settings.is_gemini_configured
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
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001"]
    AGENT_WORKSPACE_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "agent_workspace"))
    
    # Response saving settings
    SAVE_RESPONSES: bool = True
    RESPONSES_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "responses"))
    
    # Context File Setting
    CONTEXT_FILE_PATH: Optional[str] = os.getenv("CONTEXT_FILE_PATH", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", r"C:\Users\sidki\source\repos\effective\context.md")))

    # Google Gemini API Settings (migrated from Azure OpenAI)
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-001")  # Default to latest model
    
    # Alternative Vertex AI settings (for enterprise use)
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    GOOGLE_CLOUD_LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    USE_VERTEX_AI: bool = os.getenv("USE_VERTEX_AI", "false").lower() == "true"

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
    def is_gemini_configured(self) -> bool:
        """Check if Google Gemini is properly configured"""
        if self.USE_VERTEX_AI:
            return bool(self.GOOGLE_CLOUD_PROJECT and self.GOOGLE_CLOUD_LOCATION)
        return bool(self.GOOGLE_API_KEY)
    
    # Legacy property for backward compatibility
    @property
    def is_azure_openai_configured(self) -> bool:
        """Deprecated: Check if Google Gemini is properly configured (backward compatibility)"""
        return self.is_gemini_configured

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

# Print configuration status on startup
if settings.DEBUG:
    if settings.is_gemini_configured:
        provider = "Vertex AI" if settings.USE_VERTEX_AI else "Gemini Developer API"
        print(f"✓ Google Gemini configured using {provider}")
        print(f"  Model: {settings.GEMINI_MODEL}")
    else:
        print("⚠ Google Gemini not configured. Please set GOOGLE_API_KEY or Vertex AI credentials.")


# Legacy Azure OpenAI settings (commented out for migration reference)
# AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY")
# AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT")
# AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1")
# AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")