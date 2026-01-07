"""
Shared Persona Utilities

Consolidates persona-related helper functions used across all workflows.
Replaces duplicate generate_agent_context() implementations.

Usage:
    from app.core.helpers.persona_utils import generate_agent_context, get_agent_config
"""

from typing import Dict, Any, Optional
from google.genai import types


def generate_agent_context(
    agent_persona: Dict[str, Any],
    as_system_instruction: bool = True,
    include_config_hints: bool = False
) -> str:
    """
    Generate context from agent persona configuration.
    
    Outputs either:
    - System instruction format (clean, for SDK system_instruction param)
    - Embedded format (with delimiters, for prompt concatenation)
    
    Args:
        agent_persona: Dictionary containing agent configuration with keys:
            - role (str): The agent's role/title
            - persona (str): Personality description
            - description (str): Functional description
            - strengths (List[str]): List of the agent's key strengths
            - system_instruction (str, optional): Override system instruction
            - config (dict, optional): Agent-specific config (thinking_budget, temperature)
        as_system_instruction: If True, returns clean format for system_instruction param.
                              If False, returns delimited format for prompt embedding.
        include_config_hints: If True, appends behavioral hints based on config.
    
    Returns:
        Formatted context string appropriate for the selected mode.
        Returns default assistant message if agent_persona is empty/None.
    
    Example:
        >>> persona = {
        ...     "role": "Content Creator",
        ...     "persona": "Creative and thorough",
        ...     "description": "Generates high-quality content",
        ...     "strengths": ["Creativity", "Attention to detail"],
        ...     "config": {"thinking_budget": 1024, "temperature": 0.7}
        ... }
        >>> system_instruction = generate_agent_context(persona)
        >>> # Use as: config=types.GenerateContentConfig(system_instruction=system_instruction)
    """
    if not agent_persona:
        return "You are a helpful assistant."
    
    # Allow explicit system_instruction override
    if "system_instruction" in agent_persona and agent_persona["system_instruction"]:
        return agent_persona["system_instruction"]
    
    # Extract persona fields with defaults
    role = agent_persona.get("role", "Assistant")
    persona = agent_persona.get("persona", "Helpful and knowledgeable")
    description = agent_persona.get("description", "Provides helpful responses")
    strengths = agent_persona.get("strengths", ["Assistance"])
    
    # Format strengths
    if isinstance(strengths, list):
        strengths_text = "\n".join([f"  - {s}" for s in strengths])
    else:
        strengths_text = f"  - {strengths}"
    
    # Build core context
    core_context = f"""You are the {role}.

## Character
{persona}

## Function
{description}

## Key Strengths
{strengths_text}

Embody this role fully in all responses. Draw on your strengths to excel at your assigned tasks."""

    # Add behavioral hints from config if requested
    if include_config_hints and "config" in agent_persona:
        config = agent_persona["config"]
        thinking_budget = config.get("thinking_budget", 0)
        
        if thinking_budget > 1000:
            core_context += "\n\nYou have time to think deeply. Reason carefully step-by-step before responding."
        elif thinking_budget > 0:
            core_context += "\n\nBalance thoroughness with efficiency. Think when beneficial, but stay focused."
        else:
            core_context += "\n\nRespond efficiently and directly. Prioritize speed and precision."
    
    if as_system_instruction:
        # Clean format for SDK system_instruction parameter
        return core_context
    else:
        # Delimited format for prompt embedding (backward compatible)
        strengths_inline = ", ".join(strengths) if isinstance(strengths, list) else strengths
        return f"""
=== AGENT CONTEXT ===
ROLE: {role}
CHARACTER: {persona}
FUNCTION: {description}
STRENGTHS: {strengths_inline}
====================

{core_context}
"""


def get_agent_config(agent_persona: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract SDK configuration values from persona.
    
    Returns dict suitable for unpacking into generate() or generate_structured() calls.
    
    Args:
        agent_persona: Persona dictionary, optionally containing "config" key
    
    Returns:
        Dict with keys: temperature, thinking_budget, max_tokens
        Uses defaults if config not present.
    
    Example:
        >>> persona = {"role": "Planner", "config": {"thinking_budget": 1024, "temperature": 0.7}}
        >>> config = get_agent_config(persona)
        >>> response = await client.generate(prompt, **config)  # Unpack config
    """
    defaults = {
        "temperature": 0.7,
        "thinking_budget": None,  # None = use model default
        "max_tokens": 8192,
    }
    
    if not agent_persona:
        return defaults.copy()
    
    config = agent_persona.get("config", {})
    
    return {
        "temperature": config.get("temperature", defaults["temperature"]),
        "thinking_budget": config.get("thinking_budget", defaults["thinking_budget"]),
        "max_tokens": config.get("max_tokens", defaults["max_tokens"]),
    }


def build_generate_content_config(
    agent_persona: Dict[str, Any],
    **overrides
) -> types.GenerateContentConfig:
    """
    Build a complete GenerateContentConfig from persona.
    
    Combines persona's system instruction and config into SDK-ready config object.
    
    Args:
        agent_persona: Persona dictionary
        **overrides: Override any config value (temperature, max_output_tokens, etc.)
    
    Returns:
        types.GenerateContentConfig ready for use with client.models.generate_content()
    
    Example:
        >>> persona = orchestrator_workers["orchestrator_agent"]
        >>> config = build_generate_content_config(persona, max_output_tokens=4096)
        >>> response = await client.aio.models.generate_content(
        ...     model="gemini-2.5-flash",
        ...     contents=prompt,
        ...     config=config
        ... )
    """
    agent_config = get_agent_config(agent_persona)
    system_instruction = generate_agent_context(agent_persona, as_system_instruction=True)
    
    # Build thinking config if budget specified
    thinking_budget = overrides.pop("thinking_budget", agent_config["thinking_budget"])
    thinking_config = None
    if thinking_budget is not None and thinking_budget > 0:
        thinking_config = types.ThinkingConfig(thinking_budget=thinking_budget)
    
    return types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=overrides.pop("temperature", agent_config["temperature"]),
        max_output_tokens=overrides.pop("max_tokens", agent_config["max_tokens"]),
        thinking_config=thinking_config,
        **overrides  # Pass through any additional config options
    )


# =============================================================================
# Pydantic Model Version (Optional - for future evolution)
# =============================================================================

try:
    from pydantic import BaseModel
    from typing import List
    
    class AgentPersonaModel(BaseModel):
        """
        Structured persona with SDK integration.
        
        Use this when you want type safety and validation.
        Can coexist with dict-based personas during migration.
        """
        role: str
        persona: str
        description: str
        strengths: List[str]
        system_instruction: Optional[str] = None
        config: Optional[Dict[str, Any]] = None
        
        def to_system_instruction(self, include_hints: bool = False) -> str:
            """Generate system instruction string."""
            return generate_agent_context(
                self.model_dump(),
                as_system_instruction=True,
                include_config_hints=include_hints
            )
        
        def to_config(self, **overrides) -> types.GenerateContentConfig:
            """Generate SDK config object."""
            return build_generate_content_config(self.model_dump(), **overrides)
        
        def get_thinking_budget(self) -> Optional[int]:
            """Get thinking budget from config."""
            if self.config:
                return self.config.get("thinking_budget")
            return None
        
        def get_temperature(self) -> float:
            """Get temperature from config."""
            if self.config:
                return self.config.get("temperature", 0.7)
            return 0.7

except ImportError:
    # Pydantic not available - that's fine, dict version works
    AgentPersonaModel = None