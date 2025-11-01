/**
 * Calc3D Display Manager
 *
 * Single Responsibility: Manages display updates, expression tracking, and operator symbols
 * Part of SOLID refactoring to separate concerns
 */

import { CONFIG } from './config.js';

export class DisplayManager {
    constructor(displayElement, expressionElement, effects) {
        this.displayElement = displayElement;
        this.expressionElement = expressionElement;
        this.effects = effects;
        this.expression = '';
        this.lastOperator = null;
    }

    /**
     * Update the main display value
     * @param {string} value - Value to display
     */
    updateDisplay(value) {
        if (this.effects) {
            this.effects.updateDisplay(value);
        }

        this.updateExpression();
    }

    /**
     * Update the expression display
     */
    updateExpression() {
        if (this.expressionElement) {
            this.expressionElement.textContent = this.expression;
        }
    }

    /**
     * Set expression after operator input
     * @param {string} prevDisplay - Previous display value
     * @param {string} operation - Operation symbol (+, -, *, /)
     */
    setOperatorExpression(prevDisplay, operation) {
        const operatorSymbol = this.getOperatorSymbol(operation);
        this.expression = `${prevDisplay} ${operatorSymbol}`;
        this.lastOperator = operation;
    }

    /**
     * Append digit to expression if waiting for second operand
     * @param {string} digit - Digit to append
     */
    appendDigitToExpression(digit) {
        if (this.lastOperator) {
            this.expression = `${this.expression} ${digit}`;
            this.lastOperator = null;
        }
    }

    /**
     * Clear all expression state
     */
    clearExpression() {
        this.expression = '';
        this.lastOperator = null;
    }

    /**
     * Get display symbol for operator
     * @param {string} operation - Operation symbol
     * @returns {string} Display symbol
     */
    getOperatorSymbol(operation) {
        const symbols = {
            '+': '+',
            '-': '-',
            '*': '×',
            '/': '÷'
        };
        return symbols[operation] || operation;
    }

    /**
     * Show error in display
     */
    showError() {
        if (this.effects) {
            this.effects.updateDisplay('Error');
            this.effects.showError();
        }
    }

    /**
     * Check if has active operator
     * @returns {boolean}
     */
    hasActiveOperator() {
        return this.lastOperator !== null;
    }
}
