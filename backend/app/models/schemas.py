from enum import Enum
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
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Selection confidence score")
    complexity: Optional[str] = Field(default=None, description="Task complexity: simple, medium, or complex")

class AgentResponse(BaseModel):
    agent_role: str
    content: str 
    metadata: Optional[Dict[str, Any]] = None 

class WorkflowResponse(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_info: WorkflowSelection
    final_response: str 
    intermediate_steps: Optional[List[AgentResponse]] = None
    error: Optional[str] = None
    processing_time: float 

class AgentRole(str, Enum):
    PERCEPTION = "perception"
    REASONING = "reasoning"
    PLANNING = "planning"
    EXECUTION = "execution"
    REFLECTION = "reflection"
    COMMUNICATION = "communication"

class ToolCategory(str, Enum):
    SEARCH = "search"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    EXECUTION = "execution"
    COMMUNICATION = "communication"
    GENERAL = "general"

class PerceptionOutput(BaseModel):
    """Structured output from perception role"""
    key_findings: List[str] = Field(description="Key information discovered")
    information_gaps: List[str] = Field(description="Missing information needed")
    environment_state: Dict[str, Any] = Field(description="current understanding of environment")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in perception")

class ReasoningOutput(BaseModel):
    """Structured output from reasoning role"""
    conclusions: List[str] = Field(description="Key conclusions drawn")
    hypotheses: List[str] = Field(description="Hypotheses for testing")
    patterns_identified: List[str] = Field(description="Patterns found in data")
    reasoning_chain: str = Field(description="Chain of reasoning used")
    confidence: float = Field(ge=0.0, le=1.0)


class PlanningOutput(BaseModel):
    """Structured output from planning role"""
    goals: List[str] = Field(description="Current goals")
    next_actions: List[str] = Field(description="Specific next actions to take")
    dependencies: List[str] = Field(description="Dependencies blocking progress")
    estimated_completion: int = Field(description="Estimated steps to completion")
    plan_changes: str = Field(description="How plan changed from previous iteration")


class ExecutionOutput(BaseModel):
    """Structured output from execution role"""
    actions_taken: List[str] = Field(description="Actions completed")
    results: List[str] = Field(description="Results of actions")
    tools_used: List[str] = Field(description="Tools that were used")
    success: bool = Field(description="Whether execution succeeded")
    issues_encountered: List[str] = Field(default_factory=list)


class ReflectionOutput(BaseModel):
    """Structured output from reflection role"""
    successes: List[str] = Field(description="What worked well")
    failures: List[str] = Field(description="What didn't work")
    learnings: List[str] = Field(description="Key learnings")
    strategy_adjustments: List[str] = Field(description="Recommended strategy changes")
    continue_iterating: bool = Field(description="Should agent continue iterating")
    completion_confidence: float = Field(ge=0.0, le=1.0, description="Confidence task is complete")
    trigger_communication: bool = Field(description="Should communicate status now")


class ErrorRecoveryStrategy(BaseModel):
    """Strategy for recovering from errors"""
    error_type: str
    root_cause: str
    recovery_actions: List[str]
    retry_original_action: bool
    alternative_approach: Optional[str] = None
    estimated_recovery_time: int = Field(description="Steps needed to recover")

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

class PromptLevel(str, Enum):
    """Complexity levels for generated prompts."""
    SIMPLE = "simple"              # Level 1-2
    WORKFLOW = "workflow"          # Level 2-3
    CONTROL_FLOW = "control_flow"  # Level 3-4
    DELEGATION = "delegation"      # Level 4-5
    MULTI_AGENT = "multi_agent"    # Level 5-6
    AUTONOMOUS = "autonomous"      # Level 6-7


class PromptVariable(BaseModel):
    """A variable in the generated prompt."""
    name: str = Field(description="Variable name (e.g., 'user_query')")
    description: str = Field(description="What this variable represents")
    variable_type: str = Field(description="Type: static, dynamic, or computed")
    default_value: Optional[str] = Field(default=None, description="Default value if any")
    required: bool = Field(default=True)

class WorkflowStep(BaseModel):
    """A step in the prompt's workflow section."""
    step_number: int
    title: str
    description: str
    substeps: Optional[List[str]] = Field(default=None)
    condition: Optional[str] = Field(default=None, description="Conditional execution criteria")
    error_handling: Optional[str] = Field(default=None)


class PromptMetadata(BaseModel):
    """Metadata for the generated prompt."""
    recommended_model: str = Field(description="Recommended model (e.g., gemini-2.5-flash)")
    thinking_budget: Optional[int] = Field(default=None, description="Recommended thinking budget")
    temperature: float = Field(default=0.7)
    tools_required: Optional[List[str]] = Field(default=None)
    estimated_tokens: Optional[int] = Field(default=None)


class GeneratedPrompt(BaseModel):
    """Complete structured output for a generated prompt."""
    title: str = Field(description="Clear, descriptive title")
    purpose: str = Field(description="Direct, agent-focused purpose statement")
    level: PromptLevel = Field(description="Complexity level of this prompt")
    
    variables: List[PromptVariable] = Field(description="All variables used in the prompt")
    workflow: List[WorkflowStep] = Field(description="Step-by-step workflow")
    
    instructions: Optional[str] = Field(default=None, description="Auxiliary instructions")
    examples: Optional[List[str]] = Field(default=None, description="Usage examples")
    error_handling: Optional[str] = Field(default=None, description="Error handling guidelines")
    
    report_format: str = Field(description="Expected output format specification")
    metadata: PromptMetadata
    
    # The actual rendered prompt
    rendered_prompt: str = Field(description="The complete, ready-to-use prompt in markdown")
    design_rationale: str = Field(description="Brief explanation of design choices")


class PromptAnalysis(BaseModel):
    """Analysis of the task before prompt generation."""
    task_summary: str
    identified_requirements: List[str]
    recommended_level: PromptLevel
    suggested_tools: Optional[List[str]]
    complexity_factors: List[str]
    potential_challenges: List[str]


class PromptChainingStep(BaseModel):
    prompt: str
    output: Optional[str] = None

class RoutingDecision(BaseModel):
    chosen_route: str
    reasoning: str

