"""
Orchestrator-Workers Workflow - Modern GenAI SDK Implementation
"""
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Tuple, Dict, Any, Optional
import asyncio
import logging

from app.models.schemas import WorkflowSelection, AgentResponse
from app.config import settings
from app.utils.context_loader import load_context_content
from app.core.llm_client import get_llm_client, get_functions_client


# ============================================================================
# Pydantic Schemas for Structured Outputs
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
# Helper Functions
# ============================================================================

def generate_agent_context(agent_persona: dict) -> str:
    """Generate system instruction from agent persona."""
    if not agent_persona:
        return "You are a helpful assistant."
    
    role = agent_persona.get("role", "Assistant")
    persona = agent_persona.get("persona", "Helpful and knowledgeable")
    description = agent_persona.get("description", "Provides helpful responses")
    strengths = ", ".join(agent_persona.get("strengths", ["Assistance"]))
    
    return f"""You are acting as the {role}.

ROLE: {role}
CHARACTER: {persona}
FUNCTION: {description}
STRENGTHS: {strengths}

Embody this persona in all your responses."""


def format_subtask_results(subtasks: List[SubTask], results: Dict[str, str]) -> str:
    """Format subtask results for the synthesizer prompt."""
    formatted = ""
    for i, subtask in enumerate(subtasks, 1):
        formatted += f"SUBTASK {i}: {subtask.title} ({subtask.required_expertise})\n"
        formatted += f"DESCRIPTION: {subtask.description}\n"
        formatted += f"RESULT:\n{results.get(subtask.id, 'No result available')}\n\n"
    return formatted


# ============================================================================
# Main Workflow Execution
# ============================================================================

async def execute(
    workflow_selection: WorkflowSelection, 
    user_query: str
) -> Tuple[str, List[AgentResponse]]:
    """
    Orchestrator-workers workflow using modern GenAI SDK.
    
    Uses structured outputs, proper system instructions, and parallel execution.
    """
    functions_client = get_functions_client()
    llm_client = get_llm_client()
    
    # Get personas from workflow selection
    workflow_personas = workflow_selection.personas.get("orchestrator_workers", {})
    intermediate_steps = []

    # Load context (optional enhancement for prompts)
    context_content = load_context_content(settings.CONTEXT_FILE_PATH)
    context_prefix = f"{context_content}\n\n---\n\n" if context_content else ""

    # =========================================================================
    # STEP 1: Task Planning with Structured Output
    # =========================================================================
    orchestrator_agent = workflow_personas.get("orchestrator_agent", {})
    
    planning_prompt = f"""{context_prefix}USER QUERY: {user_query}

Analyze this request and create a detailed execution plan. Break it down into 
logical subtasks, identify required expertise for each, determine dependencies,
and create an execution strategy."""

    try:
        # Use structured output for guaranteed schema compliance
        task_plan: TaskPlan = await functions_client.generate_structured(
            prompt=planning_prompt,
            response_schema=TaskPlan,
            system_instruction=generate_agent_context(orchestrator_agent),
            thinking_budget=1024,  # Complex reasoning benefits from thinking
        )
    except Exception as e:
        logging.error(f"Task planning failed: {e}")
        # Fallback to a simple single-task plan
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
                f"**Subtasks:** {len(task_plan.subtasks)} identified",
        metadata=task_plan.model_dump()
    ))

    # =========================================================================
    # STEP 2: Parallel Worker Execution with Dependency Resolution
    # =========================================================================
    worker_agent = workflow_personas.get("worker_agent", {})
    worker_system_instruction = generate_agent_context(worker_agent)
    
    # Sort by priority
    pending_subtasks = sorted(task_plan.subtasks, key=lambda x: x.priority)
    subtask_results: Dict[str, str] = {}

    def dependencies_satisfied(subtask: SubTask) -> bool:
        """Check if all dependencies are completed."""
        return all(dep_id in subtask_results for dep_id in subtask.dependencies)

    async def process_subtask(subtask: SubTask) -> Dict[str, Any]:
        """Process an individual subtask using the worker agent."""
        # Build dependency context
        dependency_context = ""
        if subtask.dependencies:
            dep_results = "\n\n".join([
                f"**Result from {dep_id}:**\n{subtask_results[dep_id]}"
                for dep_id in subtask.dependencies
            ])
            dependency_context = f"\n\nPREVIOUS RESULTS:\n{dep_results}"

        worker_prompt = f"""ORIGINAL USER QUERY: {user_query}

OVERALL TASK CONTEXT: {task_plan.task_understanding}

YOUR ASSIGNED SUBTASK: {subtask.title}
SUBTASK ID: {subtask.id}
DESCRIPTION: {subtask.description}
{dependency_context}

Execute this subtask thoroughly. Provide a detailed, complete response."""

        try:
            # Use system instruction properly via the client
            worker_response = await llm_client.generate(
                prompt=worker_prompt,
                temperature=0.6,
                system_instruction=worker_system_instruction,  # If your client supports it
            )
            return {
                "subtask_id": subtask.id,
                "title": subtask.title,
                "expertise": subtask.required_expertise,
                "response": worker_response,
                "success": True
            }
        except Exception as e:
            logging.error(f"Worker failed on subtask {subtask.id}: {e}")
            return {
                "subtask_id": subtask.id,
                "title": subtask.title,
                "expertise": subtask.required_expertise,
                "response": f"Error processing subtask: {str(e)}",
                "success": False
            }

    # Process subtasks respecting dependencies
    max_iterations = len(pending_subtasks) + 5  # Safety limit
    iteration = 0
    
    while pending_subtasks and iteration < max_iterations:
        iteration += 1
        
        # Find executable subtasks (dependencies satisfied)
        executable = [st for st in pending_subtasks if dependencies_satisfied(st)]
        
        if not executable:
            logging.error("Circular dependency detected or unresolvable dependencies")
            break
        
        # Execute in parallel
        results = await asyncio.gather(
            *[process_subtask(st) for st in executable],
            return_exceptions=True
        )
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                logging.error(f"Subtask execution exception: {result}")
                continue
                
            subtask_results[result["subtask_id"]] = result["response"]
            intermediate_steps.append(AgentResponse(
                agent_role=f"{result['expertise']} Specialist",
                content=result["response"],
                metadata={
                    "subtask_id": result["subtask_id"],
                    "title": result["title"],
                    "expertise": result["expertise"],
                    "success": result["success"]
                }
            ))
        
        # Remove completed subtasks
        completed_ids = {r["subtask_id"] for r in results if not isinstance(r, Exception)}
        pending_subtasks = [st for st in pending_subtasks if st.id not in completed_ids]

    # =========================================================================
    # STEP 3: Synthesis
    # =========================================================================
    synthesizer_agent = workflow_personas.get("synthesizer_agent", {})
    
    synthesis_prompt = f"""ORIGINAL USER QUERY: {user_query}

TASK UNDERSTANDING: {task_plan.task_understanding}

EXECUTION STRATEGY: {task_plan.execution_strategy}

WORKER RESULTS:
{format_subtask_results(task_plan.subtasks, subtask_results)}

Synthesize these results into a comprehensive, cohesive response that:
1. Addresses all aspects of the original query
2. Presents information logically and coherently
3. Resolves any contradictions between subtask results
4. Provides a complete solution

IMPORTANT:
- Write a fresh, synthesized narrative - do NOT copy worker outputs verbatim
- Start with a brief executive summary
- Use clear section headings
- Deduplicate overlapping information
- Maintain consistent terminology"""

    try:
        synthesized_response = await llm_client.generate(
            prompt=synthesis_prompt,
            temperature=0.7,
            system_instruction=generate_agent_context(synthesizer_agent),
        )
    except Exception as e:
        logging.error(f"Synthesis failed: {e}")
        # Fallback: concatenate results
        synthesized_response = "## Results Summary\n\n" + "\n\n".join([
            f"### {st.title}\n{subtask_results.get(st.id, 'No result')}"
            for st in task_plan.subtasks
        ])

    # Record synthesis
    intermediate_steps.append(AgentResponse(
        agent_role="Results Integrator",
        content=synthesized_response,
        metadata={"subtask_count": len(task_plan.subtasks)}
    ))

    return synthesized_response, intermediate_steps