# app/core/workflows/prompt_chaining.py
"""
Prompt Chaining Workflow Module

This module implements a sequential prompt chaining workflow that processes user queries
through multiple LLM calls in a structured pipeline. The workflow consists of:

1. Initial Processing: Analyzes and structures the user query
2. Validation Gate: Ensures the initial processing meets quality criteria
3. Final Response Generation: Creates a comprehensive response based on structured data

Each step uses a different agent persona to specialize in its specific task.
The workflow does not use explicit tool/function calling, focusing instead on
pure prompt engineering and sequential processing.

Functions:
    execute: Main entry point that processes a user query through the workflow
    generate_agent_context: Helper to create persona-specific context for prompts
"""

from app.models.schemas import WorkflowSelection, AgentResponse
from app.core.llm_client import get_llm_client
# Remove tool-related imports
from typing import Tuple, List
import logging
from app.config import settings # Import settings
from app.utils.context_loader import load_context_content # Import context loader

logger = logging.getLogger(__name__)

async def execute(workflow_selection: WorkflowSelection, user_query: str) -> Tuple[str, List[AgentResponse]]:
    """
    Executes a simple prompt chaining workflow without explicit tool/function calling.
    
    This function implements a three-stage workflow:
    1. Initial processing to analyze and structure the query
    2. Validation gate to ensure quality of the initial processing
    3. Final response generation based on the structured information
    
    Args:
        workflow_selection: Contains workflow configuration and persona definitions
        user_query: The original query from the user
        
    Returns:
        Tuple containing:
            - final_response: The complete answer to the user's query
            - intermediate_steps: List of all agent responses during processing
            
    Raises:
        Exceptions are caught internally and converted to error messages
    """
    llm_client = get_llm_client()
    personas = workflow_selection.personas.get("prompt_chaining", {})
    intermediate_steps: List[AgentResponse] = []
    
    # Load context content
    context_content = load_context_content(settings.CONTEXT_FILE_PATH)
    context_prefix = f"{context_content}\\n\\n--- END OF CONTEXT ---\\n\\n" if context_content else ""

    # Step 1: Initial Processing
    step1_agent = personas.get("step1_agent", {})
    step1_prompt = f"""{context_prefix}{generate_agent_context(step1_agent)}
    
    USER QUERY: {user_query}
    
    Your task is to analyze this query and break it down into a structured format or initial analysis.
    Focus on understanding the core request, identifying key components, and organizing the information logically.
    Respond with a clear, structured breakdown of the query.
    """
    
    step1_result_content = "No analysis generated."
    try:
        # Use simple generation
        step1_result_content = await llm_client.generate(step1_prompt)
    except Exception as e:
        logger.error(f"Error during Step 1 LLM call: {e}", exc_info=True)
        step1_result_content = f"Error during initial processing: {e}"
        
    intermediate_steps.append(AgentResponse(
        agent_role="Initial Processor",
        content=step1_result_content
    ))
    
    # Gate: Validate the Step 1 Output
    gate_agent = personas.get("gate_agent", {})
    gate_prompt = f"""
    {generate_agent_context(gate_agent)}
    
    Original user query: {user_query}
    Step 1 processing result:
    {step1_result_content}
    
    Your task is to validate whether the processed output meets the following criteria:
    1. The output accurately captures the intent of the original query.
    2. The output is well-structured and organized.
    3. The output contains all necessary information for further processing.
    
    Respond with:
    - PASS: If the output meets all criteria.
    - FAIL: If the output fails any criteria, and explain why.
    """
    
    gate_result = "PASS" # Default to pass if error occurs
    try:
        gate_response = await llm_client.generate(gate_prompt)
        gate_result = gate_response.strip()
    except Exception as e:
        logger.error(f"Error during Gate validation LLM call: {e}", exc_info=True)
        gate_result = f"FAIL: Error during validation - {e}" # Treat LLM error as failure

    intermediate_steps.append(AgentResponse(
        agent_role="Validator",
        content=gate_result
    ))
    
    if gate_result.startswith("FAIL"):
        final_response = f"Processing stopped at validation step. Reason: {gate_result.replace('FAIL:', '').strip()}"
        return final_response, intermediate_steps
    
    # Step 2: Generate Final Response
    step2_agent = personas.get("step2_agent", {})
    step2_prompt = f"""
    {generate_agent_context(step2_agent)}
    
    Original user query: {user_query}
    Structured information from previous step:
    {step1_result_content}
    
    Your task is to create the final, complete response to the user's original query, 
    using the structured information provided.
    Focus on addressing all aspects, providing accurate information, and maintaining a natural tone.
    
    Generate the final response for the user.
    """

    final_response = "Could not generate final response."
    try:
        # Use simple generation
        final_response = await llm_client.generate(step2_prompt)
    except Exception as e:
        logger.error(f"Error during Step 2 LLM call: {e}", exc_info=True)
        final_response = f"Error during final response generation: {e}"
        
    intermediate_steps.append(AgentResponse(
        agent_role="Refiner",
        content=final_response
    ))
    
    return final_response, intermediate_steps

def generate_agent_context(agent_persona: dict) -> str:
    """
    Generates a context prompt section based on an agent persona.
    
    Creates a formatted context block that defines the agent's role,
    personality, and capabilities to guide the LLM's response style.
    
    Args:
        agent_persona: Dictionary containing persona attributes including
                      role, persona, description, and strengths
                      
    Returns:
        Formatted string containing the agent context block
        
    Note:
        Returns an empty string if agent_persona is empty or None
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