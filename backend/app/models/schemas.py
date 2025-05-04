from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union 
import uuid

class QueryRequest(BaseModel):
    query: str 
    user_id: Optional[str] = None
    session_id: Optional[str] = None 
    config: Optional[Dict[str, Any]] = None

class WorkflowSelection(BaseModel):
    selected_workflow: str 
    reasoning: Optional[str] = None
    required_agents: Optional[List[str]] = None
    personas: Optional[Dict[str, Dict[str, Any]]] = None

class AgentResponse(BaseModel):
    agent_role: str
    content: str 
    metadata: Optional[Dict[str, Any]] = None 

class WorkflowResponse(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    selected_workflow: str
    final_response: str 
    intermediate_steps: Optional[List[AgentResponse]] = None
    error: Optional[str] = None
    processing_time: float 

class ToolDefinition:
    """
    Definition of a tool available to the autonomous agent
    """
    def __init__(self, name: str, description: str, parameters: Dict[str, Any] = None, function=None):
        self.name = name
        self.description = description
        # Store parameters as provided, often a JSON schema dict already
        self.parameters = parameters or {"type": "object", "properties": {}}
        self.function = function
        
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for use in prompts or API calls"""
        # Return the structure expected by OpenAI/Azure function calling
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters # Assumes parameters is already a valid JSON schema
        }

class PromptChainingStep(BaseModel):
    prompt: str
    output: Optional[str] = None

class RoutingDecision(BaseModel):
    chosen_route: str
    reasoning: str

