"""Tests for the calculator module."""

from calc3d.calculator import Calculator


class TestCalculator:
    """Test cases for the Calculator class."""

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

    def test_division_by_zero(self):
        """Test division by zero error."""
        result = Calculator.calculate(10, 0, "/")
        assert result == "Cannot divide by zero"

    def test_power(self):
        """Test power operation."""
        result = Calculator.calculate(2, 3, "**")
        assert result == 8

    def test_invalid_operation(self):
        """Test invalid operation."""
        result = Calculator.calculate(5, 3, "%")
        assert result == "Invalid operation"

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

    def test_evaluate_invalid_expression(self):
        """Test invalid expression."""
        result = Calculator.evaluate_expression("2 + abc")
        assert isinstance(result, str) and ("Error" in result or "Invalid" in result)
