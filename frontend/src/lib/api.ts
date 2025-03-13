// lib/api.ts
import { QueryRequest, WorkflowResponse } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export async function processQuery(queryRequest: QueryRequest): Promise<WorkflowResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/workflows/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(queryRequest),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to process query');
    }

    return await response.json();
  } catch (error) {
    console.error('Error in API call:', error);
    throw error;
  }
}