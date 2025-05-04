import logging
from typing import List, Dict, Any, Optional
from app.services.rag_tools import WebScraperTool
# from app.services.file_system import FileSystemService # Don't import directly
from app.dependencies import get_file_system_service # Import the getter
# from app.core.workflows.autonomous_agent import ToolDefinition # Old import
from app.models.schemas import ToolDefinition # Import from schemas

logger = logging.getLogger(__name__)

class WebScraperWrapper:
    """Wraps the WebScraperTool to provide individual tool definitions for the registry."""
    
    def __init__(self):
        # Initialize the underlying service. Consider dependency injection if needed.
        # Assuming FileSystemService has a default constructor or is available globally.
        try:
            # self.fs_service = FileSystemService() # Don't instantiate directly
            self.fs_service = get_file_system_service() # Use the dependency getter
            self.scraper = WebScraperTool(file_system_service=self.fs_service)
            self.is_setup = True
            logger.info("WebScraperWrapper initialized with WebScraperTool.")
        except Exception as e:
            logger.error(f"Failed to initialize WebScraperWrapper: {e}", exc_info=True)
            self.scraper = None
            self.is_setup = False

    def get_function_definition(self) -> List[ToolDefinition]:
        """Returns a list of ToolDefinition objects for the scraper's capabilities."""
        if not self.is_setup or not self.scraper:
            return []

        definitions = [
            ToolDefinition(
                name="web_scrape_and_save",
                description="Scrapes a single web page URL, extracts text/HTML, and saves it to the agent's workspace. Requires the agent ID for saving.",
                parameters={
                    "agent_id": {"type": "string", "description": "The ID of the agent performing the action.", "required": True},
                    "url": {"type": "string", "description": "The URL of the web page to scrape.", "required": True}
                },
                function=self.scraper.scrape_and_save # Direct reference to the bound method
            ),
            ToolDefinition(
                name="web_crawl_and_scrape",
                description="Starts crawling from a given URL, scrapes pages within the same domain (or specified prefix), and saves them. Limited by max_pages.",
                parameters={
                    "agent_id": {"type": "string", "description": "The ID of the agent performing the action.", "required": True},
                    "start_url": {"type": "string", "description": "The initial URL to begin crawling.", "required": True},
                    "max_pages": {"type": "integer", "description": "Maximum number of pages to scrape (default: 10)."},
                    "allowed_prefix": {"type": "string", "description": "Optional URL prefix to restrict crawling (e.g., 'https://example.com/docs/')."}
                },
                function=self.scraper.crawl_and_scrape
            ),
            ToolDefinition(
                name="get_weather_data",
                description="Fetches the current weather data for a specified location using OpenWeatherMap.",
                parameters={
                    "location": {"type": "string", "description": "The city name or location (e.g., 'London', 'Paris,FR').", "required": True},
                    "units": {"type": "string", "description": "Units for temperature ('metric' for Celsius, 'imperial' for Fahrenheit - default: metric)."}
                },
                function=self.scraper.get_weather_data
            )
        ]
        return definitions

# Optional: Add execute methods if needed for direct execution via wrapper (less common for agent use)
# async def execute_scrape(self, agent_id: str, url: str):
#     if not self.is_setup: return "Web scraper not initialized."
#     return await self.scraper.scrape_and_save(agent_id, url)

# async def execute_crawl(self, agent_id: str, start_url: str, max_pages: int = 10, allowed_prefix: Optional[str] = None):
#     if not self.is_setup: return "Web scraper not initialized."
#     return await self.scraper.crawl_and_scrape(agent_id, start_url, max_pages, allowed_prefix)

# async def execute_weather(self, location: str, units: str = 'metric'):
#     if not self.is_setup: return "Web scraper not initialized."
#     # Assuming get_weather_data can be async or sync. If sync, wrap if needed.
#     # We need to ensure the underlying method is awaitable if called with await
#     # The scraper's get_weather_data seems synchronous based on rag_tools.py
#     # For simplicity, let's assume the registry handles calling sync/async appropriately
#     # or we make the underlying tool async.
#     # Let's modify the ToolDefinition function reference to call it directly.
#     return self.scraper.get_weather_data(location, units) # Assuming direct call is okay 