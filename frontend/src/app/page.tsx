// app/page.tsx
import Link from 'next/link';
import { ArrowRight, Workflow, Brain, Zap, Layers, GitMerge, SplitSquareVertical, Bot } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function HomePage() {
  // Workflow card data
  const workflows = [
    {
      name: 'Prompt Chaining',
      description: 'Sequential processing where each step builds on the previous one',
      icon: <Layers className="h-8 w-8 text-blue-500 dark:text-blue-400" />,
      examples: ['Content creation and refinement', 'Multi-step analysis', 'Translation']
    },
    {
      name: 'Routing',
      description: 'Classify inputs and direct them to specialized handlers',
      icon: <GitMerge className="h-8 w-8 text-green-500 dark:text-green-400" />,
      examples: ['Customer support queries', 'Content categorization', 'Specialized knowledge domains']
    },
    {
      name: 'Parallel Sectioning',
      description: 'Break tasks into independent components processed in parallel',
      icon: <SplitSquareVertical className="h-8 w-8 text-purple-500 dark:text-purple-400" />,
      examples: ['Multi-perspective analysis', 'Code review', 'Content evaluation']
    },
    {
      name: 'Parallel Voting',
      description: 'Run the same task multiple times to get diverse perspectives',
      icon: <Workflow className="h-8 w-8 text-red-500 dark:text-red-400" />,
      examples: ['Content moderation', 'Security assessment', 'Quality evaluation']
    },
    {
      name: 'Orchestrator-Workers',
      description: 'Central coordinator assigns and manages subtasks dynamically',
      icon: <Brain className="h-8 w-8 text-indigo-500 dark:text-indigo-400" />,
      examples: ['Complex project planning', 'Research tasks', 'Multi-step creative work']
    },
    {
      name: 'Evaluator-Optimizer',
      description: 'Generate content, evaluate, and refine iteratively',
      icon: <Zap className="h-8 w-8 text-amber-500 dark:text-amber-400" />,
      examples: ['Professional writing', 'Code optimization', 'Content refinement']
    },
    {
      name: 'Autonomous Agent',
      description: 'Self-directed agent that plans, acts, and reflects in a loop',
      icon: <Bot className="h-8 w-8 text-teal-500 dark:text-teal-400" />,
      examples: ['Complex problem solving', 'Tool-based tasks', 'Iterative research']
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Hero section */}
      <section className="bg-gradient-to-b from-white to-gray-100 dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4 py-16 md:py-24">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-gray-100 mb-6">
              Dynamic Workflow System
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
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
      <section className="py-16 bg-white dark:bg-gray-800">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 dark:text-gray-100">Supported Workflow Patterns</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {workflows.map((workflow, index) => (
              <Card key={index} className="flex flex-col overflow-hidden shadow-sm hover:shadow-lg transition-shadow duration-300 dark:border-gray-700">
                <CardHeader className="flex flex-row items-center gap-4 p-4 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700">
                  {workflow.icon}
                  <CardTitle className="text-lg font-semibold dark:text-gray-100">{workflow.name}</CardTitle>
                </CardHeader>
                <CardContent className="p-4 flex-grow text-gray-900 dark:text-gray-100">
                  <p className="text-sm mb-4">{workflow.description}</p>
                  <div>
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300 mb-2">Best for:</h4>
                    <ul className="list-disc pl-5 text-sm space-y-1 dark:text-gray-400">
                      {workflow.examples.map((example, i) => (
                        <li key={i}>{example}</li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How it works section */}
      <section className="py-16 bg-gray-50 dark:bg-gray-900/50">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-8 dark:text-gray-100">How It Works</h2>
            
            <div className="space-y-12">
              <div className="flex flex-col md:flex-row items-start gap-6">
                <div className="bg-blue-100 dark:bg-blue-900/30 rounded-full p-4 text-blue-600 dark:text-blue-300">
                  <span className="text-xl font-bold">1</span>
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2 dark:text-gray-100">Query Analysis</h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    When you submit a query, the system analyzes it to understand what you&apos;re asking
                    and what type of response would be most helpful.
                  </p>
                </div>
              </div>
              
              <div className="flex flex-col md:flex-row items-start gap-6">
                <div className="bg-green-100 dark:bg-green-900/30 rounded-full p-4 text-green-600 dark:text-green-300">
                  <span className="text-xl font-bold">2</span>
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2 dark:text-gray-100">Workflow Selection</h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    Based on the analysis, the system automatically selects the most appropriate
                    workflow pattern to handle your specific query.
                  </p>
                </div>
              </div>
              
              <div className="flex flex-col md:flex-row items-start gap-6">
                <div className="bg-purple-100 dark:bg-purple-900/30 rounded-full p-4 text-purple-600 dark:text-purple-300">
                  <span className="text-xl font-bold">3</span>
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2 dark:text-gray-100">Agent Execution</h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    Specialized AI agents with unique personas and capabilities execute each step of
                    the workflow, collaborating to generate the best possible response.
                  </p>
                </div>
              </div>
              
              <div className="flex flex-col md:flex-row items-start gap-6">
                <div className="bg-amber-100 dark:bg-amber-900/30 rounded-full p-4 text-amber-600 dark:text-amber-300">
                  <span className="text-xl font-bold">4</span>
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2 dark:text-gray-100">Transparent Response</h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    You receive the final response along with visibility into the workflow that
                    generated it, including each agent&apos;s contribution and the reasoning behind it.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="text-center mt-12">
              <Link href="/chat">
                <Button size="lg" variant="outline" className="rounded-full px-8 dark:border-gray-600 dark:text-gray-100">
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