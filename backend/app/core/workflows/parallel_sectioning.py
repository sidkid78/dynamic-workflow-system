from app.models.schemas import WorkflowSelection, AgentResponse
from app.core.llm_client import get_llm_client, get_functions_client
from typing import Tuple, List, Dict, Any
import logging
import json
import asyncio

async def execute(workflow_selection: WorkflowSelection, user_query: str) -> Tuple[str, List[AgentResponse]]:
    """
    Executes a parallel sectioning workflow that breaks a task into independent subtasks
    and processes them in parallel
    """
    functions_client = get_functions_client()
    llm_client = get_llm_client()
    personas = workflow_selection.personas.get("parallel_sectioning", {})
    intermediate_steps = []
    
    # Step 1: Break down the task using the sectioning agent
    sectioning_agent = personas.get("sectioning_agent", {})
    
    # Define the task breakdown function
    task_breakdown_function = {
        "name": "break_into_subtasks",
        "description": "Breaks down a complex task into independent subtasks that can be processed in parallel",
        "parameters": {
            "type": "object",
            "properties": {
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
                            "perspective": {
                                "type": "string",
                                "description": "The perspective or angle from which to approach this subtask"
                            }
                        },
                        "required": ["id", "title", "description", "perspective"]
                    },
                    "description": "List of independent subtasks"
                },
                "reasoning": {
                    "type": "string",
                    "description": "Explanation of how the task was broken down"
                }
            },
            "required": ["subtasks", "reasoning"]
        }
    }
    
    # Prepare the sectioning prompt
    sectioning_prompt = f"""
    {generate_agent_context(sectioning_agent)}
    
    USER QUERY: {user_query}
    
    Your task is to break down this complex query into 3-5 independent subtasks that can be processed in parallel.
    Each subtask should:
    - Focus on a different aspect or perspective of the overall task
    - Be completely independent of the others (can be processed without depending on results from other subtasks)
    - Contribute meaningful insight to the overall task
    
    For example, if the query is about analyzing a business strategy, subtasks might include:
    - Analyzing market trends and competition
    - Evaluating financial implications
    - Assessing operational feasibility
    - Considering customer impact
    """
    
    try:
        # Get task breakdown using function calling
        breakdown_response = await functions_client.generate_with_functions(
            sectioning_prompt,
            [task_breakdown_function],
            function_call={"name": "break_into_subtasks"},
            temperature=0.5
        )
        
        if breakdown_response["type"] == "function_call" and breakdown_response["name"] == "break_into_subtasks":
            task_breakdown = breakdown_response["arguments"]
        else:
            # Fallback if no function call was returned
            logging.warning("Task breakdown function call not returned, using default breakdown")
            task_breakdown = {
                "subtasks": [
                    {
                        "id": "subtask1",
                        "title": "General Analysis",
                        "description": "Analyze the general aspects of the query",
                        "perspective": "Overall perspective"
                    }
                ],
                "reasoning": "Fallback breakdown due to unexpected response format"
            }
    except Exception as e:
        logging.error(f"Error in task breakdown: {str(e)}")
        task_breakdown = {
            "subtasks": [
                {
                    "id": "subtask1",
                    "title": "General Analysis",
                    "description": "Analyze the general aspects of the query",
                    "perspective": "Overall perspective"
                }
            ],
            "reasoning": f"Fallback breakdown due to error: {str(e)}"
        }
    
    # Record the sectioning step
    intermediate_steps.append(AgentResponse(
        agent_role="Task Divider",
        content=f"Task Breakdown:\n{task_breakdown['reasoning']}\n\nSubtasks:\n" + 
                "\n".join([f"- {st['title']}: {st['description']} (From {st['perspective']} perspective)" 
                           for st in task_breakdown['subtasks']]),
        metadata=task_breakdown
    ))
    
    # Step 2: Process subtasks in parallel using worker agents
    section_worker_agent = personas.get("section_worker_agent", {})
    
    async def process_subtask(subtask):
        """Process an individual subtask"""
        # Prepare the worker prompt
        worker_prompt = f"""
        {generate_agent_context(section_worker_agent)}
        
        ORIGINAL USER QUERY: {user_query}
        
        SUBTASK: {subtask['title']}
        DESCRIPTION: {subtask['description']}
        PERSPECTIVE: {subtask['perspective']}
        
        Your task is to focus exclusively on addressing this specific subtask from the given perspective.
        Provide a thorough analysis or response focused only on this aspect of the overall query.
        """
        
        try:
            # Get worker response
            worker_response = await llm_client.generate(worker_prompt, temperature=0.7)
            return {
                "subtask_id": subtask["id"],
                "title": subtask["title"],
                "perspective": subtask["perspective"],
                "response": worker_response
            }
        except Exception as e:
            logging.error(f"Error processing subtask {subtask['id']}: {str(e)}")
            return {
                "subtask_id": subtask["id"],
                "title": subtask["title"],
                "perspective": subtask["perspective"],
                "response": f"Error processing this subtask: {str(e)}"
            }
    
    # Process all subtasks in parallel
    subtask_results = await asyncio.gather(
        *[process_subtask(subtask) for subtask in task_breakdown["subtasks"]]
    )
    
    # Record the worker responses
    for result in subtask_results:
        intermediate_steps.append(AgentResponse(
            agent_role=f"{result['perspective']} Specialist",
            content=result["response"],
            metadata={
                "subtask_id": result["subtask_id"],
                "title": result["title"],
                "perspective": result["perspective"]
            }
        ))
    
    # Step 3: Aggregate results using the aggregator agent
    aggregator_agent = personas.get("aggregator_agent", {})
    
    # Prepare the aggregator prompt
    aggregator_prompt = f"""
    {generate_agent_context(aggregator_agent)}
    
    ORIGINAL USER QUERY: {user_query}
    
    You have received responses from multiple specialists, each analyzing a different aspect of the query.
    Your task is to synthesize these perspectives into a comprehensive, cohesive response.
    
    The subtasks and their responses are:
    
    {format_subtask_results(subtask_results)}
    
    Please integrate these perspectives into a unified, well-structured response that addresses the original query comprehensively.
    Make sure to maintain cohesion between the different perspectives and avoid redundancy.
    """
    
    try:
        # Get aggregated response
        aggregated_response = await llm_client.generate(aggregator_prompt, temperature=0.7)
    except Exception as e:
        logging.error(f"Error in result aggregation: {str(e)}")
        aggregated_response = "I apologize, but I encountered an issue while synthesizing the analysis. Here are the individual perspectives:\n\n" + \
                             "\n\n".join([f"**{r['title']} ({r['perspective']})**: {r['response']}" for r in subtask_results])
    
    # Record the aggregation step
    intermediate_steps.append(AgentResponse(
        agent_role="Results Integrator",
        content=aggregated_response,
        metadata={"subtask_count": len(subtask_results)}
    ))
    
    return aggregated_response, intermediate_steps

def format_subtask_results(results: List[Dict[str, Any]]) -> str:
    """Format subtask results for the aggregator prompt"""
    formatted = ""
    for i, result in enumerate(results, 1):
        formatted += f"SUBTASK {i}: {result['title']} (From {result['perspective']} perspective)\n"
        formatted += f"RESPONSE:\n{result['response']}\n\n"
    return formatted

def generate_agent_context(agent_persona: dict) -> str:
    """
    Generates a context prompt section based on an agent persona
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