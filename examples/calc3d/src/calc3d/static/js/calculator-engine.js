/**
 * Calc3D Calculator Engine
 *
 * Core calculator logic with state management
 * Mirrors the Python reference implementation for consistency
 */

import { CONFIG } from './config.js';

export class CalculatorEngine {
    constructor() {
        this.display = '0';
        this.currentValue = 0;
        this.previousValue = null;
        this.operation = null;
        this.waitingForOperand = false;
        this.shouldResetDisplay = false;
    }

    /**
     * Handle digit input (0-9)
     * @param {string} digit - Digit character
     * @returns {string} Updated display value
     */
    inputDigit(digit) {
        if (!/^\d$/.test(digit)) {
            throw new Error(`Invalid digit: ${digit}`);
        }

        if (this.waitingForOperand || this.shouldResetDisplay) {
            this.display = digit;
            this.waitingForOperand = false;
            this.shouldResetDisplay = false;
        } else {
            // Limit display length
            if (this.display.length >= CONFIG.calculator.maxDisplayLength) {
                return this.display;
            }
            this.display = this.display === '0' ? digit : this.display + digit;
        }

        return this.display;
    }

    /**
     * Handle decimal point input
     * @returns {string} Updated display value
     */
    inputDecimal() {
        if (this.waitingForOperand || this.shouldResetDisplay) {
            this.display = '0.';
            this.waitingForOperand = false;
            this.shouldResetDisplay = false;
        } else if (!this.display.includes('.')) {
            // Limit display length
            if (this.display.length >= CONFIG.calculator.maxDisplayLength) {
                return this.display;
            }
            this.display += '.';
        }

        return this.display;
    }

    /**
     * Handle operator input (+, -, *, /)
     * @param {string} operator - Operator character
     * @returns {string} Updated display value
     */
    inputOperator(operator) {
        const validOperators = ['+', '-', '*', '/'];
        if (!validOperators.includes(operator)) {
            throw new Error(`Invalid operator: ${operator}`);
        }

        const inputValue = parseFloat(this.display);

        if (this.previousValue === null) {
            this.previousValue = inputValue;
        } else if (this.operation && !this.waitingForOperand) {
            const result = this.performCalculation(
                this.previousValue,
                inputValue,
                this.operation
            );
            this.display = this.formatDisplay(result);
            this.previousValue = result;
        }

        this.waitingForOperand = true;
        this.operation = operator;

        return this.display;
    }

    /**
     * Perform calculation when equals is pressed
     * @returns {string} Result as display string
     */
    calculate() {
        const inputValue = parseFloat(this.display);

        if (this.operation && this.previousValue !== null) {
            const result = this.performCalculation(
                this.previousValue,
                inputValue,
                this.operation
            );
            this.display = this.formatDisplay(result);
            this.currentValue = result;
            this.previousValue = null;
            this.operation = null;
            this.shouldResetDisplay = true;
        }

        return this.display;
    }

    /**
     * Clear all calculator state (AC button)
     * @returns {string} Reset display value
     */
    clearAll() {
        this.display = '0';
        this.currentValue = 0;
        this.previousValue = null;
        this.operation = null;
        this.waitingForOperand = false;
        this.shouldResetDisplay = false;
        return this.display;
    }

    /**
     * Clear current entry (CE button)
     * @returns {string} Reset display value
     */
    clearEntry() {
        this.display = '0';
        this.waitingForOperand = false;
        return this.display;
    }

    /**
     * Toggle positive/negative sign (+/- button)
     * @returns {string} Updated display value
     */
    toggleSign() {
        const value = parseFloat(this.display);
        if (!isNaN(value)) {
            this.display = this.formatDisplay(-value);
        }
        return this.display;
    }

    /**
     * Convert current value to percentage (% button)
     * @returns {string} Updated display value
     */
    percentage() {
        const value = parseFloat(this.display);
        if (!isNaN(value)) {
            this.display = this.formatDisplay(value / 100);
        }
        return this.display;
    }

    /**
     * Perform binary calculation
     * @param {number} left - Left operand
     * @param {number} right - Right operand
     * @param {string} operator - Operation to perform
     * @returns {number} Calculation result
     * @throws {Error} When dividing by zero
     */
    performCalculation(left, right, operator) {
        switch (operator) {
            case '+':
                return left + right;
            case '-':
                return left - right;
            case '*':
                return left * right;
            case '/':
                if (right === 0) {
                    throw new Error('Cannot divide by zero');
                }
                return left / right;
            default:
                throw new Error(`Unknown operator: ${operator}`);
        }
    }

    /**
     * Format number for display
     * @param {number} value - Number to format
     * @returns {string} Formatted string for display
     */
    formatDisplay(value) {
        if (!isFinite(value)) {
            return 'Error';
        }

        // Handle very large or very small numbers
        const absValue = Math.abs(value);
        if (absValue > 0 && (absValue < 1e-6 || absValue > 1e12)) {
            return value.toExponential(6);
        }

        // Convert to string and limit decimal places
        let str = value.toString();

        // If it has a decimal point, limit decimal places
        if (str.includes('.')) {
            const parts = str.split('.');
            if (parts[1].length > CONFIG.calculator.decimalPlaces) {
                str = value.toFixed(CONFIG.calculator.decimalPlaces);
            }
            // Remove trailing zeros
            str = str.replace(/\.?0+$/, '');
        }

        // Limit total display length
        if (str.length > CONFIG.calculator.maxDisplayLength) {
            return value.toExponential(6);
        }

        return str;
    }

    /**
     * Get current display value
     * @returns {string} Display value
     */
    getDisplay() {
        return this.display;
    }

    /**
     * Check if calculator has an active operation
     * @returns {boolean} True if operation is pending
     */
    hasOperation() {
        return this.operation !== null;
    }
}
