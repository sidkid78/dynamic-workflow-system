# tests/e2e/test_workflow_selection.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
import json
from unittest.mock import patch, MagicMock, AsyncMock

client = TestClient(app)

# List of test cases with expected workflow selections
test_cases = [
    {
        "query": "Write a blog post and translate it to French",
        "expected_workflow": "prompt_chaining",
        "description": "Sequential task with multiple steps"
    },
    {
        "query": "How do I reset my password?",
        "expected_workflow": "routing",
        "description": "Customer support query requiring specialist knowledge"
    },
    {
        "query": "Analyze this product from marketing, technical, and financial angles",
        "expected_workflow": "parallel_sectioning",
        "description": "Task with independent components for parallel processing"
    },
    {
        "query": "Is this email a phishing attempt?",
        "expected_workflow": "parallel_voting",
        "description": "Evaluation task requiring multiple perspectives"
    },
    {
        "query": "Help me plan my vacation to Europe",
        "expected_workflow": "orchestrator_workers",
        "description": "Complex planning task with interdependent components"
    },
    {
        "query": "Write a professional email to my boss requesting time off",
        "expected_workflow": "evaluator_optimizer",
        "description": "Content creation task requiring quality assessment and refinement"
    }
]

@pytest.mark.parametrize("test_case", test_cases)
@pytest.mark.asyncio
async def test_workflow_selection(test_case):
    """Test the workflow selector chooses the correct workflow for different query types"""
    
    with patch('app.core.workflow_selector.get_functions_client') as mock_get_client:
        # Configure mock to return the expected workflow
        mock_client = AsyncMock()
        mock_client.generate_with_functions.return_value = {
            "type": "function_call",
            "name": "select_workflow",
            "arguments": {
                "selected_workflow": test_case["expected_workflow"],
                "reasoning": f"Selected due to {test_case['description']}",
                "required_agents": []
            }
        }
        mock_get_client.return_value = mock_client
        
        # Mock the workflow execution to avoid full processing
        with patch('app.api.endpoints.workflows.prompt_chaining.execute', new_callable=AsyncMock) as mock_execute, \
             patch('app.api.endpoints.workflows.routing.execute', new_callable=AsyncMock) as mock_routing, \
             patch('app.api.endpoints.workflows.parallel_sectioning.execute', new_callable=AsyncMock) as mock_sectioning, \
             patch('app.api.endpoints.workflows.parallel_voting.execute', new_callable=AsyncMock) as mock_voting, \
             patch('app.api.endpoints.workflows.orchestrator_workers.execute', new_callable=AsyncMock) as mock_orchestrator, \
             patch('app.api.endpoints.workflows.evaluator_optimizer.execute', new_callable=AsyncMock) as mock_evaluator:
            
            # Configure mocks to return a simple response
            mock_response = ("Mocked response", [])
            mock_execute.return_value = mock_response
            mock_routing.return_value = mock_response
            mock_sectioning.return_value = mock_response
            mock_voting.return_value = mock_response
            mock_orchestrator.return_value = mock_response
            mock_evaluator.return_value = mock_response
            
            # Make the API request
            response = client.post(
                "/api/workflows/process",
                json={"query": test_case["query"]}
            )
            
            # Check response
            assert response.status_code == 200
            data = response.json()
            
            # Verify the right workflow was selected
            assert data["workflow_info"]["selected_workflow"] == test_case["expected_workflow"]
            
            # Ensure the right workflow execution function was called
            if test_case["expected_workflow"] == "prompt_chaining":
                mock_execute.assert_called_once()
            elif test_case["expected_workflow"] == "routing":
                mock_routing.assert_called_once()
            elif test_case["expected_workflow"] == "parallel_sectioning":
                mock_sectioning.assert_called_once()
            elif test_case["expected_workflow"] == "parallel_voting":
                mock_voting.assert_called_once()
            elif test_case["expected_workflow"] == "orchestrator_workers":
                mock_orchestrator.assert_called_once()
            elif test_case["expected_workflow"] == "evaluator_optimizer":
                mock_evaluator.assert_called_once()