# app/tools/search_tools.py
import os
import aiohttp
import logging
from typing import Dict, Any, List, Optional
import json

class GoogleCustomSearchTool:
    """
    Tool for performing Google Custom Search Engine (CSE) searches
    """
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.cse_id = os.getenv("GOOGLE_CSE_ID")
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        if not self.api_key or not self.cse_id:
            raise ValueError("Google API key and CSE ID must be set in environment variables")
            
    async def search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Perform a Google Custom Search
        
        Args:
            query: The search query
            num_results: Number of results to return (1-10)
            
        Returns:
            Dict containing search results and metadata
        """
        if not query:
            return {"error": "Query cannot be empty"}
            
        # Limit number of results to valid range
        num_results = max(1, min(10, num_results))
        
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
                        return {
                            "error": f"Search API returned status {response.status}",
                            "query": query
                        }
                    
                    data = await response.json()
                    
                    # Format the results
                    formatted_results = []
                    
                    if "items" in data:
                        for item in data["items"]:
                            formatted_results.append({
                                "title": item.get("title", "No title"),
                                "link": item.get("link", ""),
                                "snippet": item.get("snippet", "No description"),
                                "source": item.get("displayLink", "Unknown source")
                            })
                    
                    return {
                        "query": query,
                        "results_count": len(formatted_results),
                        "results": formatted_results,
                        "search_information": data.get("searchInformation", {})
                    }
                    
        except Exception as e:
            logging.error(f"Error performing Google search: {str(e)}")
            return {
                "error": f"Error performing search: {str(e)}",
                "query": query
            }
            
    async def get_search_summaries(self, query: str, num_results: int = 3) -> str:
        """
        Perform a search and return a summarized text version of the results
        
        Args:
            query: The search query
            num_results: Number of results to return
            
        Returns:
            A formatted string containing summarized search results
        """
        search_results = await self.search(query, num_results)
        
        if "error" in search_results:
            return f"Search Error: {search_results['error']}"
        
        if search_results["results_count"] == 0:
            return f"No results found for query: '{query}'"
        
        formatted_text = f"Search Results for: '{query}'\n\n"
        
        for i, result in enumerate(search_results["results"], 1):
            formatted_text += f"{i}. {result['title']}\n"
            formatted_text += f"   Source: {result['source']}\n"
            formatted_text += f"   {result['snippet']}\n"
            formatted_text += f"   URL: {result['link']}\n\n"
        
        if "searchInformation" in search_results:
            info = search_results["search_information"]
            if "formattedTotalResults" in info:
                formatted_text += f"Total results: {info['formattedTotalResults']}\n"
            if "searchTime" in info:
                formatted_text += f"Search time: {info['searchTime']:.2f} seconds\n"
        
        return formatted_text

# Function to create a search tool definition for the autonomous agent
def create_search_tool_definition():
    """Create a tool definition for Google Search"""
    from app.core.workflows.autonomous_agent import ToolDefinition
    
    # Initialize the search tool
    search_tool_instance = GoogleCustomSearchTool()
    
    # Create the tool definition
    search_tool = ToolDefinition(
        name="web_search",
        description="Search for information on the web using Google Custom Search",
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
        function=search_tool_instance.get_search_summaries
    )
    
    return search_tool