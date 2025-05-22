// app/about/page.tsx
import Link from 'next/link';
import { ArrowRight, GitMerge, Workflow, Brain, Bot } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function AboutPage() {
  return (
    <div className="bg-background">
      {/* Hero section */}
      <section className="bg-gradient-to-b from-background to-card">
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-3xl mx-auto">
            <h1 className="text-4xl font-bold text-foreground mb-6">
              About the Dynamic Workflow System
            </h1>
            <p className="text-xl text-muted-foreground mb-8">
              Built to revolutionize how AI systems process complex requests by dynamically
              selecting the most appropriate processing patterns.
            </p>
          </div>
        </div>
      </section>

      {/* Main content */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto prose dark:prose-invert">
            <h2 className="text-foreground">What is the Dynamic Workflow System?</h2>
            <p className="text-muted-foreground">
              The Dynamic Workflow System is an innovative approach to AI interaction that moves
              beyond simple prompt-response patterns. Instead of using a one-size-fits-all approach
              to process user queries, our system intelligently analyzes each request and dynamically
              selects the most appropriate workflow pattern to handle it.
            </p>
            
            <p className="text-muted-foreground">
              By leveraging specialized AI agents with distinct personas and capabilities, the system
              can tackle complex requests with greater precision, transparency, and effectiveness than
              traditional approaches.
            </p>
            
            <h2 className="dark:text-gray-100">Core Workflow Patterns</h2>
            
            <div className="not-prose mb-8">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="border dark:border-gray-700 rounded-lg p-4 bg-blue-50 dark:bg-blue-900/20">
                  <div className="flex items-center mb-2">
                    <GitMerge className="h-5 w-5 text-blue-500 dark:text-blue-400 mr-2" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Prompt Chaining</h3>
                  </div>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    Sequential processing where each step builds on the previous one, enabling
                    complex multi-stage reasoning and refinement.
                  </p>
                </div>
                
                <div className="border dark:border-gray-700 rounded-lg p-4 bg-green-50 dark:bg-green-900/20">
                  <div className="flex items-center mb-2">
                    <Workflow className="h-5 w-5 text-green-500 dark:text-green-400 mr-2" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Routing</h3>
                  </div>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    Classifies inputs and directs them to specialized handlers, ensuring each
                    query is processed by the most appropriate expert.
                  </p>
                </div>
                
                <div className="border dark:border-gray-700 rounded-lg p-4 bg-purple-50 dark:bg-purple-900/20">
                  <div className="flex items-center mb-2">
                    <Brain className="h-5 w-5 text-purple-500 dark:text-purple-400 mr-2" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Parallel Processing</h3>
                  </div>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    Breaks tasks into independent components or evaluates from multiple perspectives
                    simultaneously, enabling comprehensive analysis.
                  </p>
                </div>
                
                <div className="border dark:border-gray-700 rounded-lg p-4 bg-amber-50 dark:bg-amber-900/20">
                  <div className="flex items-center mb-2">
                    <Bot className="h-5 w-5 text-amber-500 dark:text-amber-400 mr-2" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">Iterative Optimization</h3>
                  </div>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    Generates content, evaluates against criteria, and refines iteratively,
                    producing higher quality outputs through successive improvements.
                  </p>
                </div>
              </div>
            </div>
            
            <h2 className="dark:text-gray-100">Technical Implementation</h2>
            <p className="dark:text-gray-300">
              The system is built using a combination of modern technologies:
            </p>
            <ul className="dark:text-gray-300">
              <li><strong>Backend:</strong> Python FastAPI with Azure OpenAI integration</li>
              <li><strong>Frontend:</strong> Next.js with TypeScript and Tailwind CSS</li>
              <li><strong>Workflow Engine:</strong> Custom implementation with dynamic selection logic</li>
              <li><strong>Agent Framework:</strong> Specialized agent personas with defined roles and responsibilities</li>
            </ul>
            
            <h2 className="dark:text-gray-100">Benefits</h2>
            <p className="dark:text-gray-300">
              The Dynamic Workflow approach offers several key advantages:
            </p>
            <ul className="dark:text-gray-300">
              <li><strong>Increased Task Complexity:</strong> Handle more complex and nuanced requests</li>
              <li><strong>Improved Response Quality:</strong> Generate more accurate, comprehensive answers</li>
              <li><strong>Enhanced Transparency:</strong> See exactly how your request is being processed</li>
              <li><strong>Specialized Expertise:</strong> Leverage different agent personas for different aspects of a task</li>
              <li><strong>Intelligent Adaptation:</strong> System adapts its approach based on the specific query</li>
            </ul>
            
            <div className="my-8 p-6 bg-gray-100 dark:bg-gray-800 rounded-lg">
              <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-gray-100">Try It Yourself</h3>
              <p className="mb-4 text-gray-700 dark:text-gray-300">
                Experience the power of dynamic workflows by starting a conversation with our system.
              </p>
              <Link href="/chat">
                <Button className="rounded-full px-6">
                  Start chatting <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
            
            <h2 className="dark:text-gray-100">Future Development</h2>
            <p className="dark:text-gray-300">
              The Dynamic Workflow System is continuously evolving. Future developments include:
            </p>
            <ul className="dark:text-gray-300">
              <li>Additional workflow patterns for specialized use cases</li>
              <li>Enhanced visualization of workflow execution</li>
              <li>User-configurable workflow preferences</li>
              <li>Integration with external tools and APIs</li>
              <li>Performance optimization for complex workflows</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
}