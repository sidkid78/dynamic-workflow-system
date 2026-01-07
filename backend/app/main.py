# app/main.py
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import workflows
from app.config import settings
import logging
import importlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)



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
    # init_tools()
    pass

# 
# Configure CORS
app.add_middleware(
    CORSMiddleware,  # Pass class as positional argument
    allow_origins=settings.CORS_ORIGINS, # Restore specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(workflows.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the Dynamic Workflow API"}



if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)

print('...', file=sys.stderr)