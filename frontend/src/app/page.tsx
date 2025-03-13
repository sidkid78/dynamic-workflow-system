// app/page.tsx
'use client'

import Link from 'next/link';
import { ArrowRight, Workflow, Brain, Zap, Layers, GitMerge, SplitSquareVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function HomePage() {
  // Workflow card data
  const workflows = [
    {
      name: 'Prompt Chaining',
      description: 'Sequential processing where each step builds on the previous one',
      icon: <Layers className="h-8 w-8 text-blue-500" />,
      examples: ['Content creation and refinement', 'Multi-step analysis', 'Translation']
    },
    {
      name: 'Routing',
      description: 'Classify inputs and direct them to specialized handlers',
      icon: <GitMerge className="h-8 w-8 text-green-500" />,
      examples: ['Customer support queries', 'Content categorization', 'Specialized knowledge domains']
    },
    {
      name: 'Parallel Sectioning',
      description: 'Break tasks into independent components processed in parallel',
      icon: <SplitSquareVertical className="h-8 w-8 text-purple-500" />,
      examples: ['Multi-perspective analysis', 'Code review', 'Content evaluation']
    },
    {
      name: 'Parallel Voting',
      description: 'Run the same task multiple times to get diverse perspectives',
      icon: <Workflow className="h-8 w-8 text-red-500" />,
      examples: ['Content moderation', 'Security assessment', 'Quality evaluation']
    },
    {
      name: 'Orchestrator-Workers',
      description: 'Central coordinator assigns and manages subtasks dynamically',
      icon: <Brain className="h-8 w-8 text-indigo-500" />,
      examples: ['Complex project planning', 'Research tasks', 'Multi-step creative work']
    },
    {
      name: 'Evaluator-Optimizer',
      description: 'Generate content, evaluate, and refine iteratively',
      icon: <Zap className="h-8 w-8 text-amber-500" />,
      examples: ['Professional writing', 'Code optimization', 'Content refinement']
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero section */}
      <section className="bg-gradient-to-b from-white to-gray-100">
        <div className="container mx-auto px-4 py-16 md:py-24">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              Dynamic Workflow System
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              An intelligent system that automatically selects and executes the optimal workflow
              pattern for each query using specialized AI agents.
            </p>
            <Link href="/chat">
              <Button size="lg" className="rounded-full px-8">
                Try it now <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Workflow explanation section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Supported Workflow Patterns</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {workflows.map((workflow, index) => (
              <div key={index} className="bg-white border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                <div className="p-6">
                  <div className="flex items-center mb-4">
                    {workflow.icon}
                    <h3 className="text-xl font-semibold ml-3">{workflow.name}</h3>
                  </div>
                  <p className="text-gray-600 mb-4">{workflow.description}</p>
                  <div>
                    <h4 className="text-sm font-medium text-gray-500 mb-2">Best for:</h4>
                    <ul className="list-disc pl-5 text-gray-600 text-sm">
                      {workflow.examples.map((example, i) => (
                        <li key={i} className="mb-1">{example}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-8">How It Works</h2>
            
            <div className="space-y-12">
              <div className="flex flex-col md:flex-row items-start gap-6">
                <div className="bg-blue-100 rounded-full p-4 text-blue-600">
                  <span className="text-xl font-bold">1</span>
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Query Analysis</h3>
                  <p className="text-gray-600">
                    When you submit a query, the system analyzes it to understand what you&apos;re asking
                    and what type of response would be most helpful.
                  </p>
                </div>
              </div>
              
              <div className="flex flex-col md:flex-row items-start gap-6">
                <div className="bg-green-100 rounded-full p-4 text-green-600">
                  <span className="text-xl font-bold">2</span>
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Workflow Selection</h3>
                  <p className="text-gray-600">
                    Based on the analysis, the system automatically selects the most appropriate
                    workflow pattern to handle your specific query.
                  </p>
                </div>
              </div>
              
              <div className="flex flex-col md:flex-row items-start gap-6">
                <div className="bg-purple-100 rounded-full p-4 text-purple-600">
                  <span className="text-xl font-bold">3</span>
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Agent Execution</h3>
                  <p className="text-gray-600">
                    Specialized AI agents with unique personas and capabilities execute each step of
                    the workflow, collaborating to generate the best possible response.
                  </p>
                </div>
              </div>
              
              <div className="flex flex-col md:flex-row items-start gap-6">
                <div className="bg-amber-100 rounded-full p-4 text-amber-600">
                  <span className="text-xl font-bold">4</span>
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Transparent Response</h3>
                  <p className="text-gray-600">
                    You receive the final response along with visibility into the workflow that
                    generated it, including each agent&apos;s contribution and the reasoning behind it.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="text-center mt-12">
              <Link href="/chat">
                <Button size="lg" variant="outline" className="rounded-full px-8">
                  Start a conversation <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}