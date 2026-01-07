"""
Orchestrator-Workers Workflow with Tool Execution
==================================================

This workflow extends the base orchestrator-workers with actual tool execution.
Workers can create files, run bash commands, git operations, etc.

Key Differences from base orchestrator_workers:
- Workers receive tools via generate_with_functions()
- Tool calls are executed in an agentic loop
- Actual files/changes are created in the workspace
"""
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Tuple, Dict, Any, Optional
import asyncio
import difflib
import logging
import json

from app.models.schemas import WorkflowSelection, AgentResponse
from app.config import settings
from app.utils.context_loader import load_context_content
from app.core.llm_client import get_llm_client, get_functions_client
from app.core.helpers.persona_utils import generate_agent_context, get_agent_config
from app.services.gemini_tools import GeminiToolsAdapter, create_tools_for_role


# ============================================================================
# Schemas
# ============================================================================

class SubTask(BaseModel):
    id: str
    title: str
    description: str
    required_expertise: str
    priority: int
    dependencies: List[str]


class TaskPlan(BaseModel):
    task_understanding: str
    subtasks: List[SubTask]
    execution_strategy: str


# ============================================================================
# Constants
# ============================================================================

MAX_TOOL_ITERATIONS = 10  # Max tool calls per subtask
WORKSPACE_ROOT = "./agent_workspace"


# ============================================================================
# Helpers
# ============================================================================

def format_subtask_results(subtasks: List[SubTask], results: Dict[str, str]) -> str:
    """Format subtask results for synthesis."""
    formatted = ""
    for i, subtask in enumerate(subtasks, 1):
        formatted += f"SUBTASK {i}: {subtask.title} ({subtask.required_expertise})\n"
        formatted += f"DESCRIPTION: {subtask.description}\n"
        formatted += f"RESULT:\n{results.get(subtask.id, 'No result available')}\n\n"
    return formatted


def format_tool_result(tool_name: str, result: Dict) -> str:
    """Format a tool result for the LLM context."""
    if result.get("success"):
        # Truncate large outputs
        result_str = json.dumps(result, indent=2)
        if len(result_str) > 2000:
            result_str = result_str[:2000] + "\n... (truncated)"
        return f"✓ {tool_name} succeeded:\n{result_str}"
    else:
        return f"✗ {tool_name} failed: {result.get('error', 'Unknown error')}"


def check_synthesis_plagiarism(
    synthesized: str, 
    subtask_results: Dict[str, str], 
    threshold: float = 0.85
) -> bool:
    """Check if synthesis is too similar to any worker output."""
    for subtask_id, worker_text in subtask_results.items():
        if not worker_text or len(worker_text) < 100:
            continue
        
        ratio = difflib.SequenceMatcher(None, synthesized, worker_text).ratio()
        if ratio >= threshold:
            logging.warning(f"Synthesis {ratio:.0%} similar to {subtask_id}")
            return True
    
    return False


# ============================================================================
# Main Workflow
# ============================================================================

async def execute(
    workflow_selection: WorkflowSelection, 
    user_query: str
):
    """
    Orchestrator-workers workflow with tool execution.
    
    Workers can now actually:
    - Create/read/update/delete files
    - Run bash commands
    - Use git operations
    - Search files with grep/glob
    """
    llm_client = get_llm_client()
    functions_client = get_functions_client()
    
    # Initialize the tools adapter
    adapter = GeminiToolsAdapter(workspace_root=WORKSPACE_ROOT)
    logging.info(f"Initialized tools with workspace: {adapter.get_workspace_path()}")
    
    workflow_personas = workflow_selection.personas or {}
    intermediate_steps = []

    # Load context
    context_content = load_context_content(settings.CONTEXT_FILE_PATH)
    context_prefix = f"{context_content}\n\n---\n\n" if context_content else ""

    # =========================================================================
    # PHASE 1: Task Planning with Structured Output
    # =========================================================================
    orchestrator_persona = workflow_personas.get("orchestrator_agent", {})
    orchestrator_config = get_agent_config(orchestrator_persona)
    
    planning_prompt = f"""{context_prefix}USER QUERY: {user_query}

Analyze this request and create a detailed execution plan:
1. Understand the overall task requirements
2. Break it into logical subtasks with clear boundaries
3. Identify required expertise for each subtask
4. Determine dependencies between subtasks
5. Create an execution strategy

Be specific - workers will execute based on your instructions.
Workers have access to file system tools (create_file, read_file, bash, git, etc.)."""

    try:
        task_plan = await functions_client.generate_structured(
            prompt=planning_prompt,
            response_schema=TaskPlan,
            system_instruction=generate_agent_context(orchestrator_persona, as_system_instruction=True),
            thinking_budget=orchestrator_config["thinking_budget"],
            temperature=orchestrator_config["temperature"],
        )
    except Exception as e:
        logging.error(f"Task planning failed: {e}")
        task_plan = TaskPlan(
            task_understanding=f"Process the user query: {user_query}",
            subtasks=[SubTask(
                id="task_1",
                title="General Processing",
                description="Process the user query comprehensively",
                required_expertise="General Knowledge",
                priority=1,
                dependencies=[]
            )],
            execution_strategy="Execute single comprehensive task"
        )

    # Record planning step
    intermediate_steps.append(AgentResponse(
        agent_role="Task Coordinator",
        content=f"**Task Understanding:**\n{task_plan.task_understanding}\n\n"
                f"**Execution Strategy:**\n{task_plan.execution_strategy}\n\n"
                f"**Subtasks:** {len(task_plan.subtasks)} identified\n" +
                "\n".join([
                    f"  {i+1}. {st.title} (Priority: {st.priority}, Deps: {st.dependencies or 'None'})"
                    for i, st in enumerate(task_plan.subtasks)
                ]),
        metadata=task_plan.model_dump()
    ))

    # =========================================================================
    # PHASE 2: Worker Execution with Tools
    # =========================================================================
    worker_persona = workflow_personas.get("worker_agent", {})
    worker_config = get_agent_config(worker_persona)
    worker_system = generate_agent_context(worker_persona, as_system_instruction=True)
    
    # Get tool declarations for workers
    tool_declarations = adapter.get_tool_declarations()
    
    pending_subtasks = sorted(task_plan.subtasks, key=lambda x: x.priority)
    subtask_results: Dict[str, str] = {}

    def dependencies_satisfied(subtask: SubTask) -> bool:
        return all(dep_id in subtask_results for dep_id in subtask.dependencies)

    async def process_subtask_with_tools(subtask: SubTask) -> Dict[str, Any]:
        """Process a subtask with tool execution in an agentic loop."""
        
        # Build dependency context
        dep_context = ""
        if subtask.dependencies:
            dep_results = "\n\n".join([
                f"**Result from {dep_id}:**\n{subtask_results[dep_id][:1500]}"
                for dep_id in subtask.dependencies
                if dep_id in subtask_results
            ])
            dep_context = f"\n\nPREVIOUS RESULTS:\n{dep_results}"

        worker_prompt = f"""ORIGINAL QUERY: {user_query}
TASK CONTEXT: {task_plan.task_understanding}

YOUR SUBTASK: {subtask.title}
DESCRIPTION: {subtask.description}

WORKSPACE: {adapter.get_workspace_path()}

You have access to file system tools. Use them to complete your task.
When you're done, provide a summary of what you accomplished.
{dep_context}

Execute this subtask thoroughly using the available tools."""

        conversation_history = [worker_prompt]
        tool_calls_made = []
        iterations = 0
        final_text = ""

        try:
            while iterations < MAX_TOOL_ITERATIONS:
                iterations += 1
                
                # Call LLM with tools
                response = await functions_client.generate_with_functions(
                    prompt="\n\n".join(conversation_history),
                    functions=tool_declarations,
                    system_instruction=worker_system,
                    thinking_budget=worker_config["thinking_budget"],
                    temperature=worker_config["temperature"],
                )
                
                if response["type"] == "text":
                    # Worker is done - got text response
                    final_text = response["content"]
                    break
                    
                elif response["type"] == "function_call":
                    # Execute the tool
                    tool_name = response["name"]
                    tool_args = response["arguments"]
                    
                    logging.info(f"[{subtask.id}] Calling tool: {tool_name}({tool_args})")
                    
                    result = adapter.execute_tool(tool_name, tool_args)
                    tool_calls_made.append({
                        "tool": tool_name,
                        "args": tool_args,
                        "result": result
                    })
                    
                    # Add tool result to conversation
                    tool_result_text = format_tool_result(tool_name, result)
                    conversation_history.append(f"TOOL RESULT:\n{tool_result_text}\n\nContinue with your task or provide a final summary if complete.")
            
            # If we hit max iterations without text response
            if not final_text:
                final_text = f"Task completed after {iterations} tool calls. Tools used: {[tc['tool'] for tc in tool_calls_made]}"

            return {
                "subtask_id": subtask.id,
                "title": subtask.title,
                "expertise": subtask.required_expertise,
                "response": final_text,
                "tool_calls": tool_calls_made,
                "iterations": iterations,
                "success": True
            }
            
        except Exception as e:
            logging.error(f"Worker failed on {subtask.id}: {e}")
            return {
                "subtask_id": subtask.id,
                "title": subtask.title,
                "expertise": subtask.required_expertise,
                "response": f"Error: {str(e)}",
                "tool_calls": tool_calls_made,
                "iterations": iterations,
                "success": False
            }

    # Process with dependency resolution
    max_iterations = len(pending_subtasks) + 5
    iteration = 0
    
    while pending_subtasks and iteration < max_iterations:
        iteration += 1
        
        executable = [st for st in pending_subtasks if dependencies_satisfied(st)]
        
        if not executable:
            logging.error("Circular dependency or unresolvable state")
            executable = pending_subtasks[:1]
        
        results = await asyncio.gather(
            *[process_subtask_with_tools(st) for st in executable],
            return_exceptions=True
        )
        
        for result in results:
            if isinstance(result, Exception):
                logging.error(f"Subtask exception: {result}")
                continue
            
            subtask_results[result["subtask_id"]] = result["response"]
            
            # Include tool call info in the step
            tool_summary = ""
            if result.get("tool_calls"):
                tool_names = [tc["tool"] for tc in result["tool_calls"]]
                tool_summary = f"\n\n**Tools Used:** {', '.join(tool_names)} ({result['iterations']} iterations)"
            
            intermediate_steps.append(AgentResponse(
                agent_role=f"{result['expertise']} Specialist",
                content=result["response"] + tool_summary,
                metadata={
                    "subtask_id": result["subtask_id"],
                    "title": result["title"],
                    "success": result["success"],
                    "tool_calls": len(result.get("tool_calls", [])),
                    "iterations": result.get("iterations", 0)
                }
            ))
        
        completed_ids = {
            r["subtask_id"] for r in results 
            if not isinstance(r, Exception)
        }
        pending_subtasks = [st for st in pending_subtasks if st.id not in completed_ids]

    # =========================================================================
    # PHASE 3: Synthesis
    # =========================================================================
    synthesizer_persona = workflow_personas.get("synthesizer_agent", {})
    synthesizer_config = get_agent_config(synthesizer_persona)
    synthesizer_system = generate_agent_context(synthesizer_persona, as_system_instruction=True)
    
    # Get workspace tree for synthesis context
    workspace_tree = adapter.execute_tool("get_project_tree", {"path": ".", "max_depth": 3})
    tree_context = ""
    if workspace_tree.get("success"):
        tree_context = f"\n\nWORKSPACE STATE:\n{json.dumps(workspace_tree.get('tree', []), indent=2)}"
    
    synthesis_prompt = f"""ORIGINAL USER QUERY: {user_query}

TASK UNDERSTANDING: {task_plan.task_understanding}

EXECUTION STRATEGY: {task_plan.execution_strategy}

WORKER RESULTS:
{format_subtask_results(task_plan.subtasks, subtask_results)}
{tree_context}

Synthesize these results into a comprehensive, cohesive response.

REQUIREMENTS:
1. Address all aspects of the original query
2. Present information logically with clear structure
3. Resolve any contradictions between worker outputs
4. Provide a complete, actionable solution
5. Include information about files/artifacts created

CRITICAL CONSTRAINTS:
- Write a FRESH narrative - do NOT copy worker outputs verbatim
- Start with a brief executive summary (2-3 sentences)
- Use clear section headings
- Deduplicate overlapping information
- Mention specific files created if applicable"""

    max_synthesis_attempts = 2
    synthesized_response = None
    
    for attempt in range(max_synthesis_attempts):
        try:
            synthesized_response = await llm_client.generate(
                prompt=synthesis_prompt if attempt == 0 else synthesis_prompt + 
                    "\n\nADDITIONAL CONSTRAINT: Your previous synthesis was too similar to worker outputs. "
                    "Write a completely fresh, distilled summary in your own words.",
                system_instruction=synthesizer_system,
                thinking_budget=synthesizer_config["thinking_budget"],
                temperature=synthesizer_config["temperature"] - (attempt * 0.1),
                max_tokens=synthesizer_config["max_tokens"],
            )
            
            if not check_synthesis_plagiarism(synthesized_response, subtask_results):
                break
            
            if attempt < max_synthesis_attempts - 1:
                logging.info(f"Synthesis attempt {attempt + 1} too similar, retrying...")
                
        except Exception as e:
            logging.error(f"Synthesis attempt {attempt + 1} failed: {e}")
            if attempt == max_synthesis_attempts - 1:
                synthesized_response = "## Results Summary\n\n" + "\n\n".join([
                    f"### {st.title}\n{subtask_results.get(st.id, 'No result')}"
                    for st in task_plan.subtasks
                ])

    # Record synthesis
    intermediate_steps.append(AgentResponse(
        agent_role="Results Integrator",
        content=synthesized_response,
        metadata={
            "subtask_count": len(task_plan.subtasks),
            "successful_subtasks": sum(1 for r in subtask_results.values() if not r.startswith("Error:")),
            "workspace": adapter.get_workspace_path(),
            "total_tool_calls": len(adapter.get_execution_log())
        }
    ))

    return synthesized_response, intermediate_steps
