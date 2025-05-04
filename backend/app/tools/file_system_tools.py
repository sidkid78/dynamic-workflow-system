# app/tools/file_system_tools.py
from app.models.schemas import ToolDefinition
from app.dependencies import get_file_system_service
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)
DEFAULT_AGENT_ID = "default_agent" # Match the ID in dependencies

# --- Pydantic Schemas for Parameters --- 

class ReadFileParams(BaseModel):
    file_path: str = Field(..., description="The relative path to the file within the agent workspace.")

class WriteFileParams(BaseModel):
    file_path: str = Field(..., description="The relative path where the file should be written within the agent workspace.")
    content: str = Field(..., description="The content to write into the file.")

class ListFilesParams(BaseModel):
    directory_path: str = Field(".", description="The relative path to the directory within the agent workspace. Defaults to the workspace root.")

class DeleteFileParams(BaseModel):
    file_path: str = Field(..., description="The relative path to the file to delete within the agent workspace.")

class CreateDirectoryParams(BaseModel):
    directory_path: str = Field(..., description="The relative path for the new directory within the agent workspace.")

class MoveFileParams(BaseModel):
    old_path: str = Field(..., description="The current relative path of the file/directory to move.")
    new_path: str = Field(..., description="The desired new relative path for the file/directory.")

class CopyFileParams(BaseModel):
    source_path: str = Field(..., description="The relative path of the source file to copy.")
    destination_path: str = Field(..., description="The relative path where the file should be copied to.")

class GetMetadataParams(BaseModel):
    path: str = Field(..., description="The relative path to the file or directory to get metadata for.")

# --- Tool Wrapper Functions --- 

async def read_file_wrapper(file_path: str) -> str:
    """Reads content from a specified file."""
    try:
        service = get_file_system_service()
        return service.read_file(DEFAULT_AGENT_ID, file_path)
    except Exception as e:
        logger.error(f"Error in read_file_wrapper for path '{file_path}': {e}", exc_info=True)
        return f"Error reading file: {e}"

async def write_file_wrapper(file_path: str, content: str) -> str:
    """Writes content to a specified file, creating directories if needed."""
    try:
        service = get_file_system_service()
        service.write_file(DEFAULT_AGENT_ID, file_path, content)
        return f"Successfully wrote content to {file_path}"
    except Exception as e:
        logger.error(f"Error in write_file_wrapper for path '{file_path}': {e}", exc_info=True)
        return f"Error writing file: {e}"

async def list_files_wrapper(directory_path: str = ".") -> str:
    """Lists files and directories within a specified directory."""
    try:
        service = get_file_system_service()
        files = service.list_files(DEFAULT_AGENT_ID, directory_path)
        if not files:
            return f"Directory '{directory_path}' is empty or does not exist."
        return f"Contents of '{directory_path}':\n" + "\n".join(files)
    except Exception as e:
        logger.error(f"Error in list_files_wrapper for path '{directory_path}': {e}", exc_info=True)
        return f"Error listing directory: {e}"

async def delete_file_wrapper(file_path: str) -> str:
    """Deletes a specified file."""
    try:
        service = get_file_system_service()
        service.delete_file(DEFAULT_AGENT_ID, file_path)
        return f"Successfully deleted file: {file_path}"
    except Exception as e:
        logger.error(f"Error in delete_file_wrapper for path '{file_path}': {e}", exc_info=True)
        return f"Error deleting file: {e}"

async def create_directory_wrapper(directory_path: str) -> str:
    """Creates a new directory, including parent directories if needed."""
    try:
        service = get_file_system_service()
        service.create_directory(DEFAULT_AGENT_ID, directory_path)
        return f"Successfully created directory (or it already existed): {directory_path}"
    except Exception as e:
        logger.error(f"Error in create_directory_wrapper for path '{directory_path}': {e}", exc_info=True)
        return f"Error creating directory: {e}"

async def move_file_wrapper(old_path: str, new_path: str) -> str:
    """Moves or renames a file or directory."""
    try:
        service = get_file_system_service()
        service.move_file(DEFAULT_AGENT_ID, old_path, new_path)
        return f"Successfully moved '{old_path}' to '{new_path}'"
    except Exception as e:
        logger.error(f"Error in move_file_wrapper for '{old_path}' -> '{new_path}': {e}", exc_info=True)
        return f"Error moving file/directory: {e}"

async def copy_file_wrapper(source_path: str, destination_path: str) -> str:
    """Copies a file to a new location."""
    try:
        service = get_file_system_service()
        service.copy_file(DEFAULT_AGENT_ID, source_path, destination_path)
        return f"Successfully copied '{source_path}' to '{destination_path}'"
    except Exception as e:
        logger.error(f"Error in copy_file_wrapper for '{source_path}' -> '{destination_path}': {e}", exc_info=True)
        return f"Error copying file: {e}"

async def get_metadata_wrapper(path: str) -> str:
    """Gets metadata (size, modification time, type) for a file or directory."""
    try:
        service = get_file_system_service()
        metadata = service.get_file_metadata(DEFAULT_AGENT_ID, path)
        import json
        return f"Metadata for '{path}':\n{json.dumps(metadata, indent=2)}"
    except Exception as e:
        logger.error(f"Error in get_metadata_wrapper for path '{path}': {e}", exc_info=True)
        return f"Error getting metadata: {e}"

# --- Tool Definitions --- 

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
    description="Lists the files and directories within a specified directory in the agent workspace. Defaults to the root.",
    parameters=ListFilesParams.model_json_schema(),
    function=list_files_wrapper
)

fs_delete_tool = ToolDefinition(
    name="file_system_delete",
    description="Deletes a specified file within the agent workspace.",
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