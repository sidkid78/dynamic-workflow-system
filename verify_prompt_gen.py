import asyncio
import httpx
import json

async def test_prompt_generator():
    url = "http://localhost:8000/api/workflows/process"
    query = "Create an optimized prompt for summarizing complex academic papers into layman's terms."
    
    payload = {
        "query": query
    }
    
    print(f"Sending query: {query}")
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            print("\nWorkflow Selection:")
            print(f"Selected: {data['workflow_info']['selected_workflow']}")
            print(f"Reasoning: {data['workflow_info']['reasoning']}")
            
            print("\nFinal Response Preview:")
            print(data['final_response'])
            
            print(f"\nProcessing Time: {data['processing_time']:.2f}s")
            print(f"Number of Intermediate Steps: {len(data['intermediate_steps'])}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_prompt_generator())
