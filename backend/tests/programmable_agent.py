# middleware/agents/programmable_agent.py

import os
import asyncio
import argparse
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from agents import Agent, Runner, function_tool, RunContextWrapper
import subprocess
import re 
import concurrent.futures 
from concurrent.futures import ThreadPoolExecutor 
import json 


@dataclass
class AgentContext:
    working_directory: str
    allowed_tools: List[str]
    git_enabled: bool = True
    commit_enabled: bool = True
    executor: ThreadPoolExecutor = None
    sub_agents: Dict[str, 'ProgrammableAgent'] = None

    def __post_init__(self):
        if self.executor is None:
            self.executor = ThreadPoolExecutor(max_workers=4)
        if self.sub_agents is None:
            self.sub_agents = {}

# Define basic tools similar to Claude Code
@function_tool
async def edit_file(wrapper: RunContextWrapper[AgentContext], path: str, content: str) -> str:
    """Edit or create a file with new content."""
    try:
        with open(os.path.join(wrapper.context.working_directory, path), 'w') as f:
            f.write(content)
        return f"Successfully edited/created {path}"
    except Exception as e:
        return f"Error editing file: {str(e)}"

@function_tool
async def read_file(wrapper: RunContextWrapper[AgentContext], path: str) -> str:
    """Read the contents of a file."""
    try:
        with open(os.path.join(wrapper.context.working_directory, path), 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

@function_tool
async def run_bash(wrapper: RunContextWrapper[AgentContext], command: str) -> str:
    """Execute a bash command."""
    if "bash" not in wrapper.context.allowed_tools:
        return "Bash tool not allowed in this context"
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=wrapper.context.working_directory
        )
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except Exception as e:
        return f"Error running command: {str(e)}"

@function_tool
async def list_files(wrapper: RunContextWrapper[AgentContext], pattern: str = "*") -> str:
    """List files in the working directory."""
    try:
        import glob
        files = glob.glob(
            os.path.join(wrapper.context.working_directory, pattern)
        )
        return "\n".join(files)
    except Exception as e:
        return f"Error listing files: {str(e)}"

@function_tool
async def git_operations(wrapper: RunContextWrapper[AgentContext], operation: str, args: List[str]) -> str:
    """Perform git operations."""
    if not wrapper.context.git_enabled:
        return "Git operations not enabled"
    
    allowed_ops = ["checkout", "branch", "add", "commit", "status"]
    if operation not in allowed_ops:
        return f"Operation {operation} not allowed"
    
    try:
        cmd = ["git", operation] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=wrapper.context.working_directory
        )
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except Exception as e:
        return f"Error with git operation: {str(e)}"
    
@function_tool
async def grep_files(
    wrapper: RunContextWrapper[AgentContext],
    pattern: str,
    path: str = ".",
    recursive: bool = True 
) -> str:
    """Search for a pattern in files using grep."""
    try:
        cmd = ["grep"]
        if recursive:
            cmd.append("-r")
        cmd.extend([pattern, os.path.join(wrapper.context.working_directory, path)])

        result = subprocess.run(
            cmd, 
            capture_output=True,
            text=True,
            cmd=wrapper.context.working_directory
        )

        if result.returncode == 0:
            return f"Found matches:\n{result.stdout}"
        elif result.returncode == 1:
            return "No matches found"
        else:
            return f"Error running grep: {result.stderr}"
    except Exception as e:
        return f"Error with grep: {str(e)}"
    
@function_tool 
async def batch_execute(
    wrapper: RunContextWrapper[AgentContext],
    tasks: List[Dict[str, Any]]
) -> str:
    """Execute multiple tasks in parallel.
    
    Each task should be a dict with:
    - tool: The tool name to use
    - params: Parameters for the tool
    """
    if "batch" not in wrapper.context.allowed_tools:
        return "Batch tool not allowed in this context"
    
    results = []

    async def execute_task(task):
        tool_name = task.get("tool")
        params = task.get("params", {})

        # Find the tool function
        tool_map = {
            "edit": edit_file,
            "read": read_file,
            "bash": run_bash,
            "ls": list_files,
            "git": git_operations,
            "grep": grep_files
        }

        tool_func = tool_map.get(tool_name)
        if not tool_func:
            return f"Tool {tool_name} not found"
        
        # Execute the tool
        try:
            return await tool_func(wrapper, **params)
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
        
    # Executre all tasks in parallel
    tasks_to_run = [execute_task(task) for task in tasks]
    results = await asyncio.gather(*tasks_to_run)

    # Format results 
    output = "Batch execution results:\n"
    for i, (task, result) in enumerate(zip(tasks, results)):
        output += f"\nTask {i+1} ({task.get('tool')}):\n{result}\n"

    return output

@function_tool
async def spawn_task(
    wrapper: RunContextWrapper[AgentContext],
    task_name: str,
    prompt: str,
    allowed_tools: List[str] = None
) -> str:
    """Spawn a sub-agent to handle a specific task."""
    if "task" not in wrapper.context.allowed_tools:
        return "Task spawning not allowed in this context"
    
    # Create a sub-agent with specific tools
    if allowed_tools is None:
        allowed_tools = ["edit", "read", "bash"]
    
    # Check if we already have this sub-agent
    if task_name not in wrapper.context.sub_agents:
        from .programmable_agent import ProgrammableAgent
        sub_agent = ProgrammableAgent(allowed_tools=allowed_tools)
        wrapper.context.sub_agents[task_name] = sub_agent
    else:
        sub_agent = wrapper.context.sub_agents[task_name]
    
    # Execute the task with the sub-agent
    try:
        result = await sub_agent.execute(prompt, wrapper.context.working_directory)
        return f"Task '{task_name}' completed:\n{result}"
    except Exception as e:
        return f"Error in task '{task_name}': {str(e)}"

@function_tool
async def glob_search(
    wrapper: RunContextWrapper[AgentContext],
    pattern: str,
    recursive: bool = True
) -> str:
    """Find files matching a glob pattern."""
    try:
        import glob
        
        search_path = os.path.join(wrapper.context.working_directory, pattern)
        if recursive and "**" in pattern:
            files = glob.glob(search_path, recursive=True)
        else:
            files = glob.glob(search_path)
        
        if files:
            return "Found files:\n" + "\n".join(files)
        else:
            return f"No files found matching pattern: {pattern}"
    except Exception as e:
        return f"Error with glob search: {str(e)}"

# Advanced batch tool for more complex operations
@function_tool
async def advanced_batch(
    wrapper: RunContextWrapper[AgentContext],
    operations: List[Dict[str, Any]],
    parallel: bool = True,
    continue_on_error: bool = True
) -> str:
    """Execute a batch of operations with advanced control.
    
    Operations can include:
    - Sequential or parallel execution
    - Error handling
    - Dependencies between tasks
    """
    if "batch" not in wrapper.context.allowed_tools:
        return "Batch tool not allowed in this context"
    
    results = []
    errors = []
    
    if parallel:
        # Execute in parallel
        futures = []
        with wrapper.context.executor as executor:
            for i, op in enumerate(operations):
                future = executor.submit(execute_operation, wrapper, op, i)
                futures.append(future)
            
            for i, future in enumerate(futures):
                try:
                    result = future.result()
                    results.append((i, result))
                except Exception as e:
                    error_msg = f"Operation {i} failed: {str(e)}"
                    errors.append(error_msg)
                    if not continue_on_error:
                        break
    else:
        # Execute sequentially
        for i, op in enumerate(operations):
            try:
                result = await execute_operation(wrapper, op, i)
                results.append((i, result))
            except Exception as e:
                error_msg = f"Operation {i} failed: {str(e)}"
                errors.append(error_msg)
                if not continue_on_error:
                    break
    
    # Format output
    output = "Batch execution completed:\n\n"
    output += f"Successful operations: {len(results)}\n"
    output += f"Failed operations: {len(errors)}\n\n"
    
    if results:
        output += "Results:\n"
        for i, result in results:
            output += f"Operation {i}: {result[:100]}...\n"
    
    if errors:
        output += "\nErrors:\n"
        for error in errors:
            output += f"{error}\n"
    
    return output

async def execute_operation(wrapper, operation, index):
    """Helper function to execute a single operation."""
    op_type = operation.get("type")
    
    if op_type == "tool":
        tool_name = operation.get("tool")
        params = operation.get("params", {})
        
        # Get the tool function
        tool_map = {
            "edit": edit_file,
            "read": read_file,
            "bash": run_bash,
            "ls": list_files,
            "git": git_operations,
            "grep": grep_files,
            "glob": glob_search
        }
        
        tool_func = tool_map.get(tool_name)
        if tool_func:
            return await tool_func(wrapper, **params)
        else:
            return f"Unknown tool: {tool_name}"
    
    elif op_type == "task":
        task_name = operation.get("name", f"task_{index}")
        prompt = operation.get("prompt")
        allowed_tools = operation.get("allowed_tools", ["edit", "read", "bash"])
        
        return await spawn_task(wrapper, task_name, prompt, allowed_tools)
    
    else:
        return f"Unknown operation type: {op_type}"



class ProgrammableAgent:
    def __init__(self, allowed_tools: List[str] = None):
        self.allowed_tools = allowed_tools or ["edit", "read", "bash", "ls", "git", "grep", "glob", "batch", "task"]
        
        # Map tool names to actual functions
        self.tool_map = {
            "edit": edit_file,
            "read": read_file,
            "bash": run_bash,
            "ls": list_files,
            "git": git_operations,
            "grep": grep_files,
            "glob": glob_search,
            "batch": batch_execute,
            "task": spawn_task,
            "advanced_batch": advanced_batch
        }
        
        # Create agent with selected tools
        selected_tools = [
            self.tool_map[tool] 
            for tool in self.allowed_tools 
            if tool in self.tool_map
        ]
        
        self.agent = Agent[AgentContext](
            name="Programmable Agent",
            instructions="""
            You are a programmable agent with advanced capabilities:
            
            1. File operations: edit, read, ls, glob
            2. Search operations: grep for text search, glob for file pattern matching
            3. Shell operations: bash for running commands
            4. Git operations: git for version control
            5. Parallel execution: batch for running multiple operations in parallel
            6. Task spawning: task for creating sub-agents to handle complex workflows
            
            When using batch operations, structure them as:
            - For simple parallel tasks: use batch with a list of tool calls
            - For complex workflows: use task to spawn specialized sub-agents
            
            Always explain what you're doing before executing commands.
            Use grep to search for patterns in files.
            Use glob to find files matching patterns.
            Use batch when you need to perform multiple operations efficiently.
            Use task to delegate complex sub-tasks to specialized agents.
            """,
            tools=selected_tools,
            model="gpt-4.1"
        )

    async def execute(self, prompt: str, working_directory: str) -> str:
        context = AgentContext(
            working_directory=working_directory,
            allowed_tools=self.allowed_tools
        )

        result = await self.agent.invoke(prompt, context)
        return result.output
    
    
