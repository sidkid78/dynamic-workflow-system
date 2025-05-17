"""
Tools for searching files and content within an agent's workspace.

This module provides tools for searching files and their contents within an agent's workspace.
It includes functionality for glob pattern matching and grep-style content searching, with
proper workspace isolation and security checks.

Classes:
    GlobSearchParams: Pydantic model for glob search parameters
    GrepFilesParams: Pydantic model for grep search parameters

Functions:
    glob_search_wrapper: Searches for files matching glob patterns
    grep_files_wrapper: Searches file contents using regex patterns

Tool Definitions:
    glob_search_tool: Tool definition for glob pattern file search
    grep_files_tool: Tool definition for content searching with grep

Constants:
    DEFAULT_AGENT_ID: Default agent ID used when none is provided
    search_tools: List of tools defined in this module for registration
"""

import os
import glob
import subprocess
from pydantic import BaseModel, Field
from app.models.schemas import ToolDefinition # Your existing ToolDefinition
from app.dependencies import get_file_system_service # To get agent workspace
import logging
from fastapi import HTTPException # For catching errors from the service

logger = logging.getLogger(__name__)
# DEFAULT_AGENT_ID = "default_agent" # No longer used by these wrappers

# --- Pydantic Schemas for Parameters ---
class GlobSearchParams(BaseModel):
    pattern: str = Field(..., description="The glob pattern to search for (e.g., '*.txt', 'data/**/*.json'). Should be relative to the agent's workspace.")
    recursive: bool = Field(True, description="Whether to search recursively (glob's '**' behavior). Default is True.")

class GrepFilesParams(BaseModel):
    pattern: str = Field(..., description="The regex pattern to search for in files.")
    path: str = Field(".", description="The relative directory or file path within the agent workspace to search. Defaults to workspace root ('.').")
    recursive: bool = Field(True, description="Whether to search recursively (grep -r). Default is True.")
    # Add other useful grep options as boolean flags if needed, e.g., ignore_case: bool

# --- Tool Wrapper Functions (Refactored for agent_id) ---
async def glob_search_wrapper(agent_id: str, pattern: str, recursive: bool = True) -> str:
    """
    Performs a glob search within the specified agent's workspace.
    """
    service = get_file_system_service()
    try:
        agent_workspace_path = service.get_agent_workspace_path(agent_id)
    except HTTPException as e:
        logger.error(f"Agent {agent_id} - Service error getting workspace path for glob_search: {e.detail}")
    except Exception as e:
        logger.error(f"Unexpected error getting workspace for agent {agent_id} in glob_search_wrapper: {e}", exc_info=True)
        return f"Unexpected error setting up search: {str(e)}"

    try:
        # Ensure the pattern is resolved relative to the agent's workspace
        # os.path.join handles leading slashes in `pattern` correctly if it's meant to be absolute within workspace
        # However, glob patterns are typically relative. If pattern might be "data/*.txt"
        # and workspace is "/base/agent_X", we want to search in "/base/agent_X/data/*.txt"
        
        # If the pattern could be absolute, we'd need more sophisticated path joining.
        # Assuming pattern is always relative to the agent's workspace root for now.
        search_pattern_full = os.path.join(agent_workspace_path, pattern)

        logger.info(f"Agent {agent_id} - Executing glob search with pattern: {search_pattern_full}, recursive: {recursive}")
        
        # For recursive glob, if the pattern itself doesn't contain '**', we might need to adjust.
        # However, Python's glob.glob with recursive=True handles patterns like '*.txt' recursively from the starting dir.
        # If pattern is 'data/**/*.txt', recursive=True is natural.
        # If pattern is 'data/*.txt' and recursive=True, it means search 'data/*.txt' and also in subdirs of 'data'.
        # The `os.path.join(agent_workspace_path, pattern)` forms the base for glob.

        # Let's make sure the path for glob is agent_workspace_path if pattern is relative
        # and recursive means searching from that root.
        # If pattern itself is like 'subfolder/**/*.py', os.path.join correctly makes it agent_workspace_path/subfolder/**/*.py
        
        results = []
        # glob.glob expects the pattern to define the starting point and the match.
        # If pattern is "foo.txt", it searches in agent_workspace_path/foo.txt.
        # If pattern is "sub/*.txt", it searches in agent_workspace_path/sub/*.txt.
        
        # The `root_dir` argument in `glob.glob` (Python 3.10+) would be ideal here,
        # but for broader compatibility, we join the pattern with the workspace path.
        
        for match in glob.glob(search_pattern_full, recursive=recursive):
            # Make paths relative to the agent_workspace_path for the output
            relative_match = os.path.relpath(match, agent_workspace_path)
            results.append(relative_match)

        if not results:
            return f"Agent {agent_id} - No files found matching pattern '{pattern}' in workspace."
        return f"Agent {agent_id} - Files found matching '{pattern}':\n" + "\n".join(results)
    except Exception as e:
        logger.error(f"Agent {agent_id} - Error during glob_search with pattern '{pattern}': {e}", exc_info=True)
        return f"Agent {agent_id} - Error during search: {str(e)}"

async def grep_files_wrapper(agent_id: str, pattern: str, path: str = ".", recursive: bool = True) -> str:
    """
    Searches for a regex pattern in files within a specified path in the agent's workspace.
    The search path is relative to the agent's workspace root.
    """
    service = get_file_system_service()
    try:
        agent_workspace_path = service.get_agent_workspace_path(agent_id)
    except HTTPException as e:
        logger.error(f"Agent {agent_id} - Service error getting workspace path for grep_files: {e.detail}")
        return f"Error setting up search: {e.detail}"
    except Exception as e:
        logger.error(f"Unexpected error getting workspace for agent {agent_id} in grep_files_wrapper: {e}", exc_info=True)
        return f"Unexpected error setting up search: {str(e)}"

    # The `path` parameter is relative to the agent's workspace.
    # `subprocess.run` will use `cwd=agent_workspace_path`, so `path` will be interpreted correctly from there.
    
    cmd = ["grep"]
    if recursive:
        cmd.append("-r")
    # Potentially add other options like -i for ignore case if exposed
    # cmd.append("-n") # Add line numbers
    cmd.extend([pattern, path]) # Path is relative to cwd

    try:
        logger.info(f"Agent {agent_id} - Executing grep: {' '.join(cmd)} in workspace: {agent_workspace_path} (relative path for grep: '{path}')")
        # timeout can be added from params if needed
        process = subprocess.run(cmd, cwd=agent_workspace_path, capture_output=True, text=True, check=False, timeout=30)
        
        if process.returncode == 0:
            if not process.stdout.strip():
                return f"Agent {agent_id} - Pattern '{pattern}' found, but with no output lines (this can happen with certain grep options or empty matches)."
            return f"Agent {agent_id} - Grep results for '{pattern}' in path '{path}':\n{process.stdout.strip()}"
        elif process.returncode == 1: # Grep returns 1 if no lines were selected
            return f"Agent {agent_id} - No lines found matching pattern '{pattern}' in path '{path}'."
        else: # Other error codes
            error_message = process.stderr.strip()
            logger.error(f"Agent {agent_id} - Grep command failed with return code {process.returncode}. Path: '{path}', Pattern: '{pattern}'. Error: {error_message}")
            return f"Agent {agent_id} - Error during grep search (code: {process.returncode}): {error_message if error_message else 'No specific error message from grep.'}"

    except subprocess.TimeoutExpired:
        logger.warning(f"Agent {agent_id} - Grep command timed out for pattern '{pattern}' in path '{path}'.")
        return f"Agent {agent_id} - Grep search timed out for pattern '{pattern}' in '{path}'."
    except FileNotFoundError:
        logger.error(f"Agent {agent_id} - Grep command not found. Ensure 'grep' is installed and in PATH.")
        return "Error: Grep command not found on the system. Please ensure it is installed."
    except Exception as e:
        logger.error(f"Agent {agent_id} - Unexpected error during grep_files for pattern '{pattern}' in path '{path}': {e}", exc_info=True)
        return f"Agent {agent_id} - An unexpected error occurred during the search: {str(e)}"

# --- Tool Definitions (Remain Unchanged in Structure) ---
# The .function attribute now points to the refactored wrappers.

glob_search_tool = ToolDefinition(
    name="glob_search",
    description="Performs a glob search for files and directories within the agent's workspace. Use patterns like '*.txt' or 'data/**/*'. Results are relative to the workspace.",
    parameters=GlobSearchParams.model_json_schema(),
    function=glob_search_wrapper 
)

grep_files_tool = ToolDefinition(
    name="grep_files",
    description="Searches for a regex PATTERN in files within a given PATH (relative to agent workspace, defaults to workspace root '.'). Supports recursive search.",
    parameters=GrepFilesParams.model_json_schema(),
    function=grep_files_wrapper
)

# List of all search tools in this module
search_tools = [
    glob_search_tool,
    grep_files_tool,
] 