# app/tools/base.py
"""
Base classes for tools
"""
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)

class Tool:
    """
    Base class for all tools usable by workflows
    """
    def __init__(
        self, 
        name: str, 
        description: str, 
        function: Callable,
        requires_setup: bool = False
    ):
        self.name = name
        self.description = description
        self.function = function
        self.requires_setup = requires_setup
        self.is_setup = not requires_setup
        
    async def execute(self, **kwargs) -> str:
        """
        Execute the tool with the provided arguments
        """
        if self.requires_setup and not self.is_setup:
            return f"Tool '{self.name}' requires setup before use."
            
        try:
            result = self.function(**kwargs)
            # Handle both regular and async functions
            if hasattr(result, '__await__'):
                return await result
            return result
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {str(e)}")
            return f"Error executing {self.name}: {str(e)}"
    
    def setup(self) -> bool:
        """
        Set up the tool. Override in subclasses if needed.
        """
        self.is_setup = True
        return True
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format for prompts
        """
        return {
            "name": self.name,
            "description": self.description
        } 