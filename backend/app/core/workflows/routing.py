from app.models.schemas import WorkflowSelection, AgentResponse
from app.core.llm_client import get_llm_client, get_functions_client
from typing import Tuple, List, Dict, Any
import logging
import json

async def execute(workflow_selection: WorkflowSelection, user_query: str) -> Tuple[str, List[AgentResponse]]:
    """
    Executes a routing workflow that classifies a user query and directs it to specialized handlers based on the classification.
    
    The workflow consists of the following steps:
    1. Classify the user query using a classifier agent to determine the appropriate category.
    2. Route the classified query to the corresponding specialist agent for a comprehensive response.
    
    Parameters:
    - workflow_selection (WorkflowSelection): The selection of workflows to execute, including personas.
    - user_query (str): The query provided by the user that needs to be processed.
    
    Returns:
    - Tuple[str, List[AgentResponse]]: A tuple containing the specialist's response and a list of intermediate agent responses recorded during the execution.
    """
    functions_client = get_functions_client()
    llm_client = get_llm_client()
    personas = workflow_selection.personas.get("routing", {})
    intermediate_steps = []
    
    # Step 1: Classify the query using the classifier agent
    classifier_agent = personas.get("classifier_agent", {})
    
    # Define categories for classification
    categories = ["technical_support", "account_management", "product_information", "billing_support", "general_inquiry"]
    
    # Define the classification function
    classification_function = {
        "name": "classify_query",
        "description": "Classifies a user query into the most appropriate category",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": categories,
                    "description": "The category that best matches the user query"
                },
                "confidence": {
                    "type": "number",
                    "description": "Confidence score for the classification (0.0 to 1.0)"
                },
                "reasoning": {
                    "type": "string",
                    "description": "Brief explanation of why this category was selected"
                }
            },
            "required": ["category", "confidence", "reasoning"]
        }
    }
    
    # Prepare the classifier prompt
    classifier_prompt = f"""
    {generate_agent_context(classifier_agent)}
    
    USER QUERY: {user_query}
    
    Your task is to classify this query into one of the following categories:
    1. technical_support - Questions about how to use products, troubleshooting issues, etc.
    2. account_management - Requests related to user accounts, login issues, profile changes, etc.
    3. product_information - Questions about product features, capabilities, pricing, etc.
    4. billing_support - Questions about billing, payments, subscriptions, refunds, etc.
    5. general_inquiry - General questions that don't fit into the other categories
    
    Analyze the query carefully and select the most appropriate category.
    """
    
    try:
        # Get classification using function calling
        classification_response = await functions_client.generate_with_functions(
            classifier_prompt,
            [classification_function],
            function_call={"name": "classify_query"},
            temperature=0.3
        )
        
        if classification_response["type"] == "function_call" and classification_response["name"] == "classify_query":
            classification = classification_response["arguments"]
        else:
            # Fallback if no function call was returned
            logging.warning("Classification function call not returned, using default category")
            classification = {
                "category": "general_inquiry",
                "confidence": 0.5,
                "reasoning": "Fallback classification due to unexpected response format"
            }
    except Exception as e:
        logging.error(f"Error in query classification: {str(e)}")
        classification = {
            "category": "general_inquiry",
            "confidence": 0.5,
            "reasoning": f"Fallback classification due to error: {str(e)}"
        }
    
    # Record the classification step
    intermediate_steps.append(AgentResponse(
        agent_role="Query Classifier",
        content=f"Classification: {classification['category']}\nConfidence: {classification['confidence']}\nReasoning: {classification['reasoning']}",
        metadata=classification
    ))
    
    # Step 2: Route to the appropriate specialist agent based on classification
    category = classification["category"]
    specialist_response = ""
    
    # Map categories to specialist agents
    category_to_agent = {
        "technical_support": "category1_agent",
        "account_management": "category2_agent",
        "product_information": "category1_agent",
        "billing_support": "category2_agent",
        "general_inquiry": "category3_agent"
    }
    
    specialist_agent_key = category_to_agent.get(category, "category3_agent")
    specialist_agent = personas.get(specialist_agent_key, {})
    
    # Prepare the specialist prompt
    specialist_prompt = f"""
    {generate_agent_context(specialist_agent)}
    
    USER QUERY: {user_query}
    
    QUERY CLASSIFICATION: {category}
    CLASSIFICATION CONFIDENCE: {classification['confidence']}
    CLASSIFICATION REASONING: {classification['reasoning']}
    
    You are a specialist in handling {category.replace('_', ' ')} queries.
    Please provide a comprehensive and helpful response to the user's query.
    """
    
    try:
        # Get specialist response
        specialist_response = await llm_client.generate(specialist_prompt, temperature=0.7)
    except Exception as e:
        logging.error(f"Error getting specialist response: {str(e)}")
        specialist_response = f"I apologize, but I encountered an issue while processing your {category.replace('_', ' ')} request. Please try again or contact our support team directly."
    
    # Record the specialist response
    intermediate_steps.append(AgentResponse(
        agent_role=f"{category.replace('_', ' ').title()} Specialist",
        content=specialist_response,
        metadata={"category": category}
    ))
    
    return specialist_response, intermediate_steps

def generate_agent_context(agent_persona: dict) -> str:
    """
    Generates a context prompt section based on an agent persona.
    
    Parameters:
    - agent_persona (dict): A dictionary containing the persona details of the agent.
    
    Returns:
    - str: A formatted string representing the agent's context.
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