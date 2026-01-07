"""
Autonomous Agent Workflow Module (Modernized)

A modern autonomous agent implementation using Gemini's latest capabilities including:
- Structured outputs with Pydantic schemas
- Native multi-turn chat API
- Parallel tool execution
- Intelligent stopping conditions
- Search grounding integration
- Advanced error recovery

The agent operates through distinct roles: perception, reasoning, planning, execution, 
reflection, and communication, with each role having specific responsibilities and tools.
"""

from typing import List, Dict, Any, Optional, Set
import logging
import json
import asyncio
import time
import os
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from google.genai import types

from app.models.schemas import WorkflowSelection, AgentResponse, WorkflowResponse, ToolDefinition, ToolCategory, PerceptionOutput, ReasoningOutput, PlanningOutput, ExecutionOutput, ReflectionOutput, ErrorRecoveryStrategy, AgentRole
from app.core.llm_client import get_functions_client, get_llm_client, GoogleGeminiClient, GoogleGeminiFunctions
from app.tools.registry import get_all_tools

# Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_dir = "logs/autonomous_agent"
os.makedirs(log_dir, exist_ok=True)
conversation_dir = f"{log_dir}/conversations"
os.makedirs(conversation_dir, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"{log_dir}/agent_{timestamp}.log"
file_handler = logging.FileHandler(log_file)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Configuration
MAX_AGENT_ITERATIONS = 15
PARALLEL_TOOL_EXECUTION = True
USE_SEARCH_GROUNDING = True

# ============================================================================
# Agent State Management
# ============================================================================

class AgentState:
    """Manages agent state across iterations"""
    
    def __init__(self, task_description: str, session_id: str):
        self.task_description = task_description
        self.session_id = session_id
        self.iteration = 0
        
        # Core state
        self.world_model: Dict[str, Any] = {}
        self.current_plan: Optional[PlanningOutput] = None
        self.history: List[Dict[str, Any]] = []
        self.learnings: List[str] = []
        
        # Role-specific outputs
        self.perception: Optional[PerceptionOutput] = None
        self.reasoning: Optional[ReasoningOutput] = None
        self.execution: Optional[ExecutionOutput] = None
        self.reflection: Optional[ReflectionOutput] = None
        
        # Tracking
        self.tools_used: Set[str] = set()
        self.errors: List[Dict[str, Any]] = []
        
    def to_context(self) -> str:
        """Convert state to context string for LLM"""
        context = f"""
TASK: {self.task_description}
ITERATION: {self.iteration}

CURRENT PLAN:
{json.dumps(self.current_plan.dict() if self.current_plan else {}, indent=2)}

RECENT PERCEPTION:
{json.dumps(self.perception.dict() if self.perception else {}, indent=2)}

RECENT REASONING:
{json.dumps(self.reasoning.dict() if self.reasoning else {}, indent=2)}

RECENT EXECUTION:
{json.dumps(self.execution.dict() if self.execution else {}, indent=2)}

LEARNINGS:
{json.dumps(self.learnings[-3:] if self.learnings else [], indent=2)}

WORLD MODEL:
{json.dumps(self.world_model, indent=2, default=str)}
"""
        return context
    
    def add_history(self, role: str, output: Any, metadata: Dict = None):
        """Add entry to history"""
        self.history.append({
            "iteration": self.iteration,
            "role": role,
            "output": output.dict() if hasattr(output, 'dict') else output,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })


# ============================================================================
# Tool Management
# ============================================================================

def categorize_tool(tool: ToolDefinition) -> ToolCategory:
    """Intelligently categorize a tool based on its properties"""
    name_lower = tool.name.lower()
    desc_lower = tool.description.lower()
    
    search_keywords = ['search', 'web', 'browse', 'scrape', 'crawl', 'gather', 'fetch', 'retrieve']
    analysis_keywords = ['analyze', 'infer', 'pattern', 'evaluate', 'compare', 'reason', 'calculate']
    planning_keywords = ['plan', 'schedule', 'organize', 'prioritize', 'goal']
    execution_keywords = ['create', 'update', 'delete', 'execute', 'run', 'send', 'write']
    communication_keywords = ['report', 'notify', 'visualize', 'summarize', 'present']
    
    text = f"{name_lower} {desc_lower}"
    
    if any(kw in text for kw in search_keywords):
        return ToolCategory.SEARCH
    elif any(kw in text for kw in analysis_keywords):
        return ToolCategory.ANALYSIS
    elif any(kw in text for kw in planning_keywords):
        return ToolCategory.PLANNING
    elif any(kw in text for kw in execution_keywords):
        return ToolCategory.EXECUTION
    elif any(kw in text for kw in communication_keywords):
        return ToolCategory.COMMUNICATION
    else:
        return ToolCategory.GENERAL


def get_tools_for_role(role: AgentRole, all_tools: Dict[str, ToolDefinition]) -> List[Dict[str, Any]]:
    """Get relevant tools for a specific agent role"""
    categorized = {category: [] for category in ToolCategory}
    
    for tool in all_tools.values():
        category = categorize_tool(tool)
        categorized[category].append({
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters if hasattr(tool, 'parameters') else {}
        })
    
    # Role-specific tool assignment
    role_tool_map = {
        AgentRole.PERCEPTION: [ToolCategory.SEARCH, ToolCategory.GENERAL],
        AgentRole.REASONING: [ToolCategory.ANALYSIS, ToolCategory.GENERAL],
        AgentRole.PLANNING: [ToolCategory.PLANNING, ToolCategory.ANALYSIS],
        AgentRole.EXECUTION: list(ToolCategory),  # All tools
        AgentRole.REFLECTION: [ToolCategory.ANALYSIS, ToolCategory.GENERAL],
        AgentRole.COMMUNICATION: [ToolCategory.COMMUNICATION, ToolCategory.GENERAL]
    }
    
    allowed_categories = role_tool_map.get(role, [ToolCategory.GENERAL])
    tools = []
    for category in allowed_categories:
        tools.extend(categorized[category])
    
    return tools


# ============================================================================
# Tool Execution
# ============================================================================

async def execute_tool(
    tool_name: str,
    tool_args: Dict[str, Any],
    session_id: str,
    all_tools: Dict[str, ToolDefinition]
) -> Dict[str, Any]:
    """Execute a single tool and return structured result"""
    try:
        tool_def = all_tools.get(tool_name)
        if not tool_def or not callable(tool_def.function):
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found or not callable",
                "result": None
            }
        
        # Execute tool (handle both sync and async)
        if asyncio.iscoroutinefunction(tool_def.function):
            result = await tool_def.function(session_id, **tool_args)
        else:
            result = tool_def.function(session_id, **tool_args)
        
        return {
            "success": True,
            "error": None,
            "result": result,
            "tool_name": tool_name
        }
        
    except Exception as e:
        logger.error(f"Error executing tool '{tool_name}': {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "result": None,
            "tool_name": tool_name
        }


async def execute_tools_parallel(
    function_calls: List[Any],
    session_id: str,
    all_tools: Dict[str, ToolDefinition]
) -> List[Dict[str, Any]]:
    """Execute multiple tools in parallel"""
    tasks = [
        execute_tool(fc.name, dict(fc.args) if fc.args else {}, session_id, all_tools)
        for fc in function_calls
    ]
    return await asyncio.gather(*tasks)


# ============================================================================
# Agent Role Execution
# ============================================================================

class ModernAutonomousAgent:
    """Modern autonomous agent with structured outputs and chat-based interaction"""
    
    def __init__(self, task_description: str, session_id: str):
        self.state = AgentState(task_description, session_id)
        self.llm_client = get_functions_client()
        self.all_tools = get_all_tools()
        self.chats: Dict[AgentRole, Any] = {}
        
        # Initialize chat sessions for each role
        self._initialize_chats()
    
    def _initialize_chats(self):
        """Initialize separate chat sessions for each role"""
        role_instructions = {
            AgentRole.PERCEPTION: f"You are the Perception agent. Your job is to gather and observe information about: {self.state.task_description}. Use available tools to collect data and identify information gaps.",
            AgentRole.REASONING: f"You are the Reasoning agent. Analyze information and draw conclusions about: {self.state.task_description}. Identify patterns and form hypotheses.",
            AgentRole.PLANNING: f"You are the Planning agent. Create and refine plans to accomplish: {self.state.task_description}. Break down goals and sequence actions.",
            AgentRole.EXECUTION: f"You are the Execution agent. Carry out planned actions for: {self.state.task_description}. Use tools to accomplish tasks.",
            AgentRole.REFLECTION: f"You are the Reflection agent. Evaluate progress on: {self.state.task_description}. Assess what's working and suggest improvements.",
            AgentRole.COMMUNICATION: f"You are the Communication agent. Report on progress for: {self.state.task_description}. Summarize findings clearly."
        }
        
        for role, instruction in role_instructions.items():
            try:
                self.chats[role] = self.llm_client.client.chats.create(
                    model=self.llm_client.model,
                    config=types.GenerateContentConfig(
                        system_instruction=instruction
                    )
                )
            except Exception as e:
                logger.warning(f"Could not create chat for {role}: {e}. Will use stateless calls.")
                self.chats[role] = None
    
    async def _call_role(
        self,
        role: AgentRole,
        prompt: str,
        response_schema: Optional[type[BaseModel]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        use_thinking: bool = False,
        use_search_grounding: bool = False
    ) -> Dict[str, Any]:
        """Call a specific role with structured output"""
        
        # Build config
        config_params = {}
        
        if response_schema:
            config_params["response_mime_type"] = "application/json"
            config_params["response_schema"] = response_schema
        
        if use_thinking:
            config_params["thinking_config"] = types.ThinkingConfig(thinking_budget=512)
        
        # Add tools
        tool_list = []
        if use_search_grounding and USE_SEARCH_GROUNDING:
            tool_list.append({"google_search": {}})
        if tools:
            tool_list.extend(tools)
        
        if tool_list:
            config_params["tools"] = tool_list
        
        config = types.GenerateContentConfig(**config_params)
        
        # Use chat if available, otherwise stateless call
        chat = self.chats.get(role)
        
        try:
            if chat:
                response = await chat.send_message_async(prompt, config=config)
            else:
                # Fallback to generate_with_functions for compatibility
                if tools:
                    llm_response = await self.llm_client.generate_with_functions(
                        prompt=prompt,
                        functions=tools,
                        function_call="auto"
                    )
                    return llm_response
                else:
                    # Use the basic client for non-function calls
                    from app.core.llm_client import get_llm_client
                    basic_client = get_llm_client()
                    response_text = await basic_client.generate(prompt)
                    
                    # Parse JSON if schema expected
                    if response_schema:
                        try:
                            parsed = json.loads(response_text)
                            return {"type": "structured", "content": parsed}
                        except json.JSONDecodeError:
                            logger.warning("Could not parse response as JSON")
                            return {"type": "text", "content": response_text}
                    return {"type": "text", "content": response_text}
            
            # Process response from chat
            if response.text:
                # If expecting structured output, parse JSON
                if response_schema:
                    try:
                        parsed = json.loads(response.text)
                        return {"type": "structured", "content": parsed}
                    except json.JSONDecodeError:
                        logger.warning(f"Could not parse {role} response as JSON")
                        return {"type": "text", "content": response.text}
                return {"type": "text", "content": response.text}
            
            # Check for function calls
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    function_calls = [
                        part.function_call 
                        for part in candidate.content.parts 
                        if hasattr(part, 'function_call') and part.function_call
                    ]
                    if function_calls:
                        return {"type": "function_calls", "calls": function_calls}
            
            return {"type": "text", "content": ""}
            
        except Exception as e:
            logger.error(f"Error in {role} role: {str(e)}", exc_info=True)
            return {"type": "error", "error": str(e)}
    
    async def run_perception(self) -> PerceptionOutput:
        """Execute perception role"""
        logger.info("Running perception phase...")
        
        tools = get_tools_for_role(AgentRole.PERCEPTION, self.all_tools)
        
        prompt = f"""
Based on the current context, gather information needed to accomplish the task.

{self.state.to_context()}

Provide your perception in structured format.
"""
        
        response = await self._call_role(
            AgentRole.PERCEPTION,
            prompt,
            response_schema=PerceptionOutput,
            tools=tools,
            use_search_grounding=True
        )
        
        if response["type"] == "structured":
            output = PerceptionOutput(**response["content"])
            self.state.perception = output
            self.state.world_model.update(output.environment_state)
            return output
        
        # Fallback if structured output failed
        return PerceptionOutput(
            key_findings=["Perception completed but unstructured"],
            information_gaps=[],
            environment_state={},
            confidence=0.5
        )
    
    async def run_reasoning(self) -> ReasoningOutput:
        """Execute reasoning role"""
        logger.info("Running reasoning phase...")
        
        tools = get_tools_for_role(AgentRole.REASONING, self.all_tools)
        
        prompt = f"""
Analyze the current information and draw conclusions.

{self.state.to_context()}

Provide your reasoning in structured format.
"""
        
        response = await self._call_role(
            AgentRole.REASONING,
            prompt,
            response_schema=ReasoningOutput,
            tools=tools,
            use_thinking=True  # Use thinking for complex reasoning
        )
        
        if response["type"] == "structured":
            output = ReasoningOutput(**response["content"])
            self.state.reasoning = output
            return output
        
        return ReasoningOutput(
            conclusions=[],
            hypotheses=[],
            patterns_identified=[],
            reasoning_chain="Reasoning completed but unstructured",
            confidence=0.5
        )
    
    async def run_planning(self) -> PlanningOutput:
        """Execute planning role"""
        logger.info("Running planning phase...")
        
        tools = get_tools_for_role(AgentRole.PLANNING, self.all_tools)
        
        prompt = f"""
Create or refine the plan based on current understanding.

{self.state.to_context()}

Provide your plan in structured format.
"""
        
        response = await self._call_role(
            AgentRole.PLANNING,
            prompt,
            response_schema=PlanningOutput,
            tools=tools,
            use_thinking=True
        )
        
        if response["type"] == "structured":
            output = PlanningOutput(**response["content"])
            self.state.current_plan = output
            return output
        
        return PlanningOutput(
            goals=["Continue working on task"],
            next_actions=["Proceed with execution"],
            dependencies=[],
            estimated_completion=5,
            plan_changes="No structured plan available"
        )
    
    async def run_execution(self) -> ExecutionOutput:
        """Execute execution role with parallel tool execution"""
        logger.info("Running execution phase...")
        
        tools = get_tools_for_role(AgentRole.EXECUTION, self.all_tools)
        
        prompt = f"""
Execute the planned actions using available tools.

{self.state.to_context()}

Take the next actions from the plan.
"""
        
        response = await self._call_role(
            AgentRole.EXECUTION,
            prompt,
            tools=tools
        )
        
        actions_taken = []
        results = []
        tools_used = []
        success = True
        issues = []
        
        # Handle function calls
        if response["type"] == "function_calls" and PARALLEL_TOOL_EXECUTION:
            # Execute tools in parallel
            tool_results = await execute_tools_parallel(
                response["calls"],
                self.state.session_id,
                self.all_tools
            )
            
            for tool_result in tool_results:
                tools_used.append(tool_result["tool_name"])
                self.state.tools_used.add(tool_result["tool_name"])
                
                if tool_result["success"]:
                    actions_taken.append(f"Executed {tool_result['tool_name']}")
                    results.append(str(tool_result["result"])[:500])
                else:
                    success = False
                    issues.append(f"{tool_result['tool_name']}: {tool_result['error']}")
        
        elif response["type"] == "function_calls":
            # Sequential execution
            for fc in response["calls"]:
                tool_result = await execute_tool(
                    fc.name,
                    dict(fc.args) if fc.args else {},
                    self.state.session_id,
                    self.all_tools
                )
                tools_used.append(fc.name)
                self.state.tools_used.add(fc.name)
                
                if tool_result["success"]:
                    actions_taken.append(f"Executed {fc.name}")
                    results.append(str(tool_result["result"])[:500])
                else:
                    success = False
                    issues.append(f"{fc.name}: {tool_result['error']}")
        
        elif response["type"] == "text":
            actions_taken.append("Provided response without tool use")
            results.append(response["content"][:500])
        
        output = ExecutionOutput(
            actions_taken=actions_taken,
            results=results,
            tools_used=tools_used,
            success=success,
            issues_encountered=issues
        )
        
        self.state.execution = output
        return output
    
    async def run_reflection(self) -> ReflectionOutput:
        """Execute reflection role"""
        logger.info("Running reflection phase...")
        
        tools = get_tools_for_role(AgentRole.REFLECTION, self.all_tools)
        
        prompt = f"""
Reflect on the progress and determine next steps.

{self.state.to_context()}

Assess whether to continue iterating or if the task is complete.
"""
        
        response = await self._call_role(
            AgentRole.REFLECTION,
            prompt,
            response_schema=ReflectionOutput,
            tools=tools
        )
        
        if response["type"] == "structured":
            output = ReflectionOutput(**response["content"])
            self.state.reflection = output
            self.state.learnings.extend(output.learnings)
            return output
        
        return ReflectionOutput(
            successes=[],
            failures=[],
            learnings=[],
            strategy_adjustments=[],
            continue_iterating=True,
            completion_confidence=0.3,
            trigger_communication=False
        )
    
    async def run_communication(self) -> str:
        """Execute communication role"""
        logger.info("Running communication phase...")
        
        tools = get_tools_for_role(AgentRole.COMMUNICATION, self.all_tools)
        
        prompt = f"""
Provide a clear summary of progress, findings, and recommendations.

{self.state.to_context()}

Create a comprehensive report for the user.
"""
        
        response = await self._call_role(
            AgentRole.COMMUNICATION,
            prompt,
            tools=tools
        )
        
        if response["type"] == "text":
            return response["content"]
        
        return "Communication phase completed."
    
    async def recover_from_error(self, error: str) -> ErrorRecoveryStrategy:
        """Generate error recovery strategy"""
        logger.info(f"Generating recovery strategy for error: {error}")
        
        prompt = f"""
An error occurred during task execution:

ERROR: {error}

CONTEXT:
{self.state.to_context()}

Provide a structured recovery strategy.
"""
        
        response = await self._call_role(
            AgentRole.REFLECTION,
            prompt,
            response_schema=ErrorRecoveryStrategy
        )
        
        if response["type"] == "structured":
            return ErrorRecoveryStrategy(**response["content"])
        
        return ErrorRecoveryStrategy(
            error_type="unknown",
            root_cause=error,
            recovery_actions=["Log error and continue"],
            retry_original_action=False,
            estimated_recovery_time=0
        )


# ============================================================================
# Main Execution Function
# ============================================================================

async def execute_autonomous_agent(
    workflow_selection: WorkflowSelection,
    user_query: str,
    session_id: str
) -> WorkflowResponse:
    """
    Execute the modernized autonomous agent workflow.
    
    Args:
        workflow_selection: Workflow configuration
        user_query: User's task/query
        session_id: Session identifier
        
    Returns:
        WorkflowResponse with results and metadata
    """
    start_time = time.time()
    logger.info(f"Starting modernized autonomous agent for session {session_id}")
    logger.info(f"Task: {user_query}")
    
    intermediate_steps: List[AgentResponse] = []
    
    def log_step(role: str, content: str, metadata: Dict = None):
        """Helper to log steps"""
        intermediate_steps.append(AgentResponse(
            agent_role=role,
            content=content,
            metadata=metadata or {}
        ))
    
    try:
        # Initialize agent
        agent = ModernAutonomousAgent(user_query, session_id)
        log_step("System", f"Initialized modern autonomous agent with {len(agent.all_tools)} tools available")
        
        # Main agent loop
        for iteration in range(MAX_AGENT_ITERATIONS):
            agent.state.iteration = iteration + 1
            logger.info(f"=== Iteration {iteration + 1}/{MAX_AGENT_ITERATIONS} ===")
            log_step("System", f"Starting iteration {iteration + 1}")
            
            try:
                # Perception
                perception = await agent.run_perception()
                log_step(
                    "Perception",
                    f"Found {len(perception.key_findings)} key findings. "
                    f"Confidence: {perception.confidence:.2f}",
                    {"output": perception.dict()}
                )
                agent.state.add_history("perception", perception)
                
                # Reasoning
                reasoning = await agent.run_reasoning()
                log_step(
                    "Reasoning",
                    f"Drew {len(reasoning.conclusions)} conclusions. "
                    f"Confidence: {reasoning.confidence:.2f}",
                    {"output": reasoning.dict()}
                )
                agent.state.add_history("reasoning", reasoning)
                
                # Planning
                planning = await agent.run_planning()
                log_step(
                    "Planning",
                    f"Created plan with {len(planning.next_actions)} next actions. "
                    f"Estimated {planning.estimated_completion} steps to completion.",
                    {"output": planning.dict()}
                )
                agent.state.add_history("planning", planning)
                
                # Execution
                execution = await agent.run_execution()
                log_step(
                    "Execution",
                    f"Executed {len(execution.actions_taken)} actions using {len(execution.tools_used)} tools. "
                    f"Success: {execution.success}",
                    {"output": execution.dict()}
                )
                agent.state.add_history("execution", execution)
                
                # Handle execution errors
                if not execution.success and execution.issues_encountered:
                    error_msg = "; ".join(execution.issues_encountered)
                    recovery = await agent.recover_from_error(error_msg)
                    log_step(
                        "Recovery",
                        f"Generated recovery strategy: {recovery.root_cause}",
                        {"strategy": recovery.dict()}
                    )
                    agent.state.errors.append({
                        "iteration": iteration + 1,
                        "error": error_msg,
                        "recovery": recovery.dict()
                    })
                
                # Reflection
                reflection = await agent.run_reflection()
                log_step(
                    "Reflection",
                    f"Identified {len(reflection.successes)} successes and {len(reflection.failures)} failures. "
                    f"Completion confidence: {reflection.completion_confidence:.2f}. "
                    f"Continue: {reflection.continue_iterating}",
                    {"output": reflection.dict()}
                )
                agent.state.add_history("reflection", reflection)
                
                # Check stopping conditions
                if not reflection.continue_iterating and reflection.completion_confidence > 0.8:
                    logger.info("Agent determined task is complete")
                    log_step("System", f"Task completed with {reflection.completion_confidence:.0%} confidence")
                    break
                
                if reflection.completion_confidence > 0.95:
                    logger.info("High confidence completion achieved")
                    log_step("System", "High confidence completion achieved")
                    break
                
                # Optional intermediate communication
                if reflection.trigger_communication:
                    comm_output = await agent.run_communication()
                    log_step("Communication", comm_output[:500] + "...")
                
            except Exception as e:
                logger.error(f"Error in iteration {iteration + 1}: {str(e)}", exc_info=True)
                log_step("Error", f"Iteration error: {str(e)}")
                
                # Attempt recovery
                try:
                    recovery = await agent.recover_from_error(str(e))
                    log_step("Recovery", f"Recovery strategy generated", {"strategy": recovery.dict()})
                except Exception as recovery_error:
                    logger.error(f"Recovery failed: {str(recovery_error)}")
        
        else:
            # Max iterations reached
            logger.warning(f"Agent reached maximum iterations ({MAX_AGENT_ITERATIONS})")
            log_step("System", f"Reached maximum iterations without full completion")

        # Finl communication
        logger.info("Generating final communication...")
        final_response = await agent.run_communication()
        log_step("Communication", "Final report generated")

        # Process time 
        processing_time = time.time() - start_time 

        # Build comprehensive final response
        summary = f"""
# Task Completion Report

**Task:** {user_query}
**Iterations:** {agent.state.iteration}
**Processing Time:** {processing_time:.2f}s
**Tools Used:** {', '.join(agent.state.tools_used) if agent.state.tools_used else 'None'}

## Final Output
{final_response}

## Key Metrics
- **Final Confidence:** {agent.state.reflection.completion_confidence:.0%} if agent.state.reflection else 'N/A'
- **Actions Taken:** {sum(len(h.get('output', {}).get('actions_taken', [])) for h in agent.state.history if h.get('role') == 'execution')}
- **Learnings:** {len(agent.state.learnings)}
- **Errors Encountered:** {len(agent.state.errors)}
"""
        
        return WorkflowResponse(
            session_id=session_id,
            selected_workflow=workflow_selection.selected_workflow,
            final_response=summary,
            intermediate_steps=intermediate_steps,
            error=None,
            processing_time=processing_time
        )
    
    except Exception as e:
        logger.error(f"Critical error in autonomous agent: {str(e)}", exc_info=True)
        processing_time = time.time() - start_time
        
        return WorkflowResponse(
            session_id=session_id,
            selected_workflow=workflow_selection.selected_workflow,
            final_response=f"Agent failed with error: {str(e)}",
            intermediate_steps=intermediate_steps,
            error=str(e),
            processing_time=processing_time
        )


# ============================================================================
# Utility Functions
# ============================================================================

def save_agent_session(agent: ModernAutonomousAgent, output_dir: str = None):
    """Save complete agent session for analysis"""
    if output_dir is None:
        output_dir = conversation_dir
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/{agent.state.session_id}_{timestamp}_session.json"
    
    session_data = {
        "session_id": agent.state.session_id,
        "task": agent.state.task_description,
        "iterations": agent.state.iteration,
        "history": agent.state.history,
        "learnings": agent.state.learnings,
        "errors": agent.state.errors,
        "tools_used": list(agent.state.tools_used),
        "final_state": {
            "world_model": agent.state.world_model,
            "plan": agent.state.current_plan.dict() if agent.state.current_plan else None,
            "reflection": agent.state.reflection.dict() if agent.state.reflection else None
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(session_data, f, indent=2, default=str)
    
    logger.info(f"Saved agent session to {filename}")
    return filename


async def analyze_agent_performance(session_file: str) -> Dict[str, Any]:
    """Analyze agent performance from saved session"""
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    analysis = {
        "total_iterations": session_data["iterations"],
        "tools_used_count": len(session_data["tools_used"]),
        "tools_used": session_data["tools_used"],
        "error_rate": len(session_data["errors"]) / session_data["iterations"] if session_data["iterations"] > 0 else 0,
        "learnings_count": len(session_data["learnings"]),
        "completion_confidence": session_data["final_state"]["reflection"]["completion_confidence"] if session_data["final_state"]["reflection"] else 0,
        "success_metrics": {
            "completed": session_data["final_state"]["reflection"]["completion_confidence"] > 0.8 if session_data["final_state"]["reflection"] else False,
            "error_free": len(session_data["errors"]) == 0,
            "efficient": session_data["iterations"] < MAX_AGENT_ITERATIONS * 0.7
        }
    }
    
    return analysis

# Example usage
# Basic usage (same interface as before)
async def main():
    response = await execute_autonomous_agent(
        workflow_selection=WorkflowSelection(selected_workflow="autonomous_agent"),
        user_query="Analyze market trends and create a summary report",
        session_id="unique-session-id"
    )
    print(response.final_response)

if __name__ == "__main__":
    asyncio.run(main())
