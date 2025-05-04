# app/main.py
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import workflows
from app.config import settings
import logging
import importlib
from app.tools.registry import initialize_tools as initialize_tool_registry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Initialize tools
def init_tools():
    """Initialize all available tools and register them."""
    logging.info("Initializing tools...")
    
    # Initialize tool registry (which imports and registers toolsets)
    initialize_tool_registry()
    
    # Import tools to register them
    try:
        importlib.import_module("app.tools.calculator")
        logging.info("Calculator tool initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing calculator tool: {str(e)}")
    
    # Initialize web search tool
    try:
        importlib.import_module("app.tools.web_search")
        logging.info("Web search tool initialized successfully")
        
        # Check if it's properly configured by importing the instance
        from app.tools.web_search import web_search as web_search_instance
        
        if web_search_instance and web_search_instance.is_setup:
            logging.info("Web search tool is fully configured")
        else:
            logging.warning("Web search tool is registered but not fully configured")
    except Exception as e:
        logging.error(f"Error initializing web search tool: {str(e)}")
    
    # Add other tool imports here as needed
    
    # Log all registered tools from the registry
    try:
        from app.tools.registry import list_tools
        tools = list_tools()
        logging.info(f"Final registered tools: {', '.join(tools)}")
    except Exception as e:
        logging.error(f"Error listing tools after registry initialization: {e}")
    
    logging.info("Tools initialization complete")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="A system that dynamically selects and executes workflow patterns based on user queries",
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Initialize tools on startup
@app.on_event("startup")
async def startup_event():
    init_tools()

# Configure CORS
app.add_middleware(
    CORSMiddleware,  # Pass class as positional argument
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(workflows.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the Dynamic Workflow API"}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring services"""
    # Check if web search is configured
    try:
        from app.tools.registry import get_tool
        web_search = get_tool("web_search")
        web_search_status = "configured" if web_search and web_search.is_setup else "not_configured"
    except:
        web_search_status = "error"
    
    return {
        "status": "healthy", 
        "tools_available": True,
        "web_search": web_search_status
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)

print('...', file=sys.stderr)