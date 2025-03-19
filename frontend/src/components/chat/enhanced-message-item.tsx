// components/chat/enhanced-message-item.tsx
import { useState } from 'react';
import { Message } from '@/types';
import EnhancedWorkflowDiagram from '../workflow/enhanced-workflow-diagram';
import AgentInteractionDiagram from '../workflow/agent-interaction-diagram';
import { Button } from '../ui/button';
import { 
  ChevronDown, 
  ChevronUp, 
  User, 
  Bot, 
  Activity,
  Workflow,
  Users,
  Layers
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

interface EnhancedMessageItemProps {
  message: Message;
}

export default function EnhancedMessageItem({ message }: EnhancedMessageItemProps) {
  const [showDetails, setShowDetails] = useState(false);
  
  const isUserMessage = message.role === 'user';
  const hasWorkflowInfo = !!message.workflow_info;
  const hasIntermediateSteps = !!message.intermediate_steps && message.intermediate_steps.length > 0;
  
  return (
    <div className={`p-4 ${
        isUserMessage 
          ? 'bg-muted/50 dark:bg-muted/25' 
          : 'bg-background dark:bg-muted/10'
      } rounded-lg mb-4 shadow-sm transition-all duration-200 hover:shadow-md`}>
      <div className="flex items-start gap-3">
        <div className="mt-1">
          {isUserMessage ? (
            <div className="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-primary-foreground">
              <User size={20} />
            </div>
          ) : (
            <div className="h-10 w-10 rounded-full bg-secondary flex items-center justify-center text-secondary-foreground">
              <Bot size={20} />
            </div>
          )}
        </div>
        
        <div className="flex-1 space-y-2">
          <div className="flex items-center justify-between">
            <div className="font-medium text-sm text-foreground">
              {isUserMessage ? 'You' : 'Assistant'}
            </div>
            <div className="text-xs text-muted-foreground">
              {formatDistanceToNow(new Date(message.timestamp), { addSuffix: true })}
            </div>
          </div>
          
          <div className="prose dark:prose-invert max-w-none">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
          
          {(hasWorkflowInfo || hasIntermediateSteps) && (
            <div className="mt-4 pt-4 border-t border-border">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowDetails(!showDetails)}
                className="text-muted-foreground hover:text-foreground"
              >
                {showDetails ? (
                  <>
                    <ChevronUp className="h-4 w-4 mr-2" />
                    Hide Details
                  </>
                ) : (
                  <>
                    <ChevronDown className="h-4 w-4 mr-2" />
                    Show Details
                  </>
                )}
              </Button>
              
              {showDetails && (
                <div className="mt-4 space-y-4 text-sm">
                  <Tabs defaultValue="workflow" className="w-full">
                    <TabsList className="w-full">
                      <TabsTrigger value="workflow" className="flex-1">
                        <Workflow className="h-4 w-4 mr-2" />
                        Workflow
                      </TabsTrigger>
                      <TabsTrigger value="agents" className="flex-1">
                        <Users className="h-4 w-4 mr-2" />
                        Agents
                      </TabsTrigger>
                      <TabsTrigger value="steps" className="flex-1">
                        <Layers className="h-4 w-4 mr-2" />
                        Steps
                      </TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="workflow" className="m-0">
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
                                <div className="prose dark:prose-invert max-w-none bg-white dark:bg-gray-800 p-4 rounded border mt-2">
                                  <div className="break-words">
                                    <ReactMarkdown>{step.content}</ReactMarkdown>
                                  </div>
                                </div>
                                
                                {step.metadata && (
                                  <div className="mt-3">
                                    <details className="text-sm">
                                      <summary className="cursor-pointer text-gray-500 hover:text-gray-800 dark:hover:text-gray-200 py-2">
                                        View Metadata
                                      </summary>
                                      <pre className="mt-2 p-4 bg-gray-100 dark:bg-gray-800 rounded-md overflow-auto text-xs font-mono">
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