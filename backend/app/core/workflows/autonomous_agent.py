# app/core/workflows/autonomous_agent.py
from app.models.schemas import WorkflowSelection, AgentResponse
from app.core.llm_client import get_llm_client, get_functions_client
from typing import Tuple, List, Dict, Any, Optional
import logging
import json
import asyncio

class ToolDefinition:
    """
    Definition of a tool available to the autonomous agent
    """
    def __init__(self, name: str, description: str, parameters: Dict[str, Any] = None, function=None):
        self.name = name
        self.description = description
        self.parameters = parameters or {}
        self.function = function
        
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for use in prompts"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }

async def execute(
    workflow_selection: WorkflowSelection, 
    user_query: str,
    max_iterations: int = 10,
    available_tools: List[ToolDefinition] = None
) -> Tuple[str, List[AgentResponse]]:
    """
    Executes an autonomous agent workflow that can plan, act, and reflect on its actions
    in a loop until the task is complete.
    
    This is a more advanced workflow that gives the agent significant autonomy to:
    1. Plan its approach to solving the task
    2. Take actions through tools to gather information or make changes
    3. Reflect on progress and decide next steps
    4. Loop until the task is determined to be complete
    
    Args:
        workflow_selection: The workflow selection object
        user_query: The user's request
        max_iterations: Maximum number of plan-act-reflect cycles to execute
        available_tools: List of tools the agent can use
        
    Returns:
        A tuple containing the final response and a list of intermediate steps
    """
    functions_client = get_functions_client()
    llm_client = get_llm_client()
    personas = workflow_selection.personas.get("autonomous_agent", {})
    intermediate_steps = []
    
    # Use default tools if none provided
    available_tools = available_tools or []
    
    # Initialize memory for the agent to store information between iterations
    agent_memory = {
        "task": user_query,
        "tools": [tool.dict() for tool in available_tools],
        "iterations": [],
        "observations": [],
        "task_complete": False
    }
    
    # Define planning function
    planning_function = {
        "name": "create_task_plan",
        "description": "Creates a plan for how to accomplish the given task",
        "parameters": {
            "type": "object",
            "properties": {
                "task_understanding": {
                    "type": "string",
                    "description": "Detailed understanding of the task requirements"
                },
                "plan_steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "step_number": {
                                "type": "integer",
                                "description": "The step number in the plan"
                            },
                            "step_description": {
                                "type": "string",
                                "description": "Description of what this step will accomplish"
                            },
                            "required_tools": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "Tools needed for this step"
                            }
                        },
                        "required": ["step_number", "step_description"]
                    },
                    "description": "Ordered steps to accomplish the task"
                },
                "expected_outcome": {
                    "type": "string",
                    "description": "What success looks like for this task"
                }
            },
            "required": ["task_understanding", "plan_steps", "expected_outcome"]
        }
    }
    
    # Define action function
    action_function = {
        "name": "execute_action",
        "description": "Executes an action or tool to work toward task completion",
        "parameters": {
            "type": "object",
            "properties": {
                "action_type": {
                    "type": "string",
                    "enum": ["use_tool", "reasoning", "intermediate_result", "final_result"],
                    "description": "Type of action to take"
                },
                "tool_name": {
                    "type": "string",
                    "description": "Name of the tool to use (if action_type is use_tool)"
                },
                "tool_parameters": {
                    "type": "object",
                    "description": "Parameters to pass to the tool (if action_type is use_tool)"
                },
                "reasoning": {
                    "type": "string",
                    "description": "Reasoning about the current state (if action_type is reasoning)"
                },
                "result": {
                    "type": "string",
                    "description": "Intermediate or final result (if action_type is intermediate_result or final_result)"
                }
            },
            "required": ["action_type"]
        }
    }
    
    # Define reflection function
    reflection_function = {
        "name": "reflect_on_progress",
        "description": "Evaluates progress toward task completion and decides next steps",
        "parameters": {
            "type": "object",
            "properties": {
                "progress_assessment": {
                    "type": "string",
                    "description": "Assessment of current progress toward the goal"
                },
                "completed_steps": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "description": "Which steps of the plan have been completed"
                },
                "unexpected_observations": {
                    "type": "string",
                    "description": "Any unexpected findings or obstacles encountered"
                },
                "task_complete": {
                    "type": "boolean",
                    "description": "Whether the overall task is now complete"
                },
                "next_step": {
                    "type": "string",
                    "description": "Description of the next step to take (if task is not complete)"
                }
            },
            "required": ["progress_assessment", "task_complete"]
        }
    }
    
    # Main loop for the autonomous agent
    iteration = 0
    while iteration < max_iterations and not agent_memory["task_complete"]:
        iteration += 1
        logging.info(f"Starting iteration {iteration} of autonomous agent")
        
        # Step 1: Planning Phase
        planner_agent = personas.get("planner_agent", {})
        
        # Prepare the history context
        history_context = ""
        if agent_memory["iterations"]:
            history_context = "Previous iterations:\n" + "\n".join([
                f"Iteration {i+1}:\n"
                f"Plan: {memory.get('plan', 'No plan')}\n"
                f"Action: {memory.get('action', 'No action')}\n"
                f"Observation: {memory.get('observation', 'No observation')}\n"
                f"Reflection: {memory.get('reflection', 'No reflection')}\n"
                for i, memory in enumerate(agent_memory["iterations"])
            ])
        
        # Create the planning prompt
        planning_prompt = f"""
        {generate_agent_context(planner_agent)}
        
        TASK: {user_query}
        
        {history_context}
        
        Available tools:
        {json.dumps([tool.dict() for tool in available_tools], indent=2)}
        
        Your task is to create a detailed plan for accomplishing the user's request.
        Think carefully about the steps needed, which tools might be useful at each step,
        and what success looks like for this task.
        
        If this is not the first iteration, consider what has been learned in previous
        iterations and adjust your plan accordingly.
        """
        
        try:
            # Get planning response using function calling
            planning_response = await functions_client.generate_with_functions(
                planning_prompt,
                [planning_function],
                function_call={"name": "create_task_plan"}
            )
            
            if planning_response["type"] == "function_call" and planning_response["name"] == "create_task_plan":
                plan = planning_response["arguments"]
            else:
                # Fallback if no function call was returned
                logging.warning("Planning function call not returned, using default plan")
                plan = {
                    "task_understanding": "Processing the user request",
                    "plan_steps": [
                        {
                            "step_number": 1,
                            "step_description": "Process the query directly",
                            "required_tools": []
                        }
                    ],
                    "expected_outcome": "A response to the user's query"
                }
        except Exception as e:
            logging.error(f"Error in planning phase: {str(e)}")
            plan = {
                "task_understanding": f"Error occurred during planning: {str(e)}",
                "plan_steps": [
                    {
                        "step_number": 1,
                        "step_description": "Process the user query in a general way",
                        "required_tools": []
                    }
                ],
                "expected_outcome": "A best-effort response to the user's query"
            }
        
        # Store the plan in memory
        current_iteration = {
            "plan": plan
        }
        agent_memory["iterations"].append(current_iteration)
        
        # Record the planning step
        intermediate_steps.append(AgentResponse(
            agent_role="Task Planner",
            content=f"Task Understanding:\n{plan['task_understanding']}\n\n" +
                    f"Expected Outcome:\n{plan['expected_outcome']}\n\n" +
                    "Plan:\n" + "\n".join([
                        f"{step['step_number']}. {step['step_description']}" +
                        (f" (Tools: {', '.join(step['required_tools'])})" if step.get('required_tools') else "")
                        for step in plan['plan_steps']
                    ]),
            metadata=plan
        ))
        
        # Step 2: Acting Phase
        actor_agent = personas.get("actor_agent", {})
        
        # Prepare the actor prompt
        actor_prompt = f"""
        {generate_agent_context(actor_agent)}
        
        TASK: {user_query}
        
        Current Plan:
        {json.dumps(plan, indent=2)}
        
        Previous Observations:
        {json.dumps(agent_memory["observations"], indent=2)}
        
        Available tools:
        {json.dumps([tool.dict() for tool in available_tools], indent=2)}
        
        Your task is to execute the next appropriate step in the plan.
        You can use available tools, perform reasoning, or generate intermediate or final results.
        
        Think step-by-step and take the most appropriate action to move closer to completing the task.
        """
        
        try:
            # Get action response using function calling
            action_response = await functions_client.generate_with_functions(
                actor_prompt,
                [action_function],
                function_call={"name": "execute_action"}
            )
            
            if action_response["type"] == "function_call" and action_response["name"] == "execute_action":
                action = action_response["arguments"]
            else:
                # Fallback if no function call was returned
                logging.warning("Action function call not returned, using default action")
                action = {
                    "action_type": "reasoning",
                    "reasoning": "Unable to determine the best action, proceeding with general processing."
                }
        except Exception as e:
            logging.error(f"Error in action phase: {str(e)}")
            action = {
                "action_type": "reasoning",
                "reasoning": f"Error occurred during action selection: {str(e)}"
            }
        
        # Process the action
        observation = "No observation recorded."
        
        if action["action_type"] == "use_tool":
            tool_name = action.get("tool_name", "")
            tool_parameters = action.get("tool_parameters", {})
            
            # Try to find and execute the tool
            tool_found = False
            for tool in available_tools:
                if tool.name == tool_name and tool.function:
                    try:
                        # Execute the tool
                        observation = await tool.function(**tool_parameters)
                        tool_found = True
                    except Exception as e:
                        observation = f"Error executing tool {tool_name}: {str(e)}"
                        logging.error(observation)
                    break
                    
            if not tool_found:
                observation = f"Tool '{tool_name}' not found or not executable."
        elif action["action_type"] == "reasoning":
            observation = f"Reasoning: {action.get('reasoning', 'No reasoning provided.')}"
        elif action["action_type"] in ["intermediate_result", "final_result"]:
            observation = f"Result: {action.get('result', 'No result provided.')}"
            
            # If this is a final result, we'll consider the task complete
            if action["action_type"] == "final_result":
                agent_memory["task_complete"] = True
        
        # Store the action and observation in memory
        current_iteration["action"] = action
        current_iteration["observation"] = observation
        agent_memory["observations"].append(observation)
        
        # Record the action step
        intermediate_steps.append(AgentResponse(
            agent_role="Action Executor",
            content=format_action_content(action, observation),
            metadata={
                "action": action,
                "observation": observation
            }
        ))
        
        # If we've reached a final result, skip the reflection phase
        if action["action_type"] == "final_result":
            final_response = action.get("result", "Task completed successfully.")
            break
            
        # Step 3: Reflection Phase
        reflector_agent = personas.get("reflector_agent", {})
        
        # Prepare the reflection prompt
        reflection_prompt = f"""
        {generate_agent_context(reflector_agent)}
        
        TASK: {user_query}
        
        Current Plan:
        {json.dumps(plan, indent=2)}
        
        Recent Action:
        {json.dumps(action, indent=2)}
        
        Observation from Action:
        {observation}
        
        Previous Iterations:
        {json.dumps(agent_memory["iterations"], indent=2)}
        
        Your task is to reflect on the current progress toward completing the overall task.
        Evaluate what has been accomplished, what steps have been completed, and what remains to be done.
        Determine if the task is now complete or what should be the next steps.
        """
        
        try:
            # Get reflection response using function calling
            reflection_response = await functions_client.generate_with_functions(
                reflection_prompt,
                [reflection_function],
                function_call={"name": "reflect_on_progress"}
            )
            
            if reflection_response["type"] == "function_call" and reflection_response["name"] == "reflect_on_progress":
                reflection = reflection_response["arguments"]
            else:
                # Fallback if no function call was returned
                logging.warning("Reflection function call not returned, using default reflection")
                reflection = {
                    "progress_assessment": "Unable to assess progress accurately.",
                    "completed_steps": [],
                    "unexpected_observations": "None",
                    "task_complete": False,
                    "next_step": "Continue with the next step in the plan."
                }
        except Exception as e:
            logging.error(f"Error in reflection phase: {str(e)}")
            reflection = {
                "progress_assessment": f"Error occurred during reflection: {str(e)}",
                "completed_steps": [],
                "task_complete": False,
                "next_step": "Continue with the next step in the plan despite the error."
            }
        
        # Update task completion status
        agent_memory["task_complete"] = reflection.get("task_complete", False)
        
        # Store the reflection in memory
        current_iteration["reflection"] = reflection
        
        # Record the reflection step
        intermediate_steps.append(AgentResponse(
            agent_role="Progress Reflector",
            content=f"Progress Assessment:\n{reflection['progress_assessment']}\n\n" +
                    f"Completed Steps: {', '.join(map(str, reflection.get('completed_steps', [])))} of {len(plan['plan_steps'])}\n\n" +
                    (f"Unexpected Observations:\n{reflection.get('unexpected_observations', 'None')}\n\n" if reflection.get('unexpected_observations') else "") +
                    f"Task Complete: {'Yes' if reflection.get('task_complete', False) else 'No'}\n\n" +
                    (f"Next Step: {reflection.get('next_step', 'None specified')}" if not reflection.get('task_complete', False) else ""),
            metadata=reflection
        ))
        
        # Check if task is complete
        if agent_memory["task_complete"]:
            logging.info(f"Task marked as complete after {iteration} iterations")
            break
    
    # Generate final response
    if not agent_memory["task_complete"]:
        logging.warning(f"Maximum iterations ({max_iterations}) reached without task completion")
        
    # Find the most recent result (either final or intermediate)
    final_response = "Task processed, but no specific result was generated."
    for iteration_data in reversed(agent_memory["iterations"]):
        action = iteration_data.get("action", {})
        if action.get("action_type") in ["final_result", "intermediate_result"]:
            final_response = action.get("result", final_response)
            break
    
    # If we haven't found any result, generate a summary response
    if final_response == "Task processed, but no specific result was generated.":
        summary_prompt = f"""
        TASK: {user_query}
        
        EXECUTION HISTORY:
        {json.dumps(agent_memory["iterations"], indent=2)}
        
        Based on the above execution history, please provide a comprehensive summary
        of the findings and results to address the user's original request.
        """
        
        try:
            final_response = await llm_client.generate(summary_prompt, temperature=0.7)
        except Exception as e:
            logging.error(f"Error generating summary response: {str(e)}")
            final_response += f" Error generating summary: {str(e)}"
    
    # Add a final summary step
    intermediate_steps.append(AgentResponse(
        agent_role="Task Summarizer",
        content=f"Summary of execution:\n" +
                f"- Completed {iteration} iterations\n" +
                f"- Task complete: {'Yes' if agent_memory['task_complete'] else 'No'}\n" +
                f"- Final response generated",
        metadata={
            "iterations": iteration,
            "task_complete": agent_memory["task_complete"],
            "memory": agent_memory
        }
    ))
    
    return final_response, intermediate_steps

def format_action_content(action, observation):
    """Format the action content for display"""
    if action["action_type"] == "use_tool":
        return (
            f"Tool Used: {action.get('tool_name', 'Unknown')}\n\n"
            f"Parameters: {json.dumps(action.get('tool_parameters', {}), indent=2)}\n\n"
            f"Observation: {observation}"
        )
    elif action["action_type"] == "reasoning":
        return (
            f"Reasoning:\n{action.get('reasoning', 'No reasoning provided.')}\n\n"
            f"Observation: {observation}"
        )
    elif action["action_type"] in ["intermediate_result", "final_result"]:
        return (
            f"{'Final' if action['action_type'] == 'final_result' else 'Intermediate'} Result:\n"
            f"{action.get('result', 'No result provided.')}\n\n"
            f"Observation: {observation}"
        )
    else:
        return f"Unknown action type: {action['action_type']}\n\nObservation: {observation}"

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