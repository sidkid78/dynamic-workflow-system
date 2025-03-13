# app/core/llm_client.py
from typing import Dict, Any, Optional
import os
import aiohttp
import logging
import json
from dotenv import load_dotenv

load_dotenv()

class AzureOpenAIClient:
    """
    Client for interacting with Azure OpenAI Service
    """
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.resource_name = os.getenv("AZURE_OPENAI_RESOURCE_NAME")
        self.deployment_id = os.getenv("AZURE_OPENAI_DEPLOYMENT_ID", "gpt-4o")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
        
        if not self.api_key or not self.resource_name:
            raise ValueError("Missing Azure OpenAI configuration. Required: AZURE_OPENAI_API_KEY, AZURE_OPENAI_RESOURCE_NAME")
        
        # Construct the API URL
        self.api_url = f"https://{self.resource_name}.openai.azure.com/openai/deployments/{self.deployment_id}/chat/completions?api-version={self.api_version}"
    
    async def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        Generate a response from Azure OpenAI
        """
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logging.error(f"Azure OpenAI API error: {error_text}")
                        raise Exception(f"Azure OpenAI API returned status {response.status}: {error_text}")
                    
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
        except Exception as e:
            logging.error(f"Error calling Azure OpenAI API: {str(e)}")
            raise

class AzureOpenAIFunctions:
    """
    Client for Azure OpenAI with support for function calling
    """
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.resource_name = os.getenv("AZURE_OPENAI_RESOURCE_NAME")
        self.deployment_id = os.getenv("AZURE_OPENAI_DEPLOYMENT_ID", "gpt-4o")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
        
        if not self.api_key or not self.resource_name:
            raise ValueError("Missing Azure OpenAI configuration. Required: AZURE_OPENAI_API_KEY, AZURE_OPENAI_RESOURCE_NAME")
        
        # Construct the API URL
        self.api_url = f"https://{self.resource_name}.openai.azure.com/openai/deployments/{self.deployment_id}/chat/completions?api-version={self.api_version}"
    
    async def generate_with_functions(
        self, 
        prompt: str, 
        functions: list, 
        function_call: str = "auto",
        temperature: float = 0.7, 
        max_tokens: int = 1200
    ) -> Dict[str, Any]:
        """
        Generate a response from Azure OpenAI with function calling
        
        Args:
            prompt: The user prompt
            functions: List of function definitions
            function_call: "auto" or {"name": "function_name"}
            temperature: Temperature parameter
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict with either message content or function call details
        """
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "functions": functions,
            "function_call": function_call,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logging.error(f"Azure OpenAI API error: {error_text}")
                        raise Exception(f"Azure OpenAI API returned status {response.status}: {error_text}")
                    
                    result = await response.json()
                    message = result["choices"][0]["message"]
                    
                    # Handle function call response
                    if "function_call" in message:
                        function_call = message["function_call"]
                        return {
                            "type": "function_call",
                            "name": function_call["name"],
                            "arguments": json.loads(function_call["arguments"])
                        }
                    
                    # Handle regular text response
                    return {
                        "type": "text",
                        "content": message["content"]
                    }
        except Exception as e:
            logging.error(f"Error calling Azure OpenAI API with functions: {str(e)}")
            raise

# Singleton instances
_regular_client = None
_functions_client = None

def get_llm_client():
    """
    Get the basic LLM client instance (singleton pattern)
    """
    global _regular_client
    if _regular_client is None:
        _regular_client = AzureOpenAIClient()
    return _regular_client

def get_functions_client():
    """
    Get the functions-enabled LLM client instance (singleton pattern)
    """
    global _functions_client
    if _functions_client is None:
        _functions_client = AzureOpenAIFunctions()
    return _functions_client