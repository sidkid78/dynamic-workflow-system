# file_system_service.py
import os
import shutil
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileSystemService:
    def __init__(self, base_path: str):
        """
        Initializes the FileSystemService.

        Args:
            base_path: The absolute base directory where all agent workspaces will be stored.
        """
        self.base_path = os.path.abspath(base_path)
        self.permissions: Dict[str, Dict[str, bool]] = {}
        
        # Create the base directory if it doesn't existethod that rigorously checks if the requested file path resolves to a location wi
        try:
            os.makedirs(self.base_path, exist_ok=True)
            logger.info(f"Initialized FileSystemService with base path: {self.base_path}")
        except Exception as e:
            logger.error(f"Failed to create base directory {self.base_path}: {e}", exc_info=True)
            # Depending on application lifecycle, you might want to raise this or handle it.
            # For now, we'll let it raise to prevent the service from starting in a bad state.
            raise
    
    def grant_permission(self, agent_id: str, permissions: Dict[str, bool]):
        """Grants specified permissions to an agent."""
        if not isinstance(permissions, dict):
            raise ValueError("Permissions must be a dictionary.")
        self.permissions[agent_id] = permissions
        logger.info(f"Granted permissions to agent {agent_id}: {permissions}")
    
    def _validate_path_and_permission(self, agent_id: str, operation: str, relative_path: str) -> str:
        """
        Validates the agent's permission and ensures the path is within the base directory.

        Args:
            agent_id: The ID of the agent performing the operation.
            operation: The operation being attempted (e.g., 'read', 'write', 'delete').
            relative_path: The file or directory path relative to the base path.

        Returns:
            The validated absolute path.

        Raises:
            HTTPException: If permission is denied or the path is invalid/outside the base directory.
        """
        agent_permissions = self.permissions.get(agent_id, {})
        if not agent_permissions.get(operation, False):
            logger.warning(f"Permission denied for agent {agent_id}, operation '{operation}', path '{relative_path}'")
            raise HTTPException(status_code=403, detail=f"Agent does not have '{operation}' permission.")

        # Prevent access to the base path itself if relative_path is empty or '.'
        if not relative_path or relative_path == '.':
             logger.warning(f"Attempt by agent {agent_id} to access base path directly for operation '{operation}'.")
             raise HTTPException(status_code=403, detail="Direct access to the base directory is not permitted.")

        absolute_path = os.path.abspath(os.path.join(self.base_path, relative_path))

        # Critical Path Traversal Check: Ensure the resolved path is truly within the base path
        if not absolute_path.startswith(self.base_path + os.sep) and absolute_path != self.base_path:
             logger.error(f"Path traversal attempt detected: Agent {agent_id}, operation '{operation}', requested path '{relative_path}', resolved to '{absolute_path}', outside base '{self.base_path}'")
             raise HTTPException(status_code=403, detail="Access denied: Path is outside the allowed base directory.")

        return absolute_path

    def get_agent_workspace_path(self, agent_id: str, ensure_exists: bool = True) -> str:
        """
        Constructs and returns the absolute path to an agent's dedicated workspace.
        This path is a subdirectory within self.base_path.

        Args:
            agent_id: The unique identifier for the agent.
            ensure_exists: If True, creates the directory if it doesn't exist.

        Returns:
            The absolute path to the agent's workspace.

        Raises:
            ValueError: If agent_id is empty or invalid, or leads to an invalid path.
            HTTPException: If there's an error creating the directory.
        """
        if not agent_id or not isinstance(agent_id, str) or not agent_id.strip():
            logger.error("Attempt to get workspace path with empty or invalid agent_id.")
            raise ValueError("Agent ID must be a non-empty string.")

        # Basic sanitization: remove potentially problematic characters for directory names.
        # This is a simple example; more robust sanitization might be needed if agent_id is user-influenced.
        safe_agent_dirname = "".join(c for c in agent_id if c.isalnum() or c in ('_', '-')).strip()
        if not safe_agent_dirname:
             logger.error(f"Sanitized agent_id '{agent_id}' became empty.")
             raise ValueError("Invalid agent_id resulting in empty directory name after sanitization.")
        
        agent_specific_workspace = os.path.abspath(os.path.join(self.base_path, safe_agent_dirname))

        # Security check: Ensure the agent's workspace is a direct subdirectory of base_path.
        # os.path.commonpath will return the longest common leading path.
        # If agent_specific_workspace is truly under base_path, commonpath will be base_path.
        if os.path.commonpath([self.base_path, agent_specific_workspace]) != self.base_path or \
           agent_specific_workspace == self.base_path: # Agent workspace cannot be the base_path itself
            logger.critical(f"Calculated agent workspace path '{agent_specific_workspace}' is not a valid subdirectory of base_path '{self.base_path}' for agent_id '{agent_id}'. This could be due to an invalid agent_id or a logic error.")
            raise ValueError("Agent workspace path is not a valid subdirectory of the service base path. Check agent_id.")

        if ensure_exists:
            try:
                os.makedirs(agent_specific_workspace, exist_ok=True)
                # logger.debug(f"Ensured agent workspace exists for agent {agent_id} at: {agent_specific_workspace}")
            except Exception as e:
                logger.error(f"Failed to create agent workspace directory {agent_specific_workspace} for agent {agent_id}: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=f"Error creating agent workspace for {agent_id}.")
        
        return agent_specific_workspace

    def _resolve_agent_path(self, agent_id: str, path_relative_to_agent_ws: str) -> str:
        """
        Resolves a path relative to an agent's workspace and validates it for security.

        Args:
            agent_id: The ID of the agent.
            path_relative_to_agent_ws: The path, as understood by the agent (relative to its own workspace root).

        Returns:
            The validated absolute path on the file system.

        Raises:
            HTTPException: If the path is invalid or attempts to traverse outside the agent's workspace.
            ValueError: If agent_id is invalid.
        """
        # Get the agent's root workspace. ensure_exists=False because this is a validation step;
        # the actual operation (e.g., read) will fail if the file doesn't exist later.
        # However, for operations like write or create_directory, the target might not exist yet,
        # but its parent structure up to the agent_workspace_root should be sound.
        agent_workspace_root = self.get_agent_workspace_path(agent_id, ensure_exists=True)


        # Normalize the relative path: remove leading slashes, handle "."
        normalized_relative_path = path_relative_to_agent_ws.lstrip('/' + os.sep)
        if normalized_relative_path == '' or normalized_relative_path == '.':
            # An operation on "." refers to the agent's workspace root itself.
            return agent_workspace_root 
            
        absolute_path = os.path.abspath(os.path.join(agent_workspace_root, normalized_relative_path))

        # Critical Path Traversal Check:
        # Ensure the resolved absolute_path starts with agent_workspace_root.
        # And if it's not identical to agent_workspace_root, it must start with agent_workspace_root + separator.
        if not (absolute_path == agent_workspace_root or \
                absolute_path.startswith(os.path.normpath(agent_workspace_root + os.sep))):
             logger.warning(f"Path traversal attempt or invalid path for agent '{agent_id}': Relative path '{path_relative_to_agent_ws}' resolved to '{absolute_path}', which is outside its workspace '{agent_workspace_root}'.")
             raise HTTPException(status_code=403, detail=f"Access denied: Path '{path_relative_to_agent_ws}' is outside the agent's allowed workspace.")
        
        return absolute_path

    def read_file(self, agent_id: str, file_path: str) -> str:
        """Reads the content of a file within the agent's workspace.
        Args: file_path: Path relative to the agent's workspace root."""
        absolute_path = self._resolve_agent_path(agent_id, file_path)
        if not os.path.isfile(absolute_path):
            logger.warning(f"Read file failed for agent {agent_id}: File '{file_path}' not found at '{absolute_path}'.")
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        try:
            with open(absolute_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Agent {agent_id} read file: {file_path}")
            return content
        except Exception as e:
            logger.error(f"Error reading file '{absolute_path}' for agent {agent_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Could not read file: {file_path}")

    def write_file(self, agent_id: str, file_path: str, content: str):
        """Writes content to a file in the agent's workspace.
        Args: file_path: Path relative to the agent's workspace root."""
        absolute_path = self._resolve_agent_path(agent_id, file_path)
        parent_dir = os.path.dirname(absolute_path)
        try:
            # Ensure parent directory exists within the workspace.
            # os.makedirs is safe here because absolute_path (and thus parent_dir) is confirmed to be within the agent's workspace.
            os.makedirs(parent_dir, exist_ok=True)
            with open(absolute_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Agent {agent_id} wrote file: {file_path}")
        except Exception as e:
            logger.error(f"Error writing file '{absolute_path}' for agent {agent_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Could not write file: {file_path}")

    def list_files(self, agent_id: str, directory_path: str) -> List[str]:
        """Lists files/dirs within a directory in the agent's workspace.
        Args: directory_path: Path relative to agent's ws root (e.g., '.' for root itself)."""
        absolute_path = self._resolve_agent_path(agent_id, directory_path)
        if not os.path.isdir(absolute_path):
            logger.warning(f"List files failed for agent {agent_id}: Directory '{directory_path}' not found at '{absolute_path}'.")
            raise HTTPException(status_code=404, detail=f"Directory not found: {directory_path}")
        try:
            entries = os.listdir(absolute_path)
            logger.info(f"Agent {agent_id} listed directory: {directory_path}")
            return entries
        except Exception as e:
            logger.error(f"Error listing directory '{absolute_path}' for agent {agent_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Could not list directory: {directory_path}")

    def delete_file(self, agent_id: str, file_path: str):
        """Deletes a file or an empty directory within the agent's workspace.
        Args: file_path: Path relative to the agent's workspace root."""
        absolute_path = self._resolve_agent_path(agent_id, file_path)
        if not os.path.exists(absolute_path): # Check if it exists at all
            logger.warning(f"Delete failed for agent {agent_id}: Path '{file_path}' not found at '{absolute_path}'.")
            raise HTTPException(status_code=404, detail=f"File or directory not found: {file_path}")
        try:
            if os.path.isfile(absolute_path):
                os.remove(absolute_path)
                logger.info(f"Agent {agent_id} deleted file: {file_path}")
            elif os.path.isdir(absolute_path):
                if not os.listdir(absolute_path): # Only delete empty directories for safety via this method
                    os.rmdir(absolute_path)
                    logger.info(f"Agent {agent_id} deleted empty directory: {file_path}")
                else:
                    logger.warning(f"Agent {agent_id} attempted to delete non-empty directory '{file_path}' via delete_file. Use a dedicated recursive delete if intended.")
                    raise HTTPException(status_code=400, detail=f"Directory '{file_path}' is not empty. Cannot delete via this method.")
            else: # Should not happen if os.path.exists is true
                logger.error(f"Delete failed for agent {agent_id}: Path '{file_path}' at '{absolute_path}' is neither a file nor a directory.")
                raise HTTPException(status_code=500, detail=f"Path is not a file or directory: {file_path}")
        except Exception as e:
            logger.error(f"Error deleting '{absolute_path}' for agent {agent_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Could not delete: {file_path}")

    def create_directory(self, agent_id: str, directory_path: str):
        """Creates a directory within the agent's workspace.
        Args: directory_path: Path relative to the agent's workspace root."""
        absolute_path = self._resolve_agent_path(agent_id, directory_path)
        try:
            os.makedirs(absolute_path, exist_ok=True)
            logger.info(f"Agent {agent_id} created directory (or it already existed): {directory_path}")
        except Exception as e:
            logger.error(f"Error creating directory '{absolute_path}' for agent {agent_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Could not create directory: {directory_path}")

    def move_file(self, agent_id: str, old_path: str, new_path: str):
        """Moves/renames a file/directory within the agent's workspace.
        Args: old_path, new_path: Paths relative to the agent's workspace root."""
        abs_old_path = self._resolve_agent_path(agent_id, old_path)
        abs_new_path = self._resolve_agent_path(agent_id, new_path)

        if not os.path.exists(abs_old_path):
            logger.warning(f"Move failed for agent {agent_id}: Source '{old_path}' not found at '{abs_old_path}'.")
            raise HTTPException(status_code=404, detail=f"Source path not found: {old_path}")
        
        # Ensure parent of new path exists, os.renames (used by shutil.move sometimes) might need it
        abs_new_parent_dir = os.path.dirname(abs_new_path)
        if not os.path.isdir(abs_new_parent_dir):
             os.makedirs(abs_new_parent_dir, exist_ok=True) # Safe due to _resolve_agent_path on new_path

        try:
            shutil.move(abs_old_path, abs_new_path)
            logger.info(f"Agent {agent_id} moved '{old_path}' to '{new_path}'.")
        except Exception as e:
            logger.error(f"Error moving '{abs_old_path}' to '{abs_new_path}' for agent {agent_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Could not move '{old_path}' to '{new_path}'.")

    def copy_file(self, agent_id: str, source_path: str, destination_path: str):
        """Copies a file within the agent's workspace.
        Args: source_path, destination_path: Paths relative to the agent's workspace root."""
        abs_source_path = self._resolve_agent_path(agent_id, source_path)
        abs_destination_path = self._resolve_agent_path(agent_id, destination_path)

        if not os.path.isfile(abs_source_path):
            logger.warning(f"Copy file failed for agent {agent_id}: Source '{source_path}' not found or not a file at '{abs_source_path}'.")
            raise HTTPException(status_code=404, detail=f"Source file not found: {source_path}")

        abs_dest_parent_dir = os.path.dirname(abs_destination_path)
        if not os.path.isdir(abs_dest_parent_dir):
             os.makedirs(abs_dest_parent_dir, exist_ok=True) # Safe due to _resolve_agent_path

        try:
            shutil.copy2(abs_source_path, abs_destination_path) # copy2 preserves metadata
            logger.info(f"Agent {agent_id} copied '{source_path}' to '{destination_path}'.")
        except Exception as e:
            logger.error(f"Error copying '{abs_source_path}' to '{abs_destination_path}' for agent {agent_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Could not copy file '{source_path}'.")

    def get_file_metadata(self, agent_id: str, path: str) -> Dict[str, Any]:
        """Gets metadata for a file/directory within the agent's workspace.
        Args: path: Path relative to the agent's workspace root."""
        absolute_path = self._resolve_agent_path(agent_id, path)
        if not os.path.exists(absolute_path):
            logger.warning(f"Get metadata failed for agent {agent_id}: Path '{path}' not found at '{absolute_path}'.")
            raise HTTPException(status_code=404, detail=f"File or directory not found: {path}")
        try:
            stats = os.stat(absolute_path)
            is_dir = os.path.isdir(absolute_path)
            metadata = {
                'path': path, # Return relative path for consistency
                'size_bytes': stats.st_size,
                'modified_timestamp': stats.st_mtime,
                'created_timestamp': stats.st_ctime,
                'is_directory': is_dir,
                'is_file': not is_dir,
            }
            logger.info(f"Agent {agent_id} retrieved metadata for: {path}")
            return metadata
        except Exception as e:
            logger.error(f"Error getting metadata for '{absolute_path}' for agent {agent_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Could not get metadata for: {path}")