# app/services/tool_service.py
"""
Service for using tools within workflows
"""
import logging
import re
from typing import Dict, Any, List, Optional
from app.tools.registry import get_tool, list_tools, get_all_tools

class ToolService:
    """
    Service for using tools within workflows
    """
    @staticmethod
    async def execute_tool(tool_name: str, **kwargs) -> str:
        """
        Execute a specific tool with provided arguments
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Arguments to pass to the tool
            
        Returns:
            The result of the tool execution
        """
        tool = get_tool(tool_name)
        if not tool:
            return f"Error: Tool '{tool_name}' not found"
            
        return await tool.execute(**kwargs)
    
    @staticmethod
    async def process_text_with_tools(text: str) -> str:
        """
        Process text that may contain tool invocations
        
        This looks for patterns like {{tool_name(arg1=value1, arg2=value2)}} in the text
        and replaces them with the result of executing the tool
        
        Args:
            text: The text to process
            
        Returns:
            The text with tool invocations replaced by their results
        """
        # Regular expression to find tool invocations
        tool_pattern = r'{{(\w+)\((.*?)\)}}'
        
        # Find all matches
        matches = re.finditer(tool_pattern, text)
        
        # Process each match
        for match in matches:
            full_match = match.group(0)
            tool_name = match.group(1)
            args_str = match.group(2)
            
            # Parse arguments
            args = {}
            if args_str:
                args_pairs = args_str.split(',')
                for pair in args_pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        args[key.strip()] = value.strip().strip('"\'')
            
            # Execute the tool
            result = await ToolService.execute_tool(tool_name, **args)
            
            # Replace the invocation with the result
            text = text.replace(full_match, str(result))
        
        return text
    
    @staticmethod
    def get_available_tools_prompt() -> str:
        """
        Get a prompt explaining available tools for LLMs
        
        Returns:
            A string explaining available tools and how to use them
        """
        tools = get_all_tools()
        if not tools:
            return "No tools are currently available."
            
        prompt = "The following tools are available for use:\n\n"
        
        for name, tool in tools.items():
            status = "ready" if tool.is_setup else "not configured"
            prompt += f"- {name}: {tool.description} ({status})\n"
            
        prompt += "\nYou can use tools by writing {{tool_name(param1=value1, param2=value2)}} in your response."
        
        return prompt
    
    @staticmethod
    def get_autonomous_agent_tools() -> List[Any]:
        """
        Get tool definitions for the autonomous agent workflow
        
        Returns:
            A list of ToolDefinition objects for the autonomous agent
        """
        tools = []
        for name, tool in get_all_tools().items():
            if hasattr(tool, "get_function_definition") and tool.is_setup:
                tools.append(tool.get_function_definition())
        return tools