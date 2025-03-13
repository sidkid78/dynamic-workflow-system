# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture(autouse=True)
def mock_llm_clients():
    """
    Automatically mock all LLM clients for tests to prevent actual API calls.
    This fixture is applied to all tests automatically.
    """
    # Create mock clients
    mock_regular_client = AsyncMock()
    mock_regular_client.generate.return_value = "Mocked response"
    
    mock_functions_client = AsyncMock()
    mock_functions_client.generate_with_functions.return_value = {
        "type": "text",
        "content": "Mocked function response"
    }
    
    # Apply patches
    with patch('app.core.llm_client.get_llm_client', return_value=mock_regular_client), \
         patch('app.core.llm_client.get_functions_client', return_value=mock_functions_client), \
         patch('app.core.llm_client.AzureOpenAIClient', return_value=mock_regular_client), \
         patch('app.core.llm_client.AzureOpenAIFunctions', return_value=mock_functions_client):
        yield 