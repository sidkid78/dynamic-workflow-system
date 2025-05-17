"""
Batch execution tools for running sequences of tool commands.

This module provides tools for executing multiple tool commands in sequence.
It includes functionality to validate, execute, and log results for each command
in the sequence while maintaining proper agent context and error handling.

Classes:
    SubToolCall: Pydantic model for individual tool command specifications
    ExecuteSequentialCommandsParams: Pydantic model for batch execution parameters

Functions:
    execute_sequential_commands_wrapper: Main wrapper function that executes tool sequences

Tool Definitions:
    execute_sequential_commands_tool: Tool definition for sequential command execution

Constants:
    DEFAULT_AGENT_ID: Default agent ID used when none is provided
    batch_execution_tools: List of tools defined in this module for registration
"""

import asyncio
import json
from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Dict, Any, Optional, Tuple
from app.models.schemas import ToolDefinition
# REMOVE: from app.tools.registry import get_tool # To look up other tools
# from app.dependencies import get_file_system_service # Not directly used here, but sub-tools might need agent_id context
import logging
import inspect # To check if sub-tools are async

logger = logging.getLogger(__name__)
# DEFAULT_AGENT_ID = "default_agent" # This will be passed to the wrapper

# --- Pydantic Schemas for Parameters ---
class SubToolCall(BaseModel):
    tool_name: str = Field(..., description="The exact name of the tool to execute (e.g., 'file_system_write', 'glob_search').")
    tool_args: Dict[str, Any] = Field({}, description="A dictionary of arguments for the sub-tool, matching its Pydantic schema.")

    @validator('tool_name')
    def validate_tool_name_is_not_batch(cls, value):
        if value == "execute_sequential_commands": # Prevent recursive batch calls
            raise ValueError("Cannot execute 'execute_sequential_commands' as a sub-tool.")
        return value

class ExecuteSequentialCommandsParams(BaseModel):
    commands: List[SubToolCall] = Field(..., description="A list of tool calls to execute in sequence. Each item specifies the tool_name and its tool_args.")
    # We don't need agent_id here as a parameter; it will be passed to the main wrapper.

# --- Tool Wrapper Function (Refactored for agent_id) ---
async def execute_sequential_commands_wrapper(agent_id: str, commands: List[SubToolCall]) -> str:
    """
    Executes a sequence of specified tool calls for a given agent.
    Each sub-tool is executed with the provided agent_id context.
    """
    # Local import to break circular dependency
    from app.tools.registry import get_tool

    if not commands:
        return "No commands provided to execute."

    results = []
    overall_success = True

    logger.info(f"Agent {agent_id} - Starting batch execution of {len(commands)} commands.")

    for i, sub_command in enumerate(commands):
        tool_name = sub_command.tool_name
        tool_args = sub_command.tool_args
        
        log_prefix = f"Agent {agent_id} - Batch Command {i+1}/{len(commands)} ('{tool_name}')"

        try:
            tool_definition = get_tool(tool_name) # Assuming get_tool returns the ToolDefinition
            if not tool_definition:
                logger.warning(f"{log_prefix}: Tool not found.")
                results.append(f"Command {i+1} ('{tool_name}'): Error - Tool not found.")
                overall_success = False
                continue # Move to the next command in the batch

            tool_function = tool_definition.function
            
            logger.info(f"{log_prefix}: Executing with args: {tool_args}")
            
            if inspect.iscoroutinefunction(tool_function):
                sub_tool_result = await tool_function(agent_id, **tool_args)
            else:
                sub_tool_result = tool_function(agent_id, **tool_args)
            
            results.append(f"Command {i+1} ('{tool_name}'): Success - Output:\n{str(sub_tool_result)}")
            logger.info(f"{log_prefix}: Succeeded. Output: {str(sub_tool_result)[:200]}...")

        except Exception as e:
            logger.error(f"{log_prefix}: Failed. Error: {e}", exc_info=True)
            results.append(f"Command {i+1} ('{tool_name}'): Error - {type(e).__name__}: {str(e)}")
            overall_success = False

    final_status = "Batch execution completed. All commands succeeded." if overall_success else "Batch execution completed with one or more errors."
    logger.info(f"Agent {agent_id} - Batch execution finished. Overall success: {overall_success}")
    
    return f"{final_status}\n\nResults:\n" + "\n---\n".join(results)

# --- Tool Definition (Structure unchanged, function refactored) ---
execute_sequential_commands_tool = ToolDefinition(
    name="execute_sequential_commands",
    description=(
        "Executes a list of tool commands in sequence for the agent. "
        "Each command in the list must specify 'tool_name' and 'tool_args'. "
        "The agent_id context is automatically passed to each sub-tool. "
        "This tool cannot call itself recursively."
    ),
    parameters=ExecuteSequentialCommandsParams.model_json_schema(),
    function=execute_sequential_commands_wrapper
)

# List of all batch tools in this module (currently just one)
batch_tools = [
    execute_sequential_commands_tool,
] 