/**
 * Calc3D Input Handler
 *
 * Single Responsibility: Process calculator input logic (DRY - eliminates duplication)
 * Centralizes input processing for both button clicks and keyboard events
 */

import { CONFIG } from './config.js';

export class InputHandler {
    constructor(engine, displayManager, audio, scene, effects) {
        this.engine = engine;
        this.display = displayManager;
        this.audio = audio;
        this.scene = scene;
        this.effects = effects;
    }

    /**
     * Process digit input (0-9)
     * @param {string} digit - Digit character
     * @throws {Error} If input processing fails
     */
    processDigit(digit) {
        this.engine.inputDigit(digit);
        this.display.appendDigitToExpression(digit);
        this.playFeedback('digit');
    }

    /**
     * Process decimal point input
     * @throws {Error} If input processing fails
     */
    processDecimal() {
        this.engine.inputDecimal();
        this.playFeedback('digit');
    }

    /**
     * Process operator input (+, -, *, /)
     * @param {string} operation - Operation symbol
     * @param {HTMLElement|null} button - Button element for highlighting (optional)
     * @throws {Error} If input processing fails
     */
    processOperator(operation, button = null) {
        const prevDisplay = this.engine.getDisplay();
        this.engine.inputOperator(operation);

        this.display.setOperatorExpression(prevDisplay, operation);

        if (button && this.effects) {
            this.effects.highlightOperator(button);
        }

        this.playFeedback('operator');
    }

    /**
     * Process equals/calculate
     * @throws {Error} If calculation fails
     */
    processEquals() {
        this.engine.calculate();
        this.display.clearExpression();

        if (this.effects) {
            this.effects.clearOperatorHighlight();
            this.effects.pulseGlow(CONFIG.colors.neonGreen);
        }

        this.playFeedback('equals');

        if (this.scene) {
            this.scene.pulse();
        }
    }

    /**
     * Process clear/reset
     * @throws {Error} If clear fails
     */
    processClear() {
        this.engine.clearAll();
        this.display.clearExpression();

        if (this.effects) {
            this.effects.clearOperatorHighlight();
        }

        this.playFeedback('clear');
    }

    /**
     * Process function button (toggleSign, percentage)
     * @param {string} action - Function action name
     * @throws {Error} If function processing fails
     */
    processFunction(action) {
        if (action === 'toggleSign') {
            this.engine.toggleSign();
        } else if (action === 'percentage') {
            this.engine.percentage();
        }

        this.playFeedback('operator');
    }

    /**
     * Play audio and visual feedback for action type
     * @param {string} type - Action type (digit, operator, equals, clear)
     * @private
     */
    playFeedback(type) {
        // Audio feedback
        switch (type) {
            case 'digit':
                this.audio?.playDigit();
                break;
            case 'operator':
                this.audio?.playOperator();
                break;
            case 'equals':
                this.audio?.playEquals();
                break;
            case 'clear':
                this.audio?.playClear();
                break;
        }

        // Visual feedback (scene mood)
        this.scene?.setMood(type);
    }

    /**
     * Update display after any input
     */
    updateDisplay() {
        const value = this.engine.getDisplay();
        this.display.updateDisplay(value);
    }

    /**
     * Handle error state
     * @param {Error} error - Error object
     */
    handleError(error) {
        console.error('Calculator error:', error);

        this.display.showError();
        this.audio?.playError();
        this.scene?.setMood('error');

        // Reset after delay
        setTimeout(() => {
            this.engine.clearAll();
            this.display.clearExpression();
            this.updateDisplay();
        }, 2000);
    }
}
