# gemini_tools.py
"""
Gemini API Tool Declarations for FileSystemTools

This module bridges the FileSystemTools with Google's Gemini API,
providing properly formatted function declarations for tool calling.

Usage:
    >>> from agentic_layer.gemini_tools import GeminiToolsAdapter
    >>> adapter = GeminiToolsAdapter(workspace_root="./workspace")
    >>> tools = adapter.get_tool_declarations()
    >>> result = adapter.execute_tool("create_file", {"path": "test.py", "content": "print('hi')"})
"""

from typing import Any, Callable, Dict, List, Optional
from google.genai import types
from datetime import datetime

from app.services.file_system_tools import FileSystemTools


# Type aliases for Gemini SDK
Schema = types.Schema
Type = types.Type


class GeminiToolsAdapter:
    """
    Adapts FileSystemTools for use with the Gemini API.
    
    Provides:
    - Tool declarations in Gemini format
    - Tool execution with logging
    - Optional Google Search grounding
    
    Example:
        >>> adapter = GeminiToolsAdapter("./my_workspace")
        >>> 
        >>> # Get tools for Gemini API
        >>> tools = adapter.get_tool_declarations()
        >>> 
        >>> # Use with generate_content
        >>> response = client.models.generate_content(
        ...     model='gemini-2.5-flash',
        ...     contents='Create a Python file that prints hello',
        ...     config=types.GenerateContentConfig(tools=tools)
        ... )
        >>> 
        >>> # Execute any function calls
        >>> for fc in response.function_calls:
        ...     result = adapter.execute_tool(fc.name, dict(fc.args))
    """
    
    def __init__(self, workspace_root: str = "./agent_workspace"):
        """
        Initialize the Gemini tools adapter.
        
        Args:
            workspace_root: Root directory for file operations
        """
        self.fs_tools = FileSystemTools(workspace_root)
        self.execution_log: List[Dict] = []
        
    def get_tool_declarations(
        self,
        include_search: bool = False,
        tool_subset: Optional[List[str]] = None
    ) -> List[types.Tool]:
        """
        Get tool declarations for the Gemini API.
        
        Args:
            include_search: If True, includes Google Search grounding tool.
                Note: Some models don't support mixing function calling with search.
            tool_subset: Optional list of tool names to include (None = all)
        
        Returns:
            List of Tool objects for Gemini API
        """
        
        all_declarations = self._build_function_declarations()
        
        # Filter if subset specified
        if tool_subset:
            all_declarations = [
                fd for fd in all_declarations 
                if fd.name in tool_subset
            ]
        
        tools: List[types.Tool] = [
            types.Tool(function_declarations=all_declarations)
        ]
        
        if include_search:
            tools.append(types.Tool(google_search={}))
        
        return tools
    
    def get_python_functions(
        self,
        tool_subset: Optional[List[str]] = None
    ) -> List[Callable]:
        """
        Get Python functions for automatic function calling.
        
        These can be passed directly to Gemini and it will
        automatically call them and return results.
        
        Args:
            tool_subset: Optional list of tool names to include
        
        Returns:
            List of callable Python functions
        """
        tool_map = self._get_tool_map()
        
        if tool_subset:
            return [tool_map[name] for name in tool_subset if name in tool_map]
        
        return list(tool_map.values())
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict:
        """
        Execute a tool with given arguments.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool
        
        Returns:
            Result dictionary from the tool
        """
        tool_map = self._get_tool_map()
        
        if tool_name not in tool_map:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
        
        try:
            start_time = datetime.now()
            result = tool_map[tool_name](**arguments)
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            self.execution_log.append({
                "tool": tool_name,
                "arguments": arguments,
                "result": result,
                "execution_time_ms": execution_time,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            error_result = {"success": False, "error": f"Tool execution failed: {str(e)}"}
            self.execution_log.append({
                "tool": tool_name,
                "arguments": arguments,
                "result": error_result,
                "timestamp": datetime.now().isoformat()
            })
            return error_result
    
    def process_function_calls(
        self,
        response: Any,
        auto_execute: bool = True
    ) -> List[Dict]:
        """
        Process function calls from a Gemini response.
        
        Args:
            response: Gemini API response object
            auto_execute: If True, automatically execute the functions
        
        Returns:
            List of results from executed functions
        """
        results = []
        
        if not hasattr(response, 'function_calls') or not response.function_calls:
            return results
        
        for function_call in response.function_calls:
            fc_info = {
                "name": function_call.name,
                "args": dict(function_call.args) if function_call.args else {}
            }
            
            if auto_execute:
                result = self.execute_tool(fc_info["name"], fc_info["args"])
                fc_info["result"] = result
            
            results.append(fc_info)
        
        return results
    
    def _get_tool_map(self) -> Dict[str, Callable]:
        """Map tool names to their implementation methods."""
        return {
            "create_file": self.fs_tools.create_file,
            "read_file": self.fs_tools.read_file,
            "update_file": self.fs_tools.update_file,
            "delete_file": self.fs_tools.delete_file,
            "create_directory": self.fs_tools.create_directory,
            "list_directory": self.fs_tools.list_directory,
            "create_project_structure": self.fs_tools.create_project_structure,
            "get_project_tree": self.fs_tools.get_project_tree,
            "get_file_info": self.fs_tools.get_file_info,
            "bash": self.fs_tools.bash,
            "git_operations": self.fs_tools.git_operations,
            "grep_files": self.fs_tools.grep_files,
            "glob_search": self.fs_tools.glob_search,
            "execute_batch": self.fs_tools.execute_batch
        }
    
    def _build_function_declarations(self) -> List[types.FunctionDeclaration]:
        """Build all function declarations for Gemini API."""
        return [
            # =========================================================
            # File Operations
            # =========================================================
            types.FunctionDeclaration(
                name="create_file",
                description="Create a new file with content. Use for code files, configs, docs, etc.",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "path": Schema(
                            type=Type.STRING,
                            description="File path relative to workspace (e.g., 'src/main.py')"
                        ),
                        "content": Schema(
                            type=Type.STRING,
                            description="Complete file content to write"
                        ),
                        "overwrite": Schema(
                            type=Type.BOOLEAN,
                            description="Whether to overwrite if file exists (default: false)"
                        )
                    },
                    required=["path", "content"]
                )
            ),
            
            types.FunctionDeclaration(
                name="read_file",
                description="Read the contents of an existing file",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "path": Schema(
                            type=Type.STRING,
                            description="File path relative to workspace"
                        )
                    },
                    required=["path"]
                )
            ),
            
            types.FunctionDeclaration(
                name="update_file",
                description="Update an existing file (replace, append, or prepend content)",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "path": Schema(
                            type=Type.STRING,
                            description="File path relative to workspace"
                        ),
                        "content": Schema(
                            type=Type.STRING,
                            description="Content to add/replace"
                        ),
                        "mode": Schema(
                            type=Type.STRING,
                            enum=["replace", "append", "prepend"],
                            description="How to update: replace (default), append, or prepend"
                        )
                    },
                    required=["path", "content"]
                )
            ),
            
            types.FunctionDeclaration(
                name="delete_file",
                description="Delete a file",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "path": Schema(
                            type=Type.STRING,
                            description="File path relative to workspace"
                        )
                    },
                    required=["path"]
                )
            ),
            
            # =========================================================
            # Directory Operations
            # =========================================================
            types.FunctionDeclaration(
                name="create_directory",
                description="Create a new directory",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "path": Schema(
                            type=Type.STRING,
                            description="Directory path relative to workspace"
                        ),
                        "parents": Schema(
                            type=Type.BOOLEAN,
                            description="Create parent directories if needed (default: true)"
                        )
                    },
                    required=["path"]
                )
            ),
            
            types.FunctionDeclaration(
                name="list_directory",
                description="List contents of a directory",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "path": Schema(
                            type=Type.STRING,
                            description="Directory path (default: workspace root)"
                        ),
                        "recursive": Schema(
                            type=Type.BOOLEAN,
                            description="List recursively"
                        ),
                        "include_hidden": Schema(
                            type=Type.BOOLEAN,
                            description="Include hidden files"
                        )
                    }
                )
            ),
            
            # =========================================================
            # Project Structure
            # =========================================================
            types.FunctionDeclaration(
                name="create_project_structure",
                description="Create a complete project with directories and files at once",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "project_name": Schema(
                            type=Type.STRING,
                            description="Name of the project"
                        ),
                        "structure": Schema(
                            type=Type.OBJECT,
                            description="Project structure with 'directories' (list) and 'files' (dict of path:content)"
                        )
                    },
                    required=["project_name", "structure"]
                )
            ),
            
            types.FunctionDeclaration(
                name="get_project_tree",
                description="Get a tree view of the project structure",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "path": Schema(
                            type=Type.STRING,
                            description="Root path for tree view"
                        ),
                        "max_depth": Schema(
                            type=Type.INTEGER,
                            description="Maximum depth to traverse (default: 5)"
                        )
                    }
                )
            ),
            
            types.FunctionDeclaration(
                name="get_file_info",
                description="Get detailed information about a file (size, dates, lines)",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "path": Schema(
                            type=Type.STRING,
                            description="File path relative to workspace"
                        )
                    },
                    required=["path"]
                )
            ),
            
            # =========================================================
            # Bash Command Execution
            # =========================================================
            types.FunctionDeclaration(
                name="bash",
                description="Execute a shell command. Supports running tests, builds, linters, etc.",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "command": Schema(
                            type=Type.STRING,
                            description="Shell command to execute"
                        ),
                        "path": Schema(
                            type=Type.STRING,
                            description="Working directory for the command"
                        ),
                        "timeout": Schema(
                            type=Type.INTEGER,
                            description="Command timeout in seconds (default: 120)"
                        )
                    },
                    required=["command"]
                )
            ),
            
            # =========================================================
            # Git Operations
            # =========================================================
            types.FunctionDeclaration(
                name="git_operations",
                description="Perform git operations (init, status, add, commit, push, pull, etc.)",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "operation": Schema(
                            type=Type.STRING,
                            description="Git operation (init, status, add, commit, push, pull, log, diff, etc.)"
                        ),
                        "args": Schema(
                            type=Type.STRING,
                            description="Space-separated arguments (e.g., '-m \"commit message\"')"
                        ),
                        "path": Schema(
                            type=Type.STRING,
                            description="Repository path"
                        )
                    },
                    required=["operation"]
                )
            ),
            
            # =========================================================
            # Search Operations
            # =========================================================
            types.FunctionDeclaration(
                name="grep_files",
                description="Search for a pattern in files (regex supported)",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "pattern": Schema(
                            type=Type.STRING,
                            description="Search pattern (regex)"
                        ),
                        "search_path": Schema(
                            type=Type.STRING,
                            description="Path to search in"
                        ),
                        "recursive": Schema(
                            type=Type.BOOLEAN,
                            description="Search recursively (default: true)"
                        ),
                        "ignore_case": Schema(
                            type=Type.BOOLEAN,
                            description="Case-insensitive search"
                        ),
                        "max_results": Schema(
                            type=Type.INTEGER,
                            description="Maximum number of results (default: 100)"
                        )
                    },
                    required=["pattern"]
                )
            ),
            
            types.FunctionDeclaration(
                name="glob_search",
                description="Find files matching a glob pattern (e.g., '*.py', 'test_*.js')",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "pattern": Schema(
                            type=Type.STRING,
                            description="Glob pattern (e.g., '*.py', '**/*.json')"
                        ),
                        "path": Schema(
                            type=Type.STRING,
                            description="Path to search in"
                        ),
                        "recursive": Schema(
                            type=Type.BOOLEAN,
                            description="Search recursively (default: true)"
                        )
                    },
                    required=["pattern"]
                )
            ),
            
            # =========================================================
            # Batch Operations
            # =========================================================
            types.FunctionDeclaration(
                name="execute_batch",
                description="Execute multiple file operations in parallel for efficiency",
                parameters=Schema(
                    type=Type.OBJECT,
                    properties={
                        "tasks": Schema(
                            type=Type.STRING,
                            description="JSON string with list of task objects: [{\"operation\": \"create_file\", \"args\": {...}}, ...]"
                        ),
                        "allowed_tools": Schema(
                            type=Type.ARRAY,
                            items=Schema(type=Type.STRING),
                            description="List of allowed operations"
                        ),
                        "default_path": Schema(
                            type=Type.STRING,
                            description="Default path for operations"
                        ),
                        "max_workers": Schema(
                            type=Type.INTEGER,
                            description="Maximum parallel workers (default: 4)"
                        )
                    },
                    required=["tasks"]
                )
            )
        ]
    
    def get_workspace_path(self) -> str:
        """Get the absolute workspace path."""
        return str(self.fs_tools.workspace_root)
    
    def get_execution_log(self) -> List[Dict]:
        """Get the tool execution log."""
        return self.execution_log


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

def create_tools_for_role(
    workspace_root: str,
    role: str
) -> tuple[GeminiToolsAdapter, List[types.Tool]]:
    """
    Create tools appropriate for a specific agent role.
    
    Args:
        workspace_root: Workspace directory
        role: Agent role (coder, reviewer, tester, planner)
    
    Returns:
        Tuple of (adapter, tools)
    """
    adapter = GeminiToolsAdapter(workspace_root)
    
    role_tools = {
        "coder": [
            "create_file", "read_file", "update_file", "delete_file",
            "create_directory", "list_directory", "bash", "grep_files"
        ],
        "reviewer": [
            "read_file", "list_directory", "grep_files", "glob_search",
            "get_file_info", "get_project_tree"
        ],
        "tester": [
            "read_file", "create_file", "update_file", "bash",
            "list_directory", "grep_files"
        ],
        "planner": [
            "read_file", "list_directory", "get_project_tree",
            "grep_files", "glob_search", "get_file_info"
        ],
        "all": None  # All tools
    }
    
    subset = role_tools.get(role.lower(), role_tools["all"])
    tools = adapter.get_tool_declarations(tool_subset=subset)
    
    return adapter, tools
