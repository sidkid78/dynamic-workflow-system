// components/chat/message-item.tsx
'use client'

import { useState } from 'react';
import { Message } from '@/types';
import WorkflowDiagram from '../workflow/workflow-diagram';
import { Button } from '../ui/button';
import { ChevronDown, ChevronUp, Info, User, Bot, Activity } from 'lucide-react';
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

interface MessageItemProps {
  message: Message;
}

export default function MessageItem({ message }: MessageItemProps) {
  const [showDetails, setShowDetails] = useState(false);
  
  const isUserMessage = message.role === 'user';
  const hasWorkflowInfo = !!message.workflow_info;
  const hasIntermediateSteps = !!message.intermediate_steps && message.intermediate_steps.length > 0;
  
  return (
    <div className={`p-4 ${isUserMessage ? 'bg-gray-100' : 'bg-white'} rounded-lg mb-4`}>
      <div className="flex items-start gap-3">
        <div className="mt-1">
          {isUserMessage ? (
            <div className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-white">
              <User size={18} />
            </div>
          ) : (
            <div className="h-8 w-8 rounded-full bg-purple-500 flex items-center justify-center text-white">
              <Bot size={18} />
            </div>
          )}
        </div>
        
        <div className="flex-1 overflow-hidden">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-medium">
              {isUserMessage ? 'You' : 'Assistant'}
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
                className="flex items-center gap-1 text-sm"
              >
                <Info size={16} />
                {showDetails ? 'Hide Details' : 'View Workflow Details'}
                {showDetails ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </Button>
              
              {showDetails && (
                <div className="mt-4 border rounded-lg p-4 bg-gray-50">
                  <Tabs defaultValue="diagram">
                    <TabsList className="mb-4">
                      <TabsTrigger value="diagram">Workflow Diagram</TabsTrigger>
                      <TabsTrigger value="steps">Processing Steps</TabsTrigger>
                      <TabsTrigger value="agents">Agents</TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="diagram">
                      {hasWorkflowInfo ? (
                        <WorkflowDiagram 
                          workflowInfo={message.workflow_info!} 
                          intermediateSteps={message.intermediate_steps || []} 
                        />
                      ) : (
                        <div className="text-center py-8 text-gray-500">
                          No workflow information available
                        </div>
                      )}
                    </TabsContent>
                    
                    <TabsContent value="steps">
                      {hasIntermediateSteps ? (
                        <Accordion type="single" collapsible className="w-full">
                          {message.intermediate_steps!.map((step, index) => (
                            <AccordionItem key={index} value={`step-${index}`}>
                              <AccordionTrigger className="flex items-center gap-2">
                                <Activity size={16} className="text-blue-500" />
                                <span>{step.agent_role}</span>
                                <span className="text-xs text-gray-500 ml-2">
                                  Step {index + 1}
                                </span>
                              </AccordionTrigger>
                              <AccordionContent>
                                <div className="prose prose-sm max-w-none bg-white p-3 rounded border mt-2">
                                  <ReactMarkdown>{step.content}</ReactMarkdown>
                                </div>
                                
                                {step.metadata && (
                                  <div className="mt-3 text-xs">
                                    <details>
                                      <summary className="cursor-pointer text-gray-500 hover:text-gray-800">
                                        View Metadata
                                      </summary>
                                      <pre className="mt-2 p-2 bg-gray-100 rounded overflow-auto text-xs">
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
                    
                    <TabsContent value="agents">
                      {hasWorkflowInfo && message.workflow_info?.personas ? (
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
                      ) : (
                        <div className="text-center py-8 text-gray-500">
                          No agent information available
                        </div>
                      )}
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