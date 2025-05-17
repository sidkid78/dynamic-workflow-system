# app/tools/registry.py
"""
Global registry for tools that can be used by any workflow
"""
import logging
from typing import Dict, Any, Callable, List, Optional, Coroutine
# from app.core.workflows.autonomous_agent import ToolDefinition # Old import
from app.models.schemas import ToolDefinition # Import from schemas
from .base import Tool # Import Tool from the new base file

# Import base tool wrappers/classes and tool lists
from .web_search import WebSearchTool
from .file_system_tools import file_system_tools # Import the list directly
from .calculator import CalculatorTool
from .web_scraper_wrapper import WebScraperWrapper
from .rag_retriever_wrapper import RAGRetrieverWrapper
from .search_tools import search_tools # Import search_tools
from .git_tools import git_tools       # Import git_tools
from .code_execution_tools import code_execution_tools
from .batch_tools import batch_tools

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

# Global registry for tool definitions
_TOOL_REGISTRY: Dict[str, ToolDefinition] = {}
_ALL_TOOLS_LIST: List[ToolDefinition] = []

# Type alias for tool functions (can be async or sync)
ToolFunction = Callable[..., Coroutine[Any, Any, str]] | Callable[..., str]

class ToolRegistryError(Exception):
    "Custom exception for tool registry errors."
    pass

def register_tool(tool_definition: ToolDefinition):
    """
    Registers a tool definition in the global registry.
    The tool_definition should be an instance of schemas.ToolDefinition.
    """
    if not isinstance(tool_definition, ToolDefinition):
        raise ToolRegistryError(f"Attempted to register an object that is not a ToolDefinition: {type(tool_definition)}")
    if not tool_definition.name or not callable(tool_definition.function):
        raise ToolRegistryError(f"Invalid ToolDefinition for '{tool_definition.name}': Missing name or non-callable function.")
    
    if tool_definition.name in _TOOL_REGISTRY:
        logger.warning(f"Tool '{tool_definition.name}' is being re-registered. Overwriting existing definition.")
    
    _TOOL_REGISTRY[tool_definition.name] = tool_definition
    # Add to list if it's not already there (based on object identity, or re-add if overwriting)
    # To avoid duplicates if re-registering, first remove by name if we want to ensure unique names in list
    _ALL_TOOLS_LIST[:] = [td for td in _ALL_TOOLS_LIST if td.name != tool_definition.name] # Remove old if exists
    _ALL_TOOLS_LIST.append(tool_definition)
    logger.debug(f"Tool '{tool_definition.name}' registered successfully.")

def get_tool(name: str) -> Optional[ToolDefinition]:
    """Retrieves a tool by name."""
    return _TOOL_REGISTRY.get(name)

def list_tools() -> List[str]:
    """Returns a list of names of all registered tools."""
    return list(_TOOL_REGISTRY.keys())

def get_all_tools() -> List[ToolDefinition]:
    """Returns a list of all registered tool definitions."""
    return _ALL_TOOLS_LIST.copy() # Return a copy to prevent external modification

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
    """
    Initializes and registers all available tools from their respective modules.
    This function should be called once at application startup.
    """
    if _TOOL_REGISTRY: # Prevent re-initialization if already done
        logger.info("Tool registry already initialized.")
        # return # Or decide to clear and re-initialize if dynamic reloading is needed

    logger.info("Initializing tool registry...")

    # 1. Register class-based tools (examples)
    # These require instantiation and then calling a method to get their ToolDefinition
    tools_to_register_class_based = [
        WebSearchTool(), 
        CalculatorTool(),
        WebScraperWrapper(),
        RAGRetrieverWrapper()
    ]
    for tool_instance in tools_to_register_class_based:
        try:
            if hasattr(tool_instance, 'get_tool_definition') and callable(tool_instance.get_tool_definition):
                tool_def = tool_instance.get_tool_definition()
                if isinstance(tool_def, ToolDefinition):
                    register_tool(tool_def)
                elif isinstance(tool_def, list): # If it returns a list of definitions
                    for single_def in tool_def:
                        if isinstance(single_def, ToolDefinition):
                            register_tool(single_def)
                        else:
                            logger.error(f"Item in list from {type(tool_instance).__name__}.get_tool_definition() is not a ToolDefinition: {type(single_def)}")
                else:
                     logger.error(f"{type(tool_instance).__name__}.get_tool_definition() did not return a ToolDefinition or list of them.")
            # Legacy support for get_function_definition (like original calculator)
            elif hasattr(tool_instance, 'get_function_definition') and callable(tool_instance.get_function_definition):
                definitions_or_dict = tool_instance.get_function_definition()
                
                if isinstance(definitions_or_dict, list): # Handle if it returns a list of ToolDefinitions
                    for single_def in definitions_or_dict:
                        if isinstance(single_def, ToolDefinition):
                            try:
                                register_tool(single_def)
                            except ToolRegistryError as e_reg:
                                logger.error(f"Error registering tool '{single_def.name if hasattr(single_def, 'name') else 'UNKNOWN'}' from list returned by {type(tool_instance).__name__}.get_function_definition(): {e_reg}")
                        else:
                            logger.error(f"Item in list from {type(tool_instance).__name__}.get_function_definition() is not a ToolDefinition: {type(single_def)}")
                elif isinstance(definitions_or_dict, dict):
                    # Attempt to create ToolDefinition from dict if structure matches.
                    try:
                        adapted_def = ToolDefinition(**definitions_or_dict) # Requires fields to match
                        register_tool(adapted_def)
                    except Exception as e_adapt:
                        logger.error(f"Could not adapt legacy dict from {type(tool_instance).__name__}.get_function_definition() to ToolDefinition: {e_adapt}")
                elif isinstance(definitions_or_dict, ToolDefinition):
                    try:
                        register_tool(definitions_or_dict)
                    except ToolRegistryError as e_reg_single:
                         logger.error(f"Error registering single tool from {type(tool_instance).__name__}.get_function_definition(): {e_reg_single}")
                else:
                    logger.error(f"Unsupported return type from {type(tool_instance).__name__}.get_function_definition(): {type(definitions_or_dict)}")       
            else:
                logger.error(f"Tool instance {type(tool_instance).__name__} does not have a recognized method to get its definition.")
        except Exception as e:
            logger.error(f"Error registering tool instance {type(tool_instance).__name__}: {e}", exc_info=True)

    # 2. Register lists of ToolDefinitions from modules
    tool_lists_to_register = [
        file_system_tools,
        search_tools,       # New
        git_tools,          # New
        code_execution_tools, # New
        batch_tools         # New
    ]

    for tool_list in tool_lists_to_register:
        if isinstance(tool_list, list):
            for tool_def in tool_list:
                if isinstance(tool_def, ToolDefinition):
                    try:
                        register_tool(tool_def)
                    except ToolRegistryError as e:
                        logger.error(f"Error registering tool '{tool_def.name if hasattr(tool_def, 'name') else 'UNKNOWN'}': {e}")
                    except Exception as e:
                         logger.error(f"Unexpected error registering tool '{tool_def.name if hasattr(tool_def, 'name') else 'UNKNOWN'}': {e}", exc_info=True)
                else:
                    logger.error(f"Item in a tool list is not a ToolDefinition: {type(tool_def)}")
        else:
            logger.error(f"Expected a list of ToolDefinitions, but got: {type(tool_list)}")

    logger.info(f"Tool registry initialization complete. Total tools registered: {len(_TOOL_REGISTRY)}")

# Call initialize_tools() when this module is imported to populate the registry.
# Ensure this is safe to call multiple times if modules are reloaded, or guard it.
# For a typical FastAPI app, this would be called during startup (e.g., in main.py or lifespan event).
# If initialize_tools is called here, it runs on first import. 
# If registry.py is imported multiple times without a guard, it might re-run.
# Current implementation of initialize_tools has a basic guard.

# initialize_tools() # Deferred to be called explicitly at app startup.

# Instead of calling here, ensure init_tools() in main.py calls this:
# from app.tools.registry import initialize_tools as init_registry
# def init_tools():
#    ... (other initializations)
#    init_registry()
#    ...