"""
Simple script to set up the search environment variables for testing
"""
import os
import sys
import subprocess

def main():
    print("Google Search Setup Script")
    print("--------------------------")
    
    # Check if API key and CSE ID are provided as arguments
    if len(sys.argv) >= 3:
        api_key = sys.argv[1]
        cse_id = sys.argv[2]
    else:
        # Get API key
        api_key = input("Enter your Google API Key: ").strip()
        
        # Get CSE ID
        cse_id = input("Enter your Google Custom Search Engine ID: ").strip()
    
    if not api_key or not cse_id:
        print("Error: Both API Key and CSE ID are required.")
        return
    
    # Set environment variables for the current process
    os.environ["GOOGLE_API_KEY"] = api_key
    os.environ["GOOGLE_CSE_ID"] = cse_id
    
    print("\nEnvironment variables set for this session:")
    print(f"GOOGLE_API_KEY={api_key[:5]}...{api_key[-5:] if len(api_key) > 10 else ''}")
    print(f"GOOGLE_CSE_ID={cse_id}")
    
    # Write to .env file for persistent storage
    create_env = input("\nDo you want to save these to a .env file? (y/n): ").lower().startswith('y')
    if create_env:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        
        # Check if file exists and if we should append
        append_mode = False
        if os.path.exists(env_path):
            append = input(".env file already exists. Append to it? (y/n): ").lower()
            if append.startswith('y'):
                append_mode = True
            else:
                confirm = input("This will overwrite the existing .env file. Continue? (y/n): ").lower()
                if not confirm.startswith('y'):
                    print("Operation cancelled.")
                    return
        
        # Write to .env file
        mode = 'a' if append_mode else 'w'
        with open(env_path, mode) as f:
            if append_mode:
                f.write("\n# Google Custom Search settings\n")
            f.write(f"GOOGLE_API_KEY={api_key}\n")
            f.write(f"GOOGLE_CSE_ID={cse_id}\n")
        
        print(f".env file {'updated' if append_mode else 'created'} at {env_path}")
    
    # Set environment variables for the current command window (Windows only)
    if sys.platform == "win32":
        set_cmd = input("\nDo you want to set these variables for the current command window? (y/n): ").lower()
        if set_cmd.startswith('y'):
            try:
                subprocess.run(f'setx GOOGLE_API_KEY "{api_key}"', shell=True, check=True)
                subprocess.run(f'setx GOOGLE_CSE_ID "{cse_id}"', shell=True, check=True)
                print("\nEnvironment variables set for the system using setx.")
                print("Note: You may need to restart your command prompt for these changes to take effect.")
            except subprocess.CalledProcessError as e:
                print(f"Error setting environment variables: {e}")
    
    # Offer to run a test
    run_test = input("\nDo you want to run a test search now? (y/n): ").lower()
    if run_test.startswith('y'):
        test_query = input("Enter a test search query (or press Enter for default): ").strip()
        if not test_query:
            test_query = "Python programming language"
        
        print(f"\nRunning test search for: '{test_query}'")
        try:
            # Import the test function and run it
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from tests.web_search import WebSearchTest
            import asyncio
            
            test = WebSearchTest()
            asyncio.run(test.test_search(test_query))
        except Exception as e:
            print(f"Error running test: {str(e)}")
            import traceback
            print(traceback.format_exc())

if __name__ == "__main__":
    main()