# app/core/workflow_selector.py
from app.models.schemas import WorkflowSelection
from app.core.llm_client import get_functions_client
from app.personas.agent_personas import agent_personas
import logging

async def select_workflow(user_query: str, use_autonomous_exclusively: bool = False) -> WorkflowSelection:
    """
    Dynamically selects the appropriate workflow based on user query using Azure OpenAI function calling,
    or forces the autonomous_agent workflow if specified.
    
    If use_autonomous_exclusively is True, this function bypasses dynamic selection and
    returns the "autonomous_agent" workflow. Otherwise, it analyzes the user's query
    to determine the most suitable workflow pattern from other available options.
    
    Args:
        user_query (str): The query text provided by the user
        use_autonomous_exclusively (bool, optional): If True, forces selection of 
                                                  the "autonomous_agent" workflow. 
                                                  Defaults to False.
        
    Returns:
        WorkflowSelection: An object containing the selected workflow name, reasoning,
                          required agent roles, and associated personas
                          
    Raises:
        Exception: If there's an error during the workflow selection process
    """
    if use_autonomous_exclusively:
        logging.info("Forcing 'autonomous_agent' workflow due to explicit flag.")
        personas = agent_personas.get("autonomous_agent", {})
        if not personas:
            logging.warning("'autonomous_agent' personas not found in agent_personas.py, though explicitly requested!")
            # Fallback to empty required_agents and personas if not found,
            # or consider raising an error if 'autonomous_agent' is critical and must have personas.
            required_agents_list = []
        else:
            # Assuming personas for 'autonomous_agent' is a dict where keys are agent roles
            required_agents_list = list(personas.keys())

        return WorkflowSelection(
            selected_workflow="autonomous_agent",
            reasoning="Autonomous agent workflow selected by explicit user/system choice.",
            required_agents=required_agents_list,
            personas=personas
        )

    functions_client = get_functions_client()
    
    # Define the workflow selection function
    workflow_selection_function = {
        "name": "select_workflow",
        "description": "Selects the most appropriate workflow pattern based on the user query",
        "parameters": {
            "type": "object",
            "properties": {
                "selected_workflow": {
                    "type": "string",
                    "enum": [
                        "prompt_chaining", 
                        "routing", 
                        "parallel_sectioning", 
                        "parallel_voting", 
                        "orchestrator_workers", 
                        "evaluator_optimizer"
                    ],
                    "description": "The name of the selected workflow pattern"
                },
                "reasoning": {
                    "type": "string",
                    "description": "Brief explanation for why this workflow is most appropriate"
                },
                "required_agents": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Array of agent roles needed for this workflow"
                }
            },
            "required": ["selected_workflow", "reasoning"]
        }
    }
    
    # Prepare prompt for the workflow selector
    selector_prompt = f"""
    Analyze the following user query and determine the most appropriate workflow pattern to handle it.
    
    Available workflow patterns:
    
    1. Prompt Chaining: Best for tasks that can be broken down into sequential steps.
       Example queries: "Write a blog post and then translate it to Spanish", "Summarize this article and then create talking points"
    
    2. Routing: Best for queries that fall into distinct categories requiring specialized handling.
       Example queries: "How do I reset my password?", "I need a refund for my order", "Explain how photosynthesis works"
    
    3. Parallel Sectioning: Best for complex tasks with independent components.
       Example queries: "Analyze this product from marketing, technical, and financial perspectives", "Review this code for bugs, style issues, and security vulnerabilities"
    
    4. Parallel Voting: Best for tasks requiring multiple perspectives or high confidence.
       Example queries: "Is this email a phishing attempt?", "Is this content appropriate for all audiences?", "Check if this code has security vulnerabilities"
    
    5. Orchestrator-Workers: Best for complex tasks where subtasks depend on initial analysis.
       Example queries: "Help me plan my vacation to Europe", "Refactor this entire codebase", "Create a marketing strategy for my new product"
    
    6. Evaluator-Optimizer: Best for tasks requiring iterative refinement against specific criteria.
       Example queries: "Write a professional email to my boss requesting time off", "Create a poem about nature that uses vivid imagery", "Optimize this SQL query for performance"
       
    # 7. Autonomous Agent: Best for open-ended tasks requiring multiple steps, tool usage, and adaptive problem-solving.
    #    (This workflow is selected via the 'use_autonomous_exclusively' flag, not by dynamic LLM choice here)
    
    User Query: "{user_query}"
    
    Select the most appropriate workflow for handling this query.
    """
    
    try:
        # Get workflow selection using function calling
        workflow_response = await functions_client.generate_with_functions(
            selector_prompt,
            [workflow_selection_function],
            function_call={"name": "select_workflow"}
        )
        
        if workflow_response["type"] == "function_call" and workflow_response["name"] == "select_workflow":
            workflow_data = workflow_response["arguments"]
            
            # Get personas for the selected workflow
            personas = agent_personas.get(workflow_data["selected_workflow"], {})
            
            return WorkflowSelection(
                selected_workflow=workflow_data["selected_workflow"],
                reasoning=workflow_data["reasoning"],
                required_agents=workflow_data.get("required_agents", []),
                personas=personas
            )
        else:
            # Fallback to default workflow if function call fails
            logging.warning("Workflow selection function call not returned, using default workflow")
            return WorkflowSelection(
                selected_workflow="prompt_chaining",
                reasoning="Fallback to default workflow due to selection error",
                required_agents=[],
                personas=agent_personas.get("prompt_chaining", {})
            )
    except Exception as e:
        logging.error(f"Error in workflow selection: {str(e)}")
        raise

#  7. Autonomous Agent: Best for open-ended tasks requiring multiple steps, tool usage, and adaptive problem-solving.
#        Example queries: "Research the latest developments in quantum computing", "Plan a comprehensive marketing campaign for my startup", "Help me debug and fix this complex coding issue"

# 7. Autonomous Agent: Best for open-ended tasks requiring multiple steps, tool usage, and adaptive problem-solving without a predefined structure. It can plan, execute, and reflect on its actions to achieve a goal.
#        Example queries: "Research the latest developments in quantum computing and write a summary", "Plan a comprehensive marketing campaign for my new e-commerce startup for the next quarter", "Help me debug and fix this complex coding issue in my Python script, then explain the root cause"
#     #   