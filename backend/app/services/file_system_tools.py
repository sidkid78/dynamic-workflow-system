# file_system_tools.py
"""
Comprehensive File System and Development Tools for Agent-Based Software Development

Provides file operations, git, bash execution, search tools, and parallel batch operations
for AI agents to build, modify, and manage software projects.

All operations are safe and sandboxed to a workspace directory.

Integrated from advanced_orch for the Agentic Layer Framework.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import subprocess
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import os


class FileSystemTools:
    """
    Comprehensive development tools for AI agents building software.
    
    Includes:
    - File/directory operations (CRUD)
    - Git operations  
    - Bash command execution (with Unix-to-Windows conversion)
    - Advanced search (grep, glob)
    - Parallel batch operations
    - Project structure management
    
    All paths are sandboxed to the workspace_root for security.
    
    Example:
        >>> fs = FileSystemTools("./my_workspace")
        >>> fs.create_file("src/main.py", "print('hello')")
        >>> fs.bash("python src/main.py")
    """
    
    def __init__(self, workspace_root: str = "./agent_workspace"):
        """
        Initialize file system tools with a workspace root.
        
        Args:
            workspace_root: Root directory for all operations. Created if doesn't exist.
        """
        self.workspace_root = Path(workspace_root).resolve()
        self.workspace_root.mkdir(exist_ok=True, parents=True)
        self.operations_log: List[Dict] = []
        
    def _resolve_path(self, path: str) -> Path:
        """
        Resolve a path within the workspace (security check).
        
        Args:
            path: Relative path from workspace root
        
        Returns:
            Resolved absolute path
        
        Raises:
            ValueError: If path tries to escape workspace
        """
        full_path = (self.workspace_root / path).resolve()
        
        if not str(full_path).startswith(str(self.workspace_root)):
            raise ValueError(
                f"Security error: Path '{path}' attempts to escape workspace"
            )
        
        return full_path
    
    def _log_operation(self, operation: str, details: Dict):
        """Log an operation for tracking."""
        self.operations_log.append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            **details
        })
    
    # =========================================================================
    # Core File Operations
    # =========================================================================
    
    def create_file(
        self,
        path: str,
        content: str,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new file with content.
        
        Args:
            path: File path relative to workspace
            content: File content to write
            overwrite: Whether to overwrite if file exists
        
        Returns:
            Result dict with success status and path
        """
        try:
            full_path = self._resolve_path(path)
            
            if full_path.exists() and not overwrite:
                return {
                    "success": False,
                    "error": f"File already exists: {path}",
                    "path": str(full_path)
                }
            
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            
            self._log_operation("create_file", {"path": path, "size": len(content)})
            
            return {
                "success": True,
                "path": str(full_path),
                "size": len(content)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def read_file(self, path: str) -> Dict[str, Any]:
        """
        Read file contents.
        
        Args:
            path: File path relative to workspace
        
        Returns:
            Result dict with content and metadata
        """
        try:
            full_path = self._resolve_path(path)
            
            if not full_path.exists():
                return {"success": False, "error": f"File not found: {path}"}
            
            content = full_path.read_text(encoding='utf-8')
            
            return {
                "success": True,
                "path": str(full_path),
                "content": content,
                "size": len(content),
                "lines": len(content.splitlines())
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_file(
        self,
        path: str,
        content: str,
        mode: str = "replace"
    ) -> Dict[str, Any]:
        """
        Update an existing file.
        
        Args:
            path: File path relative to workspace
            content: New content
            mode: 'replace', 'append', or 'prepend'
        
        Returns:
            Result dict with success status
        """
        try:
            full_path = self._resolve_path(path)
            
            if not full_path.exists():
                return {"success": False, "error": f"File not found: {path}"}
            
            if mode == "replace":
                full_path.write_text(content, encoding='utf-8')
            elif mode == "append":
                existing = full_path.read_text(encoding='utf-8')
                full_path.write_text(existing + content, encoding='utf-8')
            elif mode == "prepend":
                existing = full_path.read_text(encoding='utf-8')
                full_path.write_text(content + existing, encoding='utf-8')
            else:
                return {"success": False, "error": f"Invalid mode: {mode}"}
            
            self._log_operation("update_file", {"path": path, "mode": mode})
            
            return {"success": True, "path": str(full_path), "mode": mode}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_file(self, path: str) -> Dict[str, Any]:
        """Delete a file."""
        try:
            full_path = self._resolve_path(path)
            
            if not full_path.exists():
                return {"success": False, "error": f"File not found: {path}"}
            
            full_path.unlink()
            self._log_operation("delete_file", {"path": path})
            
            return {"success": True, "path": str(full_path)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_directory(self, path: str, parents: bool = True) -> Dict[str, Any]:
        """Create a directory."""
        try:
            full_path = self._resolve_path(path)
            full_path.mkdir(parents=parents, exist_ok=True)
            self._log_operation("create_directory", {"path": path})
            
            return {"success": True, "path": str(full_path)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_directory(
        self,
        path: str = ".",
        recursive: bool = False,
        include_hidden: bool = False
    ) -> Dict[str, Any]:
        """List directory contents."""
        try:
            full_path = self._resolve_path(path)
            
            if not full_path.exists():
                return {"success": False, "error": f"Directory not found: {path}"}
            
            if not full_path.is_dir():
                return {"success": False, "error": f"Not a directory: {path}"}
            
            items = []
            pattern = "**/*" if recursive else "*"
            
            for item in full_path.glob(pattern):
                if not include_hidden and item.name.startswith('.'):
                    continue
                
                rel_path = item.relative_to(self.workspace_root)
                
                items.append({
                    "path": str(rel_path),
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
            
            return {
                "success": True,
                "path": str(full_path),
                "items": items,
                "count": len(items)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_project_structure(
        self,
        project_name: str,
        structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a complete project structure from a specification.
        
        Args:
            project_name: Name/path of the project
            structure: Dict with 'directories' list and 'files' dict
        
        Example:
            >>> structure = {
            ...     "directories": ["src", "tests", "docs"],
            ...     "files": {
            ...         "src/__init__.py": "",
            ...         "README.md": "# My Project"
            ...     }
            ... }
            >>> fs.create_project_structure("my_project", structure)
        """
        try:
            created_items = []
            
            # Create directories
            for dir_path in structure.get("directories", []):
                full_dir = f"{project_name}/{dir_path}"
                result = self.create_directory(full_dir)
                if result["success"]:
                    created_items.append({"type": "directory", "path": full_dir})
            
            # Create files
            for file_path, content in structure.get("files", {}).items():
                full_file = f"{project_name}/{file_path}"
                result = self.create_file(full_file, content)
                if result["success"]:
                    created_items.append({"type": "file", "path": full_file})
            
            self._log_operation("create_project_structure", {
                "project_name": project_name,
                "items_created": len(created_items)
            })
            
            return {
                "success": True,
                "project_name": project_name,
                "created_items": created_items
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_project_tree(self, path: str = ".", max_depth: int = 5) -> Dict[str, Any]:
        """Get a tree view of the project structure."""
        try:
            full_path = self._resolve_path(path)
            
            def build_tree(dir_path: Path, depth: int = 0) -> List[Dict]:
                if depth >= max_depth:
                    return []
                
                items = []
                try:
                    for item in sorted(dir_path.iterdir()):
                        if item.name.startswith('.'):
                            continue
                        
                        rel_path = item.relative_to(self.workspace_root)
                        
                        node = {
                            "name": item.name,
                            "path": str(rel_path),
                            "type": "directory" if item.is_dir() else "file"
                        }
                        
                        if item.is_dir():
                            node["children"] = build_tree(item, depth + 1)
                        else:
                            node["size"] = item.stat().st_size
                        
                        items.append(node)
                except PermissionError:
                    pass
                
                return items
            
            tree = build_tree(full_path)
            
            return {"success": True, "path": str(full_path), "tree": tree}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_file_info(self, path: str) -> Dict[str, Any]:
        """Get detailed information about a file."""
        try:
            full_path = self._resolve_path(path)
            
            if not full_path.exists():
                return {"success": False, "error": f"File not found: {path}"}
            
            stat = full_path.stat()
            
            info = {
                "success": True,
                "path": str(full_path),
                "name": full_path.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_file": full_path.is_file(),
                "is_directory": full_path.is_dir()
            }
            
            if full_path.is_file():
                try:
                    content = full_path.read_text(encoding='utf-8')
                    info["lines"] = len(content.splitlines())
                except UnicodeDecodeError:
                    info["lines"] = None  # Binary file
                info["extension"] = full_path.suffix
            
            return info
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # =========================================================================
    # Bash Command Execution
    # =========================================================================
    
    def bash(
        self,
        command: str,
        path: str = ".",
        timeout: int = 120
    ) -> Dict[str, Any]:
        """
        Execute a bash command.
        
        Args:
            command: Shell command to execute
            path: Working directory (relative to workspace)
            timeout: Command timeout in seconds
        
        Returns:
            Result dict with stdout, stderr, return_code
        
        Features:
            - Unix-to-Windows command conversion (for Windows hosts)
            - Dangerous command blocking
            - Blocking server detection (prevents hangs)
            - CI=true for non-interactive npm/npx
        """
        try:
            # Use workspace root if path is "."
            if path == ".":
                full_path = self.workspace_root
            else:
                full_path = self._resolve_path(path)
            
            # Security: Block dangerous commands
            dangerous_patterns = [
                r'\brm\s+-rf\s+/',
                r'\bformat\b',
                r'\bmkfs\b',
                r'\bdd\b.*if=/dev/',
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, command, re.IGNORECASE):
                    return {
                        "success": False,
                        "error": f"Dangerous command blocked: {command}"
                    }
            
            # Unix-to-Windows command conversion (for Windows hosts)
            if os.name == 'nt':
                command = self._convert_unix_command(command)
            
            # Detect blocking server commands that would hang
            blocking_patterns = [
                r'\bflask\s+run\b',
                r'\buvicorn\b(?!.*--help)',
                r'\bgunicorn\b(?!.*--help)',
                r'\bpython\s+.*app\.py\b',
                r'\bpython\s+-m\s+http\.server\b',
                r'\bnpm\s+start\b',
                r'\bnode\s+.*server\.js\b',
                r'\byarn\s+start\b',
                r'\bng\s+serve\b',
                r'\bpython\s+manage\.py\s+runserver\b',
            ]
            
            for pattern in blocking_patterns:
                if re.search(pattern, command, re.IGNORECASE):
                    return {
                        "success": False,
                        "error": f"Blocking server command detected: '{command}'. "
                                 f"This command starts a server that runs indefinitely.",
                        "suggestion": "Use tests or health checks instead of running the server directly."
                    }
            
            # Execute command with CI=true for non-interactive mode
            env = os.environ.copy()
            env['CI'] = 'true'
            
            result = subprocess.run(
                command,
                cwd=full_path,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                stdin=subprocess.DEVNULL,
                env=env
            )
            
            self._log_operation("bash", {
                "command": command,
                "path": path,
                "return_code": result.returncode
            })
            
            return {
                "success": result.returncode == 0,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Command timed out after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _convert_unix_command(self, command: str) -> str:
        """Convert Unix commands to Windows PowerShell equivalents."""
        unix_conversions = [
            (r'^mkdir\s+-p\s+(.+)$', r'New-Item -ItemType Directory -Force -Path "\1"'),
            (r'^rm\s+-rf\s+(.+)$', r'Remove-Item -Recurse -Force "\1" -ErrorAction SilentlyContinue'),
            (r'^rm\s+-r\s+(.+)$', r'Remove-Item -Recurse "\1"'),
            (r'^rm\s+(.+)$', r'Remove-Item "\1"'),
            (r'^ls\s+-l[a]?\s*(.*)$', r'Get-ChildItem \1'),
            (r'^ls\s*(.*)$', r'Get-ChildItem \1'),
            (r'^cat\s+(.+)$', r'Get-Content "\1"'),
            (r'^touch\s+(.+)$', r'New-Item -ItemType File -Force -Path "\1"'),
            (r'^cp\s+-r\s+(.+)\s+(.+)$', r'Copy-Item -Recurse "\1" "\2"'),
            (r'^cp\s+(.+)\s+(.+)$', r'Copy-Item "\1" "\2"'),
            (r'^mv\s+(.+)\s+(.+)$', r'Move-Item "\1" "\2"'),
            (r'^pwd$', r'Get-Location'),
            (r'^echo\s+(.+)$', r'Write-Output \1'),
        ]
        
        for pattern, replacement in unix_conversions:
            if re.match(pattern, command, re.IGNORECASE):
                return re.sub(pattern, replacement, command, flags=re.IGNORECASE)
        
        return command
    
    # =========================================================================
    # Git Operations
    # =========================================================================
    
    def git_operations(
        self,
        operation: str,
        args: str = "",
        path: str = "."
    ) -> Dict[str, Any]:
        """
        Perform git operations.
        
        Args:
            operation: Git operation (init, status, add, commit, push, pull, etc.)
            args: Space-separated arguments for the git command
            path: Repository path
        
        Examples:
            >>> git_operations("init")
            >>> git_operations("add", args=".")
            >>> git_operations("commit", args='-m "Initial commit"')
        """
        try:
            if path == ".":
                full_path = self.workspace_root
            else:
                full_path = self._resolve_path(path)
            
            # Build git command
            cmd = ["git", operation]
            
            if args:
                import shlex
                cmd.extend(shlex.split(args))
            
            result = subprocess.run(
                cmd,
                cwd=full_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            self._log_operation("git_operations", {
                "operation": operation,
                "args": args,
                "return_code": result.returncode
            })
            
            return {
                "success": result.returncode == 0,
                "operation": operation,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Git operation timed out"}
        except FileNotFoundError:
            return {"success": False, "error": "Git not found. Is it installed?"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # =========================================================================
    # Search Operations
    # =========================================================================
    
    def grep_files(
        self,
        pattern: str,
        search_path: str = ".",
        recursive: bool = True,
        ignore_case: bool = False,
        max_results: int = 100
    ) -> Dict[str, Any]:
        """
        Search for a pattern in files.
        
        Args:
            pattern: Search pattern (regex)
            search_path: Path to search in
            recursive: Whether to search recursively
            ignore_case: Case-insensitive search
            max_results: Maximum results to return
        
        Returns:
            Result dict with matches (file, line number, content)
        """
        try:
            full_path = self._resolve_path(search_path)
            
            flags = re.IGNORECASE if ignore_case else 0
            regex = re.compile(pattern, flags)
            
            matches = []
            
            if recursive:
                files = full_path.rglob("*")
            else:
                files = full_path.glob("*")
            
            # Skip binary file extensions
            skip_extensions = {'.pyc', '.so', '.dll', '.exe', '.bin', '.jpg', '.png', '.gif', '.pdf'}
            
            for file_path in files:
                if not file_path.is_file():
                    continue
                
                if file_path.suffix.lower() in skip_extensions:
                    continue
                
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    for line_num, line in enumerate(content.splitlines(), 1):
                        if regex.search(line):
                            rel_path = file_path.relative_to(self.workspace_root)
                            
                            matches.append({
                                "file": str(rel_path),
                                "line": line_num,
                                "content": line.strip()[:200]  # Truncate long lines
                            })
                            
                            if len(matches) >= max_results:
                                break
                    
                    if len(matches) >= max_results:
                        break
                        
                except (UnicodeDecodeError, PermissionError):
                    continue
            
            return {
                "success": True,
                "pattern": pattern,
                "matches": matches,
                "count": len(matches),
                "truncated": len(matches) >= max_results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def glob_search(
        self,
        pattern: str,
        path: str = ".",
        recursive: bool = True
    ) -> Dict[str, Any]:
        """
        Find files matching a glob pattern.
        
        Args:
            pattern: Glob pattern (e.g., "*.py", "test_*.js")
            path: Path to search in
            recursive: Search recursively
        
        Returns:
            Result dict with list of matching file paths
        """
        try:
            if path == ".":
                full_path = self.workspace_root
            else:
                full_path = self._resolve_path(path)
            
            if recursive and not pattern.startswith("**/"):
                pattern = f"**/{pattern}"
            
            matches = []
            for file_path in full_path.glob(pattern):
                rel_path = file_path.relative_to(self.workspace_root)
                
                matches.append({
                    "path": str(rel_path),
                    "name": file_path.name,
                    "type": "directory" if file_path.is_dir() else "file",
                    "size": file_path.stat().st_size if file_path.is_file() else None
                })
            
            self._log_operation("glob_search", {
                "pattern": pattern,
                "path": path,
                "matches": len(matches)
            })
            
            return {
                "success": True,
                "pattern": pattern,
                "matches": matches,
                "count": len(matches)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # =========================================================================
    # Batch Operations
    # =========================================================================
    
    def execute_batch(
        self,
        tasks: str | List[Dict],
        allowed_tools: Optional[List[str]] = None,
        default_path: str = ".",
        max_workers: int = 4
    ) -> Dict[str, Any]:
        """
        Execute multiple tasks in parallel.
        
        Args:
            tasks: JSON string or list of task objects
            allowed_tools: List of allowed tools (None = all)
            default_path: Default path for operations
            max_workers: Maximum parallel workers
        
        Task format:
            {"operation": "create_file", "args": {"path": "...", "content": "..."}}
        
        Returns:
            Result dict with results from all tasks
        """
        try:
            # Parse tasks if JSON string
            if isinstance(tasks, str):
                task_list = json.loads(tasks)
            else:
                task_list = tasks
            
            if not isinstance(task_list, list):
                return {"success": False, "error": "Tasks must be a list"}
            
            # Map operation names to methods
            operation_map = {
                "create_file": self.create_file,
                "read_file": self.read_file,
                "update_file": self.update_file,
                "delete_file": self.delete_file,
                "create_directory": self.create_directory,
                "list_directory": self.list_directory,
                "bash": self.bash,
                "git_operations": self.git_operations,
                "grep_files": self.grep_files,
                "glob_search": self.glob_search,
                "get_file_info": self.get_file_info,
                "create_project_structure": self.create_project_structure,
                "get_project_tree": self.get_project_tree
            }
            
            # Filter by allowed tools
            if allowed_tools:
                operation_map = {k: v for k, v in operation_map.items() if k in allowed_tools}
            
            results = []
            
            def execute_task(task_dict: Dict) -> Dict:
                operation = task_dict.get("operation")
                args = task_dict.get("args", {})
                
                # Add default path if not specified
                if "path" not in args and operation in ["bash", "git_operations", "glob_search"]:
                    args["path"] = default_path
                if "search_path" not in args and operation == "grep_files":
                    args["search_path"] = default_path
                
                if operation not in operation_map:
                    return {
                        "task": task_dict,
                        "success": False,
                        "error": f"Unknown or disallowed operation: {operation}"
                    }
                
                try:
                    result = operation_map[operation](**args)
                    return {"task": task_dict, **result}
                except Exception as e:
                    return {"task": task_dict, "success": False, "error": str(e)}
            
            # Execute in parallel
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(execute_task, task) for task in task_list]
                
                for future in as_completed(futures):
                    results.append(future.result())
            
            successes = sum(1 for r in results if r.get("success"))
            failures = len(results) - successes
            
            self._log_operation("execute_batch", {
                "total_tasks": len(task_list),
                "successes": successes,
                "failures": failures
            })
            
            return {
                "success": failures == 0,
                "results": results,
                "total_tasks": len(task_list),
                "successes": successes,
                "failures": failures
            }
            
        except json.JSONDecodeError:
            return {"success": False, "error": "Invalid JSON in tasks parameter"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # =========================================================================
    # Utilities
    # =========================================================================
    
    def get_operations_log(self) -> List[Dict]:
        """Get all logged operations."""
        return self.operations_log
    
    def save_operations_log(self, filename: str = "operations_log.json") -> Dict[str, Any]:
        """Save operations log to file."""
        try:
            log_path = self.workspace_root / filename
            
            with open(log_path, 'w') as f:
                json.dump(self.operations_log, f, indent=2)
            
            return {
                "success": True,
                "path": str(log_path),
                "operations": len(self.operations_log)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def clear_workspace(self, confirm: bool = False) -> Dict[str, Any]:
        """
        Clear all contents of the workspace.
        
        Args:
            confirm: Must be True to actually clear
        
        Returns:
            Result dict
        """
        if not confirm:
            return {
                "success": False,
                "error": "Must pass confirm=True to clear workspace"
            }
        
        try:
            import shutil
            for item in self.workspace_root.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            
            self._log_operation("clear_workspace", {"confirmed": True})
            
            return {"success": True, "message": "Workspace cleared"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
