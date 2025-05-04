# minimal_search_test.py
"""
A minimal script to test the search functionality
"""
import os
import asyncio
import aiohttp
import sys

async def test_search(api_key, cse_id, query="Python programming language"):
    """Test a basic search request"""
    print(f"Testing search with Google Custom Search")
    print(f"API Key: {'*' * len(api_key)}")
    print(f"CSE ID: {cse_id}")
    print(f"Query: '{query}'")
    
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": query,
        "num": 3
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"ERROR: Google CSE returned status {response.status}")
                    print(f"Error details: {error_text}")
                    return False
                
                data = await response.json()
                
                # Print results summary
                if "items" in data:
                    print(f"\nSUCCESS: Found {len(data['items'])} results")
                    for i, item in enumerate(data["items"], 1):
                        print(f"{i}. {item.get('title', 'No title')}")
                        print(f"   URL: {item.get('link', 'No link')}")
                    return True
                else:
                    print("No search results found")
                    if "error" in data:
                        print(f"API Error: {data['error'].get('message', 'Unknown error')}")
                    return False
                
    except Exception as e:
        print(f"ERROR during search test: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

async def main():
    # Get the required values from command line or input
    api_key = None
    cse_id = None
    
    # Try to get from command line
    if len(sys.argv) >= 3:
        api_key = sys.argv[1]
        cse_id = sys.argv[2]
        query = sys.argv[3] if len(sys.argv) > 3 else "Python programming language"
    else:
        # Try to get from environment variables
        api_key = os.environ.get("GOOGLE_API_KEY")
        cse_id = os.environ.get("GOOGLE_CSE_ID")
        
        # If still not found, ask for input
        if not api_key:
            api_key = input("Enter your Google API Key: ").strip()
        if not cse_id:
            cse_id = input("Enter your Google Custom Search Engine ID: ").strip()
        
        query = input("Enter a test search query (or press Enter for default): ").strip()
        if not query:
            query = "Python programming language"
    
    if not api_key or not cse_id:
        print("Error: Both API Key and CSE ID are required.")
        return
    
    # Run the test
    await test_search(api_key, cse_id, query)

if __name__ == "__main__":
    asyncio.run(main())