# app/core/workflows/prompt_chaining.py
from app.models.schemas import WorkflowSelection, AgentResponse
from app.core.llm_client import get_llm_client
from typing import Tuple, List
import logging

async def execute(workflow_selection: WorkflowSelection, user_query: str) -> Tuple[str, List[AgentResponse]]:
    """
    Executes a prompt chaining workflow
    """
    llm_client = get_llm_client()
    personas = workflow_selection.personas.get("prompt_chaining", {})
    intermediate_steps = []
    
    # Step 1: Process the input with the first agent
    step1_agent = personas.get("step1_agent", {})
    step1_prompt = f"""
    {generate_agent_context(step1_agent)}
    
    USER QUERY: {user_query}
    
    Your task is to analyze this query and break it down into a structured format that can be processed further.
    Focus on understanding the core request, identifying key components, and organizing the information logically.
    
    Respond with a clear, structured breakdown of the query.
    """
    
    step1_result = await llm_client.generate(step1_prompt)
    intermediate_steps.append(AgentResponse(
        agent_role=step1_agent.get("role", "Initial Processor"),
        content=step1_result
    ))
    
    # Gate: Validate the step 1 output
    gate_agent = personas.get("gate_agent", {})
    gate_prompt = f"""
    {generate_agent_context(gate_agent)}
    
    Original user query: {user_query}
    
    Step 1 processing result:
    {step1_result}
    
    Your task is to validate whether the processed output meets the following criteria:
    1. The output accurately captures the intent of the original query
    2. The output is well-structured and organized
    3. The output contains all necessary information for further processing
    4. There are no misinterpretations or errors
    
    Respond with:
    - PASS: If the output meets all criteria, and a brief explanation of why
    - FAIL: If the output fails any criteria, and a detailed explanation of the issues
    """
    
    gate_result = await llm_client.generate(gate_prompt)
    intermediate_steps.append(AgentResponse(
        agent_role=gate_agent.get("role", "Validator"),
        content=gate_result
    ))
    
    # If gate check fails, return the explanation
    if "FAIL" in gate_result[:50]:
        failure_explanation = gate_result.replace("FAIL:", "").strip()
        final_response = f"I apologize, but I need to refine my understanding of your request. {failure_explanation}"
        return final_response, intermediate_steps
    
    # Step 2: Generate the final response
    step2_agent = personas.get("step2_agent", {})
    step2_prompt = f"""
    {generate_agent_context(step2_agent)}
    
    Original user query: {user_query}
    
    Structured information from previous processing:
    {step1_result}
    
    Your task is to create a complete, well-crafted response to the user's original query
    based on the structured information provided.
    
    Focus on:
    - Addressing all aspects of the query comprehensively
    - Providing accurate and helpful information
    - Maintaining a natural, conversational tone
    - Organizing information in a clear, logical manner
    
    Generate a complete response that directly addresses the user's query.
    """
    
    final_response = await llm_client.generate(step2_prompt)
    intermediate_steps.append(AgentResponse(
        agent_role=step2_agent.get("role", "Refiner"),
        content=final_response
    ))
    
    return final_response, intermediate_steps

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