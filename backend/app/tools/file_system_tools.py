"""
File system tools for managing files and directories within an agent's workspace.

This module provides tools for common file system operations like reading, writing,
listing, deleting, moving, and copying files and directories. All operations are
scoped to the agent's designated workspace for security.

Classes:
    ReadFileParams: Pydantic model for file read parameters
    WriteFileParams: Pydantic model for file write parameters
    ListFilesParams: Pydantic model for directory listing parameters
    DeleteFileParams: Pydantic model for file deletion parameters
    CreateDirectoryParams: Pydantic model for directory creation parameters
    MoveFileParams: Pydantic model for file/directory move parameters
    CopyFileParams: Pydantic model for file copy parameters
    GetMetadataParams: Pydantic model for metadata retrieval parameters

Functions:
    read_file_wrapper: Reads content from a file
    write_file_wrapper: Writes content to a file
    list_files_wrapper: Lists directory contents
    delete_file_wrapper: Deletes a file
    create_directory_wrapper: Creates a new directory
    move_file_wrapper: Moves/renames files and directories
    copy_file_wrapper: Copies files
    get_metadata_wrapper: Gets file/directory metadata

Tool Definitions:
    fs_read_tool: Tool definition for file reading
    fs_write_tool: Tool definition for file writing
    fs_list_tool: Tool definition for directory listing
    fs_delete_tool: Tool definition for file deletion
    fs_create_dir_tool: Tool definition for directory creation
    fs_move_tool: Tool definition for file/directory moving
    fs_copy_tool: Tool definition for file copying
    fs_metadata_tool: Tool definition for metadata retrieval

Constants:
    DEFAULT_AGENT_ID: Default agent ID used when none is provided
    file_system_tools: List of all file system tools for registration
"""

from app.models.schemas import ToolDefinition
from app.dependencies import get_file_system_service
from pydantic import BaseModel, Field
import logging
from fastapi import HTTPException # For catching errors from the service

logger = logging.getLogger(__name__)
# DEFAULT_AGENT_ID = "default_agent" # No longer used by these wrappers

# --- Pydantic Schemas for Parameters --- 

class ReadFileParams(BaseModel):
    file_path: str = Field(..., description="The relative path to the file within the agent workspace.")

class WriteFileParams(BaseModel):
    file_path: str = Field(..., description="The relative path where the file should be written within the agent workspace.")
    content: str = Field(..., description="The content to write into the file.")

class ListFilesParams(BaseModel):
    directory_path: str = Field(".", description="The relative path to the directory within the agent workspace. Defaults to the workspace root ('.').")

class DeleteFileParams(BaseModel):
    file_path: str = Field(..., description="The relative path to the file to delete within the agent workspace.")

class CreateDirectoryParams(BaseModel):
    directory_path: str = Field(..., description="The relative path for the new directory within the agent workspace.")

class MoveFileParams(BaseModel):
    old_path: str = Field(..., description="The current relative path of the file/directory to move within the agent workspace.")
    new_path: str = Field(..., description="The desired new relative path for the file/directory within the agent workspace.")

class CopyFileParams(BaseModel):
    source_path: str = Field(..., description="The relative path of the source file to copy within the agent workspace.")
    destination_path: str = Field(..., description="The relative path where the file should be copied to within the agent workspace.")

class GetMetadataParams(BaseModel):
    path: str = Field(..., description="The relative path to the file or directory within the agent workspace to get metadata for.")

# --- Tool Wrapper Functions (Refactored for agent_id) --- 

async def read_file_wrapper(agent_id: str, file_path: str) -> str:
    """Reads content from a specified file within the given agent's workspace."""
    try:
        service = get_file_system_service()
        # FileSystemServiceread_file now expects agent_id and file_path relative to that agent's workspace
        return service.read_file(agent_id, file_path)
    except HTTPException as e:
        logger.error(f"Agent {agent_id} - Service error reading file '{file_path}': {e.detail}")
        return f"Error reading file '{file_path}': {e.detail}"
    except Exception as e:
        logger.error(f"Unexpected error in read_file_wrapper for agent {agent_id}, path '{file_path}': {e}", exc_info=True)
        return f"Unexpected error reading file '{file_path}': {str(e)}"

async def write_file_wrapper(agent_id: str, file_path: str, content: str) -> str:
    """Writes content to a specified file in the given agent's workspace, creating directories if needed."""
    try:
        service = get_file_system_service()
        service.write_file(agent_id, file_path, content)
        return f"Successfully wrote content to '{file_path}' in agent '{agent_id}' workspace."
    except HTTPException as e:
        logger.error(f"Agent {agent_id} - Service error writing file '{file_path}': {e.detail}")
        return f"Error writing file '{file_path}': {e.detail}"
    except Exception as e:
        logger.error(f"Unexpected error in write_file_wrapper for agent {agent_id}, path '{file_path}': {e}", exc_info=True)
        return f"Unexpected error writing file '{file_path}': {str(e)}"

async def list_files_wrapper(agent_id: str, directory_path: str = ".") -> str:
    """Lists files and directories within a specified directory in the given agent's workspace."""
    try:
        service = get_file_system_service()
        files = service.list_files(agent_id, directory_path)
        if not files:
            return f"Directory '{directory_path}' in agent '{agent_id}' workspace is empty or does not exist."
        return f"Contents of '{directory_path}' in agent '{agent_id}' workspace:\n" + "\n".join(files)
    except HTTPException as e:
        logger.error(f"Agent {agent_id} - Service error listing directory '{directory_path}': {e.detail}")
        return f"Error listing directory '{directory_path}': {e.detail}"
    except Exception as e:
        logger.error(f"Unexpected error in list_files_wrapper for agent {agent_id}, path '{directory_path}': {e}", exc_info=True)
        return f"Unexpected error listing directory '{directory_path}': {str(e)}"

async def delete_file_wrapper(agent_id: str, file_path: str) -> str:
    """Deletes a specified file or empty directory within the given agent's workspace."""
    try:
        service = get_file_system_service()
        service.delete_file(agent_id, file_path)
        return f"Successfully deleted '{file_path}' from agent '{agent_id}' workspace."
    except HTTPException as e:
        logger.error(f"Agent {agent_id} - Service error deleting '{file_path}': {e.detail}")
        return f"Error deleting '{file_path}': {e.detail}"
    except Exception as e:
        logger.error(f"Unexpected error in delete_file_wrapper for agent {agent_id}, path '{file_path}': {e}", exc_info=True)
        return f"Unexpected error deleting '{file_path}': {str(e)}"

async def create_directory_wrapper(agent_id: str, directory_path: str) -> str:
    """Creates a new directory in the given agent's workspace, including parent directories if needed."""
    try:
        service = get_file_system_service()
        service.create_directory(agent_id, directory_path)
        return f"Successfully created directory (or it already existed): '{directory_path}' in agent '{agent_id}' workspace."
    except HTTPException as e:
        logger.error(f"Agent {agent_id} - Service error creating directory '{directory_path}': {e.detail}")
        return f"Error creating directory '{directory_path}': {e.detail}"
    except Exception as e:
        logger.error(f"Unexpected error in create_directory_wrapper for agent {agent_id}, path '{directory_path}': {e}", exc_info=True)
        return f"Unexpected error creating directory '{directory_path}': {str(e)}"

async def move_file_wrapper(agent_id: str, old_path: str, new_path: str) -> str:
    """Moves or renames a file or directory within the given agent's workspace."""
    try:
        service = get_file_system_service()
        service.move_file(agent_id, old_path, new_path)
        return f"Successfully moved '{old_path}' to '{new_path}' in agent '{agent_id}' workspace."
    except HTTPException as e:
        logger.error(f"Agent {agent_id} - Service error moving '{old_path}' to '{new_path}': {e.detail}")
        return f"Error moving '{old_path}' to '{new_path}': {e.detail}"
    except Exception as e:
        logger.error(f"Unexpected error in move_file_wrapper for agent {agent_id}, old '{old_path}', new '{new_path}': {e}", exc_info=True)
        return f"Unexpected error moving '{old_path}' to '{new_path}': {str(e)}"

async def copy_file_wrapper(agent_id: str, source_path: str, destination_path: str) -> str:
    """Copies a file to a new location within the given agent's workspace."""
    try:
        service = get_file_system_service()
        service.copy_file(agent_id, source_path, destination_path)
        return f"Successfully copied '{source_path}' to '{destination_path}' in agent '{agent_id}' workspace."
    except HTTPException as e:
        logger.error(f"Agent {agent_id} - Service error copying '{source_path}' to '{destination_path}': {e.detail}")
        return f"Error copying '{source_path}' to '{destination_path}': {e.detail}"
    except Exception as e:
        logger.error(f"Unexpected error in copy_file_wrapper for agent {agent_id}, source '{source_path}', dest '{destination_path}': {e}", exc_info=True)
        return f"Unexpected error copying '{source_path}' to '{destination_path}': {str(e)}"

async def get_metadata_wrapper(agent_id: str, path: str) -> str:
    """Gets metadata (size, modification time, type) for a file or directory within the given agent's workspace."""
    try:
        service = get_file_system_service()
        metadata = service.get_file_metadata(agent_id, path)
        import json # Keep json import local to where it's used or move to top if used more widely
        # Ensure metadata is a serializable dict before trying to dump it
        if not isinstance(metadata, dict):
            logger.error(f"Metadata for agent {agent_id}, path '{path}' is not a dict: {type(metadata)}")
            return "Error: Received invalid metadata format from service."
        return f"Metadata for '{path}' in agent '{agent_id}' workspace:\n{json.dumps(metadata, indent=2)}"
    except HTTPException as e:
        logger.error(f"Agent {agent_id} - Service error getting metadata for '{path}': {e.detail}")
        return f"Error getting metadata for '{path}': {e.detail}"
    except Exception as e:
        logger.error(f"Unexpected error in get_metadata_wrapper for agent {agent_id}, path '{path}': {e}", exc_info=True)
        return f"Unexpected error getting metadata for '{path}': {str(e)}"

# --- Tool Definitions (Remain Unchanged in Structure) --- 
# The .function attribute now points to the refactored wrappers.

fs_read_tool = ToolDefinition(
    name="file_system_read",
    description="Reads the content of a specified file within the agent workspace.",
    parameters=ReadFileParams.model_json_schema(),
    function=read_file_wrapper
)

fs_write_tool = ToolDefinition(
    name="file_system_write",
    description="Writes content to a specified file within the agent workspace. Creates directories if needed. Overwrites existing files.",
    parameters=WriteFileParams.model_json_schema(),
    function=write_file_wrapper
)

fs_list_tool = ToolDefinition(
    name="file_system_list",
    description="Lists the files and directories within a specified directory in the agent workspace. Defaults to the workspace root ('.').",
    parameters=ListFilesParams.model_json_schema(),
    function=list_files_wrapper
)

fs_delete_tool = ToolDefinition(
    name="file_system_delete",
    description="Deletes a specified file or empty directory within the agent workspace.",
    parameters=DeleteFileParams.model_json_schema(),
    function=delete_file_wrapper
)

fs_create_dir_tool = ToolDefinition(
    name="file_system_create_directory",
    description="Creates a new directory within the agent workspace.",
    parameters=CreateDirectoryParams.model_json_schema(),
    function=create_directory_wrapper
)

fs_move_tool = ToolDefinition(
    name="file_system_move",
    description="Moves or renames a file or directory within the agent workspace.",
    parameters=MoveFileParams.model_json_schema(),
    function=move_file_wrapper
)

fs_copy_tool = ToolDefinition(
    name="file_system_copy",
    description="Copies a file to a new location within the agent workspace.",
    parameters=CopyFileParams.model_json_schema(),
    function=copy_file_wrapper
)

fs_metadata_tool = ToolDefinition(
    name="file_system_metadata",
    description="Gets metadata (size, modification time, type) for a file or directory within the agent workspace.",
    parameters=GetMetadataParams.model_json_schema(),
    function=get_metadata_wrapper
)

# List of all file system tools
file_system_tools = [
    fs_read_tool,
    fs_write_tool,
    fs_list_tool,
    fs_delete_tool,
    fs_create_dir_tool,
    fs_move_tool,
    fs_copy_tool,
    fs_metadata_tool,
] 