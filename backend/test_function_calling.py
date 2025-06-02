#!/usr/bin/env python3
"""
Test script for Gemini function calling implementation
"""
import asyncio
import os
import sys
from typing import Dict, Any

# Add the backend app to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.llm_client import get_functions_client
from app.config import settings

async def test_simple_function_call():
    """Test a simple function call with Gemini"""
    
    print("🧪 Testing Gemini Function Calling...")
    print(f"Using model: {settings.GEMINI_MODEL}")
    print(f"API configured: {settings.is_gemini_configured}")
    
    # Define a simple test function
    test_function = {
        "name": "get_current_time",
        "description": "Get the current time",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "The timezone, e.g. UTC, EST"
                }
            },
            "required": ["timezone"]
        }
    }
    
    prompt = """What time is it in UTC? 
    
    You MUST call the get_current_time function to answer this question. Do not provide a text response."""
    
    try:
        client = get_functions_client()
        print("✅ Functions client initialized")
        
        response = await client.generate_with_functions(
            prompt=prompt,
            functions=[test_function]
        )
        
        print(f"Response type: {response.get('type')}")
        print(f"Response: {response}")
        
        if response.get("type") == "function_call":
            print("✅ Function call successful!")
            print(f"Function name: {response.get('name')}")
            print(f"Arguments: {response.get('arguments')}")
        else:
            print("❌ Expected function call but got text response")
            print(f"Content: {response.get('content', 'No content')}")
            
    except Exception as e:
        print(f"❌ Error during function call test: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_workflow_selection():
    """Test the actual workflow selection function"""
    
    print("\n🧪 Testing Workflow Selection Function...")
    
    try:
        from app.core.workflow_selector import select_workflow
        
        test_query = "Write a blog post and then translate it to Spanish"
        print(f"Test query: {test_query}")
        
        result = await select_workflow(test_query)
        
        print("✅ Workflow selection successful!")
        print(f"Selected workflow: {result.selected_workflow}")
        print(f"Reasoning: {result.reasoning}")
        print(f"Required agents: {result.required_agents}")
        
    except Exception as e:
        print(f"❌ Error during workflow selection test: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all tests"""
    print("🚀 Starting Gemini Function Calling Tests\n")
    
    # Check configuration
    if not settings.is_gemini_configured:
        print("❌ Gemini not configured. Please set GOOGLE_API_KEY in your .env file")
        return
    
    await test_simple_function_call()
    await test_workflow_selection()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 