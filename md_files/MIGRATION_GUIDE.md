# Migration Guide: Azure OpenAI → Google Gemini

This guide will help you migrate your application from Azure OpenAI to Google Gemini using the latest Google GenAI SDK.

## Overview

We've completely replaced the Azure OpenAI implementation with Google Gemini while maintaining backward compatibility. Your existing code should continue to work with minimal changes.

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Get Your Google API Key

#### Option A: Gemini Developer API (Recommended for development)
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click "Get API key"
3. Create a new API key
4. Copy your API key

#### Option B: Vertex AI (For enterprise/production)
1. Set up a Google Cloud Project
2. Enable the Vertex AI API
3. Set up authentication using gcloud or service account

### 3. Update Environment Variables

Copy the example environment file:
```bash
cp backend/env.example backend/.env
```

Edit `backend/.env` and add your Google API key:
```env
# For Gemini Developer API
GOOGLE_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-2.0-flash-001

# For Vertex AI (alternative)
# USE_VERTEX_AI=true
# GOOGLE_CLOUD_PROJECT=your-project-id
# GOOGLE_CLOUD_LOCATION=us-central1
```

### 4. Remove Old Azure Settings

Remove these from your `.env` file:
```env
# Remove these
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_DEPLOYMENT_NAME=...
AZURE_OPENAI_API_VERSION=...
```

## Key Changes

### Configuration Changes

| Before (Azure) | After (Gemini) | Notes |
|----------------|----------------|-------|
| `AZURE_OPENAI_API_KEY` | `GOOGLE_API_KEY` | Single API key for all Google services |
| `AZURE_OPENAI_ENDPOINT` | *(removed)* | Handled automatically by SDK |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | `GEMINI_MODEL` | Default: `gemini-2.0-flash-001` |
| `AZURE_OPENAI_API_VERSION` | *(removed)* | Handled automatically by SDK |
| `settings.is_azure_openai_configured` | `settings.is_gemini_configured` | New method (old one aliased) |

### Client Changes

The client interface remains the same for backward compatibility:

```python
# This code works exactly the same
from app.core.llm_client import get_llm_client, get_functions_client

client = get_llm_client()
response = await client.generate("Hello, world!")

functions_client = get_functions_client()
result = await functions_client.generate_with_functions(
    prompt="What's the weather?",
    functions=[weather_function]
)
```

### New Features

#### 1. Streaming Support
```python
client = get_llm_client()
async for chunk in client.generate_stream("Tell me a story"):
    print(chunk, end="")
```

#### 2. Synchronous Operations
```python
client = get_llm_client()
response = client.generate_sync("Quick question")  # Non-async
```

#### 3. Advanced Function Calling
```python
# Native Python functions work directly
def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Sunny in {location}"

result = await functions_client.generate_with_functions(
    prompt="What's the weather in Paris?",
    functions=[get_weather]  # Pass function directly
)
```

## Model Comparison

| Azure OpenAI | Google Gemini | Capabilities |
|---------------|---------------|--------------|
| gpt-4 | gemini-2.0-flash-001 | Text, reasoning, function calling |
| gpt-4-turbo | gemini-2.0-flash-001 | Faster, more efficient |
| gpt-4o | gemini-2.0-flash-001 | Multimodal (text, images, etc.) |

## Advanced Configuration

### Vertex AI Setup (Enterprise)

For production environments, use Vertex AI:

1. **Install Google Cloud SDK:**
   ```bash
   # Install gcloud CLI
   # Windows: Download from Google Cloud website
   # Linux/Mac: curl https://sdk.cloud.google.com | bash
   ```

2. **Authenticate:**
   ```bash
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Update environment:**
   ```env
   USE_VERTEX_AI=true
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   # Remove GOOGLE_API_KEY when using Vertex AI
   ```

### Custom Models

To use different models:

```env
GEMINI_MODEL=gemini-2.0-flash-001        # Default, fastest
GEMINI_MODEL=gemini-2.0-flash-thinking   # For complex reasoning
GEMINI_MODEL=gemini-2.0-pro             # For production workloads
```

## Testing the Migration

### 1. Basic Test

Create `test_migration.py`:

```python
import asyncio
from app.core.llm_client import get_llm_client

async def test_basic():
    client = get_llm_client()
    response = await client.generate("Say hello!")
    print(f"Response: {response}")

asyncio.run(test_basic())
```

### 2. Function Calling Test

```python
import asyncio
from app.core.llm_client import get_functions_client

def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

async def test_functions():
    client = get_functions_client()
    result = await client.generate_with_functions(
        prompt="What is 15 + 27?",
        functions=[add_numbers]
    )
    print(f"Result: {result}")

asyncio.run(test_functions())
```

### 3. Run Tests

```bash
cd backend
python test_migration.py
```

## Troubleshooting

### Common Issues

1. **"Missing Google Gemini configuration" Error**
   - Check your `.env` file has `GOOGLE_API_KEY`
   - Verify the API key is valid at [Google AI Studio](https://aistudio.google.com/)

2. **Import Errors**
   - Run: `pip install google-genai>=0.7.0`
   - Ensure you're using Python 3.8+

3. **Rate Limiting**
   - Gemini has different rate limits than Azure
   - Consider implementing backoff strategies
   - Use Vertex AI for higher quotas

4. **Function Calling Format Changes**
   - Gemini uses automatic function calling by default
   - Legacy function schemas are automatically converted
   - Native Python functions work directly

### Performance Optimization

1. **Use Async Operations**
   ```python
   # Preferred
   response = await client.generate(prompt)
   
   # Only when necessary
   response = client.generate_sync(prompt)
   ```

2. **Batch Requests**
   ```python
   # Process multiple requests concurrently
   tasks = [client.generate(prompt) for prompt in prompts]
   responses = await asyncio.gather(*tasks)
   ```

3. **Streaming for Long Responses**
   ```python
   async for chunk in client.generate_stream(long_prompt):
       process_chunk(chunk)
   ```

## Rollback Plan

If you need to rollback to Azure OpenAI:

1. **Keep backup of old `.env`:**
   ```bash
   cp .env .env.gemini.backup
   cp .env.azure.backup .env
   ```

2. **Reinstall Azure dependencies:**
   ```bash
   pip install openai aiohttp
   ```

3. **Restore old `llm_client.py`:**
   ```bash
   git checkout HEAD~1 -- backend/app/core/llm_client.py
   ```

## Cost Comparison

| Provider | Model | Cost per 1M tokens (approx.) |
|----------|-------|-------------------------------|
| Azure OpenAI | GPT-4 | $30-60 |
| Google Gemini | gemini-2.0-flash-001 | $0.075-0.30 |

*Gemini is significantly more cost-effective for most use cases.*

## Support

- **Google AI Studio:** [https://aistudio.google.com/](https://aistudio.google.com/)
- **Documentation:** [https://github.com/googleapis/python-genai](https://github.com/googleapis/python-genai)
- **Vertex AI:** [https://cloud.google.com/vertex-ai](https://cloud.google.com/vertex-ai)

## Migration Checklist

- [ ] Install new dependencies (`pip install google-genai>=0.7.0`)
- [ ] Get Google API key from AI Studio
- [ ] Update `.env` file with `GOOGLE_API_KEY`
- [ ] Remove old Azure OpenAI settings
- [ ] Test basic text generation
- [ ] Test function calling (if used)
- [ ] Test streaming (if used)
- [ ] Update any hardcoded Azure references
- [ ] Monitor performance and costs
- [ ] Update documentation and team

---

**Migration completed! Your application now uses Google Gemini instead of Azure OpenAI. 🎉** 