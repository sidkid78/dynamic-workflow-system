# tests/integration/test_api_frontend_integration.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
import json
from unittest.mock import patch, MagicMock
import re

client = TestClient(app)

@pytest.mark.integration
def test_api_response_format_for_frontend():
    """
    Test that the API returns data in a format that the frontend can consume
    This verifies the contract between backend and frontend
    """
    # Mock LLM calls to avoid real API usage
    with patch('app.core.workflow_selector.get_functions_client') as mock_selector, \
         patch('app.core.workflows.prompt_chaining.get_llm_client') as mock_llm:
        
        # Configure workflow selector mock
        selector_client = MagicMock()
        selector_client.generate_with_functions.return_value = {
            "type": "function_call",
            "name": "select_workflow",
            "arguments": {
                "selected_workflow": "prompt_chaining",
                "reasoning": "Test reasoning",
                "required_agents": ["Initial Processor", "Validator", "Refiner"]
            }
        }
        mock_selector.return_value = selector_client
        
        # Configure LLM client mock
        llm_client = MagicMock()
        llm_client.generate.side_effect = [
            "Analysis of the query",
            "PASS: The analysis is good",
            "Final response content with *markdown* formatting"
        ]
        mock_llm.return_value = llm_client
        
        # Make API request
        response = client.post(
            "/api/workflows/process",
            json={"query": "Test query for frontend integration"}
        )
        
        # Verify response status
        assert response.status_code == 200
        
        # Get response data
        data = response.json()
        
        # Verify response structure matches frontend expectations
        assert "final_response" in data
        assert "workflow_info" in data
        assert "intermediate_steps" in data
        assert "processing_time" in data
        
        # Check workflow_info structure
        assert "selected_workflow" in data["workflow_info"]
        assert "reasoning" in data["workflow_info"]
        assert "required_agents" in data["workflow_info"]
        assert "personas" in data["workflow_info"]
        
        # Verify personas format
        assert data["workflow_info"]["selected_workflow"] in data["workflow_info"]["personas"]
        
        # Check intermediate_steps structure
        for step in data["intermediate_steps"]:
            assert "agent_role" in step
            assert "content" in step
            if "metadata" in step:
                # Ensure metadata is JSON serializable
                json.dumps(step["metadata"])
        
        # Ensure processing_time is a number
        assert isinstance(data["processing_time"], (int, float))
        
        # Verify markdown formatting is preserved
        assert "*markdown*" in data["final_response"]


@pytest.mark.integration
def test_error_response_format():
    """
    Test that API errors are returned in a consistent format that the frontend can handle
    """
    # Force an error by making the workflow selection throw an exception
    with patch('app.api.endpoints.workflows.select_workflow', side_effect=Exception("Test error message")):
        response = client.post(
            "/api/workflows/process",
            json={"query": "This should cause an error"}
        )
        
        # Verify error response
        assert response.status_code == 500
        data = response.json()
        
        # Check error format
        assert "detail" in data
        assert "Test error message" in data["detail"]


@pytest.mark.integration
def test_health_endpoint():
    """Test the health check endpoint used for monitoring"""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"