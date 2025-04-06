# Setting Up Google Custom Search for the Autonomous Agent

The autonomous agent workflow has the capability to search the web using Google Custom Search. This guide will help you set up the necessary API credentials to enable this functionality.

## Prerequisites

- A Google account
- A project in Google Cloud Console
- A credit card (for Google Cloud billing - Google Custom Search offers 100 free queries per day, after which charges apply)

## Step 1: Create a Google Cloud Project

1. Visit the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Make note of your Project ID

## Step 2: Enable the Custom Search API

1. In your Google Cloud project, go to "APIs & Services" > "Library"
2. Search for "Custom Search API"
3. Click on the result and press "Enable"

## Step 3: Get an API Key

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "API Key"
3. Copy the generated API key
4. (Optional but recommended) Restrict the API key to only the Custom Search API

## Step 4: Create a Custom Search Engine

1. Visit the [Programmable Search Engine Control Panel](https://programmablesearchengine.google.com/controlpanel/create)
2. Give your search engine a name (e.g., "Dynamic Workflow Search")
3. Under "What to search":
   - Select "Search the entire web" for general search capabilities
   - Or specify sites to search if you want to limit the scope
4. Click "Create"

## Step 5: Get Your Search Engine ID

1. After creating the search engine, click on it in your Programmable Search Engine Control Panel
2. Click "Setup" in the left sidebar
3. Find the "Search engine ID" field and copy the value (it will look like: `012345678901234567890:abcdefghijk`)

## Step 6: Configure Your Environment Variables

Add the following to your `.env` file:

```
GOOGLE_API_KEY=your_api_key_here
GOOGLE_CSE_ID=your_search_engine_id_here
```

## Step 7: Test the Search Functionality

1. Start the application
2. Send a query to the autonomous agent that would benefit from web search
3. Check the logs to make sure the search is working correctly

## Usage Notes

- The free tier of Google Custom Search API includes 100 queries per day
- After exceeding the free quota, charges will apply to your Google Cloud account
- Configure rate limits in `app/config/tools_config.py` to control usage
- Consider implementing caching for frequent searches to reduce API calls

## Troubleshooting

If you encounter issues with the search functionality:

1. Check that your API key and Search Engine ID are correctly set in the environment variables
2. Verify that billing is enabled on your Google Cloud project
3. Check the application logs for specific error messages
4. Test your Custom Search Engine directly through the [Google API Explorer](https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list)

## Additional Resources

- [Google Custom Search API Documentation](https://developers.google.com/custom-search/v1/overview)
- [Google Cloud Console API Key Management](https://cloud.google.com/docs/authentication/api-keys)
