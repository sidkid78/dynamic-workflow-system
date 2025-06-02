#!/usr/bin/env python3
"""
Basic test for Gemini connection without function calling
"""
import asyncio
import os
import sys

# Add the backend app to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.llm_client import get_llm_client
from app.config import settings

async def test_basic_generation():
    """Test basic text generation with Gemini"""
    
    print("🧪 Testing Basic Gemini Generation...")
    print(f"Using model: {settings.GEMINI_MODEL}")
    print(f"API configured: {settings.is_gemini_configured}")
    
    try:
        client = get_llm_client()
        print("✅ Basic client initialized")
        
        # Try with a more stable model and simpler parameters
        response = await client.generate(
            prompt="Hello, how are you?",
            temperature=0.5,
            max_tokens=1000
        )
        
        print("✅ Generation successful!")
        print(f"Response: {response}")
            
    except Exception as e:
        print(f"❌ Error during basic generation test: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Run test"""
    print("🚀 Starting Basic Gemini Test\n")
    
    # Check configuration
    if not settings.is_gemini_configured:
        print("❌ Gemini not configured. Please set GOOGLE_API_KEY in your .env file")
        return
    
    await test_basic_generation()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(main()) 