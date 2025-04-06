import os
from typing import List
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from openai import AzureOpenAI

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "Dynamic Workflow System"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000", "http://127.0.0.1:8000", "http://192.168.18.3:3000"]

    # Azure OpenAI Settings
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    # Workflow Settings
    DEFAULT_WORKFLOW: str = "prompt_chaining"
    MAX_RETRIES: int = 3
    TIMEOUT_SECONDS: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from environment variables

    @property
    def is_azure_openai_configured(self) -> bool:
        """Check if Azure OpenAI is properly configured"""
        return all([
            self.AZURE_OPENAI_API_KEY,
            self.AZURE_OPENAI_ENDPOINT,
            self.AZURE_OPENAI_DEPLOYMENT_NAME
        ])

    def get_azure_client(self) -> AzureOpenAI:
        """Get an initialized Azure OpenAI client"""
        if not self.is_azure_openai_configured:
            raise ValueError("Azure OpenAI is not properly configured")
        
        return AzureOpenAI(
            api_key=self.AZURE_OPENAI_API_KEY,
            api_version=self.AZURE_OPENAI_API_VERSION,
            azure_endpoint=self.AZURE_OPENAI_ENDPOINT
        )

    def get_chat_completion_params(self, **kwargs) -> dict:
        """Get standardized parameters for chat completion"""
        # Remove temperature if present as it's not supported
        kwargs.pop("temperature", None)
        
        params = {
            "model": self.AZURE_OPENAI_DEPLOYMENT_NAME,
            "max_tokens": kwargs.pop("max_tokens", 2048),
            **kwargs
        }
        return params

# Create settings instance
settings = Settings()

# Initialize Azure OpenAI client
try:
    azure_client = settings.get_azure_client()
    print("Azure OpenAI client initialized successfully")
except ValueError as e:
    print(f"Failed to initialize Azure OpenAI client: {e}")































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