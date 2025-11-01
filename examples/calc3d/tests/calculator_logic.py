"""Reference implementation of calculator logic for testing.

This mirrors the JavaScript Calculator class that will be implemented
in the frontend, allowing us to validate the core calculation logic.
"""

from decimal import Decimal, InvalidOperation
from typing import Optional


class Calculator:
    """Calculator logic engine with state management."""

    def __init__(self):
        """Initialize calculator with default state."""
        self.display = "0"
        self.current_value = Decimal("0")
        self.previous_value: Optional[Decimal] = None
        self.operation: Optional[str] = None
        self.waiting_for_operand = False
        self.should_reset_display = False

    def input_digit(self, digit: str) -> str:
        """
        Handle digit input (0-9).

        Args:
            digit: String representation of digit (0-9)

        Returns:
            Updated display value
        """
        if not digit.isdigit():
            raise ValueError(f"Invalid digit: {digit}")

        if self.waiting_for_operand or self.should_reset_display:
            self.display = digit
            self.waiting_for_operand = False
            self.should_reset_display = False
        else:
            self.display = digit if self.display == "0" else self.display + digit

        return self.display

    def input_decimal(self) -> str:
        """
        Handle decimal point input.

        Returns:
            Updated display value
        """
        if self.waiting_for_operand or self.should_reset_display:
            self.display = "0."
            self.waiting_for_operand = False
            self.should_reset_display = False
        elif "." not in self.display:
            self.display += "."

        return self.display

    def input_operator(self, operator: str) -> str:
        """
        Handle operator input (+, -, *, /).

        Args:
            operator: One of +, -, *, /

        Returns:
            Updated display value
        """
        valid_operators = {"+", "-", "*", "/"}
        if operator not in valid_operators:
            raise ValueError(f"Invalid operator: {operator}")

        try:
            input_value = Decimal(self.display)
        except InvalidOperation:
            return self.display

        if self.previous_value is None:
            self.previous_value = input_value
        elif self.operation:
            result = self._perform_calculation(
                self.previous_value, input_value, self.operation
            )
            self.display = self._format_display(result)
            self.previous_value = result

        self.waiting_for_operand = True
        self.operation = operator

        return self.display

    def calculate(self) -> str:
        """
        Perform calculation when equals is pressed.

        Returns:
            Result as display string
        """
        try:
            input_value = Decimal(self.display)
        except InvalidOperation:
            return self.display

        if self.operation and self.previous_value is not None:
            result = self._perform_calculation(
                self.previous_value, input_value, self.operation
            )
            self.display = self._format_display(result)
            self.current_value = result
            self.previous_value = None
            self.operation = None
            self.should_reset_display = True

        return self.display

    def clear_all(self) -> str:
        """
        Clear all calculator state (AC button).

        Returns:
            Reset display value ("0")
        """
        self.display = "0"
        self.current_value = Decimal("0")
        self.previous_value = None
        self.operation = None
        self.waiting_for_operand = False
        self.should_reset_display = False
        return self.display

    def clear_entry(self) -> str:
        """
        Clear current entry (CE button).

        Returns:
            Reset display value ("0")
        """
        self.display = "0"
        self.waiting_for_operand = False
        return self.display

    def toggle_sign(self) -> str:
        """
        Toggle positive/negative sign (+/- button).

        Returns:
            Updated display value
        """
        try:
            value = Decimal(self.display)
            value = -value
            self.display = self._format_display(value)
        except InvalidOperation:
            pass

        return self.display

    def percentage(self) -> str:
        """
        Convert current value to percentage (% button).

        Returns:
            Updated display value
        """
        try:
            value = Decimal(self.display)
            value = value / Decimal("100")
            self.display = self._format_display(value)
        except InvalidOperation:
            pass

        return self.display

    def _perform_calculation(
        self, left: Decimal, right: Decimal, operator: str
    ) -> Decimal:
        """
        Perform binary calculation.

        Args:
            left: Left operand
            right: Right operand
            operator: Operation to perform

        Returns:
            Calculation result

        Raises:
            ZeroDivisionError: When dividing by zero
        """
        if operator == "+":
            return left + right
        elif operator == "-":
            return left - right
        elif operator == "*":
            return left * right
        elif operator == "/":
            if right == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            return left / right
        else:
            raise ValueError(f"Unknown operator: {operator}")

    def _format_display(self, value: Decimal) -> str:
        """
        Format decimal value for display.

        Args:
            value: Decimal value to format

        Returns:
            Formatted string for display
        """
        # Remove trailing zeros and unnecessary decimal point
        formatted = str(value)

        # Handle very large or very small numbers with scientific notation
        if "E" in formatted or "e" in formatted:
            return formatted

        # Remove trailing zeros after decimal point
        if "." in formatted:
            formatted = formatted.rstrip("0").rstrip(".")

        return formatted
