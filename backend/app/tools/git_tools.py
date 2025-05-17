"""
Git tools for managing repositories within an agent's workspace.

This module provides tools for executing Git commands within an agent's workspace.
It includes functionality for initializing, cloning, and managing Git repositories
with proper workspace isolation and error handling.

Classes:
    GitInitParams: Pydantic model for git init parameters
    GitStatusParams: Pydantic model for git status parameters
    GitAddParams: Pydantic model for git add parameters
    GitCommitParams: Pydantic model for git commit parameters
    GitCheckoutParams: Pydantic model for git checkout parameters
    GitBranchParams: Pydantic model for git branch parameters
    GitPullParams: Pydantic model for git pull parameters
    GitCloneParams: Pydantic model for git clone parameters

Functions:
    _run_git_command: Internal utility to execute git commands
    git_init_repository_wrapper: Initializes a new git repository
    git_status_wrapper: Shows repository status
    git_add_wrapper: Stages files for commit
    git_commit_wrapper: Records changes to repository
    git_checkout_wrapper: Switches branches or restores files
    git_branch_wrapper: Lists or creates branches
    git_pull_wrapper: Fetches and integrates remote changes
    git_clone_wrapper: Clones a repository into workspace

Tool Definitions:
    git_init_repository_tool: Tool definition for git init
    git_status_tool: Tool definition for git status
    git_add_tool: Tool definition for git add
    git_commit_tool: Tool definition for git commit
    git_checkout_tool: Tool definition for git checkout
    git_branch_tool: Tool definition for git branch
    git_pull_tool: Tool definition for git pull
    git_clone_repository_tool: Tool definition for git clone

Constants:
    DEFAULT_AGENT_ID: Default agent ID used when none is provided
    git_tools: List of tools defined in this module for registration
"""

import os
import subprocess
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Tuple
from app.models.schemas import ToolDefinition
from app.dependencies import get_file_system_service
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)
# DEFAULT_AGENT_ID = "default_agent" # No longer used

# --- Utility function to run git commands (Refactored for agent_id) ---
async def _run_git_command(agent_id: str, command: List[str], timeout: int = 60) -> Tuple[bool, str]:
    """
    Runs a git command. The command should be constructed to operate correctly
    given that the cwd will be set to the agent's root workspace path.
    For operations on a specific repo within the workspace, use 'git -C <repo_subdir>'.
    Returns a tuple (success: bool, output: str).
    """
    service = get_file_system_service()
    try:
        agent_workspace_path = service.get_agent_workspace_path(agent_id)
        logger.debug(f"Agent {agent_id} - Workspace path for git: {agent_workspace_path}")
    except HTTPException as e:
        logger.error(f"Agent {agent_id} - Service error getting workspace path for git command: {e.detail}")
        return False, f"Error setting up git environment: {e.detail}"
    except Exception as e:
        logger.error(f"Unexpected error getting workspace for agent {agent_id} in _run_git_command: {e}", exc_info=True)
        return False, f"Unexpected error setting up git environment: {str(e)}"

    try:
        # The command list (e.g., ["git", "-C", "my_repo", "status"]) is passed in fully formed.
        # The cwd is the agent's root workspace.
        logger.info(f"Agent {agent_id} - Executing git command: {' '.join(command)} in CWD: {agent_workspace_path}")
        process = subprocess.run(
            command,
            cwd=agent_workspace_path, # All commands run from agent's root workspace
            capture_output=True,
            text=True,
            check=False, 
            timeout=timeout
        )
        if process.returncode == 0:
            output = process.stdout.strip() if process.stdout.strip() else "Command executed successfully."
            logger.info(f"Agent {agent_id} - Git command {' '.join(command)} successful.")
            return True, output
        else:
            error_message = process.stderr.strip() if process.stderr else "No specific error message from git."
            logger.error(f"Agent {agent_id} - Git command {' '.join(command)} failed with code {process.returncode}. Error: {error_message}")
            return False, f"Git command failed (code {process.returncode}): {error_message}"
    except subprocess.TimeoutExpired:
        logger.warning(f"Agent {agent_id} - Git command {' '.join(command)} timed out.")
        return False, "Git command timed out."
    except FileNotFoundError: 
        logger.error(f"Agent {agent_id} - Git command not found. Ensure 'git' is installed and in PATH.")
        return False, "Error: Git command not found on the system. Please ensure it is installed."
    except Exception as e:
        logger.error(f"Agent {agent_id} - Unexpected error running git command {' '.join(command)}: {e}", exc_info=True)
        return False, f"An unexpected error occurred while running git command: {str(e)}"

# --- Pydantic Schemas for Parameters ---
# These remain unchanged as agent_id is not part of tool parameters from LLM

class GitCloneParams(BaseModel):
    repo_url: str = Field(..., description="The URL of the repository to clone.")
    directory: Optional[str] = Field(None, description="Optional name for the directory to clone into. If None, derived from repo URL. Path is relative to agent workspace.")

class GitPullParams(BaseModel):
    repo_path: Optional[str] = Field(".", description="Relative path to the local repository within the agent's workspace (e.g., 'my_repo' or '.' for workspace root). Defaults to workspace root ('.').")
    remote: Optional[str] = Field(None, description="The remote to pull from (e.g., 'origin').")
    branch: Optional[str] = Field(None, description="The branch to pull.")

class GitPushParams(BaseModel):
    repo_path: Optional[str] = Field(".", description="Relative path to the local repository within the agent's workspace. Defaults to workspace root ('.').")
    remote: Optional[str] = Field("origin", description="The remote to push to (e.g., 'origin').")
    branch: Optional[str] = Field(None, description="The branch to push. If None, pushes the current branch or default configured behavior.")

class GitCommitParams(BaseModel):
    repo_path: Optional[str] = Field(".", description="Relative path to the local repository within the agent's workspace. Defaults to workspace root ('.').")
    message: str = Field(..., description="The commit message.")
    add_all: bool = Field(True, description="Whether to stage all changes ('git add .') within the repo_path before committing. Default True.")

class GitStatusParams(BaseModel):
    repo_path: Optional[str] = Field(".", description="Relative path to the local repository within the agent's workspace. Defaults to workspace root ('.').")

class GitAddParams(BaseModel):
    repo_path: Optional[str] = Field(".", description="Relative path to the local repository within the agent's workspace. Defaults to workspace root ('.').")
    files: List[str] = Field(..., description="List of files/patterns to add (e.g., ['.', 'specific_file.py', '*.txt']). Paths are relative to repo_path.")

    @validator('files')
    def prevent_path_traversal_in_files(cls, value):
        for f_path in value:
            if ".." in f_path:
                # This check is for file patterns *within* the targeted repo_path.
                # The repo_path itself is handled by ensuring it's a subdir of agent workspace.
                raise ValueError("File paths/patterns for 'add' cannot contain '..'")
        return value
        
class GitCheckoutParams(BaseModel):
    repo_path: Optional[str] = Field(".", description="Relative path to the local repository within the agent's workspace. Defaults to workspace root ('.').")
    branch_name: str = Field(..., description="The name of the branch to checkout or create.")
    create_new: Optional[bool] = Field(False, description="If True, creates a new branch with '-b' option. Default False.")

class GitBranchParams(BaseModel):
    repo_path: Optional[str] = Field(".", description="Relative path to the local repository within the agent's workspace. Defaults to workspace root ('.').")
    list_branches: Optional[bool] = Field(True, description="If True, lists all branches. Default True.")
    delete_branch: Optional[str] = Field(None, description="Name of the branch to delete with '-d'.")
    force_delete_branch: Optional[str] = Field(None, description="Name of the branch to force delete with '-D'.")


# --- Tool Wrapper Functions (Refactored for agent_id and -C usage) ---

async def git_clone_wrapper(agent_id: str, repo_url: str, directory: Optional[str] = None) -> str:
    # Clone happens *into* the agent_workspace_path (which is the CWD for _run_git_command)
    cmd = ["git", "clone", repo_url]
    if directory:
        if ".." in directory or directory.startswith("/") or directory.startswith("\\"):
            logger.warning(f"Agent {agent_id} - Invalid clone directory specified: {directory}")
            return "Error: Clone directory must be a relative path without '..'."
        cmd.append(directory) # directory is relative to agent_workspace_path
    success, output = await _run_git_command(agent_id, cmd, timeout=300)
    return output

async def git_pull_wrapper(agent_id: str, repo_path: Optional[str] = ".", remote: Optional[str] = None, branch: Optional[str] = None) -> str:
    cmd = ["git"]
    if repo_path and repo_path != ".":
        if ".." in repo_path or repo_path.startswith("/"):
            return f"Error: repo_path '{repo_path}' must be relative and within the workspace."
        cmd.extend(["-C", repo_path]) # repo_path is relative to agent_workspace_path
    cmd.append("pull")
    if remote:
        cmd.append(remote)
    if branch:
        cmd.append(branch)
    success, output = await _run_git_command(agent_id, cmd)
    return output

async def git_push_wrapper(agent_id: str, repo_path: Optional[str] = ".", remote: Optional[str] = "origin", branch: Optional[str] = None) -> str:
    cmd = ["git"]
    if repo_path and repo_path != ".":
        if ".." in repo_path or repo_path.startswith("/"):
            return f"Error: repo_path '{repo_path}' must be relative and within the workspace."
        cmd.extend(["-C", repo_path])
    cmd.append("push")
    cmd.append(remote)
    if branch:
        cmd.append(branch)
    success, output = await _run_git_command(agent_id, cmd)
    return output

async def git_commit_wrapper(agent_id: str, message: str, repo_path: Optional[str] = ".", add_all: bool = True) -> str:
    if ".." in repo_path or repo_path.startswith("/"):
        if repo_path != ".": # Allow "." for workspace root
             return f"Error: repo_path '{repo_path}' must be relative and within the workspace."

    if add_all:
        add_cmd_list = ["git"]
        if repo_path and repo_path != ".":
            add_cmd_list.extend(["-C", repo_path])
        add_cmd_list.extend(["add", "."])
        add_success, add_output = await _run_git_command(agent_id, add_cmd_list)
        if not add_success:
            return f"Agent {agent_id} - Failed to stage files in '{repo_path}': {add_output}"

    commit_cmd_list = ["git"]
    if repo_path and repo_path != ".":
        commit_cmd_list.extend(["-C", repo_path])
    commit_cmd_list.extend(["commit", "-m", message])
    
    success, output = await _run_git_command(agent_id, commit_cmd_list)
    return output

async def git_status_wrapper(agent_id: str, repo_path: Optional[str] = ".") -> str:
    cmd = ["git"]
    if repo_path and repo_path != ".":
        if ".." in repo_path or repo_path.startswith("/"):
            return f"Error: repo_path '{repo_path}' must be relative and within the workspace."
        cmd.extend(["-C", repo_path])
    cmd.append("status")
    success, output = await _run_git_command(agent_id, cmd)
    return output

async def git_add_wrapper(agent_id: str, files: List[str], repo_path: Optional[str] = ".") -> str:
    cmd = ["git"]
    if repo_path and repo_path != ".":
        if ".." in repo_path or repo_path.startswith("/"):
            return f"Error: repo_path '{repo_path}' must be relative and within the workspace."
        cmd.extend(["-C", repo_path])
    cmd.append("add")
    cmd.extend(files) # Pydantic validator already checks `files` for ".."
    success, output = await _run_git_command(agent_id, cmd)
    return output

async def git_checkout_wrapper(agent_id: str, branch_name: str, repo_path: Optional[str] = ".", create_new: Optional[bool] = False) -> str:
    cmd = ["git"]
    if repo_path and repo_path != ".":
        if ".." in repo_path or repo_path.startswith("/"):
            return f"Error: repo_path '{repo_path}' must be relative and within the workspace."
        cmd.extend(["-C", repo_path])
    cmd.append("checkout")
    if create_new:
        cmd.append("-b")
    cmd.append(branch_name)
    success, output = await _run_git_command(agent_id, cmd)
    return output

async def git_branch_wrapper(agent_id: str, repo_path: Optional[str] = ".", list_branches: Optional[bool] = True, delete_branch: Optional[str] = None, force_delete_branch: Optional[str] = None) -> str:
    cmd = ["git"]
    if repo_path and repo_path != ".":
        if ".." in repo_path or repo_path.startswith("/"):
            return f"Error: repo_path '{repo_path}' must be relative and within the workspace."
        cmd.extend(["-C", repo_path])
    cmd.append("branch")

    if delete_branch:
        cmd.extend(["-d", delete_branch])
    elif force_delete_branch:
        cmd.extend(["-D", force_delete_branch])
    elif list_branches:
        pass 
    else: 
        return f"Agent {agent_id} - No git branch action specified for repo '{repo_path}' (list, delete, or force_delete)."

    success, output = await _run_git_command(agent_id, cmd)
    return output


# --- Tool Definitions (Structure unchanged, functions refactored) ---

git_clone_tool = ToolDefinition(
    name="git_clone",
    description="Clones a Git repository from a URL into the agent's workspace. Optionally specify a target directory name (relative to workspace).",
    parameters=GitCloneParams.model_json_schema(),
    function=git_clone_wrapper
)

git_pull_tool = ToolDefinition(
    name="git_pull",
    description="Pulls changes from a remote repository for a local Git repository within the agent's workspace. Specify repo_path (relative to workspace, default '.'), remote, and branch.",
    parameters=GitPullParams.model_json_schema(),
    function=git_pull_wrapper
)

git_push_tool = ToolDefinition(
    name="git_push",
    description="Pushes changes from a local Git repository to a remote. Specify repo_path (relative to workspace, default '.'), remote, and branch.",
    parameters=GitPushParams.model_json_schema(),
    function=git_push_wrapper
)

git_commit_tool = ToolDefinition(
    name="git_commit",
    description="Commits staged changes in a local Git repository. Specify repo_path (relative to workspace, default '.'), commit message, and whether to add all changes before commit.",
    parameters=GitCommitParams.model_json_schema(),
    function=git_commit_wrapper
)

git_status_tool = ToolDefinition(
    name="git_status",
    description="Shows the status of a local Git repository (untracked files, changes to be committed, etc.). Specify repo_path (relative to workspace, default '.').",
    parameters=GitStatusParams.model_json_schema(),
    function=git_status_wrapper
)

git_add_tool = ToolDefinition(
    name="git_add",
    description="Stages changes in a local Git repository. Specify repo_path (relative to workspace, default '.'), and a list of files/patterns to add (e.g., '.', 'file.py').",
    parameters=GitAddParams.model_json_schema(),
    function=git_add_wrapper
)

git_checkout_tool = ToolDefinition(
    name="git_checkout",
    description="Switches branches or restores working tree files. Specify repo_path (relative to workspace, default '.'), branch name, and optionally create a new branch.",
    parameters=GitCheckoutParams.model_json_schema(),
    function=git_checkout_wrapper
)

git_branch_tool = ToolDefinition(
    name="git_branch",
    description="Manages branches in a local Git repository. Lists branches by default. Can delete or force delete branches. Specify repo_path (relative to workspace, default '.').",
    parameters=GitBranchParams.model_json_schema(),
    function=git_branch_wrapper
)

# List of all git tools in this module
git_tools = [
    git_clone_tool,
    git_pull_tool,
    git_push_tool,
    git_commit_tool,
    git_status_tool,
    git_add_tool,
    git_checkout_tool,
    git_branch_tool,
] 