'use client';

import { useState } from 'react';
import AgentCard from '@/components/workflow/agent-card';
import EnhancedWorkflowDiagram from '@/components/workflow/enhanced-workflow-diagram';
import WorkflowMetrics from '@/components/workflow/workflow-metrics';
import { AgentPersona, WorkflowSelection, Message } from '@/types';

export default function TestWorkflowPage() {
  const [showComponents, setShowComponents] = useState(false);

  // Mock data for testing
  const mockWorkflowInfo: WorkflowSelection = {
    selected_workflow: 'prompt_chaining',
    reasoning: 'This query requires sequential processing with validation steps',
    required_agents: ['Initial Processor', 'Validator', 'Refiner'],
    personas: {
      prompt_chaining: {
        step1_agent: {
          role: 'Initial Processor',
          persona: 'Analytical and methodical',
          description: 'Breaks down complex queries into structured components',
          strengths: ['Analysis', 'Structuring', 'Clarity']
        },
        gate_agent: {
          role: 'Validator',
          persona: 'Quality-focused and thorough',
          description: 'Ensures output meets quality standards',
          strengths: ['Validation', 'Quality Control', 'Attention to Detail']
        },
        step2_agent: {
          role: 'Refiner',
          persona: 'Creative and comprehensive',
          description: 'Creates polished final responses',
          strengths: ['Synthesis', 'Creativity', 'Completeness']
        }
      }
    }
  };

  const mockIntermediateSteps = [
    {
      agent_role: 'Initial Processor',
      content: 'Analyzed the query and identified key components: blog post topic (AI), target audience, and content structure requirements.'
    },
    {
      agent_role: 'Validator',
      content: 'PASS: The analysis accurately captures the intent and provides a clear structure for content creation.'
    },
    {
      agent_role: 'Refiner',
      content: 'Created a comprehensive blog post about AI, covering key concepts, current trends, and future implications with engaging examples.'
    }
  ];

  const mockAgentPersonas: AgentPersona[] = [
    {
      role: 'Initial Processor',
      persona: 'Analytical and methodical',
      description: 'Breaks down complex queries into structured components',
      strengths: ['Analysis', 'Structuring', 'Clarity']
    },
    {
      role: 'Validator',
      persona: 'Quality-focused and thorough',
      description: 'Ensures output meets quality standards',
      strengths: ['Validation', 'Quality Control', 'Attention to Detail']
    },
    {
      role: 'Refiner',
      persona: 'Creative and comprehensive',
      description: 'Creates polished final responses',
      strengths: ['Synthesis', 'Creativity', 'Completeness']
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-gray-900 dark:text-gray-100">
          Workflow Components Test
        </h1>
        
        <div className="mb-6">
          <button
            onClick={() => setShowComponents(!showComponents)}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            {showComponents ? 'Hide' : 'Show'} Workflow Components
          </button>
        </div>

        {showComponents && (
          <div className="space-y-8">
            {/* Agent Cards */}
            <div>
              <h2 className="text-2xl font-semibold mb-4 dark:text-gray-200">Agent Cards</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {mockAgentPersonas.map((persona, index) => (
                  <AgentCard key={index} persona={persona} workflowType="prompt_chaining" />
                ))}
              </div>
            </div>

            {/* Workflow Diagram */}
            <div>
              <h2 className="text-2xl font-semibold mb-4 dark:text-gray-200">Workflow Diagram</h2>
              <EnhancedWorkflowDiagram 
                workflowInfo={mockWorkflowInfo}
                intermediateSteps={mockIntermediateSteps}
              />
            </div>

            {/* Workflow Metrics */}
            <div>
              <h2 className="text-2xl font-semibold mb-4 dark:text-gray-200">Workflow Metrics</h2>
              <WorkflowMetrics 
                messages={[
                  {
                    id: '1',
                    content: 'Test message',
                    role: 'assistant',
                    timestamp: Date.now(),
                    workflow_info: mockWorkflowInfo,
                    intermediate_steps: mockIntermediateSteps,
                    processing_time: 2.5
                  }
                ]}
              />
            </div>
          </div>
        )}

        <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <h3 className="font-medium mb-2 dark:text-blue-200">Test Instructions:</h3>
          <ul className="text-sm space-y-1 dark:text-blue-300">
            <li>• Click "Show Workflow Components" to see all three components</li>
            <li>• The Agent Cards should display the mock personas</li>
            <li>• The Workflow Diagram should show a prompt_chaining flow with completed steps</li>
            <li>• The Workflow Metrics should show statistics about the workflow</li>
            <li>• If these work, the issue is with the API data, not the components</li>
          </ul>
        </div>
      </div>
    </div>
  );
} 