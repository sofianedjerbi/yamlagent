"""Tests for calculator logic engine."""

import pytest
from decimal import Decimal

from tests.calculator_logic import Calculator


# ============================================================================
# CORE BEHAVIOR TESTS
# ============================================================================


def test_calculator_initial_state():
    """Test calculator initializes with correct default state."""
    calc = Calculator()

    assert calc.display == "0"
    assert calc.current_value == Decimal("0")
    assert calc.previous_value is None
    assert calc.operation is None


def test_single_digit_input():
    """Test inputting a single digit updates display."""
    calc = Calculator()

    result = calc.input_digit("5")

    assert result == "5"
    assert calc.display == "5"


def test_multiple_digit_input():
    """Test inputting multiple digits builds number correctly."""
    calc = Calculator()

    calc.input_digit("1")
    calc.input_digit("2")
    result = calc.input_digit("3")

    assert result == "123"


def test_basic_addition():
    """Test simple addition operation."""
    calc = Calculator()

    calc.input_digit("5")
    calc.input_operator("+")
    calc.input_digit("3")
    result = calc.calculate()

    assert result == "8"


def test_basic_subtraction():
    """Test simple subtraction operation."""
    calc = Calculator()

    calc.input_digit("9")
    calc.input_operator("-")
    calc.input_digit("4")
    result = calc.calculate()

    assert result == "5"


def test_basic_multiplication():
    """Test simple multiplication operation."""
    calc = Calculator()

    calc.input_digit("6")
    calc.input_operator("*")
    calc.input_digit("7")
    result = calc.calculate()

    assert result == "42"


def test_basic_division():
    """Test simple division operation."""
    calc = Calculator()

    calc.input_digit("8")
    calc.input_operator("/")
    calc.input_digit("2")
    result = calc.calculate()

    assert result == "4"


# ============================================================================
# EDGE CASES
# ============================================================================


def test_input_zero():
    """Test inputting zero as first digit."""
    calc = Calculator()

    result = calc.input_digit("0")

    assert result == "0"


def test_leading_zeros_ignored():
    """Test that leading zeros don't accumulate."""
    calc = Calculator()

    calc.input_digit("0")
    calc.input_digit("0")
    result = calc.input_digit("5")

    assert result == "5"


def test_decimal_point_input():
    """Test decimal point input creates decimal number."""
    calc = Calculator()

    calc.input_digit("3")
    calc.input_decimal()
    calc.input_digit("1")
    calc.input_digit("4")

    assert calc.display == "3.14"


def test_decimal_point_on_empty_display():
    """Test decimal point on empty display starts with 0."""
    calc = Calculator()

    result = calc.input_decimal()

    assert result == "0."


def test_multiple_decimal_points_ignored():
    """Test that only one decimal point is allowed."""
    calc = Calculator()

    calc.input_digit("3")
    calc.input_decimal()
    calc.input_digit("1")
    calc.input_decimal()  # Should be ignored
    calc.input_digit("4")

    assert calc.display == "3.14"


def test_large_number_handling():
    """Test calculator handles large numbers."""
    calc = Calculator()

    calc.input_digit("9")
    calc.input_digit("9")
    calc.input_digit("9")
    calc.input_digit("9")
    calc.input_digit("9")
    calc.input_digit("9")

    assert calc.display == "999999"


def test_chained_operations():
    """Test multiple operations in sequence."""
    calc = Calculator()

    calc.input_digit("5")
    calc.input_operator("+")
    calc.input_digit("3")
    calc.input_operator("*")  # Should calculate 5+3=8, then prepare for multiply
    calc.input_digit("2")
    result = calc.calculate()

    assert result == "16"


def test_operations_with_decimals():
    """Test operations work correctly with decimal numbers."""
    calc = Calculator()

    calc.input_digit("2")
    calc.input_decimal()
    calc.input_digit("5")
    calc.input_operator("+")
    calc.input_digit("1")
    calc.input_decimal()
    calc.input_digit("5")
    result = calc.calculate()

    assert result == "4"


# ============================================================================
# ERROR HANDLING
# ============================================================================


def test_division_by_zero_raises_error():
    """Test that division by zero raises appropriate error."""
    calc = Calculator()

    calc.input_digit("5")
    calc.input_operator("/")
    calc.input_digit("0")

    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
        calc.calculate()


def test_invalid_digit_raises_error():
    """Test that invalid digit input raises error."""
    calc = Calculator()

    with pytest.raises(ValueError, match="Invalid digit"):
        calc.input_digit("a")


def test_invalid_operator_raises_error():
    """Test that invalid operator raises error."""
    calc = Calculator()

    with pytest.raises(ValueError, match="Invalid operator"):
        calc.input_operator("^")


# ============================================================================
# CALCULATOR FUNCTIONS (AC, CE, +/-, %)
# ============================================================================


def test_clear_all_resets_state():
    """Test AC button clears all calculator state."""
    calc = Calculator()

    calc.input_digit("5")
    calc.input_operator("+")
    calc.input_digit("3")
    result = calc.clear_all()

    assert result == "0"
    assert calc.display == "0"
    assert calc.previous_value is None
    assert calc.operation is None


def test_clear_entry_clears_display():
    """Test CE button clears current entry only."""
    calc = Calculator()

    calc.input_digit("5")
    calc.input_operator("+")
    calc.input_digit("3")
    result = calc.clear_entry()

    assert result == "0"
    assert calc.display == "0"
    assert calc.previous_value == Decimal("5")  # Previous value preserved
    assert calc.operation == "+"  # Operation preserved


def test_toggle_sign_positive_to_negative():
    """Test +/- button converts positive to negative."""
    calc = Calculator()

    calc.input_digit("5")
    result = calc.toggle_sign()

    assert result == "-5"


def test_toggle_sign_negative_to_positive():
    """Test +/- button converts negative to positive."""
    calc = Calculator()

    calc.input_digit("5")
    calc.toggle_sign()
    result = calc.toggle_sign()

    assert result == "5"


def test_percentage_conversion():
    """Test % button converts to percentage."""
    calc = Calculator()

    calc.input_digit("5")
    calc.input_digit("0")
    result = calc.percentage()

    assert result == "0.5"


def test_percentage_of_small_number():
    """Test percentage conversion of single digit."""
    calc = Calculator()

    calc.input_digit("5")
    result = calc.percentage()

    assert result == "0.05"


# ============================================================================
# DISPLAY FORMATTING
# ============================================================================


def test_display_removes_trailing_zeros():
    """Test display removes unnecessary trailing zeros."""
    calc = Calculator()

    calc.input_digit("1")
    calc.input_operator("/")
    calc.input_digit("2")
    result = calc.calculate()

    assert result == "0.5"  # Not "0.50000000"


def test_display_removes_unnecessary_decimal():
    """Test display removes decimal point for whole numbers."""
    calc = Calculator()

    calc.input_digit("4")
    calc.input_operator("/")
    calc.input_digit("2")
    result = calc.calculate()

    assert result == "2"  # Not "2.0"


# ============================================================================
# STATE MANAGEMENT
# ============================================================================


def test_waiting_for_operand_after_operator():
    """Test calculator waits for new operand after operator input."""
    calc = Calculator()

    calc.input_digit("5")
    calc.input_operator("+")

    assert calc.waiting_for_operand is True


def test_new_number_after_equals():
    """Test entering new number after equals starts fresh calculation."""
    calc = Calculator()

    calc.input_digit("5")
    calc.input_operator("+")
    calc.input_digit("3")
    calc.calculate()
    result = calc.input_digit("9")

    assert result == "9"  # New number, not appended to result
