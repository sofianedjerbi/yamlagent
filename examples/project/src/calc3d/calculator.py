"""Calculator logic for Calc3D."""

import operator
from typing import Union


class Calculator:
    """A calculator that performs basic arithmetic operations."""

    OPERATIONS = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "**": operator.pow,
    }

    @staticmethod
    def calculate(num1: float, num2: float, operation: str) -> Union[float, str]:
        """
        Perform a calculation between two numbers.

        Args:
            num1: First number
            num2: Second number
            operation: Operation to perform (+, -, *, /, **)

        Returns:
            Result of the calculation or error message
        """
        if operation not in Calculator.OPERATIONS:
            return "Invalid operation"

        if operation == "/" and num2 == 0:
            return "Cannot divide by zero"

        try:
            result = Calculator.OPERATIONS[operation](num1, num2)
            return round(result, 10)  # Avoid floating point precision issues
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def evaluate_expression(expression: str) -> Union[float, str]:
        """
        Evaluate a mathematical expression.

        Args:
            expression: Mathematical expression as string

        Returns:
            Result of the evaluation or error message
        """
        try:
            # Basic security: only allow numbers, operators, and parentheses
            allowed_chars = set("0123456789+-*/.()**")
            if not all(c in allowed_chars or c.isspace() for c in expression):
                return "Invalid characters in expression"

            result = eval(expression, {"__builtins__": {}})
            return round(result, 10)
        except ZeroDivisionError:
            return "Cannot divide by zero"
        except Exception as e:
            return f"Error: {str(e)}"
