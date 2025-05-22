// components/workflow/workflow-metrics.tsx
import { useState, useEffect } from 'react';
import { Message } from '@/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Clock, Workflow, Users, Layers, PieChart } from 'lucide-react';

interface WorkflowMetricsProps {
  messages: Message[];
  className?: string;
}

interface MetricsState {
  totalMessages: number;
  responsesWithWorkflow: number;
  avgProcessingTime: number;
  totalSteps: number;
  avgStepsPerWorkflow: number;
  workflowDistribution: Record<string, number>;
  agentUsage: Record<string, number>;
  totalAgentLoops: number;
  avgAgentLoops: number;
  toolUsageDistribution: Record<string, number>;
}

interface ActionMetadata {
  action_type: string;
  tool_name: string;
}

export default function WorkflowMetrics({ messages, className = '' }: WorkflowMetricsProps) {
  const [metrics, setMetrics] = useState<MetricsState>({
    totalMessages: 0,
    responsesWithWorkflow: 0,
    avgProcessingTime: 0,
    totalSteps: 0,
    avgStepsPerWorkflow: 0,
    workflowDistribution: {},
    agentUsage: {},
    totalAgentLoops: 0,
    avgAgentLoops: 0,
    toolUsageDistribution: {},
  });

  // Calculate metrics when messages change
  useEffect(() => {
    // Filter assistant messages with workflow information
    const assistantMessages = messages.filter(
      (msg) => msg.role === 'assistant' && msg.workflow_info
    );

    // Basic counts
    const totalMessages = messages.length;
    const responsesWithWorkflow = assistantMessages.length;

    // Processing time
    const totalProcessingTime = assistantMessages.reduce(
      (sum, msg) => sum + (msg.processing_time || 0),
      0
    );
    const avgProcessingTime = responsesWithWorkflow 
      ? totalProcessingTime / responsesWithWorkflow 
      : 0;

    // Steps calculation
    const totalSteps = assistantMessages.reduce(
      (sum, msg) => sum + (msg.intermediate_steps?.length || 0),
      0
    );
    const avgStepsPerWorkflow = responsesWithWorkflow 
      ? totalSteps / responsesWithWorkflow 
      : 0;

    // Workflow distribution
    const workflowDistribution = assistantMessages.reduce((dist, msg) => {
      const workflow = msg.workflow_info?.selected_workflow || 'unknown';
      const formattedWorkflow = workflow.replace(/_/g, ' ');
      dist[formattedWorkflow] = (dist[formattedWorkflow] || 0) + 1;
      return dist;
    }, {} as Record<string, number>);

    // Agent usage
    const agentUsage = assistantMessages.reduce((usage, msg) => {
      msg.intermediate_steps?.forEach(step => {
        usage[step.agent_role] = (usage[step.agent_role] || 0) + 1;
      });
      return usage;
    }, {} as Record<string, number>);
    
    // Count autonomous agent iterations
    const autonomousAgentMessages = assistantMessages.filter(
      msg => msg.workflow_info?.selected_workflow === 'autonomous_agent'
    );
    
    // Track iterations for autonomous agents
    const totalAgentLoops = autonomousAgentMessages.reduce((sum, msg) => {
      const iterations = msg.intermediate_steps?.filter(
        step => step.agent_role === "Progress Reflector"
      ).length || 0;
      return sum + iterations;
    }, 0);
    
    const avgAgentLoops = autonomousAgentMessages.length > 0 
      ? totalAgentLoops / autonomousAgentMessages.length 
      : 0;
      
    // Tool usage in autonomous agents
    const toolUsageDistribution = assistantMessages.reduce((toolUsage, msg) => {
      msg.intermediate_steps?.forEach(step => {
        const metadata = step.metadata as { action?: ActionMetadata };
        if (metadata?.action?.action_type === "use_tool") {
          const toolName = metadata.action.tool_name || "unknown";
          toolUsage[toolName] = (toolUsage[toolName] || 0) + 1;
        }
      });
      return toolUsage;
    }, {} as Record<string, number>);

    setMetrics({
      totalMessages,
      responsesWithWorkflow,
      avgProcessingTime,
      totalSteps,
      avgStepsPerWorkflow,
      workflowDistribution,
      agentUsage,
      totalAgentLoops,
      avgAgentLoops,
      toolUsageDistribution
    });
  }, [messages]);

  // Format time in seconds
  const formatTime = (time: number): string => {
    return `${time.toFixed(2)}s`;
  };

  // Get the top workflow types by usage
  const topWorkflows = Object.entries(metrics.workflowDistribution)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  // Get the top agents by usage
  const topAgents = Object.entries(metrics.agentUsage)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 ${className}`}>
      {/* Total Workflows */}
      <Card className="dark:border-gray-800 dark:bg-gray-800/30">
        <CardHeader className="pb-2">
          <CardDescription className="dark:text-gray-400">Total Workflows</CardDescription>
          <CardTitle className="text-3xl flex items-center justify-between dark:text-white">
            {metrics.responsesWithWorkflow}
            <Workflow className="h-6 w-6 text-blue-500 dark:text-blue-400" />
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-gray-500 dark:text-gray-400">
          Out of {metrics.totalMessages} total messages
        </CardContent>
      </Card>

      {/* Average Processing Time */}
      <Card className="dark:border-gray-800 dark:bg-gray-800/30">
        <CardHeader className="pb-2">
          <CardDescription className="dark:text-gray-400">Average Processing Time</CardDescription>
          <CardTitle className="text-3xl flex items-center justify-between dark:text-white">
            {formatTime(metrics.avgProcessingTime)}
            <Clock className="h-6 w-6 text-green-500 dark:text-green-400" />
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-gray-500 dark:text-gray-400">
          Per workflow execution
        </CardContent>
      </Card>

      {/* Total Steps */}
      <Card className="dark:border-gray-800 dark:bg-gray-800/30">
        <CardHeader className="pb-2">
          <CardDescription className="dark:text-gray-400">Total Steps</CardDescription>
          <CardTitle className="text-3xl flex items-center justify-between dark:text-white">
            {metrics.totalSteps}
            <Layers className="h-6 w-6 text-purple-500 dark:text-purple-400" />
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-gray-500 dark:text-gray-400">
          Avg {metrics.avgStepsPerWorkflow.toFixed(1)} steps per workflow
        </CardContent>
      </Card>

      {/* Unique Agents */}
      <Card className="dark:border-gray-800 dark:bg-gray-800/30">
        <CardHeader className="pb-2">
          <CardDescription className="dark:text-gray-400">Unique Agents</CardDescription>
          <CardTitle className="text-3xl flex items-center justify-between dark:text-white">
            {Object.keys(metrics.agentUsage).length}
            <Users className="h-6 w-6 text-amber-500 dark:text-amber-400" />
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-gray-500 dark:text-gray-400">
          Specialized agent personas used
        </CardContent>
      </Card>

      {/* Workflow Distribution */}
      <Card className="md:col-span-2 dark:border-gray-800 dark:bg-gray-800/30">
        <CardHeader>
          <CardTitle className="text-lg flex items-center dark:text-white">
            <PieChart className="h-5 w-5 mr-2 text-blue-500 dark:text-blue-400" />
            Workflow Distribution
          </CardTitle>
        </CardHeader>
        <CardContent>
          {topWorkflows.length > 0 ? (
            <div className="space-y-4">
              {topWorkflows.map(([workflow, count]) => (
                <div key={workflow} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium dark:text-gray-300">{workflow}</span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {count} ({Math.round((count / metrics.responsesWithWorkflow) * 100)}%)
                    </span>
                  </div>
                  <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden dark:bg-gray-800">
                    <div
                      className="h-full bg-blue-500 rounded-full dark:bg-blue-600"
                      style={{ width: `${(count / metrics.responsesWithWorkflow) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-4 text-gray-500 dark:text-gray-400">No workflow data available</div>
          )}
        </CardContent>
      </Card>

      {/* Top Agents */}
      <Card className="md:col-span-2 dark:border-gray-800 dark:bg-gray-800/30">
        <CardHeader>
          <CardTitle className="text-lg flex items-center dark:text-white">
            <Users className="h-5 w-5 mr-2 text-amber-500 dark:text-amber-400" />
            Top Agents
          </CardTitle>
        </CardHeader>
        <CardContent>
          {topAgents.length > 0 ? (
            <div className="space-y-4">
              {topAgents.map(([agent, count]) => (
                <div key={agent} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium dark:text-gray-300">{agent}</span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {count} uses
                    </span>
                  </div>
                  <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden dark:bg-gray-800">
                    <div
                      className="h-full bg-amber-500 rounded-full dark:bg-amber-600"
                      style={{ width: `${(count / metrics.totalSteps) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-4 text-gray-500 dark:text-gray-400">No agent data available</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}