# app/core/workflows/evaluator_optimizer.py
from app.models.schemas import WorkflowSelection, AgentResponse
from app.core.llm_client import get_llm_client, get_functions_client
from typing import Tuple, List, Dict, Any
import logging
import json

async def execute(workflow_selection: WorkflowSelection, user_query: str) -> Tuple[str, List[AgentResponse]]:
    """
    Executes an evaluator-optimizer workflow where one LLM generates content and another
    provides evaluation and feedback for iterative refinement
    """
    functions_client = get_functions_client()
    llm_client = get_llm_client()
    personas = workflow_selection.personas.get("evaluator_optimizer", {})
    intermediate_steps = []
    
    # Step 1: Determine evaluation criteria based on task type
    # Define the criteria definition function
    criteria_function = {
        "name": "define_evaluation_criteria",
        "description": "Defines criteria for evaluating the response to the user query",
        "parameters": {
            "type": "object",
            "properties": {
                "task_type": {
                    "type": "string",
                    "description": "The type of task involved in the user query"
                },
                "criteria": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the criterion"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of what this criterion measures"
                            },
                            "weight": {
                                "type": "number",
                                "description": "Relative importance of this criterion (0.0 to 1.0)"
                            }
                        },
                        "required": ["name", "description", "weight"]
                    },
                    "description": "List of criteria for evaluating the response"
                },
                "max_iterations": {
                    "type": "integer",
                    "description": "Maximum number of optimization iterations recommended"
                },
                "target_audience": {
                    "type": "string",
                    "description": "The target audience for the response"
                },
                "special_considerations": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Any special considerations for this task"
                }
            },
            "required": ["task_type", "criteria", "max_iterations", "target_audience"]
        }
    }
    
    # Prepare the criteria definition prompt
    criteria_prompt = f"""
    {generate_agent_context(personas.get("evaluator_agent", {}))}
    
    USER QUERY: {user_query}
    
    Before generating a response, we need to establish clear evaluation criteria.
    Your task is to analyze this query and determine:
    
    1. What type of task is being requested (e.g., creative writing, informational content, technical explanation)
    2. What criteria should be used to evaluate the quality of the response
    3. The relative importance (weight) of each criterion
    4. How many iterations might be needed to refine the response
    5. Who the target audience appears to be
    6. Any special considerations that should be taken into account
    
    Define these evaluation parameters to guide the content creation and refinement process.
    """
    
    try:
        # Get criteria using function calling
        criteria_response = await functions_client.generate_with_functions(
            criteria_prompt,
            [criteria_function],
            function_call={"name": "define_evaluation_criteria"},
            temperature=0.4
        )
        
        if criteria_response["type"] == "function_call" and criteria_response["name"] == "define_evaluation_criteria":
            criteria_data = criteria_response["arguments"]
        else:
            # Fallback if no function call was returned
            logging.warning("Criteria function call not returned, using default criteria")
            criteria_data = {
                "task_type": "general response",
                "criteria": [
                    {
                        "name": "Accuracy",
                        "description": "Factual correctness and precision of information",
                        "weight": 0.4
                    },
                    {
                        "name": "Completeness",
                        "description": "Coverage of all aspects of the query",
                        "weight": 0.3
                    },
                    {
                        "name": "Clarity",
                        "description": "Clear, concise, and well-organized presentation",
                        "weight": 0.3
                    }
                ],
                "max_iterations": 3,
                "target_audience": "General user",
                "special_considerations": []
            }
    except Exception as e:
        logging.error(f"Error in criteria definition: {str(e)}")
        criteria_data = {
            "task_type": "general response",
            "criteria": [
                {
                    "name": "Accuracy",
                    "description": "Factual correctness and precision of information",
                    "weight": 0.4
                },
                {
                    "name": "Completeness",
                    "description": "Coverage of all aspects of the query",
                    "weight": 0.3
                },
                {
                    "name": "Clarity",
                    "description": "Clear, concise, and well-organized presentation",
                    "weight": 0.3
                }
            ],
            "max_iterations": 3,
            "target_audience": "General user",
            "special_considerations": []
        }
    
    # Record the criteria definition step
    intermediate_steps.append(AgentResponse(
        agent_role="Evaluation Criteria Designer",
        content=f"Task Type: {criteria_data['task_type']}\n\n" +
                f"Target Audience: {criteria_data['target_audience']}\n\n" +
                f"Maximum Iterations: {criteria_data['max_iterations']}\n\n" +
                "Evaluation Criteria:\n" + "\n".join([
                    f"- {c['name']} (Weight: {c['weight']}): {c['description']}"
                    for c in criteria_data['criteria']
                ]) + "\n\n" +
                (f"Special Considerations:\n" + "\n".join([f"- {c}" for c in criteria_data.get('special_considerations', [])]) 
                 if criteria_data.get('special_considerations') else ""),
        metadata=criteria_data
    ))
    
    # Step 2: Generate initial response using the generator agent
    generator_agent = personas.get("generator_agent", {})
    
    # Prepare the generator prompt
    generator_prompt = f"""
    {generate_agent_context(generator_agent)}
    
    USER QUERY: {user_query}
    
    TASK TYPE: {criteria_data['task_type']}
    TARGET AUDIENCE: {criteria_data['target_audience']}
    
    Your task is to generate an initial response to the user's query.
    Focus on creating content that meets these key criteria:
    
    {format_criteria(criteria_data['criteria'])}
    
    {format_special_considerations(criteria_data.get('special_considerations', []))}
    
    This is the first draft, which will be evaluated and refined, so aim for a comprehensive 
    initial response that addresses all aspects of the query.
    """
    
    try:
        # Get initial response
        initial_response = await llm_client.generate(generator_prompt, temperature=0.7)
    except Exception as e:
        logging.error(f"Error generating initial response: {str(e)}")
        initial_response = f"I apologize, but I encountered an issue while generating the initial response. Error: {str(e)}"
    
    # Record the initial generation step
    intermediate_steps.append(AgentResponse(
        agent_role="Content Creator",
        content=initial_response,
        metadata={"iteration": 1, "stage": "initial_generation"}
    ))
    
    # Initialize current response
    current_response = initial_response
    max_iterations = min(criteria_data["max_iterations"], 3)  # Cap at 3 to prevent excessive iterations
    
    # Define the evaluation function
    evaluation_function = {
        "name": "evaluate_response",
        "description": "Evaluates a response against defined criteria",
        "parameters": {
            "type": "object",
            "properties": {
                "overall_score": {
                    "type": "number",
                    "description": "Overall score of the response (0.0 to 1.0)"
                },
                "criterion_scores": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "criterion": {
                                "type": "string",
                                "description": "Name of the criterion"
                            },
                            "score": {
                                "type": "number",
                                "description": "Score for this criterion (0.0 to 1.0)"
                            },
                            "feedback": {
                                "type": "string",
                                "description": "Specific feedback for this criterion"
                            }
                        },
                        "required": ["criterion", "score", "feedback"]
                    },
                    "description": "Scores and feedback for each criterion"
                },
                "improvement_suggestions": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Specific suggestions for improvement"
                },
                "is_satisfactory": {
                    "type": "boolean",
                    "description": "Whether the response is satisfactory or needs further improvement"
                }
            },
            "required": ["overall_score", "criterion_scores", "improvement_suggestions", "is_satisfactory"]
        }
    }
    
    # Iterative refinement loop
    for iteration in range(1, max_iterations + 1):
        # Skip evaluation on the final iteration
        if iteration == max_iterations:
            break
            
        # Step 3: Evaluate the current response
        evaluator_agent = personas.get("evaluator_agent", {})
        
        # Prepare the evaluator prompt
        evaluator_prompt = f"""
        {generate_agent_context(evaluator_agent)}
        
        ORIGINAL USER QUERY: {user_query}
        
        TASK TYPE: {criteria_data['task_type']}
        TARGET AUDIENCE: {criteria_data['target_audience']}
        
        CURRENT RESPONSE (ITERATION {iteration}):
        {current_response}
        
        Your task is to evaluate this response against the following criteria:
        
        {format_criteria(criteria_data['criteria'])}
        
        {format_special_considerations(criteria_data.get('special_considerations', []))}
        
        Provide a detailed evaluation of how well the response meets each criterion,
        along with specific suggestions for improvement.
        """
        
        try:
            # Get evaluation using function calling
            evaluation_response = await functions_client.generate_with_functions(
                evaluator_prompt,
                [evaluation_function],
                function_call={"name": "evaluate_response"},
                temperature=0.5
            )
            
            if evaluation_response["type"] == "function_call" and evaluation_response["name"] == "evaluate_response":
                evaluation = evaluation_response["arguments"]
            else:
                # Fallback if no function call was returned
                logging.warning("Evaluation function call not returned, using default evaluation")
                evaluation = {
                    "overall_score": 0.7,
                    "criterion_scores": [
                        {
                            "criterion": c["name"],
                            "score": 0.7,
                            "feedback": f"The response could be improved in terms of {c['name'].lower()}"
                        } for c in criteria_data["criteria"]
                    ],
                    "improvement_suggestions": ["Consider revising for clarity and completeness"],
                    "is_satisfactory": False
                }
        except Exception as e:
            logging.error(f"Error in response evaluation: {str(e)}")
            evaluation = {
                "overall_score": 0.7,
                "criterion_scores": [
                    {
                        "criterion": c["name"],
                        "score": 0.7,
                        "feedback": f"Error during evaluation: {str(e)}"
                    } for c in criteria_data["criteria"]
                ],
                "improvement_suggestions": ["Unable to provide specific suggestions due to an error"],
                "is_satisfactory": False
            }
        
        # Record the evaluation step
        intermediate_steps.append(AgentResponse(
            agent_role="Quality Assessor",
            content=f"Overall Score: {evaluation['overall_score']:.2f}\n\n" +
                    "Criterion Scores:\n" + "\n".join([
                        f"- {s['criterion']}: {s['score']:.2f} - {s['feedback']}"
                        for s in evaluation['criterion_scores']
                    ]) + "\n\n" +
                    "Improvement Suggestions:\n" + "\n".join([
                        f"- {s}" for s in evaluation['improvement_suggestions']
                    ]) + "\n\n" +
                    f"Is Satisfactory: {'Yes' if evaluation['is_satisfactory'] else 'No'}",
            metadata={"iteration": iteration, "stage": "evaluation", **evaluation}
        ))
        
        # If the response is satisfactory, break the loop
        if evaluation["is_satisfactory"]:
            break
            
        # Step 4: Optimize the response based on evaluation
        optimizer_agent = personas.get("optimizer_agent", {})
        
        # Prepare the optimizer prompt
        optimizer_prompt = f"""
        {generate_agent_context(optimizer_agent)}
        
        ORIGINAL USER QUERY: {user_query}
        
        TASK TYPE: {criteria_data['task_type']}
        TARGET AUDIENCE: {criteria_data['target_audience']}
        
        CURRENT RESPONSE (ITERATION {iteration}):
        {current_response}
        
        EVALUATION:
        Overall Score: {evaluation['overall_score']:.2f}
        
        Criterion Scores:
        {format_criterion_scores(evaluation['criterion_scores'])}
        
        Improvement Suggestions:
        {format_suggestions(evaluation['improvement_suggestions'])}
        
        Your task is to optimize the response based on this evaluation.
        Focus on addressing the specific improvement suggestions while maintaining 
        the strengths of the current response.
        
        Create an improved version that better meets all the evaluation criteria.
        """
        
        try:
            # Get optimized response
            optimized_response = await llm_client.generate(optimizer_prompt, temperature=0.6)
        except Exception as e:
            logging.error(f"Error in response optimization: {str(e)}")
            optimized_response = current_response + "\n\n[Note: An error occurred during optimization. This is the previous version.]"
        
        # Record the optimization step
        intermediate_steps.append(AgentResponse(
            agent_role="Refinement Specialist",
            content=optimized_response,
            metadata={"iteration": iteration + 1, "stage": "optimization"}
        ))
        
        # Update current response for next iteration
        current_response = optimized_response
    
    # Return the final response
    return current_response, intermediate_steps

def format_criteria(criteria):
    """Format criteria for prompts"""
    return "\n".join([
        f"- {c['name']} (Weight: {c['weight']}): {c['description']}"
        for c in criteria
    ])

def format_special_considerations(considerations):
    """Format special considerations for prompts"""
    if not considerations:
        return ""
    return "Special Considerations:\n" + "\n".join([f"- {c}" for c in considerations])

def format_criterion_scores(scores):
    """Format criterion scores for the optimizer prompt"""
    return "\n".join([
        f"- {s['criterion']}: {s['score']:.2f} - {s['feedback']}"
        for s in scores
    ])

def format_suggestions(suggestions):
    """Format improvement suggestions for the optimizer prompt"""
    return "\n".join([f"- {s}" for s in suggestions])

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