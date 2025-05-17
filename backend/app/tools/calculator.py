# app/tools/calculator.py
"""
Calculator tool for performing mathematical calculations
"""
import math
import logging
from .base import Tool # Import from base.py
from app.models.schemas import ToolDefinition # Corrected import

class CalculatorTool(Tool):
    """
    Tool for performing mathematical calculations
    """
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform mathematical calculations safely",
            function=self.calculate
        )
        
        # Set up safe math operations
        self.safe_math_ops = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            'pow': pow,
            # Add math module functions
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'pi': math.pi,
            'e': math.e,
        }
    
    def calculate(self, expression: str) -> str:
        """
        Safely evaluate a mathematical expression string
        
        Args:
            expression: The mathematical expression to evaluate
            
        Returns:
            A string with the calculation result or error message
        """
        if not expression:
            return "Error: No expression provided"
        
        try:
            # Replace common operators with function calls for safety
            expression = expression.replace('^', '**')  # Handle caret as power
            
            # Evaluate the expression with the safe dictionary
            result = eval(expression, {"__builtins__": {}}, self.safe_math_ops)
            
            # Format the result based on type
            if isinstance(result, (int, float)):
                if result.is_integer() and isinstance(result, float):
                    return f"Result: {int(result)}"
                return f"Result: {result}"
            return f"Result: {result}"
            
        except Exception as e:
            return f"Error evaluating expression: {str(e)}"

    def get_function_definition(self):
        """
        Get the function definition for use in the autonomous agent
        """
        from app.models.schemas import ToolDefinition
        
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string", 
                        "description": "The mathematical expression to evaluate (e.g., '2+2', 'sqrt(16)', 'sin(pi/2)')"
                    }
                },
                "required": ["expression"]
            },
            function=self.calculate
        )

# Create the calculator tool instance
# Registration is handled by registry.py's initialize_tools function
calculator = CalculatorTool()
# register_tool(calculator) # Removed redundant registration call

# Convenience function to get the calculator for autonomous agent
def get_calculator_tool_definition():
    """Get the calculator tool definition for autonomous agent"""
    return calculator.get_function_definition()