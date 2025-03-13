# tests/unit/workflows/test_prompt_chaining.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.models.schemas import WorkflowSelection, AgentResponse
from app.core.workflows.prompt_chaining import execute, generate_agent_context

@pytest.mark.asyncio
async def test_prompt_chaining_workflow():
    """Test the prompt chaining workflow execution"""
    # Mock data
    mock_workflow_selection = WorkflowSelection(
        selected_workflow="prompt_chaining",
        reasoning="Test reasoning",
        required_agents=["Initial Processor", "Validator", "Refiner"],
        personas={
            "prompt_chaining": {
                "step1_agent": {
                    "role": "Initial Processor",
                    "persona": "Analytical",
                    "description": "Analyzes queries",
                    "strengths": ["Analysis"]
                },
                "gate_agent": {
                    "role": "Validator",
                    "persona": "Critical",
                    "description": "Validates outputs",
                    "strengths": ["Validation"]
                },
                "step2_agent": {
                    "role": "Refiner",
                    "persona": "Creative",
                    "description": "Refines outputs",
                    "strengths": ["Refinement"]
                }
            }
        }
    )
    
    user_query = "Explain quantum computing and translate it to Spanish"
    
    # Mock LLM client responses
    with patch('app.core.workflows.prompt_chaining.get_llm_client', autospec=True) as mock_get_client:
        mock_client = AsyncMock()
        mock_client.generate.side_effect = [
            "Structured analysis of quantum computing query",  # step1 response
            "PASS: The analysis correctly captures the intent",  # gate response
            "Quantum computing is a type of computing...\n\nEn español: La computación cuántica es..."  # step2 response
        ]
        mock_get_client.return_value = mock_client
        
        # Execute workflow
        result, steps = await execute(mock_workflow_selection, user_query)
        
        # Assert client was called correctly
        assert mock_client.generate.call_count == 3
        
        # Assert steps were recorded
        assert len(steps) == 3
        assert steps[0].agent_role == "Initial Processor"
        assert steps[1].agent_role == "Validator"
        assert steps[2].agent_role == "Refiner"
        
        # Assert final response
        assert "quantum computing" in result.lower()
        assert "computación cuántica" in result.lower()

@pytest.mark.asyncio
async def test_prompt_chaining_validation_failure():
    """Test the prompt chaining workflow when validation fails"""
    # Mock data
    mock_workflow_selection = WorkflowSelection(
        selected_workflow="prompt_chaining",
        reasoning="Test reasoning",
        required_agents=["Initial Processor", "Validator", "Refiner"],
        personas={
            "prompt_chaining": {
                "step1_agent": {
                    "role": "Initial Processor",
                    "persona": "Analytical",
                    "description": "Analyzes queries",
                    "strengths": ["Analysis"]
                },
                "gate_agent": {
                    "role": "Validator",
                    "persona": "Critical",
                    "description": "Validates outputs",
                    "strengths": ["Validation"]
                },
                "step2_agent": {
                    "role": "Refiner",
                    "persona": "Creative",
                    "description": "Refines outputs",
                    "strengths": ["Refinement"]
                }
            }
        }
    )
    
    user_query = "Explain quantum computing and translate it to Spanish"
    
    # Mock LLM client responses
    with patch('app.core.workflows.prompt_chaining.get_llm_client', autospec=True) as mock_get_client:
        mock_client = AsyncMock()
        mock_client.generate.side_effect = [
            "Incomplete analysis",  # step1 response
            "FAIL: The analysis is incomplete and doesn't address the translation requirement",  # gate response
        ]
        mock_get_client.return_value = mock_client
        
        # Execute workflow
        result, steps = await execute(mock_workflow_selection, user_query)
        
        # Assert client was called correctly (should only call step1 and gate, not step2)
        assert mock_client.generate.call_count == 2
        
        # Assert steps were recorded
        assert len(steps) == 2
        assert steps[0].agent_role == "Initial Processor"
        assert steps[1].agent_role == "Validator"
        
        # Assert final response contains the failure explanation
        assert "refine my understanding" in result
        assert "translation requirement" in result

def test_generate_agent_context():
    """Test the agent context generation function"""
    agent_persona = {
        "role": "Test Agent",
        "persona": "Analytical and precise",
        "description": "Analyzes complex data",
        "strengths": ["Analysis", "Precision", "Clarity"]
    }
    
    context = generate_agent_context(agent_persona)
    
    assert "ROLE: Test Agent" in context
    assert "CHARACTER: Analytical and precise" in context
    assert "FUNCTION: Analyzes complex data" in context
    assert "STRENGTHS: Analysis, Precision, Clarity" in context
    assert "You are acting as the Test Agent" in context

@pytest.mark.asyncio
async def test_routing_workflow():
    """Test the routing workflow execution"""
    # Mock data
    mock_workflow_selection = WorkflowSelection(
        selected_workflow="routing",
        reasoning="Test reasoning",
        required_agents=["Query Classifier", "Specialist"],
        personas={
            "routing": {
                "classifier_agent": {
                    "role": "Query Classifier",
                    "persona": "Analytical",
                    "description": "Classifies queries",
                    "strengths": ["Classification"]
                },
                "category1_agent": {
                    "role": "Technical Support Specialist",
                    "persona": "Technical",
                    "description": "Handles technical queries",
                    "strengths": ["Technical support"]
                },
                "category2_agent": {
                    "role": "Account Management Specialist",
                    "persona": "Administrative",
                    "description": "Handles account queries",
                    "strengths": ["Account management"]
                },
                "category3_agent": {
                    "role": "General Inquiry Specialist",
                    "persona": "Helpful",
                    "description": "Handles general queries",
                    "strengths": ["General knowledge"]
                }
            }
        }
    )
    
    user_query = "How do I reset my password?"
    
    # Mock function client response for classification
    with patch('app.core.workflows.routing.get_functions_client', autospec=True) as mock_get_functions_client, \
         patch('app.core.workflows.routing.get_llm_client', autospec=True) as mock_get_llm_client:
        
        mock_functions_client = AsyncMock()
        mock_functions_client.generate_with_functions.return_value = {
            "type": "function_call",
            "name": "classify_query",
            "arguments": {
                "category": "account_management",
                "confidence": 0.95,
                "reasoning": "Password reset is related to account management"
            }
        }
        mock_get_functions_client.return_value = mock_functions_client
        
        mock_llm_client = AsyncMock()
        mock_llm_client.generate.return_value = "To reset your password, please follow these steps..."
        mock_get_llm_client.return_value = mock_llm_client
        
        # Execute workflow
        from app.core.workflows.routing import execute as routing_execute
        result, steps = await routing_execute(mock_workflow_selection, user_query)
        
        # Assert clients were called correctly
        assert mock_functions_client.generate_with_functions.call_count == 1
        assert mock_llm_client.generate.call_count == 1
        
        # Assert steps were recorded
        assert len(steps) == 2
        assert steps[0].agent_role == "Query Classifier"
        assert steps[1].agent_role == "Account Management Specialist"
        
        # Assert final response
        assert "reset your password" in result

@pytest.mark.asyncio
async def test_workflow_selector_prompt_chaining():
    """Test the workflow selector with prompt chaining selection"""
    from app.core.workflow_selector import select_workflow
    
    with patch('app.core.workflow_selector.get_functions_client', autospec=True) as mock_get_client:
        mock_client = AsyncMock()
        mock_client.generate_with_functions.return_value = {
            "type": "function_call",
            "name": "select_workflow",
            "arguments": {
                "selected_workflow": "prompt_chaining",
                "reasoning": "This query requires sequential processing",
                "required_agents": ["Initial Processor", "Validator", "Refiner"]
            }
        }
        mock_get_client.return_value = mock_client
        
        result = await select_workflow("Write a blog post and translate it to French")
        
        assert result.selected_workflow == "prompt_chaining"
        assert "sequential processing" in result.reasoning
        assert "prompt_chaining" in result.personas

@pytest.mark.asyncio
async def test_workflow_selector_routing():
    """Test the workflow selector with routing selection"""
    from app.core.workflow_selector import select_workflow
    
    with patch('app.core.workflow_selector.get_functions_client', autospec=True) as mock_get_client:
        mock_client = AsyncMock()
        mock_client.generate_with_functions.return_value = {
            "type": "function_call",
            "name": "select_workflow",
            "arguments": {
                "selected_workflow": "routing",
                "reasoning": "This query requires specialized handling",
                "required_agents": ["Query Classifier", "Specialist"]
            }
        }
        mock_get_client.return_value = mock_client
        
        result = await select_workflow("How do I reset my password?")
        
        assert result.selected_workflow == "routing"
        assert "specialized handling" in result.reasoning
        assert "routing" in result.personas

@pytest.mark.asyncio
async def test_workflow_selector_error_handling():
    """Test the workflow selector error handling"""
    from app.core.workflow_selector import select_workflow
    
    with patch('app.core.workflow_selector.get_functions_client', autospec=True) as mock_get_client:
        mock_client = AsyncMock()
        mock_client.generate_with_functions.side_effect = Exception("Test error")
        mock_get_client.return_value = mock_client
        
        result = await select_workflow("Test query")
        
        # Should fall back to prompt_chaining
        assert result.selected_workflow == "prompt_chaining"
        assert "error" in result.reasoning.lower()