export interface QueryRequest {
  query: string;
  user_id?: string;
  session_id?: string;
}

export interface AgentPersona {
  role: string;
  persona: string;
  description: string;
  strengths: string[];
}

export interface WorkflowPersonas {
  [workflowType: string]: {
    [agentType: string]: AgentPersona;
  };
}

export interface WorkflowSelection {
  selected_workflow: string;
  reasoning: string;
  required_agents: string[];
  personas: WorkflowPersonas;
}

export interface AgentResponse {
  agent_role: string;
  content: string;
  metadata?: Record<string, unknown>;
}

export interface WorkflowResponse {
  final_response: string;
  workflow_info: WorkflowSelection;
  intermediate_steps: AgentResponse[];
  processing_time: number;
}

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: number;
  workflow_info?: WorkflowSelection;
  intermediate_steps?: AgentResponse[];
  processing_time?: number;
}

export interface ChatSession {
  id: string;
  messages: Message[];
  created_at: number;
  updated_at: number;
}