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

# Import Google GenAI SDK (unified package)
from google import genai
from google.genai import types

load_dotenv()

class GoogleGeminiClient:
    """
    Basic client for Google Gemini using the unified Google GenAI SDK.

    Attributes:
        client: The Google GenAI client instance.
        model: The Gemini model to use for text generation.
    """
    def __init__(self):
        if not settings.is_gemini_configured:
            raise ValueError("Missing Google Gemini configuration.")
        
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
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        self.model = settings.GEMINI_MODEL
        logging.info(f"Initialized Google Gemini client with model: {self.model}")
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 8192,
        auto_continue: bool = True,
        max_continuations: int = 2,
        system_instruction: Optional[str] = None,
        thinking_budget: Optional[int] = None,
    ) -> str:
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
            # Build thinking config
            thinking_cfg = None
            if thinking_budget is not None:
                # Explicit param takes precedence
                if thinking_budget > 0:
                    thinking_cfg = types.ThinkingConfig(thinking_budget=thinking_budget)
                # thinking_budget=0 means no thinking config (disabled)
            elif hasattr(settings, 'GEMINI_THINKING_BUDGET') and settings.GEMINI_THINKING_BUDGET:
                # Fall back to settings
                try:
                    budget = int(settings.GEMINI_THINKING_BUDGET)
                    if budget > 0:
                        thinking_cfg = types.ThinkingConfig(thinking_budget=budget)
                except (ValueError, TypeError):
                    logging.warning(f"Invalid GEMINI_THINKING_BUDGET: {settings.GEMINI_THINKING_BUDGET}")

            # Build config with all options
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                thinking_config=thinking_cfg,
            )
            
            # Add system instruction if provided (NEW)
            if system_instruction:
                config.system_instruction = system_instruction

            # Make the API call
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )

            # Extract text from response
            response_text = self._extract_text(response)
            
            # Handle truncation with auto-continuation (existing logic)
            if auto_continue and self._is_truncated(response):
                continuations = 0
                while continuations < max_continuations and self._is_truncated(response):
                    continuations += 1
                    logging.info(f"Response truncated, attempting continuation {continuations}")
                    
                    continuation_prompt = f"{prompt}\n\n{response_text}\n\nPlease continue from where you left off:"
                    
                    response = await self.client.aio.models.generate_content(
                        model=self.model,
                        contents=continuation_prompt,
                        config=config,  # Reuse same config including system_instruction
                    )
                    
                    continuation_text = self._extract_text(response)
                    response_text += continuation_text

            return response_text

        except Exception as e:
            logging.error(f"Gemini generation error: {e}")
            raise

    def _extract_text(self, response) -> str:
        """Extract text from response, handling multiple parts."""
        if not response.candidates:
            return ""
        
        parts = response.candidates[0].content.parts
        text_parts = [part.text for part in parts if hasattr(part, 'text') and part.text]
        return "".join(text_parts)
    
    def _is_truncated(self, response) -> bool:
        """Check if response was truncated due to max tokens."""
        if not response.candidates:
            return False
        
        finish_reason = response.candidates[0].finish_reason
        # Check for MAX_TOKENS finish reason
        return finish_reason == "MAX_TOKENS" or str(finish_reason) == "2"

    
    def generate_sync(self, prompt: str, temperature: float = 0.7, max_tokens: int = 8192) -> str:
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
            
            logging.error("Empty response from Gemini API")
            raise Exception("Empty response from Gemini API")
                
        except Exception as e:
            logging.error(f"Error calling Google Gemini API: {str(e)}")
            raise
    
    async def generate_stream(self, prompt: str, temperature: float = 0.7, max_tokens: int = 8192):
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
    Client for Google Gemini with support for function calling using the unified Google GenAI SDK.

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
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        self.model = settings.GEMINI_MODEL
        logging.info(f"Initialized Google Gemini Functions client with model: {self.model}")
    
    async def generate_with_functions(
        self, 
        prompt: str, 
        functions: List[Union[callable, Dict[str, Any]]], 
        max_tokens: int = 8192,
        temperature: float = 0.7,
        function_call: Union[str, Dict[str, str], None] = None,
        system_instruction: Optional[str] = None,
        thinking_budget: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate a response from Google Gemini with function calling.

        Args:
            prompt (str): The user prompt to send to the Gemini API.
            functions (List): List of function definitions or callable functions.
            max_tokens (int): The maximum number of tokens to generate in the response.
            temperature (float): Controls randomness in the output (0.0 to 1.0).
            function_call (Union[str, Dict[str, str], None]): For OpenAI compatibility. 
                Can be "auto", "none", or {"name": "function_name"} to force a specific function call.

        Returns:
            Dict[str, Any]: A dictionary containing either the message content or function call details.
        """
        try:
            tools = [] 
            for func in functions:
                if callable(func):
                    tools.append(func)
                elif isinstance(func, dict) and "name" in func:
                    # Convert dict to FunctionDeclaration 
                    tools.append(types.Tool(
                        function_declarations=[types.FunctionDeclaration(
                            name=func["name"],
                            description=func.get("description", ""),
                            parameters=func.get("parameters", {})
                        )]
                    ))
                else:
                    tools.append(func)

            tool_config = None 
            if function_call:
                if function_call == "none":
                    tool_config = types.ToolConfig(
                        function_calling_config=types.FunctionCallingConfig(mode="NONE")
                    )
                elif function_call == "auto":
                    tool_config = types.ToolConfig(
                        function_calling_config=types.FunctionCallingConfig(mode="AUTO")
                    )
                elif isinstance(function_call, dict) and "name" in function_call:
                    # Force specific function call
                    tool_config = types.ToolConfig(
                        function_calling_config=types.FunctionCallingConfig(
                            mode="ANY",
                            allowed_function_names=[function_call["name"]]
                        )
                    )

            # Build thinking config if specified 
            thinking_cfg = None 
            if thinking_budget is not None:
                thinking_cfg = types.ThinkingConfig(thinking_budget=thinking_budget)
            elif settings.GEMINI_THINKING_BUDGET:
                thinking_cfg = types.ThinkingConfig(
                    thinking_budget=int(settings.GEMINI_THINKING_BUDGET)
                )

            # Build the config 
            config = types.GenerateContentConfig(
                tools=tools,
                tool_config=tool_config,
                temperature=temperature,
                max_output_tokens=max_tokens,
                thinking_config=thinking_cfg
            )

            # Add system nstruction:
            if system_instruction:
                config.system_instruction = system_instruction

            # Generate content 
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )

            # Check for function calls first
            if response.function_calls:
                fn_call = response.function_calls[0]
                return {
                    "type": "function_call",
                    "name": fn_call.name,
                    "arguments": dict(fn_call.args) if fn_call.args else {}
                }

            # Otherwise return text 
            if response.text:
                return {"type": "text", "content": response.text}

            raise Exception("Empty response from Gemini API")

        except Exception as e:
            logging.error(f"Error in generate_with_functions: {str(e)}")
            raise 

    async def generate_structured(
        self,
        prompt: str,
        response_schema: type,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        thinking_budget: Optional[int] = None,
    ) -> Any:
        """
        Generate structured output using pydantic schema.

        Args:
            prompt: User prompt 
            response_schema: Pydantic BaseModel class defining output structure 
            system_instruction: System-level instructions

        Returns:
            Validated Pydantic model instance
        """
        thinking_cfg = None 
        if thinking_budget:
            thinking_cfg = types.ThinkingConfig(thinking_budget=thinking_budget)

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=temperature,
                thinking_config=thinking_cfg,
            )
        )

        # Parse and validate with Pydantic
        return response_schema.model_validate_json(response.text)



#             # Handle function_call parameter for OpenAI compatibility
#             enhanced_prompt = prompt
#             if function_call and isinstance(function_call, dict) and "name" in function_call:
#                 forced_function_name = function_call["name"]
#                 enhanced_prompt = f"""{prompt}

# IMPORTANT: You MUST call the '{forced_function_name}' function to respond to this request. Do not provide a text response."""
            
#             # Convert OpenAI-style function definitions to Gemini-compatible tools
#             tools = []
#             for func in functions:
#                 if callable(func):
#                     tools.append(func)
#                 elif isinstance(func, dict) and "name" in func:
#                     function_declaration = types.FunctionDeclaration(
#                         name=func["name"],
#                         description=func["description"],
#                         parameters=func.get("parameters", {})
#                     )
#                     tool = types.Tool(function_declarations=[function_declaration])
#                     tools.append(tool)
#                 else:
#                     tools.append(func)
            
#             # Generate content with function calling
#             response = await self.client.aio.models.generate_content(
#                 model=self.model,
#                 contents=enhanced_prompt,
#                 config=types.GenerateContentConfig(
#                     tools=tools,
#                     temperature=temperature,
#                     max_output_tokens=max_tokens,
#                 )
#             )
            
#             # Process first candidate only
#             if response.candidates and len(response.candidates) > 0:
#                 candidate = response.candidates[0]
#                 if candidate.content and candidate.content.parts:
#                     for part in candidate.content.parts:
#                         if hasattr(part, 'function_call') and part.function_call:
#                             # Rename variable to avoid parameter shadowing
#                             fn_call = part.function_call
#                             return {
#                                 "type": "function_call",
#                                 "name": fn_call.name,
#                                 "arguments": dict(fn_call.args) if fn_call.args else {}
#                             }
            
#             if response and response.text:
#                 return {"type": "text", "content": response.text}
            
#             logging.error("Empty response from Gemini API")
#             raise Exception("Empty response from Gemini API")
                
#         except Exception as e:
#             logging.error(f"Error calling Google Gemini API with functions: {str(e)}")
#             raise

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
def get__client():
    """Deprecated: Use get_llm_client() instead"""
    logging.warning("get_azure_client() is deprecated. Use get_llm_client() instead.")
    return get_llm_client()

def get_azure_functions_client():
    """Deprecated: Use get_functions_client() instead"""
    logging.warning("get_azure_functions_client() is deprecated. Use get_functions_client() instead.")
    return get_functions_client()