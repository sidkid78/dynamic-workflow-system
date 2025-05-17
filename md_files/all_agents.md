```python

  def _build_prompt_chaining(self, task_description: str, tools: List[ToolDefinition]) -> dict:
        """
        Build a prompt chaining workflow.
        """
        all_tools_dict = [tool.dict() for tool in tools]
        return {
            "type": "prompt_chaining",
            "steps": [
                {
                    "role": "planner",
                    "prompt": f"Develop a step-by-step plan to accomplish the following task: '{task_description}'. Consider the available tools and outline the actions needed.",
                    "tools": all_tools_dict
                },
                {
                    "role": "executor",
                    "prompt": f"Execute the following plan step-by-step to achieve the original task: '{task_description}'. Plan: [Output from Planner Step]. Use the available tools as needed and document the results of each step.",
                    "tools": all_tools_dict
                },
                {
                    "role": "reviewer",
                    "prompt": f"Review the execution results based on the original task: '{task_description}' and the generated plan: [Output from Planner Step]. Execution Results: [Output from Executor Step]. Verify correctness, completeness, and quality. Provide feedback or confirm completion.",
                    "tools": all_tools_dict
                }
            ]
        }

    def _build_routing(self, task_description: str, tools: List[ToolDefinition]) -> dict:
        """
        Build a routing workflow where a router step determines the next specialized step.
        """
        all_tools_dict = [tool.dict() for tool in tools]
        
        # Simple heuristic tool filtering based on name keywords
        web_keywords = ['search', 'web', 'scrape', 'browse', 'crawl', 'url', 'weather']
        file_keywords = ['file', 'read', 'write', 'list', 'delete', 'directory', 'metadata', 'workspace']
        
        web_tools = [t for t in all_tools_dict if any(kw in t.get('name', '').lower() for kw in web_keywords)]
        file_tools = [t for t in all_tools_dict if any(kw in t.get('name', '').lower() for kw in file_keywords)]
        
        # Assume other tools are general purpose or for analysis
        other_tools = [t for t in all_tools_dict if t not in web_tools and t not in file_tools]

        possible_routes = ["web_researcher", "file_manager", "general_processor"]

        return {
            "type": "routing",
            "router_step": "router", # Identifies the step making the routing decision
            "steps": [
                {
                    "role": "router",
                    "prompt": (
                        f"Analyze the task: '{task_description}'. "
                        f"Determine the most appropriate next step based on the primary required action. "
                        f"Choose one of the following roles: {', '.join(possible_routes)}. "
                        f"Output *only* the chosen role name."
                    ),
                    # Router might need context of available tools, or just task description
                    "tools": all_tools_dict 
                },
                {
                    "role": "web_researcher",
                    "prompt": "Perform web searches, scraping, or related online tasks based on the original request.",
                    "tools": web_tools
                },
                {
                    "role": "file_manager",
                    "prompt": "Perform file system operations (read, write, list, delete) as required by the original task.",
                    "tools": file_tools
                },
                {
                    "role": "general_processor", # Fallback or for tasks not fitting above
                    "prompt": "Process the request using general tools or by generating a direct response based on the original task.",
                    "tools": other_tools
                }
                # Note: The execution engine needs to interpret the output of the 'router' step 
                #       to invoke the correct subsequent step (e.g., 'web_researcher').
            ],
            "metadata": {
                "description": "A workflow that routes tasks to specialized steps based on initial analysis.",
                "possible_routes": possible_routes
            }
        }
        
    def _build_parallelization(self, task_description: str, tools: List[ToolDefinition]) -> dict:
        """
        Build a parallelization workflow that divides tasks into subtasks
        that can be executed concurrently.
        """
        all_tools_dict = [tool.dict() for tool in tools]
        return {
            "type": "parallelization",
            "steps": [
                {
                    "role": "task_divider",
                    "prompt": f"Analyze the original task: '{task_description}'. Break it down into a list of independent subtasks that can be executed in parallel. Output only the list of subtask descriptions.",
                    "tools": all_tools_dict
                },
                {
                    # Note: This step is intended to be invoked multiple times in parallel by the execution engine,
                    # once for each subtask identified by the task_divider.
                    "role": "parallel_workers",
                    "prompt": f"Execute the following subtask independently: [Subtask Description from Divider]. Use the available tools and provide the result for this specific subtask. Original Task Context: '{task_description}'.",
                    "tools": all_tools_dict,
                    "execution_mode": "parallel" # Hint for the execution engine
                },
                {
                    "role": "aggregator",
                    "prompt": f"Combine the results from the parallel execution of subtasks: [List of Results from Workers]. Synthesize these into a single, coherent final output that addresses the original task: '{task_description}'.",
                    "tools": all_tools_dict
                },
                {
                    "role": "validator",
                    "prompt": f"Review the aggregated result: [Aggregated Output from Aggregator]. Does it fully satisfy the original task requirements: '{task_description}'? Verify correctness, completeness, and quality. Provide final validation or suggest corrections.",
                    "tools": all_tools_dict
                }
            ],
            "metadata": {
                "description": "Divides a task into subtasks, executes them in parallel, aggregates results, and validates.",
                "max_parallel_tasks": 5, # Suggestion for the execution engine
                "timeout_per_task": 300,  # Suggestion for the execution engine
                "retry_policy": {         # Suggestion for the execution engine
                    "max_retries": 2,
                    "retry_delay": 5  # seconds
                }
            }
        }
        
    def _build_orchestrator_workers(self, task_description: str, tools: List[ToolDefinition]) -> dict:
        """
        Build an orchestrator-workers workflow where a central orchestrator agent
        coordinates specialized worker agents to complete complex tasks.
        """
        all_tools_dict = [tool.dict() for tool in tools]
        
        # Keyword-based tool filtering for workers
        research_keywords = ['search', 'web', 'browse', 'scrape', 'crawl', 'research', 'gather', 'arxiv', 'weather', 'url']
        planning_keywords = ['plan', 'schedule', 'dependency', 'strategize', 'organize']
        execution_keywords = ['file', 'read', 'write', 'list', 'delete', 'directory', 'metadata', 'api', 'execute', 'run', 'process', 'code']
        quality_keywords = ['validate', 'test', 'quality', 'check', 'verify', 'review', 'evaluate']

        research_tools = [t for t in all_tools_dict if any(kw in t.get('name', '').lower() for kw in research_keywords)]
        planning_tools = [t for t in all_tools_dict if any(kw in t.get('name', '').lower() for kw in planning_keywords)]
        execution_tools = [t for t in all_tools_dict if any(kw in t.get('name', '').lower() for kw in execution_keywords)]
        quality_tools = [t for t in all_tools_dict if any(kw in t.get('name', '').lower() for kw in quality_keywords)]
        
        # Orchestrator likely needs broader context, possibly all tools
        orchestrator_tools = all_tools_dict 
        
        worker_roles = ["research_worker", "planning_worker", "execution_worker", "quality_worker"]

        return {
            "type": "orchestrator_workers",
            "orchestrator_role": "orchestrator", # Identify the main coordinating role
            "worker_roles": worker_roles,       # List available worker specializations
            "steps": [
                {
                    # This is the central coordinator
                    "role": "orchestrator", 
                    "prompt": (
                        f"You are the orchestrator for the task: '{task_description}'. "
                        f"Your goal is to create a plan and coordinate calls to specialized worker roles ({', '.join(worker_roles)}) to achieve the task. "
                        f"Analyze the task, determine the sequence of worker roles needed, and specify the instructions for each worker call. "
                        f"Monitor progress based on worker outputs and adapt the plan as needed. "
                        f"You have access to these tools for planning and potentially direct execution: [List of Orchestrator Tools]. "
                        f"Produce the next step in the plan (e.g., 'Call research_worker with instructions: [...]' or 'Final result: [...]')."
                    ),
                    "tools": orchestrator_tools, 
                    "responsibilities": [
                        "Task decomposition and planning",
                        "Worker selection and instruction generation",
                        "Coordination and progress monitoring",
                        "Handling dependencies and errors",
                        "Final result aggregation and synthesis"
                    ]
                },
                {
                    # Specialized worker - invoked by the orchestrator
                    "role": "research_worker",
                    "prompt": "You are a research specialist. Execute the research instructions provided by the orchestrator: [Instructions from Orchestrator]. Use your tools to gather and analyze information. Report your findings back to the orchestrator.",
                    "tools": research_tools,
                    "specialization": "information gathering and analysis"
                },
                {
                    # Specialized worker - invoked by the orchestrator
                    "role": "planning_worker",
                    "prompt": "You are a planning specialist. Execute the planning instructions provided by the orchestrator: [Instructions from Orchestrator]. Develop detailed plans, schedules, or strategies as requested. Report the plan back to the orchestrator.",
                    "tools": planning_tools,
                    "specialization": "strategic and tactical planning"
                },
                {
                    # Specialized worker - invoked by the orchestrator
                    "role": "execution_worker",
                    "prompt": "You are an execution specialist. Execute the specific actions or operations instructed by the orchestrator: [Instructions from Orchestrator]. Use your tools to perform file operations, API calls, data processing, etc. Report the outcome back to the orchestrator.",
                    "tools": execution_tools,
                    "specialization": "task execution and operation"
                },
                {
                     # Specialized worker - invoked by the orchestrator
                    "role": "quality_worker",
                    "prompt": "You are a quality assurance specialist. Evaluate the work product based on instructions from the orchestrator: [Instructions from Orchestrator]. Verify outputs, validate results against criteria, and report your assessment back to the orchestrator.",
                    "tools": quality_tools,
                    "specialization": "quality assurance and validation"
                }
                # Note: The execution engine needs to manage the interaction loop: 
                # 1. Call orchestrator.
                # 2. Parse orchestrator output to identify the next worker call and instructions.
                # 3. Call the designated worker with the instructions.
                # 4. Feed the worker's result back to the orchestrator for the next loop iteration.
                # 5. Repeat until orchestrator indicates completion.
            ],
            "metadata": {
                "description": "A workflow with a central orchestrator coordinating specialized worker agents.",
                "communication_protocol": {
                    "message_format": "structured_json", # Suggestion
                    "status_updates": "required",         # Suggestion
                    "synchronization_points": ["planning_complete", "execution_milestone", "final_review"] # Suggestion
                },
                "escalation_policy": { # Suggestion
                    "worker_timeout": 180,  # seconds
                    "retry_attempts": 2,
                    "fallback_strategy": "report_failure_to_orchestrator"
                },
                "adaptive_workflow": True, # Suggestion
                "worker_selection_strategy": "orchestrator_directed" # Reflects the pattern
            }
        }
    
    def _build_evaluator_optimizer(self, task_description: str, tools: List[ToolDefinition]) -> dict:
        """
        Build an evaluator-optimizer workflow that continuously improves outputs through
        iterative evaluation and optimization cycles.
        """
        all_tools_dict = [tool.dict() for tool in tools]

        # Keyword-based tool filtering
        evaluator_keywords = ['validate', 'test', 'quality', 'check', 'verify', 'review', 'evaluate', 'critique', 'assess']
        optimizer_keywords = ['generate', 'write', 'edit', 'modify', 'improve', 'refine', 'optimize', 'code', 'file'] # Needs tools to change the solution
        meta_keywords = ['compare', 'trend', 'analyze', 'decide', 'converge', 'progress']
        
        evaluator_tools = [t for t in all_tools_dict if any(kw in t.get('name', '').lower() for kw in evaluator_keywords)]
        optimizer_tools = [t for t in all_tools_dict if any(kw in t.get('name', '').lower() for kw in optimizer_keywords)]
        meta_evaluator_tools = [t for t in all_tools_dict if any(kw in t.get('name', '').lower() for kw in meta_keywords)]
        # Initial producer likely needs the same tools as the optimizer for the first draft
        producer_tools = optimizer_tools 

        return {
            "type": "evaluator_optimizer",
            "producer_role": "initial_producer",
            "evaluator_role": "evaluator",
            "optimizer_role": "optimizer",
            "controller_role": "meta_evaluator", # Role that controls the loop continuation
            "steps": [
                {
                    "role": "initial_producer",
                    "prompt": f"Generate the first version of the solution for the task: '{task_description}'. Focus on addressing the core requirements. Output the initial solution.",
                    "tools": producer_tools,
                    "output_requirements": "Produce a complete initial solution"
                },
                {
                    "role": "evaluator",
                    "prompt": f"Critically evaluate the following solution: [Current Solution from Producer/Optimizer] against the original task '{task_description}' and these criteria: [Evaluation Criteria]. Identify specific strengths, weaknesses, and areas for improvement. Output a structured critique.",
                    "tools": evaluator_tools,
                    "evaluation_criteria": [
                        "Correctness and accuracy",
                        "Completeness",
                        "Clarity and coherence",
                        "Efficiency and optimization",
                        "Adherence to requirements",
                        "Edge case handling"
                    ]
                },
                {
                    "role": "optimizer",
                    "prompt": f"Improve the solution based on the following critique: [Critique from Evaluator]. Original Task: '{task_description}'. Current Solution: [Current Solution]. Focus on addressing the identified weaknesses while maintaining strengths. Output the improved solution.",
                    "tools": optimizer_tools,
                    "optimization_focus": "Targeted improvements based on evaluation feedback"
                },
                {
                    "role": "meta_evaluator",
                    "prompt": f"Assess the optimization progress after iteration [Iteration Number]. Critique Received: [Critique from Evaluator]. Optimized Solution: [Optimized Solution from Optimizer]. Consider previous iterations' progress: [Iteration History/Summary]. Has the solution quality significantly improved and converged, or are further iterations likely to yield diminishing returns? Output 'continue' to proceed with another evaluation/optimization cycle, or 'stop' if the solution is satisfactory or progress has stalled.",
                    "tools": meta_evaluator_tools,
                    "convergence_criteria": "Meaningful improvement, meets quality threshold, or max iterations reached"
                }
                # Note: The execution engine manages the loop:
                # 1. Call initial_producer -> solution_v1
                # 2. Loop starts (max_iterations or until meta_evaluator says 'stop'):
                #    a. Call evaluator(solution_vN) -> critique_vN
                #    b. Call optimizer(solution_vN, critique_vN) -> solution_vN+1
                #    c. Call meta_evaluator(critique_vN, solution_vN+1, history) -> decision
                #    d. If decision == 'stop', break loop.
                # 3. Final result is the last generated solution.
            ],
            "metadata": {
                "description": "Iteratively improves a solution using evaluation and optimization cycles, controlled by a meta-evaluator.",
                "iteration_config": { # Suggestions for the execution engine
                    "max_iterations": 5,
                    "improvement_threshold": 0.05, 
                    "early_stopping": True,
                    "timeout_per_iteration": 240
                },
                "feedback_mechanism": {
                    "format": "structured_critique",
                    "quantitative_metrics": True,
                    "qualitative_assessment": True
                },
                "version_control": {
                    "track_all_versions": True,
                    "reversion_capability": True,
                    "branch_exploration": False
                },
                "learning_strategy": {
                    "incorporate_previous_feedback": True,
                    "prioritize_critical_issues": True,
                    "balance_exploration_exploitation": True
                }
            }
        }
        
    def _build_autonomous_agent(self, task_description: str, tools: List[ToolDefinition]) -> dict:
        """
        Build an autonomous agent workflow that can independently plan, execute, 
        and adapt to complete complex tasks with minimal human intervention.
        """
        all_tools_dict = [tool.dict() for tool in tools]
        
        # Keyword-based tool filtering
        perception_keywords = ['search', 'web', 'browse', 'scrape', 'crawl', 'gather', 'read', 'list', 'metadata', 'observe', 'url', 'weather']
        reasoning_keywords = ['analyze', 'infer', 'pattern', 'knowledge', 'evaluate', 'compare', 'reason', 'hypothesize', 'deduce']
        planning_keywords = ['plan', 'schedule', 'dependency', 'strategize', 'organize', 'risk', 'goal']
        # Execution needs broad access to act
        reflection_keywords = ['evaluate', 'compare', 'learn', 'meta', 'review', 'assess', 'reflect', 'critique', 'improve']
        communication_keywords = ['summarize', 'visualize', 'report', 'explain', 'communicate', 'present', 'notify']

        perception_tools = [t for t in all_tools_dict if any(kw in t.get('name', '').lower() for kw in perception_keywords)]
        reasoning_tools = [t for t in all_tools_dict if any(kw in t.get('name', '').lower() for kw in reasoning_keywords)]
        planning_tools = [t for t in all_tools_dict if any(kw in t.get('name', '').lower() for kw in planning_keywords)]
        execution_tools = all_tools_dict # Give execution access to all available tools
        reflection_tools = [t for t in all_tools_dict if any(kw in t.get('name', '').lower() for kw in reflection_keywords)]
        communication_tools = [t for t in all_tools_dict if any(kw in t.get('name', '').lower() for kw in communication_keywords)]

        return {
            "type": "autonomous_agent",
            # Define the core roles in the typical agent loop
            "loop_roles": ["perception", "reasoning", "planning", "execution", "reflection"],
            "communication_role": "communication", # Separate role, potentially triggered
            "steps": [
                {
                    "role": "perception",
                    "prompt": f"Based on the overall task '{task_description}' and the current state of the world/task [Current World Model/State], use your tools to gather the most relevant new information. Update the world model with your findings.",
                    "tools": perception_tools,
                    "capabilities": [
                        "Information gathering from multiple sources",
                        "Context analysis and understanding",
                        "Identification of relevant constraints and resources",
                        "Detection of ambiguities requiring clarification"
                    ]
                },
                {
                    "role": "reasoning",
                    "prompt": f"Process the updated information [Perceived Information from Perception Step] in the context of the overall task '{task_description}' and current plan [Current Plan]. Identify patterns, draw inferences, evaluate options, and formulate hypotheses or conclusions to guide planning. Update the agent's understanding.",
                    "tools": reasoning_tools,
                    "reasoning_frameworks": [
                        "Deductive reasoning",
                        "Inductive reasoning",
                        "Abductive reasoning",
                        "Causal reasoning",
                        "Analogical reasoning"
                    ]
                },
                {
                    "role": "planning",
                    "prompt": f"Based on the current understanding [Reasoned Understanding from Reasoning Step] and the overall task '{task_description}', develop or refine a comprehensive, adaptable plan to achieve the objectives. Define the next concrete action(s). Output the updated plan and the next action(s).",
                    "tools": planning_tools,
                    "planning_aspects": [
                        "Goal decomposition into achievable subgoals",
                        "Resource allocation and optimization",
                        "Action sequencing and prioritization",
                        "Contingency planning for identified risks",
                        "Success criteria definition"
                    ]
                },
                {
                    "role": "execution",
                    "prompt": f"Implement the next action(s) specified in the current plan: [Next Action(s) from Planning Step]. Use the available tools to perform the action(s). Monitor the immediate outcome and report the result.",
                    "tools": execution_tools,
                    "execution_capabilities": [
                        "Tool selection and utilization",
                        "Sequential and parallel task execution",
                        "Progress tracking against plan",
                        "Real-time problem solving",
                        "Resource utilization optimization"
                    ]
                },
                {
                    "role": "reflection",
                    "prompt": f"Evaluate the outcome of the last action(s) [Execution Outcome from Execution Step] in relation to the plan [Current Plan] and the overall task '{task_description}'. Assess success, failures, and learning opportunities. Update the agent's knowledge and suggest improvements to strategy or plan for the next cycle. Determine if communication is needed.",
                    "tools": reflection_tools,
                    "reflection_processes": [
                        "Success and failure analysis",
                        "Strategy effectiveness assessment",
                        "Knowledge and capability gap identification",
                        "Learning integration for future cycles",
                        "Self-improvement opportunity identification"
                    ]
                },
                {
                    # This step might be triggered conditionally based on reflection or external events
                    "role": "communication", 
                    "prompt": f"Based on the current status, progress, recent reflections [Reflection Insights], or specific triggers, report relevant information (progress, results, insights, issues, recommendations) regarding the task '{task_description}' in a clear, actionable format. Target audience: [Specify Audience, e.g., User, Log].",
                    "tools": communication_tools,
                    "communication_objectives": [
                        "Status reporting at appropriate intervals",
                        "Clear presentation of findings and results",
                        "Explanation of reasoning and decisions",
                        "Highlighting of key insights and implications",
                        "Recommendation formulation for next steps or completion"
                    ]
                }
                # Note: The execution engine manages the loop:
                # 1. Initialize state (world model, plan, etc.) based on task_description.
                # 2. Loop starts (until task completion, error, or max iterations):
                #    a. Call perception(state) -> updated_state, perceived_info
                #    b. Call reasoning(state, perceived_info) -> reasoned_understanding
                #    c. Call planning(state, reasoned_understanding) -> updated_plan, next_action
                #    d. Call execution(next_action) -> execution_outcome
                #    e. Call reflection(state, execution_outcome) -> learnings, updated_state, trigger_communication?
                #    f. If trigger_communication?: Call communication(state, learnings)
                # 3. Final result is derived from the agent's state upon loop termination.
            ],
            "metadata": {
                "description": "Defines a cyclical autonomous agent capable of perception, reasoning, planning, execution, reflection, and communication.",
                "autonomy_level": { # Suggestions for the execution engine
                    "decision_making": "high",
                    "tool_selection": "full",
                    "goal_refinement": "adaptive",
                    "human_intervention_points": ["critical_decisions", "ethical_dilemmas", "high_risk_actions"]
                },
                "memory_system": { # Suggestions for the execution engine
                    "working_memory": "active_task_context",
                    "episodic_memory": "previous_actions_and_outcomes",
                    "semantic_memory": "domain_knowledge_and_learnings",
                    "memory_consolidation": True
                },
                "adaptation_mechanisms": { # Suggestions for the execution engine
                    "strategy_adjustment": "continuous",
                    "learning_from_feedback": True,
                    "environmental_responsiveness": "high",
                    "goal_reprioritization": "context_sensitive"
                },
                "safety_protocols": { # Suggestions for the execution engine
                    "action_verification": "pre_execution_check",
                    "impact_assessment": "required_for_high_risk_actions",
                    "rollback_capability": True,
                    "ethical_guidelines_enforcement": True,
                    "boundary_condition_monitoring": "continuous"
                },
                "performance_metrics": { # Suggestions for the execution engine
                    "task_completion_quality": "comprehensive",
                    "resource_efficiency": "optimized",
                    "time_to_completion": "tracked",
                    "adaptation_effectiveness": "measured",
                    "learning_curve": "monitored"
                }
            }
        }
``` 