# app/tools/registry.py
"""
Global registry for tools that can be used by any workflow
"""
import logging
from typing import Dict, Any, Callable, List, Optional
# from app.core.workflows.autonomous_agent import ToolDefinition # Old import
from app.models.schemas import ToolDefinition # Import from schemas
from .base import Tool # Import Tool from the new base file

# Import base tool wrappers/classes and tool lists
from .web_search import WebSearchTool
from .file_system_tools import file_system_tools # Import the list directly
from .calculator import CalculatorTool
from .web_scraper_wrapper import WebScraperWrapper
from .rag_retriever_wrapper import RAGRetrieverWrapper

logger = logging.getLogger(__name__)

# Registry to hold all available tools
_global_tools = {}

# In-memory storage for tools
_tools: Dict[str, ToolDefinition] = {}

# Dictionary to hold tool instances (singleton pattern)
_tool_instances: Dict[str, Any] = {}

# List of tool classes/wrappers to register
# FileSystemToolsWrapper is removed as it doesn't exist
_TOOL_CLASSES = [
    WebSearchTool,
    # FileSystemToolsWrapper removed
    CalculatorTool,
    WebScraperWrapper,
    RAGRetrieverWrapper
]

def register_tool(tool: ToolDefinition):
    """Registers a tool definition."""
    if tool.name in _tools:
        logger.warning(f"Tool '{tool.name}' is already registered. Overwriting.")
    _tools[tool.name] = tool
    logger.info(f"Registered tool: {tool.name}")

def get_tool(name: str) -> Optional[ToolDefinition]:
    """Retrieves a tool by name."""
    return _tools.get(name)

def list_tools() -> List[str]:
    """Returns a list of names of all registered tools."""
    return list(_tools.keys())

def get_all_tools() -> Dict[str, ToolDefinition]:
    """Returns the dictionary of all registered tools."""
    return _tools.copy()

def _initialize_tools():
    """Initialize tool instances if not already done."""
    global _tool_instances
    if not _tool_instances:
        logger.info("Initializing tool instances...")
        for tool_cls in _TOOL_CLASSES:
            try:
                instance = tool_cls()
                # We store the instance by its class name for potential internal use
                _tool_instances[tool_cls.__name__] = instance
                logger.info(f"Initialized tool wrapper: {tool_cls.__name__}")
            except Exception as e:
                logger.error(f"Failed to initialize tool {tool_cls.__name__}: {e}", exc_info=True)
        logger.info(f"Tool initialization complete. {_tool_instances.keys()}")

def get_all_tools() -> Dict[str, Any]:
    """
    Returns a dictionary of all *individual tool functions* derived from wrappers,
    keyed by their intended callable name (e.g., 'web_search', 'read_file').

    This is used by ToolService to provide definitions to the autonomous agent.
    """
    _initialize_tools()
    all_individual_tools = {}

    for wrapper_instance in _tool_instances.values():
        # Check if the wrapper instance provides individual function definitions
        if hasattr(wrapper_instance, 'get_function_definition') and callable(wrapper_instance.get_function_definition):
            try:
                # This method should return a list or single ToolDefinition object
                definitions = wrapper_instance.get_function_definition()

                if isinstance(definitions, list): # Handle wrappers returning multiple tools
                    for tool_def in definitions:
                         if tool_def.name in all_individual_tools:
                             logger.warning(f"Duplicate tool name '{tool_def.name}' detected. Overwriting.")
                         all_individual_tools[tool_def.name] = tool_def
                         logger.debug(f"Registered individual tool: {tool_def.name}")

                elif isinstance(definitions, ToolDefinition): # Handle wrappers returning a single tool
                     tool_def = definitions
                     if tool_def.name in all_individual_tools:
                         logger.warning(f"Duplicate tool name '{tool_def.name}' detected. Overwriting.")
                     all_individual_tools[tool_def.name] = tool_def
                     logger.debug(f"Registered single tool: {tool_def.name}")
                else:
                    logger.error(f"Wrapper {type(wrapper_instance).__name__} returned unexpected type from get_function_definition: {type(definitions)}")

            except Exception as e:
                logger.error(f"Error getting function definitions from {type(wrapper_instance).__name__}: {e}", exc_info=True)
    
    # Also add the directly imported file system tools
    for tool_def in file_system_tools:
        if tool_def.name in all_individual_tools:
            logger.warning(f"Duplicate tool name '{tool_def.name}' detected (from file_system_tools list). Overwriting.")
        all_individual_tools[tool_def.name] = tool_def
        logger.debug(f"Registered individual tool from file_system_tools list: {tool_def.name}")

    if not all_individual_tools:
        logger.warning("No individual tools were registered. Check wrapper implementations and get_function_definition methods.")

    logger.info(f"Returning {len(all_individual_tools)} individual tools: {list(all_individual_tools.keys())}")
    return all_individual_tools

# Import and register toolsets
def initialize_tools():
    # Register calculator tool
    try:
        from .calculator import calculator # Import the instance
        if hasattr(calculator, 'get_function_definition'):
            register_tool(calculator.get_function_definition()) # Register the ToolDefinition
        else:
             logger.error("Calculator tool instance does not have get_function_definition method.")
    except ImportError:
        logger.warning("Calculator tool not found or couldn't be imported.")
    except Exception as e:
        logger.error(f"Error registering calculator tool: {e}", exc_info=True)
        
    # Register web search tool
    try:
        from .web_search import web_search # Import the instance
        logger.info("Attempting to register web_search tool...")
        if hasattr(web_search, 'get_function_definition'):
            logger.info("web_search instance has get_function_definition method.")
            the_definition = web_search.get_function_definition()
            logger.info(f"Successfully obtained ToolDefinition: {type(the_definition)}")
            tool_name = the_definition.name
            logger.info(f"ToolDefinition name is: {tool_name}")
            register_tool(the_definition)
            logger.info(f"Successfully called register_tool for {tool_name}")
        else:
            logger.error("Web search tool instance does not have get_function_definition method.")
    except ImportError:
        logger.warning("Web search tool not found or couldn't be imported.")
    except Exception as e:
        logger.error(f"Error registering web search tool: {e}", exc_info=True)
        
    # Register file system tools (already imported as a list)
    try:
        # file_system_tools is already imported at the top
        for tool in file_system_tools:
            register_tool(tool)
        logger.info(f"Registered {len(file_system_tools)} file system tools.")
    except NameError:
        logger.error("file_system_tools list not found. Check import at the top of registry.py.")
    except Exception as e:
        logger.error(f"Error registering file system tools: {e}", exc_info=True)

# Instead of calling here, ensure init_tools() in main.py calls this:
# from app.tools.registry import initialize_tools as init_registry
# def init_tools():
#    ... (other initializations)
#    init_registry()
#    ...