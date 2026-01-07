"""
Parallel Section-Voting Workflow

A hybrid workflow that combines parallel sectioning (task decomposition) with 
multi-perspective voting (quality validation) for higher quality outputs.

Workflow Phases:
1. Task Sectioning: Break the query into 3-5 independent subtasks
2. Parallel Processing: Process each subtask with a worker agent
3. Multi-Perspective Voting: Evaluate each worker output from multiple perspectives
4. Consensus Aggregation: Combine validated section outputs into a cohesive response
"""

from app.models.schemas import WorkflowSelection, AgentResponse
from app.core.llm_client import get_llm_client, get_functions_client
from app.core.helpers.persona_utils import generate_agent_context, get_agent_config
from typing import Tuple, List, Dict, Any
import logging
import asyncio


async def execute(workflow_selection: WorkflowSelection, user_query: str) -> Tuple[str, List[AgentResponse]]:
    """
    Executes the parallel section-voting workflow.
    
    This hybrid workflow combines task decomposition with multi-perspective validation:
    1. Sections the task into independent subtasks
    2. Processes each subtask in parallel with worker agents
    3. Validates each worker output through multi-perspective voting
    4. Aggregates validated results into a cohesive final response
    
    Args:
        workflow_selection: Contains workflow configuration and agent personas
        user_query: The original query from the user to be processed
        
    Returns:
        A tuple containing:
        - The final aggregated response as a string
        - A list of intermediate AgentResponse objects tracking the workflow execution
    """
    functions_client = get_functions_client()
    llm_client = get_llm_client()
    personas = workflow_selection.personas.get("parallel_section_voting", {})
    intermediate_steps = []
    
    # ==========================================================================
    # PHASE 1: Task Sectioning
    # ==========================================================================
    section_planner = personas.get("section_planner", {})
    planner_config = get_agent_config(section_planner)
    
    task_breakdown_function = {
        "name": "break_into_sections",
        "description": "Breaks down a complex task into independent sections that can be processed and validated in parallel",
        "parameters": {
            "type": "object",
            "properties": {
                "sections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "Unique identifier for the section"
                            },
                            "title": {
                                "type": "string",
                                "description": "Brief title of the section"
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed description of what the section covers"
                            },
                            "perspective": {
                                "type": "string",
                                "description": "The perspective or angle for this section"
                            },
                            "validation_criteria": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Criteria for validating this section's output"
                            }
                        },
                        "required": ["id", "title", "description", "perspective", "validation_criteria"]
                    },
                    "description": "List of independent sections"
                },
                "reasoning": {
                    "type": "string",
                    "description": "Explanation of how the task was broken down"
                }
            },
            "required": ["sections", "reasoning"]
        }
    }
    
    sectioning_prompt = f"""
    {generate_agent_context(section_planner)}
    
    USER QUERY: {user_query}
    
    Your task is to break down this complex query into 3-5 independent sections that can be:
    1. Processed in parallel by worker agents
    2. Validated through multi-perspective voting
    
    For each section:
    - Focus on a different aspect or perspective of the overall task
    - Be completely independent of the others
    - Define clear validation criteria for quality assessment
    
    The validation criteria will be used by voting agents to evaluate each section's output.
    """
    
    try:
        breakdown_response = await functions_client.generate_with_functions(
            sectioning_prompt,
            [task_breakdown_function],
            function_call={"name": "break_into_sections"}
        )
        
        if breakdown_response["type"] == "function_call" and breakdown_response["name"] == "break_into_sections":
            task_breakdown = breakdown_response["arguments"]
        else:
            logging.warning("Task breakdown function call not returned, using default breakdown")
            task_breakdown = _get_default_breakdown()
    except Exception as e:
        logging.error(f"Error in task breakdown: {str(e)}")
        task_breakdown = _get_default_breakdown(str(e))
    
    # Record the sectioning step
    intermediate_steps.append(AgentResponse(
        agent_role="Section Planner",
        content=f"Task Breakdown:\n{task_breakdown['reasoning']}\n\nSections:\n" + 
                "\n".join([f"- {s['title']}: {s['description']} (Criteria: {', '.join(s['validation_criteria'])})" 
                           for s in task_breakdown['sections']]),
        metadata=task_breakdown
    ))
    
    # ==========================================================================
    # PHASE 2 & 3: Parallel Processing with Voting
    # ==========================================================================
    section_worker = personas.get("section_worker", {})
    section_voter = personas.get("section_voter", {})
    
    async def process_and_vote_section(section: Dict[str, Any]) -> Dict[str, Any]:
        """Process a section and validate through voting"""
        
        # Step 2a: Worker processes the section
        worker_prompt = f"""
        {generate_agent_context(section_worker)}
        
        ORIGINAL USER QUERY: {user_query}
        
        SECTION: {section['title']}
        DESCRIPTION: {section['description']}
        PERSPECTIVE: {section['perspective']}
        
        Your task is to provide a thorough, high-quality response for this specific section.
        Focus exclusively on this aspect of the overall query.
        """
        
        try:
            worker_response = await llm_client.generate(
                worker_prompt, 
                temperature=get_agent_config(section_worker).get("temperature", 0.7)
            )
        except Exception as e:
            logging.error(f"Error processing section {section['id']}: {str(e)}")
            worker_response = f"Error processing this section: {str(e)}"
        
        # Step 2b: Multi-perspective voting on the worker output
        voting_perspectives = ["accuracy", "completeness", "clarity"]
        votes = await asyncio.gather(
            *[vote_on_section(section, worker_response, perspective, section_voter) 
              for perspective in voting_perspectives]
        )
        
        # Calculate consensus
        approval_count = sum(1 for v in votes if v["judgment"] == "approve")
        avg_confidence = sum(v["confidence"] for v in votes) / len(votes)
        consensus = "approved" if approval_count >= 2 else "needs_revision"
        
        return {
            "section_id": section["id"],
            "title": section["title"],
            "perspective": section["perspective"],
            "worker_response": worker_response,
            "votes": votes,
            "consensus": consensus,
            "approval_count": approval_count,
            "avg_confidence": avg_confidence,
            "validation_criteria": section["validation_criteria"]
        }
    
    # Process all sections in parallel (each section goes through worker + voting)
    section_results = await asyncio.gather(
        *[process_and_vote_section(section) for section in task_breakdown["sections"]]
    )
    
    # Record worker and voting steps
    for result in section_results:
        # Worker step
        intermediate_steps.append(AgentResponse(
            agent_role=f"{result['perspective']} Worker",
            content=result["worker_response"],
            metadata={
                "section_id": result["section_id"],
                "title": result["title"]
            }
        ))
        
        # Voting step
        vote_summary = "\n".join([
            f"- {v['perspective'].capitalize()}: {v['judgment'].upper()} (confidence: {v['confidence']:.0%})"
            for v in result["votes"]
        ])
        intermediate_steps.append(AgentResponse(
            agent_role=f"{result['title']} Voter Panel",
            content=f"Consensus: {result['consensus'].upper()}\n"
                    f"Approval Rate: {result['approval_count']}/{len(result['votes'])}\n"
                    f"Average Confidence: {result['avg_confidence']:.0%}\n\n"
                    f"Individual Votes:\n{vote_summary}",
            metadata={
                "section_id": result["section_id"],
                "consensus": result["consensus"],
                "votes": result["votes"]
            }
        ))
    
    # ==========================================================================
    # PHASE 4: Consensus Aggregation
    # ==========================================================================
    consensus_aggregator = personas.get("consensus_aggregator", {})
    
    aggregation_prompt = f"""
    {generate_agent_context(consensus_aggregator)}
    
    ORIGINAL USER QUERY: {user_query}
    
    You have received validated section outputs from multiple workers.
    Each section has been evaluated through multi-perspective voting.
    
    Your task is to synthesize these validated sections into a comprehensive, cohesive response.
    
    VALIDATED SECTIONS:
    
    {format_section_results(section_results)}
    
    Guidelines:
    1. Prioritize sections with higher approval ratings and confidence
    2. Maintain cohesion between sections while avoiding redundancy
    3. Address any sections that received lower consensus by integrating them carefully
    4. Provide a unified response that addresses the original query comprehensively
    """
    
    try:
        aggregated_response = await llm_client.generate(
            aggregation_prompt,
            temperature=get_agent_config(consensus_aggregator).get("temperature", 0.7)
        )
    except Exception as e:
        logging.error(f"Error in aggregation: {str(e)}")
        # Fallback: concatenate validated sections
        aggregated_response = "Here are the validated section responses:\n\n" + \
            "\n\n".join([f"**{r['title']}** (Confidence: {r['avg_confidence']:.0%}):\n{r['worker_response']}" 
                         for r in section_results])
    
    # Record the aggregation step
    intermediate_steps.append(AgentResponse(
        agent_role="Consensus Aggregator",
        content=aggregated_response,
        metadata={
            "section_count": len(section_results),
            "overall_confidence": sum(r["avg_confidence"] for r in section_results) / len(section_results),
            "all_approved": all(r["consensus"] == "approved" for r in section_results)
        }
    ))
    
    return aggregated_response, intermediate_steps


async def vote_on_section(
    section: Dict[str, Any], 
    worker_response: str, 
    perspective: str,
    voter_persona: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Vote on a section's worker output from a specific perspective.
    
    Args:
        section: The section definition with validation criteria
        worker_response: The worker's output to evaluate
        perspective: The voting perspective (accuracy, completeness, clarity)
        voter_persona: The voter agent's persona configuration
        
    Returns:
        A dictionary with judgment, confidence, and reasoning
    """
    functions_client = get_functions_client()
    
    vote_function = {
        "name": "cast_vote",
        "description": "Casts a vote on the quality of a section's output",
        "parameters": {
            "type": "object",
            "properties": {
                "judgment": {
                    "type": "string",
                    "enum": ["approve", "reject", "uncertain"],
                    "description": "The overall judgment"
                },
                "confidence": {
                    "type": "number",
                    "description": "Confidence in this judgment (0.0 to 1.0)"
                },
                "reasoning": {
                    "type": "string",
                    "description": "Explanation for the judgment"
                }
            },
            "required": ["judgment", "confidence", "reasoning"]
        }
    }
    
    vote_prompt = f"""
    {generate_agent_context(voter_persona)}
    
    You are evaluating a section's output from the perspective of: {perspective.upper()}
    
    SECTION: {section['title']}
    VALIDATION CRITERIA: {', '.join(section['validation_criteria'])}
    
    WORKER OUTPUT TO EVALUATE:
    {worker_response}
    
    Evaluate this output from your {perspective} perspective:
    - Does it meet the validation criteria?
    - Is it high quality from your perspective?
    - Should it be approved, rejected, or are you uncertain?
    
    Provide your judgment with confidence and reasoning.
    """
    
    try:
        vote_response = await functions_client.generate_with_functions(
            vote_prompt,
            [vote_function],
            function_call={"name": "cast_vote"}
        )
        
        if vote_response["type"] == "function_call" and vote_response["name"] == "cast_vote":
            vote = vote_response["arguments"]
            vote["perspective"] = perspective
            return vote
        else:
            return {
                "perspective": perspective,
                "judgment": "uncertain",
                "confidence": 0.5,
                "reasoning": "Unable to parse vote response"
            }
    except Exception as e:
        logging.error(f"Error in voting for section {section['id']} from {perspective}: {str(e)}")
        return {
            "perspective": perspective,
            "judgment": "uncertain",
            "confidence": 0.5,
            "reasoning": f"Error during voting: {str(e)}"
        }


def format_section_results(results: List[Dict[str, Any]]) -> str:
    """Format section results for the aggregation prompt."""
    formatted = ""
    for i, result in enumerate(results, 1):
        formatted += f"SECTION {i}: {result['title']}\n"
        formatted += f"Perspective: {result['perspective']}\n"
        formatted += f"Consensus: {result['consensus'].upper()} "
        formatted += f"(Approval: {result['approval_count']}/{len(result['votes'])}, "
        formatted += f"Confidence: {result['avg_confidence']:.0%})\n"
        formatted += f"Content:\n{result['worker_response']}\n\n"
    return formatted


def _get_default_breakdown(error_msg: str = None) -> Dict[str, Any]:
    """Get a default task breakdown as fallback."""
    return {
        "sections": [
            {
                "id": "section1",
                "title": "Primary Analysis",
                "description": "Main analysis of the query",
                "perspective": "Core perspective",
                "validation_criteria": ["Accuracy", "Relevance", "Completeness"]
            },
            {
                "id": "section2",
                "title": "Supporting Context",
                "description": "Additional context and considerations",
                "perspective": "Contextual perspective",
                "validation_criteria": ["Consistency", "Balance", "Objectivity"]
            }
        ],
        "reasoning": f"Fallback breakdown" + (f" due to error: {error_msg}" if error_msg else "")
    }
