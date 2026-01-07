# app/core/workflow_selector.py
"""
Workflow Selector - Phase 2 Modernization

Uses structured outputs (Pydantic) instead of function calling for more
reliable workflow selection with confidence scoring.
"""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
import logging

from app.models.schemas import WorkflowSelection
from app.core.llm_client import get_functions_client
from app.personas.agent_personas import agent_personas, get_workflow_personas
from app.core.helpers.persona_utils import generate_agent_context, get_agent_config


# ============================================================================
# Pydantic Schemas for Structured Output
# ============================================================================

class WorkflowType(str, Enum):
    """Available workflow patterns."""
    PROMPT_CHAINING = "prompt_chaining"
    ROUTING = "routing"
    PARALLEL_SECTIONING = "parallel_sectioning"
    PARALLEL_VOTING = "parallel_voting"
    PARALLEL_SECTION_VOTING = "parallel_section_voting"
    ORCHESTRATOR_WORKERS = "orchestrator_workers"
    EVALUATOR_OPTIMIZER = "evaluator_optimizer"
    PROMPT_GENERATOR = "prompt_generator"
    AUTONOMOUS_AGENT = "autonomous_agent"


class WorkflowDecision(BaseModel):
    """Structured output for workflow selection with confidence scoring."""
    
    selected_workflow: WorkflowType = Field(
        description="The workflow pattern best suited for the query"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score (0.0-1.0) in this selection"
    )
    reasoning: str = Field(
        description="Brief explanation for why this workflow is most appropriate"
    )
    alternative_workflow: Optional[WorkflowType] = Field(
        default=None,
        description="Second-best workflow if confidence is below 0.8"
    )
    required_agents: List[str] = Field(
        default_factory=list,
        description="Agent roles needed for this workflow"
    )
    complexity_assessment: str = Field(
        default="medium",
        description="Task complexity: simple, medium, or complex"
    )


# ============================================================================
# Workflow Descriptions (for prompt construction)
# ============================================================================

WORKFLOW_DESCRIPTIONS = """
## Available Workflow Patterns

### 1. prompt_chaining
**Best for:** Sequential, multi-step tasks where each step builds on the previous.
**Examples:** "Write a blog post and then translate it", "Summarize then create talking points"
**Signals:** Sequential words (then, after, next), clear step order, transformation chains

### 2. routing  
**Best for:** Queries that fit distinct categories needing specialized handling.
**Examples:** "Reset my password", "Explain photosynthesis", "Debug this error"
**Signals:** Single clear intent, domain-specific questions, FAQ-style queries

### 3. parallel_sectioning
**Best for:** Complex tasks with independent components that can run simultaneously.
**Examples:** "Analyze from marketing, technical, and financial perspectives"
**Signals:** Multiple independent aspects, "perspectives", "angles", comprehensive analysis

### 4. parallel_voting
**Best for:** Tasks requiring consensus, verification, or high-confidence decisions.
**Examples:** "Is this phishing?", "Is this content appropriate?", "Verify this claim"
**Signals:** Yes/no decisions, safety checks, fact verification, consensus needed

### 5. parallel_section_voting
**Best for:** Complex tasks requiring both decomposition AND multi-perspective validation.
**Examples:** "Write a comprehensive report with verified facts", "Analyze this proposal from all angles with consensus"
**Signals:** Complex + needs validation, comprehensive + verified, multi-faceted + consensus

### 5. orchestrator_workers
**Best for:** Complex tasks requiring dynamic subtask planning and coordination.
**Examples:** "Plan my vacation", "Refactor this codebase", "Create marketing strategy"
**Signals:** Open-ended complexity, multiple unknowns, requires planning phase

### 6. evaluator_optimizer
**Best for:** Tasks requiring iterative refinement against quality criteria.
**Examples:** "Write a professional email", "Optimize this query", "Improve this essay"
**Signals:** Quality improvement, "make it better", specific criteria to meet

### 7. prompt_generator
**Best for:** Creating optimized prompts/templates for AI tasks.
**Examples:** "Create a prompt for summarizing legal docs", "Build a code review prompt"
**Signals:** Meta-prompting, "create a prompt", "generate instructions for AI"

### 8. autonomous_agent
**Best for:** Open-ended research/exploration requiring tool use and adaptive planning.
**Examples:** "Research quantum computing developments", "Investigate this security issue"
**Signals:** Research tasks, exploration, requires external tools, multi-step discovery
"""


# ============================================================================
# Main Selection Function
# ============================================================================

async def select_workflow(
    user_query: str, 
    use_autonomous_exclusively: bool = False
) -> WorkflowSelection:
    """
    Select the optimal workflow for a user query using structured output.
    
    Args:
        user_query: The user's request to analyze
        use_autonomous_exclusively: Force autonomous_agent workflow
        
    Returns:
        WorkflowSelection with workflow name, reasoning, and personas
    """
    
    # Handle forced autonomous mode
    if use_autonomous_exclusively:
        logging.info("Forcing 'autonomous_agent' workflow due to explicit flag.")
        return _build_workflow_selection(
            workflow_name="autonomous_agent",
            reasoning="Autonomous agent workflow selected by explicit user/system choice.",
            confidence=1.0
        )
    
    # Get selector persona from meta
    selector_persona = agent_personas.get("meta", {}).get("workflow_selector", {})
    selector_config = get_agent_config(selector_persona)
    system_instruction = generate_agent_context(selector_persona, as_system_instruction=True)
    
    # Build the selection prompt
    selection_prompt = f"""{WORKFLOW_DESCRIPTIONS}

---

## Your Task

Analyze the following user query and select the most appropriate workflow pattern.

**User Query:** "{user_query}"

Consider:
1. What is the core intent of this query?
2. Does it require sequential steps, parallel processing, or dynamic planning?
3. Is quality iteration needed, or is a single pass sufficient?
4. Does it involve prompt/template creation (→ prompt_generator)?

Provide your selection with confidence score and reasoning.
"""

    try:
        functions_client = get_functions_client()
        
        # Use structured output instead of function calling
        decision: WorkflowDecision = await functions_client.generate_structured(
            prompt=selection_prompt,
            response_schema=WorkflowDecision,
            system_instruction=system_instruction,
            temperature=selector_config.get("temperature", 0.3),
            thinking_budget=selector_config.get("thinking_budget", 256),
        )
        
        # Log the decision
        logging.info(
            f"Workflow selected: {decision.selected_workflow.value} "
            f"(confidence: {decision.confidence:.0%}, "
            f"complexity: {decision.complexity_assessment})"
        )
        
        # If low confidence, log the alternative
        if decision.confidence < 0.8 and decision.alternative_workflow:
            logging.info(f"Alternative considered: {decision.alternative_workflow.value}")
        
        return _build_workflow_selection(
            workflow_name=decision.selected_workflow.value,
            reasoning=decision.reasoning,
            confidence=decision.confidence,
            complexity=decision.complexity_assessment,
            required_agents=decision.required_agents
        )
        
    except Exception as e:
        logging.error(f"Workflow selection failed: {e}")
        # Fallback to orchestrator_workers as safe default for complex queries
        return _build_workflow_selection(
            workflow_name="orchestrator_workers",
            reasoning=f"Fallback to orchestrator_workers due to selection error: {str(e)}",
            confidence=0.5,
            complexity="medium"
        )


def _build_workflow_selection(
    workflow_name: str,
    reasoning: str,
    confidence: float = 1.0,
    complexity: str = "medium",
    required_agents: List[str] = None
) -> WorkflowSelection:
    """
    Build a WorkflowSelection object with personas.
    
    Args:
        workflow_name: Name of the selected workflow
        reasoning: Explanation for the selection
        confidence: Confidence score (0.0-1.0)
        complexity: Task complexity (simple/medium/complex)
        required_agents: List of agent roles (auto-detected if not provided)
        
    Returns:
        Complete WorkflowSelection object
    """
    # Get personas for the selected workflow
    personas = get_workflow_personas(workflow_name)
    
    # Auto-detect required agents from personas if not provided
    if required_agents is None or len(required_agents) == 0:
        required_agents = list(personas.keys()) if personas else []
    
    return WorkflowSelection(
        selected_workflow=workflow_name,
        reasoning=reasoning,
        required_agents=required_agents,
        personas=personas,
        confidence=confidence,
        complexity=complexity
    )


# ============================================================================
# Utility Functions
# ============================================================================

def get_available_workflows() -> List[str]:
    """Return list of available workflow names."""
    return [wf.value for wf in WorkflowType]


def get_workflow_description(workflow_name: str) -> str:
    """Get description for a specific workflow."""
    descriptions = {
        "prompt_chaining": "Sequential multi-step processing",
        "routing": "Category-based dispatch to specialists",
        "parallel_sectioning": "Independent parallel component processing",
        "parallel_voting": "Multi-perspective consensus building",
        "parallel_section_voting": "Section decomposition with multi-perspective voting",
        "orchestrator_workers": "Dynamic subtask planning and coordination",
        "evaluator_optimizer": "Iterative quality refinement",
        "prompt_generator": "AI prompt/template creation",
        "autonomous_agent": "Open-ended tool-using exploration",
    }
    return descriptions.get(workflow_name, "Unknown workflow")
