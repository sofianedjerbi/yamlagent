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

    # ============ Additional Edge Cases ============

    def test_power_of_zero(self):
        """Test zero raised to a power."""
        assert Calculator.calculate(0, 5, "**") == 0
        assert Calculator.calculate(0, 0, "**") == 1  # 0^0 = 1 by convention

    def test_multiply_by_one(self):
        """Test multiplication identity."""
        assert Calculator.calculate(42, 1, "*") == 42
        assert Calculator.calculate(1, 42, "*") == 42

    def test_divide_by_one(self):
        """Test division by one."""
        assert Calculator.calculate(42, 1, "/") == 42

    def test_consecutive_operations_different_signs(self):
        """Test subtraction with negative result."""
        result = Calculator.calculate(3, 5, "-")
        assert result == -2

    def test_evaluate_expression_order_of_operations(self):
        """Test proper order of operations."""
        result = Calculator.evaluate_expression("10 - 2 * 3")
        assert result == 4  # Should be 10 - 6, not 8 * 3

    def test_evaluate_expression_division_precedence(self):
        """Test division precedence."""
        result = Calculator.evaluate_expression("20 / 4 / 2")
        assert result == 2.5  # Should be (20 / 4) / 2 = 5 / 2

    def test_evaluate_multiple_parentheses_groups(self):
        """Test multiple separate parentheses groups."""
        result = Calculator.evaluate_expression("(2 + 3) + (4 * 5)")
        assert result == 25

    def test_evaluate_expression_negative_in_parentheses(self):
        """Test negative numbers in parentheses."""
        result = Calculator.evaluate_expression("(-5) + 10")
        assert result == 5

    # ============ Additional Error Cases ============

    def test_evaluate_unmatched_opening_parenthesis(self):
        """Test unmatched opening parenthesis."""
        result = Calculator.evaluate_expression("(2 + 3")
        assert isinstance(result, str) and "Error" in result

    def test_evaluate_unmatched_closing_parenthesis(self):
        """Test unmatched closing parenthesis."""
        result = Calculator.evaluate_expression("2 + 3)")
        assert isinstance(result, str) and "Error" in result

    def test_evaluate_double_operators(self):
        """Test consecutive operators (++ is valid as unary plus)."""
        # Note: Python eval treats ++ as two unary plus operators, which is valid
        result = Calculator.evaluate_expression("2 ++ 3")
        assert result == 5  # 2 + (+3) = 5

    def test_evaluate_trailing_operator(self):
        """Test expression ending with operator."""
        result = Calculator.evaluate_expression("2 + 3 *")
        assert isinstance(result, str) and "Error" in result

    def test_evaluate_leading_operator_multiplication(self):
        """Test expression starting with multiplication operator."""
        result = Calculator.evaluate_expression("* 2 + 3")
        assert isinstance(result, str) and "Error" in result

    def test_calculate_exception_handling(self):
        """Test that unexpected errors are caught."""
        result = Calculator.calculate(float('inf'), 2, "*")
        # Should return inf, not an error
        assert result == float('inf')
