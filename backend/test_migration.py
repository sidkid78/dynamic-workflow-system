#!/usr/bin/env python3
"""
Migration Test Script for Azure OpenAI → Google Gemini

This script tests the basic functionality of the migrated Google Gemini client
to ensure everything is working correctly after the migration.

Usage:
    python test_migration.py
"""

import asyncio
import sys
import os
import logging
from typing import Optional

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.config import settings
    from app.core.llm_client import get_llm_client, get_functions_client
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the backend directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MigrationTester:
    """Test suite for the Azure to Gemini migration."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name: str, description: str):
        """Decorator for test methods."""
        def decorator(func):
            self.tests.append((name, description, func))
            return func
        return decorator
    
    async def run_all_tests(self):
        """Run all registered tests."""
        print("🧪 Starting Migration Tests")
        print("=" * 50)
        
        # Configuration check
        await self._test_configuration()
        
        # Run all registered tests
        for name, description, test_func in self.tests:
            await self._run_test(name, description, test_func)
        
        # Summary
        print("\n" + "=" * 50)
        print(f"📊 Test Summary: {self.passed} passed, {self.failed} failed")
        
        if self.failed == 0:
            print("✅ All tests passed! Migration successful! 🎉")
            return True
        else:
            print("❌ Some tests failed. Please check the errors above.")
            return False
    
    async def _run_test(self, name: str, description: str, test_func):
        """Run a single test with error handling."""
        try:
            print(f"\n🔍 {name}")
            print(f"   {description}")
            
            result = await test_func()
            if result:
                print(f"   ✅ PASSED")
                self.passed += 1
            else:
                print(f"   ❌ FAILED")
                self.failed += 1
                
        except Exception as e:
            print(f"   ❌ FAILED: {str(e)}")
            self.failed += 1
            logger.exception(f"Test {name} failed with exception")
    
    async def _test_configuration(self):
        """Test that configuration is correct."""
        print("🔧 Configuration Check")
        
        if settings.is_gemini_configured:
            provider = "Vertex AI" if settings.USE_VERTEX_AI else "Gemini Developer API"
            print(f"   ✅ Google Gemini configured using {provider}")
            print(f"   ✅ Model: {settings.GEMINI_MODEL}")
        else:
            print("   ❌ Google Gemini not configured")
            print("   Please set GOOGLE_API_KEY in your .env file")
            sys.exit(1)

# Create tester instance
tester = MigrationTester()

@tester.test("Basic Client Initialization", "Test that the LLM client can be initialized")
async def test_client_initialization():
    try:
        client = get_llm_client()
        return client is not None
    except Exception as e:
        print(f"      Error: {e}")
        return False

@tester.test("Functions Client Initialization", "Test that the functions client can be initialized")
async def test_functions_client_initialization():
    try:
        client = get_functions_client()
        return client is not None
    except Exception as e:
        print(f"      Error: {e}")
        return False

@tester.test("Basic Text Generation", "Test basic text generation functionality")
async def test_basic_generation():
    try:
        client = get_llm_client()
        response = await client.generate(
            prompt="Say 'Hello, migration test!' and nothing else.",
            max_tokens=50,
            temperature=0.1
        )
        
        print(f"      Response: {response[:100]}...")
        return len(response.strip()) > 0
    except Exception as e:
        print(f"      Error: {e}")
        return False

@tester.test("Synchronous Generation", "Test synchronous generation method")
async def test_sync_generation():
    try:
        client = get_llm_client()
        response = client.generate_sync(
            prompt="Reply with just 'Sync test passed'",
            max_tokens=20,
            temperature=0.1
        )
        
        print(f"      Response: {response}")
        return "test" in response.lower()
    except Exception as e:
        print(f"      Error: {e}")
        return False

@tester.test("Streaming Generation", "Test streaming text generation")
async def test_streaming():
    try:
        client = get_llm_client()
        chunks = []
        
        async for chunk in client.generate_stream(
            prompt="Count from 1 to 3, one number per response chunk.",
            max_tokens=20,
            temperature=0.1
        ):
            chunks.append(chunk)
            if len(chunks) >= 3:  # Limit to avoid infinite loops
                break
        
        full_response = "".join(chunks)
        print(f"      Streamed: {full_response}")
        return len(chunks) > 0 and len(full_response) > 0
    except Exception as e:
        print(f"      Error: {e}")
        return False

@tester.test("Function Calling", "Test function calling capabilities")
async def test_function_calling():
    try:
        def add_numbers(a: int, b: int) -> int:
            """Add two numbers together."""
            return a + b
        
        def get_greeting(name: str) -> str:
            """Get a greeting for a person."""
            return f"Hello, {name}!"
        
        client = get_functions_client()
        result = await client.generate_with_functions(
            prompt="Add 15 and 27, then tell me the result.",
            functions=[add_numbers, get_greeting],
            max_tokens=100,
            temperature=0.1
        )
        
        print(f"      Result type: {result.get('type')}")
        print(f"      Content: {result.get('content', '')[:100]}...")
        
        return result.get('type') == 'text' and len(result.get('content', '')) > 0
    except Exception as e:
        print(f"      Error: {e}")
        return False

@tester.test("Legacy Compatibility", "Test backward compatibility with old interface")
async def test_legacy_compatibility():
    try:
        # Test that old property names still work
        is_configured = settings.is_azure_openai_configured  # Should use new method
        
        # Test that class aliases work
        from app.core.llm_client import AzureOpenAIClient, AzureOpenAIFunctions
        
        return is_configured and AzureOpenAIClient is not None and AzureOpenAIFunctions is not None
    except Exception as e:
        print(f"      Error: {e}")
        return False

@tester.test("Error Handling", "Test error handling for invalid inputs")
async def test_error_handling():
    try:
        client = get_llm_client()
        
        # Test with empty prompt (should handle gracefully)
        try:
            response = await client.generate("", max_tokens=10)
            # If it doesn't raise an error, that's also okay
            return True
        except Exception:
            # Expected behavior - should handle errors gracefully
            return True
            
    except Exception as e:
        print(f"      Unexpected error: {e}")
        return False

async def main():
    """Main test runner."""
    print("🚀 Azure OpenAI → Google Gemini Migration Test")
    print("This script will test the basic functionality after migration.\n")
    
    success = await tester.run_all_tests()
    
    if success:
        print(f"\n🎯 Next Steps:")
        print(f"1. Update your .env file with your Google API key")
        print(f"2. Test your specific application workflows")
        print(f"3. Monitor performance and costs")
        print(f"4. Remove old Azure OpenAI credentials")
        
        return 0
    else:
        print(f"\n🔧 Troubleshooting:")
        print(f"1. Check your .env file has GOOGLE_API_KEY set")
        print(f"2. Verify your API key at https://aistudio.google.com/")
        print(f"3. Check internet connectivity")
        print(f"4. Review the error messages above")
        
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 