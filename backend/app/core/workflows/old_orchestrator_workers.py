# app/core/workflows/orchestrator_workers.py
"""
Orchestrator-Workers Workflow Module

This module implements a workflow pattern where a central orchestrator LLM:
1. Analyzes a complex user query
2. Breaks it down into subtasks
3. Delegates these subtasks to specialized worker LLMs
4. Synthesizes their results into a cohesive response

The workflow follows these steps:
1. Task Planning: The orchestrator analyzes the query and creates a structured plan
2. Subtask Execution: Workers execute subtasks based on dependencies and priorities
3. Result Synthesis: A synthesizer combines all worker outputs into a final response

This approach is particularly effective for complex, multi-faceted queries that
require different types of expertise or processing approaches.
"""
from app.models.schemas import WorkflowSelection, AgentResponse
import difflib
from app.core.llm_client import get_llm_client, get_functions_client
from typing import Tuple, List, Dict, Any
import logging
import json
import asyncio
from app.config import settings # Import settings
from app.utils.context_loader import load_context_content # Import context loader

async def execute(workflow_selection: WorkflowSelection, user_query: str) -> Tuple[str, List[AgentResponse]]:
    """
    Executes an orchestrator-workers workflow where a central LLM analyzes a user query,
    breaks it down into subtasks, delegates these subtasks to worker LLMs, and synthesizes
    their results into a cohesive response.

    This function implements a three-phase workflow:
    1. Task Planning: An orchestrator agent analyzes the query and creates a structured plan
       with subtasks, priorities, and dependencies using function calling.
    2. Subtask Execution: Worker agents execute subtasks in parallel when dependencies are
       satisfied, respecting priority order.
    3. Result Synthesis: A synthesizer agent integrates all worker outputs into a unified,
       cohesive response that addresses the original query.

    The workflow supports:
    - Parallel execution of independent subtasks
    - Dependency management between subtasks
    - Context injection from external files
    - Fallback handling for errors at each stage
    - Validation to prevent verbatim copying of worker outputs

    Parameters:
    - workflow_selection (WorkflowSelection): The selection of workflows to execute, containing
      persona configurations for orchestrator, worker, and synthesizer agents.
    - user_query (str): The query provided by the user that needs to be processed.

    Returns:
    - Tuple[str, List[AgentResponse]]: A tuple containing:
      - str: The final synthesized response addressing the user's query
      - List[AgentResponse]: A list of intermediate agent responses recorded during execution,
        including the task plan, individual worker outputs, and the synthesis step.

    Raises:
    - Logs errors but does not raise exceptions; instead provides fallback responses.

    Example:
        >>> workflow_selection = WorkflowSelection(personas={...})
        >>> response, steps = await execute(workflow_selection, "Analyze market trends")
        >>> print(response)  # Final synthesized answer
        >>> print(len(steps))  # Number of intermediate steps
    """
    functions_client = get_functions_client()
    llm_client = get_llm_client()
    personas = workflow_selection.personas.get("orchestrator_workers", {})
    intermediate_steps = []
    
    # Load context content - REMOVE FROM HERE
    # context_content = load_context_content(settings.CONTEXT_FILE_PATH)
    # context_prefix = f"{context_content}\\n\\n--- END OF CONTEXT ---\\n\\n" if context_content else ""

    # Step 1: Orchestrator analyzes the task and creates a plan
    orchestrator_agent = personas.get("orchestrator_agent", {})
    
    # Define the task planning function
    task_planning_function = {
        "name": "create_task_plan",
        "description": "Creates a plan for breaking down and executing a complex task",
        "parameters": {
            "type": "object",
            "properties": {
                "task_understanding": {
                    "type": "string",
                    "description": "Summary of the overall task and its requirements"
                },
                "subtasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "Unique identifier for the subtask"
                            },
                            "title": {
                                "type": "string",
                                "description": "Brief title of the subtask"
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed description of what the subtask involves"
                            },
                            "required_expertise": {
                                "type": "string",
                                "description": "Type of expertise needed for this subtask"
                            },
                            "priority": {
                                "type": "integer",
                                "description": "Priority order (1 being highest)"
                            },
                            "dependencies": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "IDs of subtasks that must be completed before this one"
                            }
                        },
                        "required": ["id", "title", "description", "required_expertise", "priority", "dependencies"]
                    },
                    "description": "List of subtasks that make up the overall task"
                },
                "execution_strategy": {
                    "type": "string",
                    "description": "Overall strategy for executing the task"
                }
            },
            "required": ["task_understanding", "subtasks", "execution_strategy"]
        }
    }
    
    # Load context and define prefix right before use - RESTORE
    context_content = load_context_content(settings.CONTEXT_FILE_PATH)
    logging.info(f"Attempting to load context from: {settings.CONTEXT_FILE_PATH}")
    context_prefix = f"{context_content}\\n\\n--- END OF CONTEXT ---\\n\\n" if context_content else ""
    # context_prefix = "" # Remove temporary empty string assignment
    
    # Prepare the orchestrator prompt - Restore context_prefix
    orchestrator_prompt = f"""{context_prefix}{generate_agent_context(orchestrator_agent)}
    
    USER QUERY: {user_query}
    
    Your task is to analyze this complex request and create a detailed plan for execution.
    You should:
    
    1. Understand the overall task and its requirements
    2. Break it down into logical subtasks
    3. Identify the type of expertise needed for each subtask
    4. Determine any dependencies between subtasks
    5. Create an execution strategy
    
    Be specific and detailed in your planning, as worker agents will execute 
    each subtask based on your instructions.
    """
    
    try:
        # Get task plan using function calling
        plan_response = await functions_client.generate_with_functions(
            orchestrator_prompt,
            [task_planning_function],
            function_call={"name": "create_task_plan"}
        )
        
        if plan_response["type"] == "function_call" and plan_response["name"] == "create_task_plan":
            task_plan = plan_response["arguments"]
        else:
            # Fallback if no function call was returned
            logging.warning("Task planning function call not returned, using default plan")
            task_plan = {
                "task_understanding": "Processing the user's request",
                "subtasks": [
                    {
                        "id": "subtask1",
                        "title": "General Processing",
                        "description": "Process the user query in a general way",
                        "required_expertise": "General Knowledge",
                        "priority": 1,
                        "dependencies": []
                    }
                ],
                "execution_strategy": "Execute the general processing subtask"
            }
    except Exception as e:
        logging.error(f"Error in task planning: {str(e)}")
        task_plan = {
            "task_understanding": f"Error occurred during planning: {str(e)}",
            "subtasks": [
                {
                    "id": "subtask1",
                    "title": "General Processing",
                    "description": "Process the user query in a general way",
                    "required_expertise": "General Knowledge",
                    "priority": 1,
                    "dependencies": []
                }
            ],
            "execution_strategy": "Execute the general processing subtask as a fallback"
        }
    
    # Record the orchestration step
    intermediate_steps.append(AgentResponse(
        agent_role="Task Coordinator",
        content=f"Task Understanding:\n{task_plan['task_understanding']}\n\n" +
                f"Execution Strategy:\n{task_plan['execution_strategy']}\n\n" +
                "Subtasks:\n" + "\n".join([
                    f"{i+1}. {st['title']} (Priority: {st['priority']}, Expertise: {st['required_expertise']})\n" +
                    f"   Description: {st['description']}\n" +
                    f"   Dependencies: {', '.join(st['dependencies']) if st['dependencies'] else 'None'}"
                    for i, st in enumerate(task_plan['subtasks'])
                ]),
        metadata=task_plan
    ))
    
    # Step 2: Execute subtasks in order of priority and dependencies
    worker_agent = personas.get("worker_agent", {})
    
    # Sort subtasks by priority and dependencies
    sorted_subtasks = sorted(task_plan["subtasks"], key=lambda x: x["priority"])
    
    # Create a mapping of subtask IDs to their results
    subtask_results = {}
    
    # Function to check if dependencies are satisfied
    def dependencies_satisfied(subtask):
        return all(dep_id in subtask_results for dep_id in subtask["dependencies"])
    
    # Process subtasks
    while sorted_subtasks:
        # Find all subtasks that can be executed in parallel (dependencies satisfied)
        executable_subtasks = [st for st in sorted_subtasks if dependencies_satisfied(st)]
        
        if not executable_subtasks:
            # If no subtasks can be executed, there might be a circular dependency
            logging.error("Circular dependency detected in subtasks")
            break
        
        # Execute these subtasks in parallel
        async def process_subtask(subtask):
            """Process an individual subtask"""
            # Prepare the worker prompt
            dependency_results = "\n\n".join([
                f"RESULT FROM {dep_id}:\n{subtask_results[dep_id]}"
                for dep_id in subtask["dependencies"]
            ])
            
            worker_prompt = f"""{generate_agent_context(worker_agent)}
            
            ORIGINAL USER QUERY: {user_query}
            
            OVERALL TASK: {task_plan['task_understanding']}
            
            CURRENT SUBTASK: {subtask['title']}
            SUBTASK DESCRIPTION: {subtask['description']}
            SUBTASK ID: {subtask['id']}
            
            {"DEPENDENCY RESULTS:\\n" + dependency_results if subtask["dependencies"] else ""}

            Your task is to execute this specific subtask based on the description provided.
            Provide a detailed and complete response for your assigned subtask.
            """

            try:
                # Get worker response
                worker_response = await llm_client.generate(worker_prompt, temperature=0.6)
                return {
                    "subtask_id": subtask["id"],
                    "title": subtask["title"],
                    "expertise": subtask["required_expertise"],
                    "response": worker_response
                }
            except Exception as e:
                logging.error(f"Error processing subtask {subtask['id']}: {str(e)}")
                return {
                    "subtask_id": subtask["id"],
                    "title": subtask["title"],
                    "expertise": subtask["required_expertise"],
                    "response": f"Error processing this subtask: {str(e)}"
                }
        
        # Process all executable subtasks in parallel
        current_results = await asyncio.gather(
            *[process_subtask(subtask) for subtask in executable_subtasks]
        )
        
        # Store results and record worker responses
        for result in current_results:
            subtask_results[result["subtask_id"]] = result["response"]
            intermediate_steps.append(AgentResponse(
                agent_role=f"{result['expertise']} Specialist",
                content=result["response"],
                metadata={
                    "subtask_id": result["subtask_id"],
                    "title": result["title"],
                    "expertise": result["expertise"]
                }
            ))
        
        # Remove processed subtasks from the list
        sorted_subtasks = [st for st in sorted_subtasks if st["id"] not in [r["subtask_id"] for r in current_results]]
    
    # Step 3: Synthesize results using the synthesizer agent
    synthesizer_agent = personas.get("synthesizer_agent", {})
    
    # Prepare the synthesizer prompt
    synthesizer_prompt = f"""{generate_agent_context(synthesizer_agent)}
    
    ORIGINAL USER QUERY: {user_query}
    
    TASK UNDERSTANDING: {task_plan['task_understanding']}
    
    EXECUTION STRATEGY: {task_plan['execution_strategy']}
    
    You have received results from multiple workers, each completing a specific subtask.
    Your task is to synthesize these results into a comprehensive, cohesive response that
    addresses the original query.
    
    The subtasks and their results are:
    
    {format_subtask_results(task_plan["subtasks"], subtask_results)}
    
    Please integrate these results into a unified, well-structured response that:
    1. Addresses all aspects of the original query
    2. Presents information in a logical, cohesive manner
    3. Resolves any contradictions or inconsistencies between subtask results
    4. Provides a complete solution to the user's request

    IMPORTANT:
    - Do NOT copy and paste worker outputs verbatim; write a fresh, synthesized narrative.
    - Avoid repeating the full subtask lists; integrate them into a single cohesive answer.
    - Start with a short executive summary, then detailed sections with clear headings.
    - Deduplicate overlapping points and ensure consistent terminology.
    """
    
    try:
        # Get synthesized response
        synthesized_response = await llm_client.generate(synthesizer_prompt, temperature=0.7)
    except Exception as e:
        logging.error(f"Error in result synthesis: {str(e)}")
        synthesized_response = "I apologize, but I encountered an issue while synthesizing the results. Here are the individual components:\n\n" + \
                               "\n\n".join([f"**{st['title']}**:\n{subtask_results.get(st['id'], 'No result available')}" 
                                          for st in task_plan["subtasks"]])
    
    # If the synthesized response is too similar to any single worker output, request a proper synthesis
    try:
        similarity_threshold = 0.92
        is_copy_like = False
        for st in task_plan["subtasks"]:
            worker_text = subtask_results.get(st["id"], "")
            if not worker_text:
                continue
            ratio = difflib.SequenceMatcher(None, synthesized_response, worker_text).ratio()
            if ratio >= similarity_threshold or synthesized_response.strip() in worker_text:
                is_copy_like = True
                break
        if is_copy_like:
            logging.info("Synthesized response appears too similar to a worker output; regenerating with stricter guidance")
            strict_prompt = synthesizer_prompt + "\n\nConstraints: Do not repeat worker text verbatim. Produce a distilled, integrated answer with your own wording, structured with headings, and limited redundancy."
            synthesized_response = await llm_client.generate(strict_prompt, temperature=0.6)
    except Exception as e:
        logging.warning(f"Post-synthesis validation failed: {str(e)}")

    # Record the synthesis step
    intermediate_steps.append(AgentResponse(
        agent_role="Results Integrator",
        content=synthesized_response,
        metadata={"subtask_count": len(task_plan["subtasks"])}
    ))
    
    return synthesized_response, intermediate_steps

def format_subtask_results(subtasks, results):
    """
    Format subtask results for the synthesizer prompt.

    Combines subtask metadata (title, description, expertise) with their execution results
    into a structured text format suitable for the synthesizer agent to process.

    Parameters:
    - subtasks (List[Dict]): List of subtask dictionaries containing metadata like title,
      description, and required_expertise.
    - results (Dict[str, str]): Mapping of subtask IDs to their execution results.

    Returns:
    - str: A formatted string containing all subtasks and their results, numbered and
      structured for easy parsing by the synthesizer.
    """
    formatted = ""
    for i, subtask in enumerate(subtasks, 1):
        formatted += f"SUBTASK {i}: {subtask['title']} ({subtask['required_expertise']})\n"
        formatted += f"DESCRIPTION: {subtask['description']}\n"
        formatted += f"RESULT:\n{results.get(subtask['id'], 'No result available')}\n\n"
    return formatted

def generate_agent_context(agent_persona: dict) -> str:
    """
    Generates a context prompt section based on an agent persona.

    Creates a formatted string that defines the agent's role, personality, function,
    and strengths. This context is prepended to prompts to guide the agent's behavior
    and responses.

    Parameters:
    - agent_persona (dict): The persona of the agent to generate context for. Expected keys:
      - role (str): The agent's role (e.g., "Task Coordinator")
      - persona (str): The agent's personality traits
      - description (str): Functional description of the agent
      - strengths (List[str]): List of the agent's key strengths

    Returns:
    - str: A formatted string representing the agent's context, or an empty string if
      no persona is provided.

    Example:
        >>> persona = {
        ...     "role": "Analyst",
        ...     "persona": "Detail-oriented and analytical",
        ...     "description": "Analyzes data and provides insights",
        ...     "strengths": ["Data analysis", "Pattern recognition"]
        ... }
        >>> context = generate_agent_context(persona)
        >>> print(context)
        === AGENT CONTEXT ===
        ROLE: Analyst
        ...
    """
    if not agent_persona:
        return ""
        
    role = agent_persona.get("role", "Assistant")
    persona = agent_persona.get("persona", "Helpful and knowledgeable")
    description = agent_persona.get("description", "Provides helpful responses")
    strengths = ", ".join(agent_persona.get("strengths", ["Assistance"]))
    
    return f"""
    === AGENT CONTEXT ===
    ROLE: {role}
    CHARACTER: {persona}
    FUNCTION: {description}
    STRENGTHS: {strengths}
    ==================
    
    You are acting as the {role}. Your personality is {persona}
    """