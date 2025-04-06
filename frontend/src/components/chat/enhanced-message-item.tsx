// components/chat/enhanced-message-item.tsx
import { useState } from 'react';
import { Message } from '@/types';
import EnhancedWorkflowDiagram from '../workflow/enhanced-workflow-diagram';
import AgentInteractionDiagram from '../workflow/agent-interaction-diagram';
import { Button } from '../ui/button';
import { 
  ChevronDown, 
  ChevronUp, 
  Info,
  User, 
  Bot, 
  Activity,
  BarChart,
  Workflow,
  Users,
  Layers,
  PieChart
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { formatDistanceToNow } from 'date-fns';
import { 
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger 
} from '@/components/ui/accordion';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import AgentCard from '../workflow/agent-card';
import WorkflowMetrics from '../workflow/workflow-metrics';

interface EnhancedMessageItemProps {
  message: Message;
  allMessages: Message[];
}

export default function EnhancedMessageItem({ message, allMessages }: EnhancedMessageItemProps) {
  const [showDetails, setShowDetails] = useState(false);
  
  const isUserMessage = message.role === 'user';
  const hasWorkflowInfo = !!message.workflow_info;
  const hasIntermediateSteps = !!message.intermediate_steps && message.intermediate_steps.length > 0;
  
  return (
    <div className={`p-4 ${isUserMessage ? 'bg-gray-100' : 'bg-white'} rounded-lg mb-4 shadow-sm transition-all duration-200 hover:shadow-md`}>
      <div className="flex items-start gap-3">
        <div className="mt-1">
          {isUserMessage ? (
            <div className="h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center text-white">
              <User size={20} />
            </div>
          ) : (
            <div className="h-10 w-10 rounded-full bg-purple-500 flex items-center justify-center text-white">
              <Bot size={20} />
            </div>
          )}
        </div>
        
        <div className="flex-1 overflow-hidden">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-medium flex items-center">
              {isUserMessage ? 'You' : 'Assistant'}
              {!isUserMessage && hasWorkflowInfo && (
                <span className="ml-2 px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                  {message.workflow_info!.selected_workflow.replace(/_/g, ' ')}
                </span>
              )}
            </h3>
            <span className="text-xs text-gray-500">
              {formatDistanceToNow(new Date(message.timestamp), { addSuffix: true })}
            </span>
          </div>
          
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
          
          {(hasWorkflowInfo || hasIntermediateSteps) && (
            <div className="mt-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowDetails(!showDetails)}
                className="flex items-center gap-1 text-sm hover:bg-purple-50"
              >
                {showDetails ? (
                  <>
                    <ChevronUp size={16} />
                    Hide Workflow Details
                  </>
                ) : (
                  <>
                    <Info size={16} />
                    View Workflow Details 
                    {hasIntermediateSteps && (
                      <span className="ml-1 px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full text-xs">
                        {message.intermediate_steps!.length} steps
                      </span>
                    )}
                  </>
                )}
              </Button>
              
              {showDetails && (
                <div className="mt-4 border rounded-lg overflow-hidden bg-gray-50 animate-fadeIn">
                  <Tabs defaultValue="diagram">
                    <TabsList className="bg-white border-b p-0 w-full flex">
                      <TabsTrigger value="diagram" className="flex items-center gap-1.5 py-3">
                        <Workflow size={16} />
                        <span>Workflow Diagram</span>
                      </TabsTrigger>
                      <TabsTrigger value="timeline" className="flex items-center gap-1.5 py-3">
                        <BarChart size={16} />
                        <span>Timeline</span>
                      </TabsTrigger>
                      <TabsTrigger value="steps" className="flex items-center gap-1.5 py-3">
                        <Layers size={16} />
                        <span>Steps</span>
                      </TabsTrigger>
                      <TabsTrigger value="agents" className="flex items-center gap-1.5 py-3">
                        <Users size={16} />
                        <span>Agents</span>
                      </TabsTrigger>
                      <TabsTrigger value="metrics" className="flex items-center gap-1.5 py-3">
                        <PieChart size={16} />
                        <span>Metrics</span>
                      </TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="diagram" className="m-0">
                      {hasWorkflowInfo ? (
                        <EnhancedWorkflowDiagram 
                          workflowInfo={message.workflow_info!} 
                          intermediateSteps={message.intermediate_steps || []} 
                        />
                      ) : (
                        <div className="text-center py-8 text-gray-500">
                          No workflow information available
                        </div>
                      )}
                    </TabsContent>
                    
                    <TabsContent value="timeline" className="m-0">
                      {hasIntermediateSteps ? (
                        <AgentInteractionDiagram steps={message.intermediate_steps!} />
                      ) : (
                        <div className="text-center py-8 text-gray-500">
                          No intermediate steps available
                        </div>
                      )}
                    </TabsContent>
                    
                    <TabsContent value="steps" className="m-0 p-4">
                      {hasIntermediateSteps ? (
                        <Accordion type="single" collapsible className="w-full">
                          {message.intermediate_steps!.map((step, index) => (
                            <AccordionItem key={index} value={`step-${index}`} className="border-b border-gray-200">
                              <AccordionTrigger className="flex items-center gap-2 py-3 px-4 hover:bg-gray-50 rounded group">
                                <div className="flex items-center gap-2">
                                  <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                                    <Activity size={16} />
                                  </div>
                                  <div className="flex flex-col text-left">
                                    <span className="font-medium text-sm">{step.agent_role}</span>
                                    <span className="text-xs text-gray-500">
                                      Step {index + 1}
                                    </span>
                                  </div>
                                </div>
                                <ChevronDown size={18} className="ml-auto text-gray-400 group-hover:text-gray-600 transform transition-transform duration-200 group-data-[state=open]:rotate-180" />
                              </AccordionTrigger>
                              <AccordionContent className="px-4 pt-0 pb-4">
                                <div className="prose prose-sm max-w-none bg-white p-4 rounded border mt-2">
                                  <ReactMarkdown>{step.content}</ReactMarkdown>
                                </div>
                                
                                {step.metadata && (
                                  <div className="mt-3">
                                    <details className="text-sm">
                                      <summary className="cursor-pointer text-gray-500 hover:text-gray-800 py-2">
                                        View Metadata
                                      </summary>
                                      <pre className="mt-2 p-4 bg-gray-100 rounded-md overflow-auto text-xs font-mono">
                                        {JSON.stringify(step.metadata, null, 2)}
                                      </pre>
                                    </details>
                                  </div>
                                )}
                              </AccordionContent>
                            </AccordionItem>
                          ))}
                        </Accordion>
                      ) : (
                        <div className="text-center py-8 text-gray-500">
                          No processing steps available
                        </div>
                      )}
                    </TabsContent>
                    
                    <TabsContent value="agents" className="m-0 p-4">
                      {hasWorkflowInfo && message.workflow_info?.personas ? (
                        <div>
                          <h3 className="text-lg font-medium mb-4">
                            Agents in {message.workflow_info.selected_workflow.replace(/_/g, ' ')} Workflow
                          </h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {Object.entries(message.workflow_info.personas).flatMap(([workflowType, agents]) => 
                              Object.entries(agents).map(([agentType, persona]) => (
                                <AgentCard 
                                  key={`${workflowType}-${agentType}`}
                                  persona={persona}
                                  workflowType={workflowType} 
                                />
                              ))
                            )}
                          </div>
                        </div>
                      ) : (
                        <div className="text-center py-8 text-gray-500">
                          No agent information available
                        </div>
                      )}
                    </TabsContent>

                    <TabsContent value="metrics" className="m-0">
                      <WorkflowMetrics messages={allMessages} className="p-4" />
                    </TabsContent>
                  </Tabs>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}