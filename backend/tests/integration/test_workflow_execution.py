import pytest
from unittest.mock import patch, AsyncMock
from app.core.workflow_selector import select_workflow
from app.api.endpoints.workflows import process_query
from app.models.schemas import QueryRequest
import json
import os

# Should integration tests use real API calls?
USE_REAL_API = os.getenv("TEST_USE_REAL_API", "False").lower() in ("true", "1", "t")

@pytest.mark.integration
@pytest.mark.asyncio
async def test_workflow_selector_to_execution_integration():
    """
    Test the integration between workflow selector and execution
    """
    if USE_REAL_API:
        # Skip mocking if using real API
        pass
    else:
        # Setup mocks for workflow selector
        with patch('app.core.workflow_selector.get_functions_client') as mock_functions_client, \
             patch('app.core.workflows.prompt_chaining.get_llm_client') as mock_llm_client:
            
            # Mock the workflow selector to choose prompt_chaining
            functions_client = AsyncMock()
            functions_client.generate_with_functions.return_value = {
                "type": "function_call",
                "name": "select_workflow",
                "arguments": {
                    "selected_workflow": "prompt_chaining",
                    "reasoning": "This is a sequential task",
                    "required_agents": ["Initial Processor", "Validator", "Refiner"]
                }
            }
            mock_functions_client.return_value = functions_client
            
            # Mock the LLM client for prompt_chaining
            llm_client = AsyncMock()
            llm_client.generate.side_effect = [
                "Analysis of the query",
                "PASS: The analysis is good",
                "Final response content"
            ]
            mock_llm_client.return_value = llm_client
            
            # Create a query request
            request = QueryRequest(query="Summarize this article and create bullet points")
            
            # Process the query
            response = await process_query(request)
            
            # Verify the response
            assert response.workflow_info.selected_workflow == "prompt_chaining"
            assert len(response.intermediate_steps) == 3
            assert response.final_response == "Final response content"
            
            # Verify the right functions were called
            functions_client.generate_with_functions.assert_called_once()
            assert llm_client.generate.call_count == 3

@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize("workflow_type", [
    "prompt_chaining",
    "routing",
    "parallel_sectioning",
    "parallel_voting",
    "orchestrator_workers",
    "evaluator_optimizer"
])
async def test_each_workflow_integration(workflow_type):
    """
    Test each workflow type with minimal mocking to verify integration
    """
    if USE_REAL_API:
        # Skip mocking if using real API
        pass
    else:
        # Setup mocks for the test
        with patch('app.core.workflow_selector.get_functions_client') as mock_selector, \
             patch(f'app.core.workflows.{workflow_type}.get_llm_client') as mock_llm, \
             patch(f'app.core.workflows.{workflow_type}.get_functions_client', return_value=AsyncMock()) as mock_functions:
            
            # Configure workflow selector mock
            selector_client = AsyncMock()
            selector_client.generate_with_functions.return_value = {
                "type": "function_call",
                "name": "select_workflow",
                "arguments": {
                    "selected_workflow": workflow_type,
                    "reasoning": f"Test case for {workflow_type}",
                    "required_agents": []
                }
            }
            mock_selector.return_value = selector_client
            
            # Configure LLM client mock with appropriate number of responses
            llm_client = AsyncMock()
            # Different workflows need different numbers of responses
            response_count = {
                "prompt_chaining": 3,
                "routing": 1,
                "parallel_sectioning": 5,  # 1 for each worker + 1 for aggregator
                "parallel_voting": 4,  # 1 for each perspective + 1 for consensus
                "orchestrator_workers": 7,  # 1 for each worker + 1 for synthesizer
                "evaluator_optimizer": 4  # Initial + evaluations + optimizations
            }
            llm_client.generate.side_effect = [f"Mock response {i}" for i in range(response_count.get(workflow_type, 3))]
            mock_llm.return_value = llm_client
            
            # Create a query request
            request = QueryRequest(query=f"Test query for {workflow_type}")
            
            # Process the query
            response = await process_query(request)
            
            # Verify the response
            assert response.workflow_info.selected_workflow == workflow_type
            assert len(response.intermediate_steps) > 0
            
            # Verify the right functions were called
            selector_client.generate_with_functions.assert_called_once()
            assert llm_client.generate.call_count > 0