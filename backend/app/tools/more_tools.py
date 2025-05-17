# import os
# from typing import Dict, List, Any
# import subprocess
# from dataclasses import dataclass 
# import argparse 
# import asyncio 

# @dataclass
# class AgentContext:
#     working_directory: str

# async def edit_file(path: str, content: str) -> str:
#     """Edit or create a file with new content."""
#     try:
#         with open(os.path.join(path), 'w') as f:
#             f.write(content)
#         return f"Successfully edited/created {path}"
#     except Exception as e:
#         return f"Error editing file: {str(e)}"


# async def read_file(path: str) -> str:
#     """Read the contents of a file."""
#     try:
#         with open(os.path.join(path), 'r') as f:
#             content = f.read()
#         return content
#     except Exception as e:
#         return f"Error reading file: {str(e)}"

# async def run_bash(command: str) -> str:
#     """Execute a bash command."""
    
#     try:
#         result = subprocess.run(
#             command, 
#             shell=True, 
#             capture_output=True, 
#             text=True,
#             cwd=working_directory
#         )
#         return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
#     except Exception as e:
#         return f"Error running command: {str(e)}"

# async def list_files(pattern: str = "*") -> str:
#     """List files in the working directory."""
#     try:
#         import glob
#         files = glob.glob(
#             os.path.join(working_directory, pattern)
#         )
#         return "\n".join(files)
#     except Exception as e:
#         return f"Error listing files: {str(e)}"


# async def git_operations(operation: str, args: List[str]) -> str:
#     """Perform git operations."""
    
#     allowed_ops = ["checkout", "branch", "add", "commit", "status"]
#     if operation not in allowed_ops:
#         return f"Operation {operation} not allowed"
    
#     try:
#         cmd = ["git", operation] + args
#         result = subprocess.run(
#             cmd,
#             capture_output=True,
#             text=True,
#             cwd=working_directory
#         )
#         return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
#     except Exception as e:
#         return f"Error with git operation: {str(e)}"

# async def grep_files( 
#     pattern: str, 
#     path: str = ".", 
#     recursive: bool = True
# ) -> str:
#     """Search for a pattern in files using grep."""
#     try:
#         cmd = ["grep"]
#         if recursive:
#             cmd.append("-r")
#         cmd.extend([pattern, os.path.join(path)])
        
#         result = subprocess.run(
#             cmd,
#             capture_output=True,
#             text=True,
#             cwd=path
#         )
        
#         if result.returncode == 0:
#             return f"Found matches:\n{result.stdout}"
#         elif result.returncode == 1:
#             return "No matches found"
#         else:
#             return f"Error running grep: {result.stderr}"
#     except Exception as e:
#         return f"Error with grep: {str(e)}"


# async def batch_execute(
#     tasks: List[Dict[str, Any]]
# ) -> str:
#     """Execute multiple tasks in parallel.
    
#     Each task should be a dict with:
#     - tool: The tool name to use
#     - params: Parameters for the tool
#     """ 
#     results = []
    
#     async def execute_task(task):
#         tool_name = task.get("tool")
#         params = task.get("params", {})
        
#         # Find the tool function
#         tool_map = {
#             "edit": edit_file,
#             "read": read_file,
#             "bash": run_bash,
#             "ls": list_files,
#             "git": git_operations,
#             "grep": grep_files
#         }
        
#         tool_func = tool_map.get(tool_name)
#         if not tool_func:
#             return f"Tool {tool_name} not found"
        
#         # Execute the tool
#         try:
#             return await tool_func(**params)
#         except Exception as e:
#             return f"Error executing {tool_name}: {str(e)}"
    
#     # Execute all tasks in parallel
#     tasks_to_run = [execute_task(task) for task in tasks]
#     results = await asyncio.gather(*tasks_to_run)
    
#     # Format results
#     output = "Batch execution results:\n"
#     for i, (task, result) in enumerate(zip(tasks, results)):
#         output += f"\nTask {i+1} ({task.get('tool')}):\n{result}\n"
    
#     return output


# async def spawn_task(
#     task_name: str,
#     prompt: str,
#     allowed_tools: List[str] = None
# ) -> str:
#     """Spawn a sub-agent to handle a specific task."""
    
#     # Create a sub-agent with specific tools
#     if allowed_tools is None:
#         allowed_tools = ["edit", "read", "bash"]
    
#     # Check if we already have this sub-agent
#     if task_name not in sub_agents:
#         from core.workflows.autonomousAgent import _build_autonomous_agent
#         sub_agent = _build_autonomous_agent(allowed_tools=allowed_tools)
#         sub_agents[task_name] = sub_agent
#     else:
#         sub_agent = sub_agents[task_name]
    
#     # Execute the task with the sub-agent
#     try:
#         result = await sub_agent.execute(prompt)
#         return f"Task '{task_name}' completed:\n{result}"
#     except Exception as e:
#         return f"Error in task '{task_name}': {str(e)}"

# async def glob_search(
#     pattern: str,
#     recursive: bool = True
# ) -> str:
#     """Find files matching a glob pattern."""
#     try:
#         import glob
        
#         search_path = os.path.join(working_directory, pattern)
#         if recursive and "**" in pattern:
#             files = glob.glob(search_path, recursive=True)
#         else:
#             files = glob.glob(search_path)
        
#         if files:
#             return "Found files:\n" + "\n".join(files)
#         else:
#             return f"No files found matching pattern: {pattern}"
#     except Exception as e:
#         return f"Error with glob search: {str(e)}"

# # Advanced batch tool for more complex operations

# async def advanced_batch(
#     operations: List[Dict[str, Any]],
#     parallel: bool = True,
#     continue_on_error: bool = True
# ) -> str:
#     """Execute a batch of operations with advanced control.
    
#     Operations can include:
#     - Sequential or parallel execution
#     - Error handling
#     - Dependencies between tasks
#     """
#     results = []
#     errors = []
    
#     if parallel:
#         # Execute in parallel
#         futures = []
#         with executor as executor:
#             for i, op in enumerate(operations):
#                 future = executor.submit(execute_operation, op, i)
#                 futures.append(future)
            
#             for i, future in enumerate(futures):
#                 try:
#                     result = future.result()
#                     results.append((i, result))
#                 except Exception as e:
#                     error_msg = f"Operation {i} failed: {str(e)}"
#                     errors.append(error_msg)
#                     if not continue_on_error:
#                         break
#     else:
#         # Execute sequentially
#         for i, op in enumerate(operations):
#             try:
#                 result = await execute_operation(op, i)
#                 results.append((i, result))
#             except Exception as e:
#                 error_msg = f"Operation {i} failed: {str(e)}"
#                 errors.append(error_msg)
#                 if not continue_on_error:
#                     break
    
#     # Format output
#     output = "Batch execution completed:\n\n"
#     output += f"Successful operations: {len(results)}\n"
#     output += f"Failed operations: {len(errors)}\n\n"
    
#     if results:
#         output += "Results:\n"
#         for i, result in results:
#             output += f"Operation {i}: {result[:100]}...\n"
    
#     if errors:
#         output += "\nErrors:\n"
#         for error in errors:
#             output += f"{error}\n"
    
#     return output

# async def execute_operation(operation, index):
#     """Helper function to execute a single operation."""
#     op_type = operation.get("type")
    
#     if op_type == "tool":
#         tool_name = operation.get("tool")
#         params = operation.get("params", {})
        
#         # Get the tool function
#         tool_map = {
#             "edit": edit_file,
#             "read": read_file,
#             "bash": run_bash,
#             "ls": list_files,
#             "git": git_operations,
#             "grep": grep_files,
#             "glob": glob_search
#         }
        
#         tool_func = tool_map.get(tool_name)
#         if tool_func:
#             return await tool_func(**params)
#         else:
#             return f"Unknown tool: {tool_name}"
    
#     elif op_type == "task":
#         task_name = operation.get("name", f"task_{index}")
#         prompt = operation.get("prompt")
#         allowed_tools = operation.get("allowed_tools", ["edit", "read", "bash"])
        
#         return await spawn_task(task_name, prompt, allowed_tools)
    
#     else:
#         return f"Unknown operation type: {op_type}"