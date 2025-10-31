"""Tests for the calculator module."""

import pytest

from calc3d.calculator import Calculator


class TestCalculator:
    """Test cases for the Calculator class."""

    # ============ Basic Operations Tests ============

    def test_addition(self):
        """Test addition operation."""
        result = Calculator.calculate(5, 3, "+")
        assert result == 8

    def test_subtraction(self):
        """Test subtraction operation."""
        result = Calculator.calculate(10, 4, "-")
        assert result == 6

    def test_multiplication(self):
        """Test multiplication operation."""
        result = Calculator.calculate(6, 7, "*")
        assert result == 42

    def test_division(self):
        """Test division operation."""
        result = Calculator.calculate(15, 3, "/")
        assert result == 5

    def test_power(self):
        """Test power operation."""
        result = Calculator.calculate(2, 3, "**")
        assert result == 8

    # ============ Edge Cases - Numbers ============

    def test_negative_numbers(self):
        """Test operations with negative numbers."""
        assert Calculator.calculate(-5, 3, "+") == -2
        assert Calculator.calculate(-10, -4, "*") == 40

    def test_zero_operations(self):
        """Test operations with zero."""
        assert Calculator.calculate(0, 5, "+") == 5
        assert Calculator.calculate(0, 5, "*") == 0
        assert Calculator.calculate(5, 0, "-") == 5

    def test_floating_point_numbers(self):
        """Test operations with floats."""
        result = Calculator.calculate(0.1, 0.2, "+")
        assert abs(result - 0.3) < 0.0001  # Account for float precision

    def test_large_numbers(self):
        """Test operations with large numbers."""
        result = Calculator.calculate(1e10, 2e10, "+")
        assert result == 3e10

    def test_very_small_numbers(self):
        """Test operations with very small numbers."""
        result = Calculator.calculate(1e-10, 2e-10, "+")
        assert abs(result - 3e-10) < 1e-15

    # ============ Edge Cases - Power Operation ============

    def test_power_zero_exponent(self):
        """Test power with zero exponent."""
        assert Calculator.calculate(5, 0, "**") == 1

    def test_power_negative_exponent(self):
        """Test power with negative exponent."""
        result = Calculator.calculate(2, -2, "**")
        assert result == 0.25

    def test_power_fractional_exponent(self):
        """Test power with fractional exponent."""
        result = Calculator.calculate(4, 0.5, "**")
        assert result == 2.0

    # ============ Error Conditions ============

    def test_division_by_zero(self):
        """Test division by zero error."""
        result = Calculator.calculate(10, 0, "/")
        assert result == "Cannot divide by zero"

    def test_invalid_operation(self):
        """Test invalid operation."""
        result = Calculator.calculate(5, 3, "%")
        assert result == "Invalid operation"

    # ============ Expression Evaluation Tests ============

    def test_evaluate_expression(self):
        """Test expression evaluation."""
        result = Calculator.evaluate_expression("2 + 3 * 4")
        assert result == 14

    def test_evaluate_complex_expression(self):
        """Test complex expression evaluation."""
        result = Calculator.evaluate_expression("(10 + 5) * 2")
        assert result == 30

    def test_evaluate_expression_with_power(self):
        """Test expression with power."""
        result = Calculator.evaluate_expression("2**3 + 1")
        assert result == 9

    def test_evaluate_nested_parentheses(self):
        """Test nested parentheses."""
        result = Calculator.evaluate_expression("((2 + 3) * (4 + 5))")
        assert result == 45

    def test_evaluate_expression_with_decimals(self):
        """Test expression with decimal numbers."""
        result = Calculator.evaluate_expression("3.5 + 2.5")
        assert result == 6.0

    # ============ Expression Edge Cases ============

    def test_evaluate_empty_string(self):
        """Test empty expression returns error."""
        result = Calculator.evaluate_expression("")
        assert isinstance(result, str) and "Error" in result

    def test_evaluate_whitespace_only(self):
        """Test whitespace-only expression."""
        result = Calculator.evaluate_expression("   ")
        assert isinstance(result, str) and "Error" in result

    def test_evaluate_single_number(self):
        """Test single number expression."""
        result = Calculator.evaluate_expression("42")
        assert result == 42

    def test_evaluate_division_by_zero_in_expression(self):
        """Test division by zero in expression."""
        result = Calculator.evaluate_expression("10 / 0")
        assert result == "Cannot divide by zero"

    # ============ Security & Validation Tests ============

    def test_evaluate_invalid_characters(self):
        """Test expression with invalid characters."""
        result = Calculator.evaluate_expression("2 + abc")
        assert isinstance(result, str) and ("Error" in result or "Invalid" in result)

    def test_evaluate_no_code_injection(self):
        """Test that code injection is prevented."""
        result = Calculator.evaluate_expression("__import__('os').system('ls')")
        assert isinstance(result, str) and "Invalid" in result

    def test_evaluate_expression_with_spaces(self):
        """Test expression with various spacing."""
        result = Calculator.evaluate_expression("  2   +   3  ")
        assert result == 5

    # ============ Precision Tests ============

    def test_floating_point_precision_rounding(self):
        """Test that results are rounded to 10 decimal places."""
        result = Calculator.calculate(1, 3, "/")
        # Result should be rounded, not infinite decimals
        assert len(str(result).split('.')[-1]) <= 10
