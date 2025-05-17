"""
Tools for executing code within an agent's workspace.

This module provides tools for executing Python scripts within an agent's workspace in a secure
and controlled manner. It includes functionality for running Python scripts with arguments,
timeouts, and proper workspace isolation.

Classes:
    RunPythonScriptParams: Pydantic model for Python script execution parameters

Functions:
    run_python_script_wrapper: Executes a Python script within an agent's workspace

Tool Definitions:
    run_python_script_tool: Tool definition for Python script execution

Constants:
    code_execution_tools: List of tools defined in this module for registration
"""

import os
import subprocess
import sys # To get the current python executable
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
from app.models.schemas import ToolDefinition
from app.dependencies import get_file_system_service
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)
# DEFAULT_AGENT_ID = "default_agent" # No longer used

# --- Pydantic Schemas for Parameters ---
class RunPythonScriptParams(BaseModel):
    script_path: str = Field(..., description="The relative path to the Python script within the agent's workspace (e.g., 'my_script.py', 'utils/helper.py').")
    script_args: Optional[List[str]] = Field(None, description="A list of arguments to pass to the Python script.")
    timeout_seconds: Optional[int] = Field(30, description="Maximum time in seconds to allow the script to run. Defaults to 30 seconds.")

# --- Tool Wrapper Function (Refactored for agent_id) ---
async def run_python_script_wrapper(agent_id: str, script_path: str, script_args: Optional[List[str]] = None, timeout_seconds: Optional[int] = 30) -> str:
    """
    Executes a Python script located within the agent's workspace.
    The script_path is relative to the agent's workspace root.
    """
    service = get_file_system_service()
    try:
        agent_workspace_path = service.get_agent_workspace_path(agent_id)
        logger.debug(f"Agent {agent_id} - Workspace path for python execution: {agent_workspace_path}")
    except HTTPException as e:
        logger.error(f"Agent {agent_id} - Service error getting workspace path for script execution: {e.detail}")
        return f"Error setting up script execution environment: {e.detail}"
    except Exception as e:
        logger.error(f"Unexpected error getting workspace for agent {agent_id} in run_python_script_wrapper: {e}", exc_info=True)
        return f"Unexpected error setting up script execution environment: {str(e)}"

    if ".." in script_path or script_path.startswith("/") or script_path.startswith("\\"):
        logger.warning(f"Agent {agent_id} - Attempt to execute script with invalid path: {script_path}")
        return "Error: script_path must be a relative path within the agent workspace and cannot contain '..'."

    # script_to_execute is the path on the server's filesystem
    script_to_execute_abs = os.path.normpath(os.path.join(agent_workspace_path, script_path))

    # Security check: Ensure the resolved script path is still within the agent's workspace
    # This is critical to prevent execution of arbitrary scripts outside the designated workspace.
    if not script_to_execute_abs.startswith(os.path.normpath(agent_workspace_path) + os.sep) and \
       script_to_execute_abs != os.path.normpath(agent_workspace_path):
        # This check is a bit redundant if _resolve_agent_path in FileSystemService already did its job when writing the file,
        # but good for defense in depth, especially if script could exist via other means.
        # However, script_path is relative, so os.path.join should keep it within if agent_workspace_path is correct.
        # The main concern here is a tricky script_path like "../../../../some_other_script.py"
        # `os.path.normpath` will resolve this. So the check `script_to_execute_abs.startswith(agent_workspace_path)` is vital.
        logger.error(f"Agent {agent_id} - Script path resolved outside agent workspace. Original: '{script_path}', Resolved: '{script_to_execute_abs}', Workspace: '{agent_workspace_path}'")
        return "Error: Script path resolved outside the agent's designated workspace. Execution denied."
    
    if not os.path.isfile(script_to_execute_abs):
        logger.warning(f"Agent {agent_id} - Python script not found at resolved path: {script_to_execute_abs} (original: '{script_path}')")
        return f"Error: Python script '{script_path}' not found in the agent workspace."

    command = [sys.executable, script_to_execute_abs] # Use the same Python interpreter that runs the FastAPI app
    if script_args:
        command.extend(script_args)

    try:
        logger.info(f"Agent {agent_id} - Executing Python script: {' '.join(command)} in CWD: {agent_workspace_path}")
        process = subprocess.run(
            command,
            cwd=agent_workspace_path,  # Execute with the script's directory as CWD
            capture_output=True,
            text=True,
            check=False, # We'll check returncode manually
            timeout=timeout_seconds
        )
        if process.returncode == 0:
            output = process.stdout.strip() if process.stdout.strip() else "Script executed successfully with no output."
            logger.info(f"Agent {agent_id} - Script '{script_path}' executed successfully.")
            # Consider logging output at DEBUG level if it can be verbose
            # logger.debug(f"Agent {agent_id} - Script '{script_path}' output:\n{output}")
            return output
        else:
            error_message = process.stderr.strip() if process.stderr.strip() else "No specific error message from script."
            logger.error(f"Agent {agent_id} - Script '{script_path}' failed with code {process.returncode}. Error: {error_message}")
            return f"Script '{script_path}' failed (code {process.returncode}): {error_message}"
    except subprocess.TimeoutExpired:
        logger.warning(f"Agent {agent_id} - Python script '{script_path}' timed out after {timeout_seconds} seconds.")
        return f"Error: Python script '{script_path}' timed out after {timeout_seconds} seconds."
    except FileNotFoundError: # Should ideally not happen if sys.executable is valid and script_to_execute_abs is checked
        logger.error(f"Agent {agent_id} - Python interpreter or script '{script_path}' not found during execution. This is unexpected.")
        return "Error: Python interpreter or script not found during execution. Please check system configuration."
    except Exception as e:
        logger.error(f"Agent {agent_id} - Unexpected error executing Python script '{script_path}': {e}", exc_info=True)
        return f"An unexpected error occurred while executing Python script '{script_path}': {str(e)}"

# --- Tool Definition (Structure unchanged, function refactored) ---
run_python_script_tool = ToolDefinition(
    name="run_python_script",
    description=(
        "Executes a Python script located within the agent's workspace. "
        "Provide the script_path (relative to the workspace root, e.g., 'my_code/script.py'), "
        "optional script_args (list of strings), and optional timeout_seconds. "
        "The script will run with the agent's workspace as its current working directory. "
        "Output (stdout) or errors (stderr) from the script will be returned."
    ),
    parameters=RunPythonScriptParams.model_json_schema(),
    function=run_python_script_wrapper
)

# List of all code execution tools in this module
code_execution_tools = [
    run_python_script_tool,
] 