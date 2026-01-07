'use client';

import { useState } from 'react';
import { processQuery } from '@/lib/api';

export default function DebugPage() {
  const [query, setQuery] = useState('Write a blog post about AI');
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const testAPI = async () => {
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const result = await processQuery({ query });
      setResponse(result);
      console.log('API Response:', result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-gray-900 dark:text-gray-100">
          API Debug Page
        </h1>
        
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2 dark:text-gray-200">
              Test Query:
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full p-3 border rounded-lg dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200"
              rows={3}
            />
          </div>
          
          <button
            onClick={testAPI}
            disabled={loading}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? 'Testing...' : 'Test API'}
          </button>

          {error && (
            <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded dark:bg-red-900/20 dark:border-red-800 dark:text-red-400">
              <strong>Error:</strong> {error}
            </div>
          )}

          {response && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold dark:text-gray-200">API Response:</h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border dark:border-gray-700">
                  <h3 className="font-medium mb-2 dark:text-gray-200">Response Structure:</h3>
                  <pre className="text-xs overflow-auto dark:text-gray-300 max-h-96">
                    {JSON.stringify(response, null, 2)}
                  </pre>
                </div>
                
                <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border dark:border-gray-700">
                  <h3 className="font-medium mb-2 dark:text-gray-200">Key Fields:</h3>
                  <ul className="text-sm space-y-1 dark:text-gray-300">
                    <li><strong>Has workflow_info:</strong> {response.workflow_info ? '✅ Yes' : '❌ No'}</li>
                    <li><strong>Selected workflow:</strong> {response.workflow_info?.selected_workflow || 'N/A'}</li>
                    <li><strong>Has intermediate_steps:</strong> {response.intermediate_steps ? '✅ Yes' : '❌ No'}</li>
                    <li><strong>Steps count:</strong> {response.intermediate_steps?.length || 0}</li>
                    <li><strong>Processing time:</strong> {response.processing_time || 'N/A'}s</li>
                    <li><strong>Final response:</strong> {response.final_response ? '✅ Yes' : '❌ No'}</li>
                  </ul>
                </div>

                <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border dark:border-gray-700">
                  <h3 className="font-medium mb-2 dark:text-gray-200">Workflow Details:</h3>
                  {response.workflow_info ? (
                    <div className="text-sm space-y-1 dark:text-gray-300">
                      <div><strong>Workflow:</strong> {response.workflow_info.selected_workflow}</div>
                      <div><strong>Reasoning:</strong> {response.workflow_info.reasoning}</div>
                      <div><strong>Required Agents:</strong> {response.workflow_info.required_agents?.join(', ')}</div>
                    </div>
                  ) : (
                    <p className="text-sm text-red-500">No workflow_info found</p>
                  )}
                </div>
              </div>

              {response.intermediate_steps && response.intermediate_steps.length > 0 && (
                <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border dark:border-gray-700">
                  <h3 className="font-medium mb-2 dark:text-gray-200">Intermediate Steps:</h3>
                  <div className="space-y-2">
                    {response.intermediate_steps.map((step: any, index: number) => (
                      <div key={index} className="p-2 bg-gray-50 dark:bg-gray-700 rounded">
                        <div className="font-medium text-sm dark:text-gray-200">
                          Step {index + 1}: {step.agent_role}
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                          {step.content.substring(0, 200)}...
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 