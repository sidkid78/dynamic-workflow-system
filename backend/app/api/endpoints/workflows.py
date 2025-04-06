# app/api/endpoints/workflows.py
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import QueryRequest, WorkflowResponse
from app.core.workflow_selector import select_workflow
from app.core.workflows import (
    prompt_chaining, routing, parallel_sectioning,
    parallel_voting, orchestrator_workers, evaluator_optimizer, autonomous_agent
)
from app.tools.search_tools import create_search_tool_definition
import time
import logging

router = APIRouter(
    prefix="/workflows",
    tags=["workflows"],
)

@router.post("/process", response_model=WorkflowResponse)
async def process_query(request: QueryRequest):
    start_time = time.time()
    
    try:
        # Select the appropriate workflow
        workflow_selection = await select_workflow(request.query)
        
        # Execute the selected workflow
        selected_workflow = workflow_selection.selected_workflow
        intermediate_steps = []
        
        # Route to the appropriate workflow handler
        if selected_workflow == "prompt_chaining":
            final_response, steps = await prompt_chaining.execute(workflow_selection, request.query)
        elif selected_workflow == "routing":
            final_response, steps = await routing.execute(workflow_selection, request.query)
        elif selected_workflow == "parallel_sectioning":
            final_response, steps = await parallel_sectioning.execute(workflow_selection, request.query)
        elif selected_workflow == "parallel_voting":
            final_response, steps = await parallel_voting.execute(workflow_selection, request.query)
        elif selected_workflow == "orchestrator_workers":
            final_response, steps = await orchestrator_workers.execute(workflow_selection, request.query)
        elif selected_workflow == "evaluator_optimizer":
            final_response, steps = await evaluator_optimizer.execute(workflow_selection, request.query)
        elif selected_workflow == "autonomous_agent":
            # For the autonomous agent, we pass available tools
            from app.core.workflows.autonomous_agent import ToolDefinition
            
            # Create the Google search tool
            web_search_tool = create_search_tool_definition()
            
            # Define additional tools
            calculator_tool = ToolDefinition(
                name="calculator",
                description="Perform mathematical calculations",
                parameters={
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string", 
                            "description": "The mathematical expression to evaluate"
                        }
                    },
                    "required": ["expression"]
                },
                function=lambda expression: str(eval(expression))
            )
            
            # Wikipedia summary tool
            wikipedia_tool = ToolDefinition(
                name="wikipedia_summary",
                description="Get a summary of a topic from Wikipedia",
                parameters={
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string", 
                            "description": "The topic to look up"
                        }
                    },
                    "required": ["topic"]
                },
                # This is a placeholder - would need to implement actual Wikipedia API call
                function=lambda topic: f"Wikipedia summary for {topic} would be fetched here."
            )
            
            # Execute with tools
            final_response, steps = await autonomous_agent.execute(
                workflow_selection, 
                request.query,
                available_tools=[web_search_tool, calculator_tool, wikipedia_tool],
                max_iterations=5  # Limit iterations for API response time
            )
        else:
            # Fallback to direct query if workflow is not recognized
            raise HTTPException(status_code=400, detail=f"Unsupported workflow: {selected_workflow}")
        
        intermediate_steps.extend(steps)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return WorkflowResponse(
            final_response=final_response,
            workflow_info=workflow_selection,
            intermediate_steps=intermediate_steps,
            processing_time=processing_time
        )
    
    except Exception as e:
        logging.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))