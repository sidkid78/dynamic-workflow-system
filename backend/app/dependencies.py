from app.services.file_system import FileSystemService
from app.config import settings
from functools import lru_cache

# Create a singleton instance of the FileSystemService
@lru_cache()
def get_file_system_service() -> FileSystemService:
    service = FileSystemService(base_path=settings.AGENT_WORKSPACE_PATH)
    # Grant basic permissions to a default agent ID for now
    # In a real app, this would be more sophisticated
    service.grant_permission("default_agent", {
        "read": True, 
        "write": True, 
        "delete": True
    })
    return service 