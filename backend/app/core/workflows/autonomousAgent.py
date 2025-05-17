# """
# Autonomous Agent Module

# This module implements an autonomous agent workflow system that can independently plan, execute, and adapt to complete complex tasks with minimal human intervention.

# The agent follows a cognitive cycle of:
# 1. Perception - Gathering information from the environment
# 2. Reasoning - Processing and analyzing information
# 3. Planning - Developing action strategies
# 4. Execution - Carrying out planned actions
# 5. Reflection - Evaluating outcomes and learning
# 6. Communication - Reporting progress and results (when needed)

# Key Components:
# - _build_autonomous_agent: Constructs the agent's workflow definition with role-specific tools
# - execute_autonomous_agent: Executes the agent workflow through iterative cognitive cycles

# The agent uses a tool-based architecture where different cognitive roles have access to specific tools based on their function. Tools are filtered and assigned based on keyword matching to ensure appropriate capabilities for each role.

# Example:
#     workflow_selection = WorkflowSelection(...)
#     user_query = "Analyze market trends and create a summary report"
#     session_id = "123"
#     response = await execute_autonomous_agent(workflow_selection, user_query, session_id)

# Dependencies:
#     - app.models.schemas: WorkflowSelection, AgentResponse, WorkflowResponse, ToolDefinition
#     - app.core.llm_client: LLM client for function calling
#     - app.tools.registry: Tool registry and management
# """

# from typing import List, Dict, Any, Tuple, Optional
# import logging
# import json
# import asyncio
# import time # For processing_time
# import os
# from datetime import datetime

# from app.models.schemas import WorkflowSelection, AgentResponse, WorkflowResponse, ToolDefinition
# from app.core.llm_client import get_functions_client # Assuming this is AzureOpenAIFunctions
# from app.tools.registry import get_all_tools # To get all registered ToolDefinition objects

# # Set up logging
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

# # Create logs directory if it doesn't exist
# log_dir = "logs/autonomous_agent"
# os.makedirs(log_dir, exist_ok=True)

# # Create file handler
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# log_file = f"{log_dir}/agent_{timestamp}.log"
# file_handler = logging.FileHandler(log_file)
# file_handler.setLevel(logging.DEBUG)

# # Create console handler
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)

# # Create formatter
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(formatter)
# console_handler.setFormatter(formatter)

# # Add handlers to logger
# logger.addHandler(file_handler)
# logger.addHandler(console_handler)

# # Create conversation log directory
# conversation_dir = "logs/autonomous_agent/conversations"
# os.makedirs(conversation_dir, exist_ok=True)

# MAX_AGENT_ITERATIONS = 10 # Define a max number of cycles for the agent

# def save_conversation(session_id: str, role: str, content: str, metadata: Dict = None):
#     """Save conversation turn to file"""
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     conversation_file = f"{conversation_dir}/{session_id}_{timestamp}.jsonl"
    
#     conversation_entry = {
#         "timestamp": timestamp,
#         "role": role,
#         "content": content,
#         "metadata": metadata or {}
#     }
    
#     with open(conversation_file, "a") as f:
#         f.write(json.dumps(conversation_entry) + "\n")
        
#     logger.debug(f"Saved conversation entry to {conversation_file}")

# def _build_autonomous_agent(self, task_description: str, tools: List[ToolDefinition]) -> dict: 
#     """
#     Build an autonomous agent workflow that can independently plan, execute, and adapt to complete complex tasks with minimal human intervention.
#     """
#     logger.info(f"Building autonomous agent for task: {task_description}")
#     logger.debug(f"Number of available tools: {len(tools)}")
    
#     all_tools_dict = [tool.dict() for tool in tools]

#     # Keyword-based tool filtering
#     perception_keywords = ['search', 'web', 'browse', 'scrape', 'crawl', 'gather', 'read', 'list', 'metadata', 'observe', 'url', 'weather']
#     reasoning_keywords = ['analyze', 'infer', 'pattern', 'knowledge', 'evaluate', 'compare', 'reason', 'hypothesize', 'deduce']
#     planning_keywords = ['plan', 'schedule', 'dependency', 'strategize', 'organize', 'risk', 'goal']
#     # Execution needs broad access to act
#     reflection_keywords = ['evaluate', 'compare', 'learn', 'meta', 'review', 'assess', 'reflect', 'critique', 'improve']
#     communication_keywords = ['summarize', 'visualize', 'report', 'explain', 'communicate', 'present', 'notify']

#     perception_tools = [t for t in all_tools_dict if any(kw in t.get('name', '').lower() for kw in perception_keywords)]
#     reasoning_tools = [t for t in all_tools_dict if any(kw in t.get('name', '').lower() for kw in reasoning_keywords)]
#     planning_tools = [t for t in all_tools_dict if any(kw in t.get('name', '').lower() for kw in planning_keywords)]
#     execution_tools = all_tools_dict # Give execution access to all available tools
#     reflection_tools = [t for t in all_tools_dict if any(kw in t.get('name', '').lower() for kw in reflection_keywords)]
#     communication_tools = [t for t in all_tools_dict if any(kw in t.get('name', '').lower() for kw in communication_keywords)]

#     logger.debug(f"Tools assigned per role: Perception: {len(perception_tools)}, Reasoning: {len(reasoning_tools)}, Planning: {len(planning_tools)}, Execution: {len(execution_tools)}, Reflection: {len(reflection_tools)}, Communication: {len(communication_tools)}")

#     agent_definition = {
#         "type": "autonomous_agent",
#         # Define the core roles in the typical agent loop
#         "loop_roles": ["perception", "reasoning", "planning", "execution", "reflection"],
#         "communication_role": "communication", # Separate role, potentially triggered
#         "steps": [
#             {
#                 "role": "perception",
#                 "prompt": f"Based on the overall task '{task_description}' and the current state of the world/task [Current World Model/State], use your tools to gather the most relevant new information. Update the world model with your findings.",
#                 "tools": perception_tools,
#                 "capabilities": [
#                     "Information gathering from multiple sources",
#                     "Context analysis and understanding",
#                     "Identification of relevant constraints and resources",
#                     "Detection of ambiguities requiring clarification"
#                 ]
#             },
#             {
#                 "role": "reasoning",
#                 "prompt": f"Process the updated information [Perceived Information from Perception Step] in the context of the overall task '{task_description}' and current plan [Current Plan]. Identify patterns, draw inferences, evaluate options, and formulate hypotheses or conclusions to guide planning. Update the agent's understanding.",
#                 "tools": reasoning_tools,
#                 "reasoning_frameworks": [
#                     "Deductive reasoning",
#                     "Inductive reasoning",
#                     "Abductive reasoning",
#                     "Causal reasoning",
#                     "Analogical reasoning"
#                 ]
#             },
#             {
#                 "role": "planning",
#                 "prompt": f"Based on the current understanding [Reasoned Understanding from Reasoning Step] and the overall task '{task_description}', develop or refine a comprehensive, adaptable plan to achieve the objectives. Define the next concrete action(s). Output the updated plan and the next action(s).",
#                 "tools": planning_tools,
#                 "planning_aspects": [
#                     "Goal decomposition into achievable subgoals",
#                     "Resource allocation and optimization",
#                     "Action sequencing and prioritization",
#                     "Contingency planning for identified risks",
#                     "Success criteria definition"
#                 ]
#             },
#             {
#                 "role": "execution",
#                 "prompt": f"Implement the next action(s) specified in the current plan: [Next Action(s) from Planning Step]. Use the available tools to perform the action(s). Monitor the immediate outcome and report the result.",
#                 "tools": execution_tools,
#                 "execution_capabilities": [
#                     "Tool selection and utilization",
#                     "Sequential and parallel task execution",
#                     "Progress tracking against plan",
#                     "Real-time problem solving",
#                     "Resource utilization optimization"
#                 ]
#             },
#             {
#                 "role": "reflection",
#                 "prompt": f"Evaluate the outcome of the last action(s) [Execution Outcome from Execution Step] in relation to the plan [Current Plan] and the overall task '{task_description}'. Assess success, failures, and learning opportunities. Update the agent's knowledge and suggest improvements to strategy or plan for the next cycle. Determine if communication is needed.",
#                 "tools": reflection_tools,
#                 "reflection_processes": [
#                     "Success and failure analysis",
#                     "Strategy effectiveness assessment",
#                     "Knowledge and capability gap identification",
#                     "Learning integration for future cycles",
#                     "Self-improvement opportunity identification"
#                 ]
#             },
#             {
#                 # This step might be triggered conditionally based on reflection or external events
#                 "role": "communication", 
#                 "prompt": f"Based on the current status, progress, recent reflections [Reflection Insights], or specific triggers, report relevant information (progress, results, insights, issues, recommendations) regarding the task '{task_description}' in a clear, actionable format. Target audience: [Specify Audience, e.g., User, Log].",
#                 "tools": communication_tools,
#                 "communication_objectives": [
#                     "Status reporting at appropriate intervals",
#                     "Clear presentation of findings and results",
#                     "Explanation of reasoning and decisions",
#                     "Highlighting of key insights and implications",
#                     "Recommendation formulation for next steps or completion"
#                 ]
#             }
#             # Note: The execution engine manages the loop:
#             # 1. Initialize state (world model, plan, etc.) based on task_description.
#             # 2. Loop starts (until task completion, error, or max iterations):
#             #    a. Call perception(state) -> updated_state, perceived_info
#             #    b. Call reasoning(state, perceived_info) -> reasoned_understanding
#             #    c. Call planning(state, reasoned_understanding) -> updated_plan, next_action
#             #    d. Call execution(next_action) -> execution_outcome
#             #    e. Call reflection(state, execution_outcome) -> learnings, updated_state, trigger_communication?
#             #    f. If trigger_communication?: Call communication(state, learnings)
#             # 3. Final result is derived from the agent's state upon loop termination.
#         ],
#         "metadata": {
#             "description": "Defines a cyclical autonomous agent capable of perception, reasoning, planning, execution, reflection, and communication.",
#             "autonomy_level": { # Suggestions for the execution engine
#                 "decision_making": "high",
#                 "tool_selection": "full",
#                 "goal_refinement": "adaptive",
#                 "human_intervention_points": ["critical_decisions", "ethical_dilemmas", "high_risk_actions"]
#             },
#             "memory_system": { # Suggestions for the execution engine
#                 "working_memory": "active_task_context",
#                 "episodic_memory": "previous_actions_and_outcomes",
#                 "semantic_memory": "domain_knowledge_and_learnings",
#                 "memory_consolidation": True
#             },
#             "adaptation_mechanisms": { # Suggestions for the execution engine
#                 "strategy_adjustment": "continuous",
#                 "learning_from_feedback": True,
#                 "environmental_responsiveness": "high",
#                 "goal_reprioritization": "context_sensitive"
#             },
#             "safety_protocols": { # Suggestions for the execution engine
#                 "action_verification": "pre_execution_check",
#                 "impact_assessment": "required_for_high_risk_actions",
#                 "rollback_capability": True,
#                 "ethical_guidelines_enforcement": True,
#                 "boundary_condition_monitoring": "continuous"
#             },
#             "performance_metrics": { # Suggestions for the execution engine
#                 "task_completion_quality": "comprehensive",
#                 "resource_efficiency": "optimized",
#                 "time_to_completion": "tracked",
#                 "adaptation_effectiveness": "measured",
#                 "learning_curve": "monitored"
#             }
#         }
#     }

#     logger.info("Successfully built autonomous agent definition")
#     return agent_definition

# async def execute_autonomous_agent(
#     workflow_selection: WorkflowSelection,
#     user_query: str,
#     session_id: str # Or get it from workflow_selection if available/needed
# ) -> WorkflowResponse:
#     """
#     Executes the autonomous agent workflow.
#     The agent will perceive, reason, plan, execute actions (potentially using tools),
#     and reflect, iterating until the task is complete or limits are reached.
#     """
#     start_time = time.time()
#     logger.info(f"Starting autonomous agent execution for session {session_id}")
#     logger.info(f"User query: {user_query}")
    
#     llm_client = get_functions_client() # The client that supports "functions" parameter

#     # 1. Setup and Initialization
#     intermediate_steps: List[AgentResponse] = []
#     agent_state: Dict[str, Any] = {
#         "task_description": user_query,
#         "world_model": {}, # Agent's understanding of the current state
#         "current_plan": None, # Agent's plan
#         "history": [], # History of actions, observations, tool uses
#         "last_action_outcome": None,
#         "learnings": [],
#         "communication_log": []
#     }

#     # Get all available tools from the registry
#     # get_all_tools() from registry returns Dict[str, ToolDefinition]
#     all_registered_tools: Dict[str, ToolDefinition] = get_all_tools()
#     available_tool_definitions: List[ToolDefinition] = list(all_registered_tools.values())

#     if not available_tool_definitions:
#         logger.warning("Autonomous agent started with NO tools available from the registry.")

#     # Build the agent's structural definition using the provided function
#     # _build_autonomous_agent expects List[ToolDefinition]
#     agent_definition = _build_autonomous_agent(self=None, task_description=user_query, tools=available_tool_definitions) # Assuming 'self' is not strictly needed if it's a static method or can be omitted.

#     # Initial message to record the setup
#     initial_message = f"Autonomous agent initialized for task: {user_query}. Structure: {agent_definition['type']}. Loop roles: {agent_definition['loop_roles']}"
#     intermediate_steps.append(AgentResponse(
#         agent_role="System",
#         content=initial_message,
#         metadata={"initial_agent_definition": agent_definition}
#     ))
#     save_conversation(session_id, "System", initial_message, {"type": "initialization"})

#     final_response_content = "Agent processing did not complete."

#     try:
#         # 2. Agent Execution Loop
#         for iteration in range(MAX_AGENT_ITERATIONS):
#             agent_state["current_iteration"] = iteration + 1
#             logger.info(f"Agent Iteration {iteration + 1}/{MAX_AGENT_ITERATIONS}")
#             iteration_start_msg = f"Starting iteration {iteration + 1}."
#             intermediate_steps.append(AgentResponse(agent_role="System", content=iteration_start_msg))
#             save_conversation(session_id, "System", iteration_start_msg, {"type": "iteration_start", "iteration": iteration + 1})

#             for role_step_config in agent_definition["steps"]:
#                 current_role_name = role_step_config["role"]

#                 # Skip communication role in the main loop, handle it separately if triggered
#                 if current_role_name == agent_definition.get("communication_role"):
#                     continue

#                 logger.info(f"Executing role: {current_role_name}")

#                 # Prepare prompt for the current role
#                 # This needs to be more dynamic, incorporating agent_state
#                 prompt_template = role_step_config["prompt"]
#                 # Simple state injection for now, can be made more sophisticated
#                 current_prompt = f"{prompt_template}\\n\\nCURRENT AGENT STATE:\\n{json.dumps(agent_state, indent=2, default=str)}"

#                 # Get tools for the current role (already in OpenAI dict format)
#                 # These are dicts, not ToolDefinition objects
#                 role_specific_tools_dict_list: List[Dict[str, Any]] = role_step_config.get("tools", [])

#                 # Log the tools being provided to the LLM for this step
#                 tool_names_for_role = [t.get('name', 'unknown_tool') for t in role_specific_tools_dict_list]
#                 logger.debug(f"Role '{current_role_name}' has access to tools: {tool_names_for_role}")
                
#                 step_prep_msg = f"Preparing to execute. Prompt (first 100 chars): {current_prompt[:100]}... Tools: {tool_names_for_role}"
#                 intermediate_steps.append(AgentResponse(
#                     agent_role=current_role_name,
#                     content=step_prep_msg,
#                     metadata={"full_prompt": current_prompt, "available_tools_for_step": role_specific_tools_dict_list}
#                 ))
#                 save_conversation(session_id, current_role_name, step_prep_msg, {
#                     "type": "step_preparation",
#                     "tools": tool_names_for_role,
#                     "prompt": current_prompt
#                 })

#                 llm_response = await llm_client.generate_with_functions(
#                     prompt=current_prompt,
#                     functions=role_specific_tools_dict_list, # Client uses 'functions' key
#                     function_call="auto" # Let LLM decide if it wants to call a function
#                 )

#                 # Process LLM response
#                 if llm_response.get("type") == "function_call":
#                     tool_name = llm_response.get("name")
#                     tool_args_str = llm_response.get("arguments", "{}") # Arguments are a string
                    
#                     # Initialize for broader scope in case of parsing errors before definition
#                     parsed_tool_args: Optional[Dict[str, Any]] = None 
#                     tool_result_content = ""

#                     try:
#                         # Parse arguments string to dict
#                         if tool_args_str:
#                             parsed_tool_args = json.loads(tool_args_str)
#                             if not isinstance(parsed_tool_args, dict):
#                                 logger.error(f"Tool '{tool_name}' arguments not a valid JSON object: {tool_args_str}")
#                                 raise ValueError("Tool arguments must be a JSON object.")
#                         else:
#                             parsed_tool_args = {} # Empty dict if no args string

#                         current_agent_id_for_tool = session_id 

#                         logger.info(f"Executing tool '{tool_name}' for agent '{current_agent_id_for_tool}' with parsed args: {parsed_tool_args}")
                        
#                         called_tool_definition: Optional[ToolDefinition] = all_registered_tools.get(tool_name)

#                         if called_tool_definition and callable(called_tool_definition.function):
#                             tool_execution_msg = f"Executing tool: {tool_name}"
#                             intermediate_steps.append(AgentResponse(
#                                 agent_role=current_role_name, 
#                                 content=tool_execution_msg,
#                                 metadata={"tool_name": tool_name, "arguments": parsed_tool_args}
#                             ))
#                             save_conversation(session_id, current_role_name, tool_execution_msg, {
#                                 "type": "tool_execution",
#                                 "tool_name": tool_name,
#                                 "arguments": parsed_tool_args
#                             })
                            
#                             # Execute the actual tool function
#                             if asyncio.iscoroutinefunction(called_tool_definition.function):
#                                 tool_result = await called_tool_definition.function(current_agent_id_for_tool, **parsed_tool_args)
#                             else:
#                                 tool_result = called_tool_definition.function(current_agent_id_for_tool, **parsed_tool_args)
                            
#                             tool_result_content = str(tool_result) if tool_result is not None else "Tool executed successfully with no return value."
#                             logger.info(f"Tool {tool_name} executed. Result: {tool_result_content[:200]}...")
#                             agent_state["last_action_outcome"] = tool_result
#                             agent_state["history"].append({"role": current_role_name, "action": "tool_call", "tool_name": tool_name, "arguments": parsed_tool_args, "result": tool_result_content})
                            
#                             tool_result_msg = f"Tool '{tool_name}' result: {tool_result_content[:500]}..."
#                             intermediate_steps.append(AgentResponse(
#                                 agent_role=current_role_name, 
#                                 content=tool_result_msg, 
#                                 metadata={"tool_name": tool_name, "result": tool_result_content}
#                             ))
#                             save_conversation(session_id, current_role_name, tool_result_msg, {
#                                 "type": "tool_result",
#                                 "tool_name": tool_name,
#                                 "result": tool_result_content
#                             })
                            
#                         else:
#                             logger.warning(f"LLM tried to call undefined or non-callable tool: {tool_name}")
#                             tool_result_content = f"Error: Tool '{tool_name}' is not defined or not callable."
#                             agent_state["last_action_outcome"] = tool_result_content
#                             agent_state["history"].append({"role": current_role_name, "action": "undefined_tool_call", "tool_name": tool_name})
#                             intermediate_steps.append(AgentResponse(agent_role=current_role_name, content=tool_result_content, metadata=llm_response, is_error=True))
#                             save_conversation(session_id, current_role_name, tool_result_content, {
#                                 "type": "tool_error",
#                                 "error_type": "undefined_tool",
#                                 "tool_name": tool_name
#                             })

#                     except json.JSONDecodeError as e:
#                         error_msg = f"Error decoding JSON arguments for tool '{tool_name}': {tool_args_str}. Details: {str(e)}"
#                         logger.error(error_msg)
#                         tool_result_content = error_msg
#                         intermediate_steps.append(AgentResponse(agent_role=current_role_name, content=tool_result_content, tool_name=tool_name, is_error=True, is_tool_response=True))
#                         save_conversation(session_id, current_role_name, error_msg, {
#                             "type": "error",
#                             "error_type": "json_decode",
#                             "tool_name": tool_name
#                         })
#                         agent_state["last_action_outcome"] = {"tool_name": tool_name, "error": error_msg, "success": False}
#                     except TypeError as e: 
#                         # Ensure parsed_tool_args is defined for the error message, even if it's None from an earlier parsing failure
#                         parsed_args_for_log = parsed_tool_args if parsed_tool_args is not None else '(Args not available due to parsing error or None provided)'
#                         error_msg = f"Type error executing tool '{tool_name}' with args {parsed_args_for_log}. This might be due to mismatched arguments or a Pydantic validation error in the tool itself. Details: {str(e)}"
#                         logger.error(error_msg, exc_info=True)
#                         tool_result_content = error_msg # Ensure tool_result_content is set
#                         intermediate_steps.append(AgentResponse(agent_role=current_role_name, content=tool_result_content, tool_name=tool_name, is_error=True, is_tool_response=True))
#                         save_conversation(session_id, current_role_name, error_msg, {
#                             "type": "error",
#                             "error_type": "type_error",
#                             "tool_name": tool_name,
#                             "arguments": parsed_args_for_log
#                         })
#                         agent_state["last_action_outcome"] = {"tool_name": tool_name, "error": error_msg, "success": False}
#                     except Exception as e:
#                         # Ensure parsed_tool_args is defined for the error message
#                         parsed_args_for_log = parsed_tool_args if parsed_tool_args is not None else '(Args not available due to parsing error or None provided)'
#                         error_msg = f"Unexpected error processing or executing tool '{tool_name}' with args {parsed_args_for_log}. Details: {type(e).__name__} - {str(e)}"
#                         logger.error(error_msg, exc_info=True) 
#                         tool_result_content = error_msg # Ensure tool_result_content is set
#                         intermediate_steps.append(AgentResponse(agent_role=current_role_name, content=tool_result_content, tool_name=tool_name, is_error=True, is_tool_response=True))
#                         save_conversation(session_id, current_role_name, error_msg, {
#                             "type": "error",
#                             "error_type": "unexpected",
#                             "tool_name": tool_name,
#                             "arguments": parsed_args_for_log
#                         })
#                         agent_state["last_action_outcome"] = {"tool_name": tool_name, "error": error_msg, "success": False}

#                 elif llm_response.get("type") == "text":
#                     text_output = llm_response.get("content", "")
#                     logger.info(f"Role {current_role_name} produced text output: {text_output[:200]}...")
#                     agent_state["last_action_outcome"] = text_output # Or specific field based on role
#                     agent_state["history"].append({"role": current_role_name, "action": "text_response", "output": text_output})
#                     # Update specific parts of agent_state based on role
#                     if current_role_name == "perception":
#                         agent_state["world_model"].update({"perception_findings": text_output, "last_updated_by": "perception"})
#                     elif current_role_name == "reasoning":
#                         agent_state["world_model"].update({"reasoning_conclusions": text_output, "last_updated_by": "reasoning"})
#                     elif current_role_name == "planning":
#                         agent_state["current_plan"] = text_output # Assuming plan is text for now
#                         agent_state["history"].append({"plan_updated": text_output})
#                     elif current_role_name == "reflection":
#                          agent_state["learnings"].append(text_output)
                    
#                     intermediate_steps.append(AgentResponse(
#                         agent_role=current_role_name,
#                         content=text_output,
#                         metadata=llm_response
#                     ))
#                     save_conversation(session_id, current_role_name, text_output, {
#                         "type": "text_response",
#                         "role_specific_update": current_role_name
#                     })
#                 else:
#                     logger.error(f"Unexpected LLM response type for role {current_role_name}: {llm_response.get('type')}")
#                     error_msg = "Error: Received unexpected response type from LLM."
#                     intermediate_steps.append(AgentResponse(agent_role=current_role_name, content=error_msg, metadata=llm_response))
#                     save_conversation(session_id, current_role_name, error_msg, {
#                         "type": "error",
#                         "error_type": "unexpected_response_type",
#                         "response_type": llm_response.get('type')
#                     })
#                     # Potentially break or handle error
            
#             # Basic check for task completion (example, needs refinement)
#             # This should be driven by the 'reflection' step ideally
#             if agent_state.get("current_plan") and "task complete" in str(agent_state.get("current_plan","")).lower(): # very naive
#                 logger.info("Agent believes task is complete based on plan.")
#                 final_response_content = agent_state["history"][-1].get("output", "Task completed.") if agent_state["history"] else "Task completed."
#                 completion_msg = "Task marked as complete by agent."
#                 intermediate_steps.append(AgentResponse(agent_role="System", content=completion_msg))
#                 save_conversation(session_id, "System", completion_msg, {"type": "task_completion"})
#                 break
#         else: # Else for the for loop (if MAX_AGENT_ITERATIONS reached)
#             logger.warning(f"Agent reached maximum iterations ({MAX_AGENT_ITERATIONS}).")
#             final_response_content = "Agent reached maximum iterations without completing the task."
#             max_iterations_msg = final_response_content
#             intermediate_steps.append(AgentResponse(agent_role="System", content=max_iterations_msg))
#             save_conversation(session_id, "System", max_iterations_msg, {"type": "max_iterations_reached"})

#         # 3. Handle Communication Step (Simplified)
#         # This would ideally be triggered by the reflection step
#         communication_role_config = next((step for step in agent_definition["steps"] if step["role"] == agent_definition.get("communication_role")), None)
#         if communication_role_config:
#             logger.info("Executing final communication step...")
#             communication_prompt_template = communication_role_config["prompt"]
#             # Incorporate final state for communication
#             communication_prompt = f"{communication_prompt_template}\\n\\nFINAL AGENT STATE:\\n{json.dumps(agent_state, indent=2, default=str)}"
#             communication_tools_dicts = communication_role_config.get("tools", [])

#             comm_response = await llm_client.generate_with_functions(
#                 prompt=communication_prompt,
#                 functions=communication_tools_dicts,
#                 function_call="auto"
#             )
#             if comm_response.get("type") == "text":
#                 final_response_content = comm_response.get("content", final_response_content)
#                 intermediate_steps.append(AgentResponse(agent_role=agent_definition["communication_role"], content=final_response_content, metadata=comm_response))
#                 save_conversation(session_id, agent_definition["communication_role"], final_response_content, {
#                     "type": "final_communication",
#                     "response_type": "text"
#                 })
#             elif comm_response.get("type") == "function_call": # If communication step also calls a tool
#                 # Simplified: log it, but don't execute further for this example
#                 comm_tool_msg = f"Communication step suggested tool call: {comm_response.get('name')}"
#                 intermediate_steps.append(AgentResponse(agent_role=agent_definition["communication_role"], content=comm_tool_msg, metadata=comm_response))
#                 save_conversation(session_id, agent_definition["communication_role"], comm_tool_msg, {
#                     "type": "final_communication",
#                     "response_type": "function_call",
#                     "tool_name": comm_response.get('name')
#                 })


#     except Exception as e:
#         logger.error(f"Error during autonomous agent execution: {e}", exc_info=True)
#         final_response_content = f"An error occurred: {str(e)}"
#         intermediate_steps.append(AgentResponse(agent_role="System", content=f"Workflow error: {str(e)}"))
#         processing_time = time.time() - start_time
#         return WorkflowResponse(
#             session_id=session_id, # Ensure session_id is correctly passed or generated
#             selected_workflow=workflow_selection.selected_workflow,
#             final_response=final_response_content,
#             intermediate_steps=intermediate_steps,
#             error=str(e),
#             processing_time=processing_time
#         )

#     processing_time = time.time() - start_time
#     return WorkflowResponse(
#         session_id=session_id, # Ensure session_id is correctly passed or generated
#         selected_workflow=workflow_selection.selected_workflow,
#         final_response=final_response_content,
#         intermediate_steps=intermediate_steps,
#         error=None, # No error if we reached here
#         processing_time=processing_time
#     )

# # Note: The _build_autonomous_agent function expects 'tools: List[ToolDefinition]'.
# # The `role_step_config.get("tools", [])` inside the loop are already dictionaries.
# # The `llm_client.generate_with_functions` expects `functions: list` (of these dictionaries).
# # The `all_registered_tools: Dict[str, ToolDefinition]` is used to look up the actual callable ToolDefinition.function.
# # This structure seems compatible.
