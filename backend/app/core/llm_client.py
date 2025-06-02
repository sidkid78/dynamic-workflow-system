# app/core/llm_client.py
"""
LLM Client Module

This module provides client interfaces for interacting with Google Gemini services.
It includes two main client classes:

1. GoogleGeminiClient: Basic client for text generation using Google Gemini
2. GoogleGeminiFunctions: Extended client with function calling capabilities

The module implements a singleton pattern for both clients to ensure efficient
resource usage across the application.

Functions:
    get_llm_client: Returns the singleton instance of the basic LLM client
    get_functions_client: Returns the singleton instance of the functions-enabled client
"""

from typing import Dict, Any, Optional, List, Union
import logging
import json
import asyncio
from app.config import settings
import os
from dotenv import load_dotenv

# Import Google GenAI SDK
from google import genai
from google.genai import types

load_dotenv()

class GoogleGeminiClient:
    """
    Basic client for Google Gemini.

    Attributes:
        client: The Google GenAI client instance.
        model: The Gemini model to use for text generation.
    """
    def __init__(self):
        if not settings.is_gemini_configured:
            raise ValueError("Missing Google Gemini configuration. Please set GOOGLE_API_KEY or configure Vertex AI settings.")
        
        # Initialize the Google GenAI client
        if settings.USE_VERTEX_AI:
            # Use Vertex AI
            self.client = genai.Client(
                vertexai=True,
                project=settings.GOOGLE_CLOUD_PROJECT,
                location=settings.GOOGLE_CLOUD_LOCATION
            )
        else:
            # Use Gemini Developer API
            self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        
        self.model = settings.GEMINI_MODEL
        logging.info(f"Initialized Google Gemini client with model: {self.model}")
    
    async def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 4096) -> str:
        """
        Generate a response from Google Gemini.

        Args:
            prompt (str): The prompt to send to the Gemini API.
            temperature (float): Controls randomness in the output (0.0 to 1.0).
            max_tokens (int): The maximum number of tokens to generate in the response.

        Returns:
            str: The generated response content from the Gemini API.
        """
        try:
            # Use async content generation
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            
            if response and response.text:
                return response.text
            else:
                logging.error(f"Empty response from Gemini API")
                raise Exception("Empty response from Gemini API")
                
        except Exception as e:
            logging.error(f"Error calling Google Gemini API: {str(e)}")
            raise
    
    def generate_sync(self, prompt: str, temperature: float = 0.7, max_tokens: int = 4096) -> str:
        """
        Synchronous version of generate for compatibility.
        
        Args:
            prompt (str): The prompt to send to the Gemini API.
            temperature (float): Controls randomness in the output (0.0 to 1.0).
            max_tokens (int): The maximum number of tokens to generate in the response.

        Returns:
            str: The generated response content from the Gemini API.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            
            if response and response.text:
                return response.text
            else:
                logging.error(f"Empty response from Gemini API")
                raise Exception("Empty response from Gemini API")
                
        except Exception as e:
            logging.error(f"Error calling Google Gemini API: {str(e)}")
            raise
    
    async def generate_stream(self, prompt: str, temperature: float = 0.7, max_tokens: int = 4096):
        """
        Generate a streaming response from Google Gemini.

        Args:
            prompt (str): The prompt to send to the Gemini API.
            temperature (float): Controls randomness in the output (0.0 to 1.0).
            max_tokens (int): The maximum number of tokens to generate in the response.

        Yields:
            str: Chunks of the generated response content.
        """
        try:
            async for chunk in await self.client.aio.models.generate_content_stream(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            ):
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logging.error(f"Error streaming from Google Gemini API: {str(e)}")
            raise

class GoogleGeminiFunctions:
    """
    Client for Google Gemini with support for function calling.

    This client extends the basic Gemini client to handle function calling capabilities,
    allowing for more complex interactions with the API.

    Attributes:
        client: The Google GenAI client instance.
        model: The Gemini model to use for text generation and function calling.
    """
    def __init__(self):
        if not settings.is_gemini_configured:
            raise ValueError("Missing Google Gemini configuration. Please set GOOGLE_API_KEY or configure Vertex AI settings.")
        
        # Initialize the Google GenAI client
        if settings.USE_VERTEX_AI:
            # Use Vertex AI
            self.client = genai.Client(
                vertexai=True,
                project=settings.GOOGLE_CLOUD_PROJECT,
                location=settings.GOOGLE_CLOUD_LOCATION
            )
        else:
            # Use Gemini Developer API
            self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        
        self.model = settings.GEMINI_MODEL
        logging.info(f"Initialized Google Gemini Functions client with model: {self.model}")
    
    async def generate_with_functions(
        self, 
        prompt: str, 
        functions: List[Union[callable, Dict[str, Any]]], 
        function_call: str = "auto",
        max_tokens: int = 8192,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate a response from Google Gemini with function calling.

        Args:
            prompt (str): The user prompt to send to the Gemini API.
            functions (List): List of function definitions or callable functions.
            function_call (str): Specifies whether to call a function automatically (legacy parameter).
            max_tokens (int): The maximum number of tokens to generate in the response.
            temperature (float): Controls randomness in the output (0.0 to 1.0).

        Returns:
            Dict[str, Any]: A dictionary containing either the message content or function call details.
        """
        try:
            # Prepare tools for Gemini (can be callable functions or schemas)
            tools = []
            for func in functions:
                if callable(func):
                    tools.append(func)
                else:
                    # Handle legacy function schema format
                    tools.append(func)
            
            # Use automatic function calling for simplicity
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=tools,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        maximum_remote_calls=3  # Allow up to 3 function calls
                    ),
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            
            if response and response.text:
                # Return text response (function calls are handled automatically)
                return {
                    "type": "text",
                    "content": response.text
                }
            else:
                logging.error(f"Empty response from Gemini API")
                raise Exception("Empty response from Gemini API")
                
        except Exception as e:
            logging.error(f"Error calling Google Gemini API with functions: {str(e)}")
            raise
    
    def _convert_legacy_function_schema(self, legacy_function: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert legacy OpenAI function schema to Gemini-compatible format.
        
        Args:
            legacy_function: OpenAI-style function definition
            
        Returns:
            Gemini-compatible function definition
        """
        # This is a helper method to convert OpenAI-style function schemas
        # to Gemini format if needed for backward compatibility
        return {
            "name": legacy_function.get("name"),
            "description": legacy_function.get("description"),
            "parameters": legacy_function.get("parameters", {})
        }

# Legacy class aliases for backward compatibility
AzureOpenAIClient = GoogleGeminiClient
AzureOpenAIFunctions = GoogleGeminiFunctions

# Singleton instances
_regular_client = None
_functions_client = None

def get_llm_client() -> GoogleGeminiClient:
    """
    Get the basic LLM client instance (singleton pattern).

    Returns:
        GoogleGeminiClient: The singleton instance of the GoogleGeminiClient.
    """
    global _regular_client
    if _regular_client is None:
        _regular_client = GoogleGeminiClient()
    return _regular_client

def get_functions_client() -> GoogleGeminiFunctions:
    """
    Get the functions-enabled LLM client instance (singleton pattern).

    Returns:
        GoogleGeminiFunctions: The singleton instance of the GoogleGeminiFunctions.
    """
    global _functions_client
    if _functions_client is None:
        _functions_client = GoogleGeminiFunctions()
    return _functions_client

# Legacy function aliases for backward compatibility
def get_azure_client():
    """Deprecated: Use get_llm_client() instead"""
    logging.warning("get_azure_client() is deprecated. Use get_llm_client() instead.")
    return get_llm_client()

def get_azure_functions_client():
    """Deprecated: Use get_functions_client() instead"""
    logging.warning("get_azure_functions_client() is deprecated. Use get_functions_client() instead.")
    return get_functions_client()