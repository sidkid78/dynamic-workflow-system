from app.models.schemas import WorkflowSelection, AgentResponse
from app.core.llm_client import get_llm_client, get_functions_client
from typing import Tuple, List, Dict, Any
import logging
import json
import asyncio

async def execute(workflow_selection: WorkflowSelection, user_query: str) -> Tuple[str, List[AgentResponse]]:
    """
    Executes a parallel voting workflow that runs the same task multiple times with different perspectives
    to obtain diverse outputs for higher confidence. The workflow consists of three main steps:
    
    1. **Define Perspectives**: Analyzes the user query to determine the type of evaluation task,
       identifies different perspectives for evaluation, and establishes a voting threshold for consensus.
       
    2. **Evaluate Perspectives**: Each perspective evaluates the query in parallel, providing judgments,
       confidence levels, and reasoning based on predefined criteria.
       
    3. **Determine Consensus**: A consensus agent analyzes the evaluations to reach a final decision,
       providing a comprehensive response based on the gathered evaluations and the established voting threshold.
    """
    functions_client = get_functions_client()
    llm_client = get_llm_client()
    personas = workflow_selection.personas.get("parallel_voting", {})
    intermediate_steps = []
    
    # Step 1: Define the perspectives for analysis
    # The function will help determine what kind of voting/evaluation is needed
    perspective_function = {
        "name": "define_voting_perspectives",
        "description": "Defines the different perspectives from which to evaluate the query",
        "parameters": {
            "type": "object",
            "properties": {
                "task_type": {
                    "type": "string",
                    "enum": ["classification", "verification", "assessment", "selection", "other"],
                    "description": "The type of task to be performed"
                },
                "perspectives": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "Unique identifier for the perspective"
                            },
                            "name": {
                                "type": "string",
                                "description": "Name of the perspective"
                            },
                            "focus": {
                                "type": "string",
                                "description": "What this perspective focuses on when evaluating"
                            },
                            "criteria": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "Key criteria this perspective considers"
                            }
                        },
                        "required": ["id", "name", "focus", "criteria"]
                    },
                    "description": "List of perspectives to evaluate from"
                },
                "voting_threshold": {
                    "type": "number",
                    "description": "The threshold (0.0 to 1.0) for consensus"
                },
                "reasoning": {
                    "type": "string",
                    "description": "Explanation of why these perspectives were chosen"
                }
            },
            "required": ["task_type", "perspectives", "voting_threshold", "reasoning"]
        }
    }
    
    # Prepare the perspective definition prompt
    perspective_prompt = f"""
    {generate_agent_context(personas.get("perspective_agent", {}))}
    
    USER QUERY: {user_query}
    
    Your task is to analyze this query and determine:
    1. What type of evaluation task this is (classification, verification, assessment, etc.)
    2. What different perspectives should evaluate this query
    3. What each perspective should focus on
    4. What threshold should be used for consensus
    
    Consider how this query might benefit from multiple viewpoints to ensure accuracy and reduce bias.
    """
    
    try:
        # Get perspectives using function calling
        perspective_response = await functions_client.generate_with_functions(
            perspective_prompt,
            [perspective_function],
            function_call={"name": "define_voting_perspectives"},
            temperature=0.5
        )
        
        if perspective_response["type"] == "function_call" and perspective_response["name"] == "define_voting_perspectives":
            perspective_data = perspective_response["arguments"]
        else:
            # Fallback if no function call was returned
            logging.warning("Perspective function call not returned, using default perspectives")
            perspective_data = {
                "task_type": "assessment",
                "perspectives": [
                    {
                        "id": "perspective1",
                        "name": "General Assessment",
                        "focus": "Overall evaluation of the query",
                        "criteria": ["Accuracy", "Relevance", "Completeness"]
                    },
                    {
                        "id": "perspective2",
                        "name": "Alternative Assessment",
                        "focus": "Secondary evaluation with different criteria",
                        "criteria": ["Consistency", "Objectivity", "Balance"]
                    },
                    {
                        "id": "perspective3",
                        "name": "Critical Assessment",
                        "focus": "Critical evaluation looking for potential issues",
                        "criteria": ["Logic", "Evidence", "Assumptions"]
                    }
                ],
                "voting_threshold": 0.67,  # 2/3 majority
                "reasoning": "Fallback perspectives due to unexpected response format"
            }
    except Exception as e:
        logging.error(f"Error in perspective definition: {str(e)}")
        perspective_data = {
            "task_type": "assessment",
            "perspectives": [
                {
                    "id": "perspective1",
                    "name": "General Assessment",
                    "focus": "Overall evaluation of the query",
                    "criteria": ["Accuracy", "Relevance", "Completeness"]
                },
                {
                    "id": "perspective2",
                    "name": "Alternative Assessment",
                    "focus": "Secondary evaluation with different criteria",
                    "criteria": ["Consistency", "Objectivity", "Balance"]
                },
                {
                    "id": "perspective3",
                    "name": "Critical Assessment",
                    "focus": "Critical evaluation looking for potential issues",
                    "criteria": ["Logic", "Evidence", "Assumptions"]
                }
            ],
            "voting_threshold": 0.67,  # 2/3 majority
            "reasoning": f"Fallback perspectives due to error: {str(e)}"
        }
    
    # Record the perspective definition step
    intermediate_steps.append(AgentResponse(
        agent_role="Perspective Coordinator",
        content=f"Task Type: {perspective_data['task_type']}\n\n" +
                f"Perspectives:\n" + "\n".join([f"- {p['name']}: {p['focus']} (Criteria: {', '.join(p['criteria'])})" 
                                                for p in perspective_data['perspectives']]) + "\n\n" +
                f"Voting Threshold: {perspective_data['voting_threshold']}\n\n" +
                f"Reasoning: {perspective_data['reasoning']}",
        metadata=perspective_data
    ))
    
    # Step 2: Evaluate from each perspective in parallel
    perspective_agent = personas.get("perspective_agent", {})
    
    # Define evaluation function for the specific task type
    evaluation_function = {
        "name": "evaluate_from_perspective",
        "description": f"Evaluates the query from a specific perspective for {perspective_data['task_type']}",
        "parameters": {
            "type": "object",
            "properties": {
                "judgment": {
                    "type": "string",
                    "enum": ["approve", "reject", "uncertain"],
                    "description": "The overall judgment from this perspective"
                },
                "confidence": {
                    "type": "number",
                    "description": "Confidence in this judgment (0.0 to 1.0)"
                },
                "reasoning": {
                    "type": "string",
                    "description": "Detailed reasoning for this judgment"
                },
                "criteria_assessment": {
                    "type": "object",
                    "description": "Assessment against each criterion"
                }
            },
            "required": ["judgment", "confidence", "reasoning"]
        }
    }
    
    async def evaluate_from_perspective(perspective):
        """Evaluate the query from a specific perspective"""
        # Prepare the evaluation prompt
        evaluation_prompt = f"""
        {generate_agent_context(perspective_agent)}
        
        ORIGINAL USER QUERY: {user_query}
        
        You are evaluating this query from the perspective of: {perspective['name']}
        Focus area: {perspective['focus']}
        Key criteria: {', '.join(perspective['criteria'])}
        
        Your task is to thoroughly evaluate this query from your specific perspective.
        
        Task type: {perspective_data['task_type']}
        
        You should:
        1. Carefully consider each of your assigned criteria
        2. Provide an overall judgment (approve, reject, or uncertain)
        3. Explain your reasoning in detail
        4. Assess how well the query meets each of your criteria
        """
        
        try:
            # Get evaluation response using function calling
            evaluation_response = await functions_client.generate_with_functions(
                evaluation_prompt,
                [evaluation_function],
                function_call={"name": "evaluate_from_perspective"},
                temperature=0.7
            )
            
            if evaluation_response["type"] == "function_call" and evaluation_response["name"] == "evaluate_from_perspective":
                evaluation = evaluation_response["arguments"]
                evaluation["perspective_id"] = perspective["id"]
                evaluation["perspective_name"] = perspective["name"]
                return evaluation
            else:
                # Fallback if no function call was returned
                return {
                    "perspective_id": perspective["id"],
                    "perspective_name": perspective["name"],
                    "judgment": "uncertain",
                    "confidence": 0.5,
                    "reasoning": "Unable to reach a clear judgment due to response format issues",
                    "criteria_assessment": {}
                }
        except Exception as e:
            logging.error(f"Error in perspective evaluation {perspective['id']}: {str(e)}")
            return {
                "perspective_id": perspective["id"],
                "perspective_name": perspective["name"],
                "judgment": "uncertain",
                "confidence": 0.5,
                "reasoning": f"Error during evaluation: {str(e)}",
                "criteria_assessment": {}
            }
    
    # Evaluate from all perspectives in parallel
    evaluation_results = await asyncio.gather(
        *[evaluate_from_perspective(perspective) for perspective in perspective_data["perspectives"]]
    )
    
    # Record the evaluation results
    for result in evaluation_results:
        intermediate_steps.append(AgentResponse(
            agent_role=f"{result['perspective_name']} Evaluator",
            content=f"Judgment: {result['judgment'].upper()}\n" +
                    f"Confidence: {result['confidence']}\n\n" +
                    f"Reasoning:\n{result['reasoning']}",
            metadata=result
        ))
    
    # Step 3: Determine consensus using the consensus agent
    consensus_agent = personas.get("consensus_agent", {})
    
    # Prepare the consensus prompt
    consensus_prompt = f"""
    {generate_agent_context(consensus_agent)}
    
    ORIGINAL USER QUERY: {user_query}
    
    You have received evaluations from multiple perspectives, each providing their judgment.
    Your task is to determine the consensus and provide a final decision.
    
    Voting threshold: {perspective_data['voting_threshold']}
    
    The evaluations are:
    
    {format_evaluation_results(evaluation_results)}
    
    Based on these evaluations, determine:
    1. Whether there is consensus (approval or rejection)
    2. If there is no clear consensus, provide your own judgment
    3. Explain the reasoning for the final decision
    4. Provide a comprehensive response to the original query
    """
    
    try:
        # Get consensus response
        consensus_response = await llm_client.generate(consensus_prompt, temperature=0.5)
    except Exception as e:
        logging.error(f"Error in consensus determination: {str(e)}")
        # Calculate basic majority vote as fallback
        approvals = sum(1 for result in evaluation_results if result["judgment"] == "approve")
        rejections = sum(1 for result in evaluation_results if result["judgment"] == "reject")
        uncertain = sum(1 for result in evaluation_results if result["judgment"] == "uncertain")
        
        if approvals / len(evaluation_results) >= perspective_data["voting_threshold"]:
            consensus = "Approved"
        elif rejections / len(evaluation_results) >= perspective_data["voting_threshold"]:
            consensus = "Rejected"
        else:
            consensus = "No clear consensus"
        
        consensus_response = (
            f"Based on the evaluations, the result is: {consensus}\n\n"
            f"Voting results: {approvals} approvals, {rejections} rejections, {uncertain} uncertain\n\n"
            "Here are the perspectives that were considered:\n\n" + 
            "\n\n".join([f"**{r['perspective_name']}**: {r['judgment'].upper()} - {r['reasoning']}" 
                          for r in evaluation_results])
        )
    
    # Record the consensus step
    intermediate_steps.append(AgentResponse(
        agent_role="Consensus Builder",
        content=consensus_response,
        metadata={
            "evaluations": [
                {"perspective": r["perspective_name"], 
                 "judgment": r["judgment"], 
                 "confidence": r["confidence"]} 
                for r in evaluation_results
            ]
        }
    ))
    
    return consensus_response, intermediate_steps

def format_evaluation_results(results: List[Dict[str, Any]]) -> str:
    """Format evaluation results for the consensus prompt"""
    formatted = ""
    for i, result in enumerate(results, 1):
        formatted += f"EVALUATION {i} - {result['perspective_name']}:\n"
        formatted += f"Judgment: {result['judgment'].upper()}\n"
        formatted += f"Confidence: {result['confidence']}\n"
        formatted += f"Reasoning: {result['reasoning']}\n\n"
    return formatted

def generate_agent_context(agent_persona: dict) -> str:
    """
    Generates a context prompt section based on an agent persona.
    
    Args:
        agent_persona (dict): A dictionary containing information about the agent's role, persona,
                              description, and strengths.
    
    Returns:
        str: A formatted string representing the agent's context.
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