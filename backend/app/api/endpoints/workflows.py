# app/api/endpoints/workflows.py
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import (
    QueryRequest, WorkflowResponse
)
from app.core.workflow_selector import select_workflow
from app.core.workflows import (
    prompt_chaining, routing,
    orchestrator_workers, evaluator_optimizer,
    prompt_generator, parallel_section_voting
)

from app.utils.response_saver import ResponseSaver
from app.config import settings
import time
import logging

router = APIRouter(
    prefix="/workflows",
    tags=["workflows"],
)

# Initialize ResponseSaver if enabled
response_saver = ResponseSaver(settings.RESPONSES_DIR) if settings.SAVE_RESPONSES else None

@router.post("/process", response_model=WorkflowResponse)
async def process_query(request: QueryRequest):
    """
    Process a user query through the appropriate workflow.
    
    This endpoint:
    1. Selects the most appropriate workflow for the query
    2. Executes the selected workflow
    3. Tracks intermediate processing steps
    4. Measures processing time
    5. Optionally saves the response to disk
    
    Args:
        request: The QueryRequest containing the user's query
        
    Returns:
        WorkflowResponse: Contains the final response, selected workflow,
                         intermediate steps, and processing time
                         
    Raises:
        HTTPException: If an unsupported workflow is selected or if processing fails
    """
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
        elif selected_workflow == "orchestrator_workers":
            final_response, steps = await orchestrator_workers.execute(workflow_selection, request.query)
        elif selected_workflow == "evaluator_optimizer":
            final_response, steps = await evaluator_optimizer.execute(workflow_selection, request.query)
        elif selected_workflow == "prompt_generator":
            final_response, steps = await prompt_generator.execute(workflow_selection, request.query)
        elif selected_workflow == "parallel_section_voting":
            final_response, steps = await parallel_section_voting.execute(workflow_selection, request.query)
        else:
            # Fallback to direct query if workflow is not recognized
            raise HTTPException(status_code=400, detail=f"Unsupported workflow: {selected_workflow}")
        
        intermediate_steps.extend(steps)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create the response object
        response = WorkflowResponse(
            workflow_info=workflow_selection,
            final_response=final_response,
            intermediate_steps=intermediate_steps,
            processing_time=processing_time
        )
        
        # Save the response to a file if enabled
        if response_saver is not None:
            try:
                saved_path = response_saver.save_response(response)
                logging.info(f"Response saved to: {saved_path}")
            except Exception as save_error:
                logging.error(f"Error saving response: {str(save_error)}")
                # Don't fail the request if saving fails
        
        return response
    
    except Exception as e:
        logging.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to get information about available tools
@router.get("/tools")
async def list_tools():
    """
    Get information about all available tools in the system.
    
    This endpoint retrieves details about registered tools including:
    - Total count of available tools
    - Name and description of each tool
    - Setup requirements and current setup status
    
    Returns:
        dict: A dictionary containing tool count and detailed information about each tool
    """
    from app.tools.registry import get_all_tools
    
    tools = get_all_tools()
    return {
        "tool_count": len(tools),
        "tools": [
            {
                "name": name,
                "description": tool.description,
                "requires_setup": tool.requires_setup,
                "is_setup": tool.is_setup
            }
            for name, tool in tools.items()
        ]
    }