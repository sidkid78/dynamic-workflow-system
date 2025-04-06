// lib/api.ts
import { QueryRequest, WorkflowResponse } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export async function processQuery(queryRequest: QueryRequest): Promise<WorkflowResponse> {
  try {
    console.log('Making API request to:', `${API_BASE_URL}/workflows/process`);
    console.log('Request payload:', queryRequest);
    
    const response = await fetch(`${API_BASE_URL}/workflows/process`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(queryRequest),
    });

    // Log the raw response details
    console.log('Response status:', response.status);
    console.log('Response status text:', response.statusText);
    console.log('Response headers:', Object.fromEntries(response.headers.entries()));

    if (!response.ok) {
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch (parseError) {
        console.error('Failed to parse error response:', parseError);
        try {
          // Try to get raw text if JSON parsing fails
          const errorText = await response.text();
          errorMessage = `${errorMessage} - Raw response: ${errorText}`;
        } catch (textError) {
          console.error('Failed to get error response text:', textError);
        }
      }
      throw new Error(errorMessage);
    }

    const data = await response.json();
    console.log('API response data:', data);
    return data;
  } catch (error: Error | unknown) {
    console.error('Error in API call:', {
      name: error instanceof Error ? error.name : 'Unknown Error',
      message: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
      cause: error instanceof Error ? error.cause : undefined,
    });
    
    // If it's a fetch error (network error)
    if (error instanceof TypeError && error.message === 'Failed to fetch') {
      throw new Error('Network error: Unable to connect to the API server. Please check if the server is running and accessible.');
    }
    
    // Re-throw the error with additional context
    throw new Error(`API request failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

