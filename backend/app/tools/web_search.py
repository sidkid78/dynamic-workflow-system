# app/tools/search_tools.py
import os
import aiohttp
import logging
from typing import Dict, Any, List, Optional
import json
from .base import Tool  # Import from base.py

class WebSearchTool(Tool):
    """
    Tool for performing web searches using Google Custom Search 
    """
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search for information on the web using Google Custom Search",
            function=self.search,
            requires_setup=True
        )
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.cse_id = os.getenv("GOOGLE_CSE_ID")
        self.base_url = "https://www.googleapis.com/customsearch/v1"

        if self.api_key and self.cse_id:
            self.is_setup = True
        else:
            self.is_setup = False 
        
    def setup(self) -> bool:
        """Set up the search tool by checking for required credentials"""
        if not self.api_key or not self.cse_id:
            self.api_key = os.getenv("GOOGLE_API_KEY")
            self.cse_id = os.getenv("GOOGLE_CSE_ID")
            
        self.is_setup = bool(self.api_key and self.cse_id)
        return self.is_setup
        
    async def search(self, query: str, num_results: int = 3) -> str:
        """
        Perform a web search
        
        Args:
            query: The search query
            num_results: Number of results to return (1-10)
            
        Returns:
            A formatted string containing search results
        """
        if not self.is_setup:
            setup_success = self.setup()
            if not setup_success:
                return "Web search is not available: API credentials not configured."
                
        if not query or not isinstance(query, str):
            return "Error: Search query must be a non-empty string."
            
        # Limit number of results to valid range
        try:
            num_results = int(num_results)
            num_results = max(1, min(10, num_results))
        except (ValueError, TypeError):
            num_results = 3
            
        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": query,
            "num": num_results
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logging.error(f"Google CSE error: {error_text}")
                        return f"Search error (HTTP {response.status}): Unable to complete search."
                    
                    data = await response.json()
                    
                    # Format the results
                    if "items" not in data or not data["items"]:
                        return f"No results found for query: '{query}'"
                    
                    formatted_text = f"Search Results for: '{query}'\n\n"
                    
                    for i, item in enumerate(data["items"], 1):
                        title = item.get("title", "No title")
                        link = item.get("link", "")
                        snippet = item.get("snippet", "No description")
                        source = item.get("displayLink", "Unknown source")
                        
                        formatted_text += f"{i}. {title}\n"
                        formatted_text += f"   Source: {source}\n"
                        formatted_text += f"   {snippet}\n"
                        formatted_text += f"   URL: {link}\n\n"
                    
                    if "searchInformation" in data:
                        info = data["searchInformation"]
                        if "formattedTotalResults" in info:
                            formatted_text += f"Total results: {info['formattedTotalResults']}\n"
                    
                    return formatted_text
                    
        except Exception as e:
            logging.error(f"Error performing web search: {str(e)}")
            return f"Search error: {str(e)}"
    
    def get_function_definition(self):
        """
        Get the function definition for use in the autonomous agent
        
        This version includes better debugging and parameter handling
        """
        from app.core.workflows.autonomous_agent import ToolDefinition
    
        async def search_wrapper(**kwargs):
            """Wrapper with explicit debugging and parameter handling"""
            logging.info(f"Web search tool received kwargs: {kwargs}")
         
            # Directly extract query parameter with fallback
            query = None
            if 'query' in kwargs:
                query = kwargs['query']
            # Handle case where parameters might be nested one level deeper
            elif isinstance(kwargs.get('tool_parameters'), dict):
                query = kwargs['tool_parameters'].get('query')
            
            # Log what we found
            logging.info(f"Web search extracted query: {query}")
            
            # Safe conversion for num_results
            try:
                num_results = int(kwargs.get('num_results', 3))
            except (ValueError, TypeError):
                num_results = 3
            
            if not query:
                error_msg = f"Error: Search query is required. Received parameters: {kwargs}"
                logging.error(error_msg)
                return error_msg

            # Execute the search with the extracted parameters
            return await self.search(query, num_results)
        
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string", 
                        "description": "The search query"
                    },
                    "num_results": {
                        "type": "integer", 
                        "description": "Number of results to return (1-10, default: 3)"
                    }
                },
                "required": ["query"]
            },
            function=search_wrapper
        )

# Create and register the web search tool
web_search = WebSearchTool()

# Convenience function to get the web search tool for autonomous agent
def get_web_search_tool_definition():
    """Get the web search tool definition for autonomous agent"""
    return web_search.get_function_definition()