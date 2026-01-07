# app/core/workflows/prompt_generator.py
"""
Prompt Generator Workflow

A meta-workflow that generates optimized agentic prompts for specific tasks.
Uses structured outputs and multi-stage refinement to produce high-quality prompts.
"""

from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Tuple, List, Optional, Dict, Any
import asyncio
import logging

from app.models.schemas import WorkflowSelection, AgentResponse
from app.models.schemas import (
    GeneratedPrompt, 
    PromptAnalysis, 
    PromptLevel,
    PromptVariable,
    WorkflowStep,
    PromptMetadata
)
from app.config import settings
from app.core.llm_client import get_functions_client, get_llm_client


# ============================================================================
# Helper Functions
# ============================================================================

def generate_agent_context(agent_persona: dict) -> str:
    """Generate system instruction from agent persona."""
    if not agent_persona:
        return "You are a helpful assistant."
    
    if "system_instruction" in agent_persona:
        return agent_persona["system_instruction"]
    
    role = agent_persona.get("role", "Assistant")
    persona = agent_persona.get("persona", "Helpful and knowledgeable")
    description = agent_persona.get("description", "Provides helpful responses")
    strengths = agent_persona.get("strengths", ["Assistance"])
    
    strengths_text = "\n".join([f"  - {s}" for s in strengths])
    
    return f"""You are the {role}.

## Character
{persona}

## Function
{description}

## Key Strengths
{strengths_text}

Embody this role fully in all responses."""


def level_to_int(level: PromptLevel) -> int:
    """Convert PromptLevel enum to integer for display."""
    mapping = {
        PromptLevel.SIMPLE: 1,
        PromptLevel.WORKFLOW: 2,
        PromptLevel.CONTROL_FLOW: 3,
        PromptLevel.DELEGATION: 4,
        PromptLevel.MULTI_AGENT: 5,
        PromptLevel.AUTONOMOUS: 7,
    }
    return mapping.get(level, 3)


# ============================================================================
# Main Workflow
# ============================================================================

async def execute(
    workflow_selection: WorkflowSelection,
    user_query: str,
    complexity_hint: Optional[str] = None,
    include_examples: bool = True,
    target_model: str = "gemini-3-flash-preview"
) -> Tuple[str, List[AgentResponse]]:
    """
    Generate an optimized agentic prompt for the given task description.
    
    Args:
        workflow_selection: Workflow configuration with personas
        user_query: The task description to generate a prompt for
        complexity_hint: Optional hint ("low", "medium", "high", "autonomous")
        include_examples: Whether to include usage examples
        target_model: The model the generated prompt will be used with
    
    Returns:
        Tuple of (rendered_prompt, intermediate_steps)
    """
    functions_client = get_functions_client()
    llm_client = get_llm_client()
    
    workflow_personas = workflow_selection.personas.get("prompt_generator", {})
    intermediate_steps = []
    
    # =========================================================================
    # STEP 1: Analyze the Task
    # =========================================================================
    analyzer_agent = workflow_personas.get("analyzer_agent", {})
    
    analysis_prompt = f"""Analyze the following task description for prompt generation:

TASK DESCRIPTION:
{user_query}

COMPLEXITY HINT: {complexity_hint or "not specified"}
TARGET MODEL: {target_model}

Provide a thorough analysis including:
1. Summarize what the task requires
2. List all identified requirements (explicit and implicit)
3. Recommend a complexity level with justification
4. Identify any tools or APIs that might be needed
5. List factors contributing to complexity
6. Identify potential challenges and edge cases"""

    try:
        analysis: PromptAnalysis = await functions_client.generate_structured(
            prompt=analysis_prompt,
            response_schema=PromptAnalysis,
            system_instruction=generate_agent_context(analyzer_agent),
            thinking_budget=1024,
        )
    except Exception as e:
        logging.error(f"Task analysis failed: {e}")
        # Fallback analysis
        analysis = PromptAnalysis(
            task_summary=user_query[:200],
            identified_requirements=["Process user request"],
            recommended_level=PromptLevel.WORKFLOW,
            suggested_tools=None,
            complexity_factors=["Unable to fully analyze"],
            potential_challenges=["Analysis failed - using defaults"]
        )
    
    intermediate_steps.append(AgentResponse(
        agent_role="Task Analyst",
        content=f"""**Task Summary:** {analysis.task_summary}

**Recommended Level:** {analysis.recommended_level.value} (Level {level_to_int(analysis.recommended_level)})

**Requirements Identified:** {len(analysis.identified_requirements)}
{chr(10).join(f'- {req}' for req in analysis.identified_requirements)}

**Complexity Factors:**
{chr(10).join(f'- {factor}' for factor in analysis.complexity_factors)}

**Potential Challenges:**
{chr(10).join(f'- {challenge}' for challenge in analysis.potential_challenges)}""",
        metadata=analysis.model_dump()
    ))
    
    # =========================================================================
    # STEP 2: Generate the Prompt
    # =========================================================================
    generator_agent = workflow_personas.get("generator_agent", {})
    
    generation_prompt = f"""Generate an optimized agentic prompt based on this analysis:

ORIGINAL TASK:
{user_query}

ANALYSIS RESULTS:
- Task Summary: {analysis.task_summary}
- Recommended Level: {analysis.recommended_level.value}
- Requirements: {', '.join(analysis.identified_requirements)}
- Suggested Tools: {', '.join(analysis.suggested_tools) if analysis.suggested_tools else 'None identified'}
- Complexity Factors: {', '.join(analysis.complexity_factors)}
- Potential Challenges: {', '.join(analysis.potential_challenges)}

GENERATION REQUIREMENTS:
- Target Model: {target_model}
- Include Examples: {include_examples}
- Optimize for: Clarity, completeness, and robustness

Generate a complete, production-ready prompt with all required sections.
The 'rendered_prompt' field should contain the final markdown-formatted prompt ready for use."""

    try:
        generated: GeneratedPrompt = await functions_client.generate_structured(
            prompt=generation_prompt,
            response_schema=GeneratedPrompt,
            system_instruction=generate_agent_context(generator_agent),
            thinking_budget=2048,  # Higher budget for creative generation
        )
    except Exception as e:
        logging.error(f"Prompt generation failed: {e}")
        raise RuntimeError(f"Failed to generate prompt: {e}")
    
    intermediate_steps.append(AgentResponse(
        agent_role="Prompt Engineer",
        content=f"""**Generated Prompt:** {generated.title}

**Level:** {generated.level.value}
**Purpose:** {generated.purpose}

**Variables:** {len(generated.variables)}
**Workflow Steps:** {len(generated.workflow)}

**Design Rationale:**
{generated.design_rationale}""",
        metadata={
            "title": generated.title,
            "level": generated.level.value,
            "variables_count": len(generated.variables),
            "workflow_steps_count": len(generated.workflow),
        }
    ))
    
    # =========================================================================
    # STEP 3: Review and Refine (Optional Enhancement)
    # =========================================================================
    reviewer_agent = workflow_personas.get("reviewer_agent", {})
    
    review_prompt = f"""Review this generated prompt for quality and completeness:

ORIGINAL TASK:
{user_query}

GENERATED PROMPT:
```markdown
{generated.rendered_prompt}
```

PROMPT METADATA:
- Level: {generated.level.value}
- Variables: {len(generated.variables)}
- Workflow Steps: {len(generated.workflow)}

Review against these criteria:
1. Completeness - Are all necessary sections present?
2. Clarity - Are instructions unambiguous?
3. Variables - Are all properly defined and used?
4. Workflow - Is the sequence logical?
5. Error Handling - Are edge cases addressed?
6. Output Format - Is expected output clear?

Provide:
1. Overall quality assessment (1-10)
2. Specific issues found (if any)
3. Suggested improvements (if any)
4. Final recommendation (approve/revise)"""

    try:
        review_response = await llm_client.generate(
            prompt=review_prompt,
            system_instruction=generate_agent_context(reviewer_agent),
            temperature=0.3,  # Lower temperature for critical review
        )
    except Exception as e:
        logging.warning(f"Review step failed: {e}")
        review_response = "Review skipped due to error."
    
    intermediate_steps.append(AgentResponse(
        agent_role="Prompt Reviewer",
        content=review_response,
        metadata={"step": "review"}
    ))
    
    # =========================================================================
    # Final Output
    # =========================================================================
    
    # Create a comprehensive output
    final_output = f"""# Generated Prompt: {generated.title}

## Metadata
- **Complexity Level:** {generated.level.value} (Level {level_to_int(generated.level)})
- **Recommended Model:** {generated.metadata.recommended_model}
- **Temperature:** {generated.metadata.temperature}
- **Thinking Budget:** {generated.metadata.thinking_budget or 'Default'}

## Design Rationale
{generated.design_rationale}

---

## The Prompt

{generated.rendered_prompt}

---

## Variables Reference

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
{chr(10).join(f"| `{v.name}` | {v.variable_type} | {'Yes' if v.required else 'No'} | {v.description} |" for v in generated.variables)}

## Workflow Summary

{chr(10).join(f"{step.step_number}. **{step.title}**: {step.description}" for step in generated.workflow)}
"""
    
    intermediate_steps.append(AgentResponse(
        agent_role="Output Formatter",
        content=final_output,
        metadata=generated.model_dump()
    ))
    
    return final_output, intermediate_steps


# ============================================================================
# Utility Function for Direct Use
# ============================================================================

async def generate_prompt(
    task_description: str,
    complexity: str = "medium",
    target_model: str = "gemini-2.5-flash",
    include_examples: bool = True
) -> GeneratedPrompt:
    """
    Simplified utility function for generating prompts without full workflow.
    
    Useful for programmatic prompt generation from other workflows.
    
    Args:
        task_description: What the prompt should accomplish
        complexity: "low", "medium", "high", or "autonomous"
        target_model: Model the prompt will be used with
        include_examples: Include usage examples
    
    Returns:
        GeneratedPrompt object with all fields populated
    """
    functions_client = get_functions_client()
    
    complexity_to_level = {
        "low": PromptLevel.SIMPLE,
        "medium": PromptLevel.CONTROL_FLOW,
        "high": PromptLevel.MULTI_AGENT,
        "autonomous": PromptLevel.AUTONOMOUS,
    }
    
    target_level = complexity_to_level.get(complexity, PromptLevel.CONTROL_FLOW)
    
    prompt = f"""Generate an optimized agentic prompt for this task:

TASK: {task_description}

TARGET COMPLEXITY: {target_level.value}
TARGET MODEL: {target_model}
INCLUDE EXAMPLES: {include_examples}

Create a complete, production-ready prompt with:
- Clear title and purpose
- Well-defined variables
- Step-by-step workflow
- Error handling
- Output format specification
- The full rendered prompt in markdown"""

    system_instruction = """You are an expert Prompt Engineer. Generate clear, complete, 
and robust prompts optimized for AI agents. Use direct language, include all necessary 
sections, and ensure the prompt handles edge cases appropriately."""

    return await functions_client.generate_structured(
        prompt=prompt,
        response_schema=GeneratedPrompt,
        system_instruction=system_instruction,
        thinking_budget=2048,
    )