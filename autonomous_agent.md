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