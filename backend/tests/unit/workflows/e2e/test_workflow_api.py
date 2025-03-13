# tests/e2e/test_workflow_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
import json
from unittest.mock import patch, MagicMock, AsyncMock

client = TestClient(app)

@pytest.fixture
def mock_llm_responses():
    """Mock responses for all LLM calls in the end-to-end flow"""
    with patch('app.core.workflow_selector.get_functions_client') as mock_workflow_selector, \
         patch('app.core.workflows.prompt_chaining.get_llm_client') as mock_prompt_chaining, \
         patch('app.core.workflows.routing.get_functions_client') as mock_routing_functions, \
         patch('app.core.workflows.routing.get_llm_client') as mock_routing_llm:
         
        # Mock workflow selector response (selects prompt_chaining)
        ws_client = AsyncMock()
        ws_client.generate_with_functions.return_value = {
            "type": "function_call",
            "name": "select_workflow",
            "arguments": {
                "selected_workflow": "prompt_chaining",
                "reasoning": "This query requires sequential processing for translation",
                "required_agents": ["Initial Processor", "Validator", "Refiner"]
            }
        }
        mock_workflow_selector.return_value = ws_client
        
        # Mock prompt chaining responses
        pc_client = AsyncMock()
        pc_client.generate.side_effect = [
            "Structured analysis of the blog post about AI request",
            "PASS: The analysis correctly captures the requirements",
            "# The Future of AI\n\nArtificial Intelligence has come a long way...\n\n# El Futuro de la IA\n\nLa Inteligencia Artificial ha avanzado mucho..."
        ]
        mock_prompt_chaining.return_value = pc_client
        
        # Mock routing function client
        rf_client = AsyncMock()
        rf_client.generate_with_functions.return_value = {
            "type": "function_call",
            "name": "classify_query",
            "arguments": {
                "category": "technical_support",
                "confidence": 0.9,
                "reasoning": "This is a technical support question"
            }
        }
        mock_routing_functions.return_value = rf_client
        
        # Mock routing LLM client
        rl_client = AsyncMock()
        rl_client.generate.return_value = "To fix your connection, try these steps..."
        mock_routing_llm.return_value = rl_client
        
        yield

@pytest.mark.asyncio
async def test_process_query_prompt_chaining(mock_llm_responses):
    """Test the process query endpoint with prompt chaining workflow"""
    response = client.post(
        "/api/workflows/process",
        json={"query": "Write a blog post about the future of AI and translate it to Spanish"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "final_response" in data
    assert "workflow_info" in data
    assert "intermediate_steps" in data
    assert "processing_time" in data
    
    # Check workflow selection
    assert data["workflow_info"]["selected_workflow"] == "prompt_chaining"
    
    # Check intermediate steps
    assert len(data["intermediate_steps"]) == 3
    assert data["intermediate_steps"][0]["agent_role"] == "Initial Processor"
    assert data["intermediate_steps"][1]["agent_role"] == "Validator"
    assert data["intermediate_steps"][2]["agent_role"] == "Refiner"
    
    # Check final response
    assert "AI" in data["final_response"]
    assert "IA" in data["final_response"]  # Spanish part

@pytest.mark.asyncio
async def test_process_query_error_handling():
    """Test error handling in the process query endpoint"""
    with patch('app.api.endpoints.workflows.select_workflow', side_effect=Exception("Test error"), new_callable=AsyncMock):
        response = client.post(
            "/api/workflows/process",
            json={"query": "Test query"}
        )
        
        assert response.status_code == 500
        assert "Test error" in response.json()["detail"]