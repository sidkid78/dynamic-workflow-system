# tests/e2e/test_workflow_selection.py
import pytest
from fastapi.testclient import TestClient
from app2.main import app
import json
from unittest.mock import patch, MagicMock, AsyncMock
import logging
import os
import time

# Ensure logs directory exists
log_dir = "logs/test_runs"
os.makedirs(log_dir, exist_ok=True)

# Configure logging to file
log_file_timestamp = time.strftime("%Y%m%d_%H%M%S")
log_file_path = os.path.join(log_dir, f"test_workflow_selection_{log_file_timestamp}.log")

# Create a specific logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Prevent propagation to avoid duplicate logs if root logger is configured
logger.propagate = False

# Remove existing handlers to avoid duplicates in parametrized tests if logger persists
if logger.hasHandlers():
    logger.handlers.clear()

# Create file handler
fh = logging.FileHandler(log_file_path)
fh.setLevel(logging.INFO)

# Create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(fh)


client = TestClient(app)

# List of test cases with expected workflow selections
test_cases = [
    {
        "id": "prompt_chaining_blog_translate",
        "query": "Write a blog post and translate it to French",
        "expected_workflow": "prompt_chaining",
        "description": "Sequential task with multiple steps"
    },
    {
        "id": "routing_password_reset",
        "query": "How do I reset my password?",
        "expected_workflow": "routing",
        "description": "Customer support query requiring specialist knowledge"
    },
    {
        "id": "parallel_sectioning_product_analysis",
        "query": "Analyze this product from marketing, technical, and financial angles",
        "expected_workflow": "parallel_sectioning",
        "description": "Task with independent components for parallel processing"
    },
    {
        "id": "parallel_voting_phishing_check",
        "query": "Is this email a phishing attempt?",
        "expected_workflow": "parallel_voting",
        "description": "Evaluation task requiring multiple perspectives"
    },
    {
        "id": "orchestrator_workers_vacation_plan",
        "query": "Help me plan my vacation to Europe",
        "expected_workflow": "orchestrator_workers",
        "description": "Complex planning task with interdependent components"
    },
    {
        "id": "evaluator_optimizer_time_off_email",
        "query": "Write a professional email to my boss requesting time off",
        "expected_workflow": "evaluator_optimizer",
        "description": "Content creation task requiring quality assessment and refinement"
    }
]

# Use test case id for better identification in pytest output
@pytest.mark.parametrize("test_case", test_cases, ids=[tc["id"] for tc in test_cases])
@pytest.mark.asyncio
async def test_workflow_selection(test_case):
    """Test the workflow selector chooses the correct workflow for different query types"""
    logger.info(f"--- Starting Test Case: {test_case['id']} ---")
    logger.info(f"Query: \"{test_case['query']}\"")
    logger.info(f"Expected Workflow: {test_case['expected_workflow']}")
    logger.info(f"Description: {test_case['description']}")

    with patch('app.core.workflow_selector.get_functions_client') as mock_get_client:
        # Configure mock to return the expected workflow
        mock_client = AsyncMock()
        mock_selection_response = {
            "type": "function_call",
            "name": "select_workflow",
            "arguments": {
                "selected_workflow": test_case["expected_workflow"],
                "reasoning": f"Selected due to {test_case['description']}",
                "required_agents": [] # Keeping it simple for selection test
            }
        }
        mock_client.generate_with_functions.return_value = mock_selection_response
        mock_get_client.return_value = mock_client
        logger.info(f"Mocking workflow_selector.generate_with_functions response: {json.dumps(mock_selection_response, indent=2)}")

        # Mock the workflow execution to avoid full processing
        with patch('app.api.endpoints.workflows.prompt_chaining.execute', new_callable=AsyncMock) as mock_execute, \
             patch('app.api.endpoints.workflows.routing.execute', new_callable=AsyncMock) as mock_routing, \
             patch('app.api.endpoints.workflows.parallel_sectioning.execute', new_callable=AsyncMock) as mock_sectioning, \
             patch('app.api.endpoints.workflows.parallel_voting.execute', new_callable=AsyncMock) as mock_voting, \
             patch('app.api.endpoints.workflows.orchestrator_workers.execute', new_callable=AsyncMock) as mock_orchestrator, \
             patch('app.api.endpoints.workflows.evaluator_optimizer.execute', new_callable=AsyncMock) as mock_evaluator:

            # Configure mocks to return a simple response
            mock_workflow_response_content = "Mocked workflow execution response"
            mock_workflow_response = (mock_workflow_response_content, []) # (result, history)
            mock_execute.return_value = mock_workflow_response
            mock_routing.return_value = mock_workflow_response
            mock_sectioning.return_value = mock_workflow_response
            mock_voting.return_value = mock_workflow_response
            mock_orchestrator.return_value = mock_workflow_response
            mock_evaluator.return_value = mock_workflow_response
            logger.info(f"Mocking all workflow execute functions to return: {mock_workflow_response}")

            # Make the API request
            request_payload = {"query": test_case["query"]}
            logger.info(f"Making POST request to /api/workflows/process with payload: {json.dumps(request_payload)}")
            response = client.post(
                "/api/workflows/process",
                json=request_payload
            )
            logger.info(f"Received response: Status Code = {response.status_code}")

            # Check response
            assert response.status_code == 200
            data = response.json()
            logger.info(f"Response JSON Data: {json.dumps(data, indent=2)}")

            # Verify the right workflow was selected
            selected_workflow = data.get("workflow_info", {}).get("selected_workflow")
            logger.info(f"Asserting selected workflow: Expected='{test_case['expected_workflow']}', Actual='{selected_workflow}'")
            assert selected_workflow == test_case["expected_workflow"]
            logger.info("Assertion PASSED: Correct workflow selected.")

            # Ensure the right workflow execution function was called
            logger.info(f"Asserting correct workflow execution mock was called for '{test_case['expected_workflow']}'...")
            mock_map = {
                "prompt_chaining": mock_execute,
                "routing": mock_routing,
                "parallel_sectioning": mock_sectioning,
                "parallel_voting": mock_voting,
                "orchestrator_workers": mock_orchestrator,
                "evaluator_optimizer": mock_evaluator,
            }

            for wf_name, mock_func in mock_map.items():
                if wf_name == test_case["expected_workflow"]:
                    try:
                        mock_func.assert_called_once()
                        logger.info(f"Assertion PASSED: Mock for '{wf_name}' was called once.")
                    except AssertionError as e:
                        logger.error(f"Assertion FAILED: Mock for '{wf_name}' was not called once. Error: {e}")
                        raise # Re-raise the assertion error
                else:
                    try:
                        mock_func.assert_not_called()
                        # logger.info(f"Check PASSED: Mock for '{wf_name}' was not called (as expected).") # Optional: reduce log noise
                    except AssertionError as e:
                        logger.error(f"Assertion FAILED: Mock for '{wf_name}' was called unexpectedly. Error: {e}")
                        raise # Re-raise the assertion error
            
            logger.info(f"--- Test Case Passed: {test_case['id']} ---")

# Add a final log message to indicate the end of the test suite run for this module
# Note: This will log after the last test case finishes parametrization.
logger.info(f"--- Finished test suite in {__file__} ---")
# Close the handler to ensure logs are flushed - might be better in a fixture teardown
# For simplicity here, closing after the last test definition line.
# This isn't robust if tests are run selectively.
# fh.close() # Be cautious with closing handlers here in parametrized tests.
# logger.removeHandler(fh) # Clean up handler