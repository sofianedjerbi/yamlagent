/**
 * Calc3D Event Manager
 *
 * Single Responsibility: Handle DOM events (keyboard, mouse) and delegate to handlers
 * Separates event handling from business logic (SOLID principle)
 */

export class EventManager {
    constructor(inputHandler, effects) {
        this.inputHandler = inputHandler;
        this.effects = effects;
        this.soundToggle = null;
        this.audioManager = null;
    }

    /**
     * Set audio manager for sound toggle
     * @param {Object} audioManager - Audio manager instance
     * @param {HTMLElement} soundToggle - Sound toggle button element
     */
    setAudioManager(audioManager, soundToggle) {
        this.audioManager = audioManager;
        this.soundToggle = soundToggle;
    }

    /**
     * Set up all event listeners
     */
    setupEventListeners() {
        this.setupButtonListeners();
        this.setupKeyboardListeners();
        this.setupSoundToggle();

        console.log('Event listeners registered');
    }

    /**
     * Set up button click listeners
     * @private
     */
    setupButtonListeners() {
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => {
            button.addEventListener('click', (e) => this.handleButtonClick(e));
        });
    }

    /**
     * Set up keyboard event listeners
     * @private
     */
    setupKeyboardListeners() {
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
    }

    /**
     * Set up sound toggle listener
     * @private
     */
    setupSoundToggle() {
        if (this.soundToggle && this.audioManager) {
            this.soundToggle.addEventListener('click', () => this.toggleSound());
        }
    }

    /**
     * Handle button click event
     * @param {Event} event - Click event
     */
    handleButtonClick(event) {
        const button = event.currentTarget;
        const { type, action, digit, operation } = button.dataset;

        // Trigger button animation
        this.effects?.pressButton(button, type);

        try {
            this.processInput(type, { action, digit, operation, button });
            this.inputHandler.updateDisplay();
        } catch (error) {
            this.inputHandler.handleError(error);
        }
    }

    /**
     * Handle keyboard press event
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleKeyPress(event) {
        const key = event.key;

        // Map keyboard input to calculator action
        const inputType = this.getInputTypeFromKey(key);
        if (!inputType) return;

        // Prevent default for calculator keys
        event.preventDefault();

        try {
            this.processInput(inputType.type, inputType.data);
            this.inputHandler.updateDisplay();

            // Show key press effect
            if (/^[0-9]$/.test(key)) {
                this.effects?.showKeyPress(key);
            }
        } catch (error) {
            this.inputHandler.handleError(error);
        }
    }

    /**
     * Process input based on type and data
     * @param {string} type - Input type (digit, decimal, operator, etc.)
     * @param {Object} data - Input data (digit, operation, action, button)
     * @private
     */
    processInput(type, data) {
        switch (type) {
            case 'digit':
                this.inputHandler.processDigit(data.digit);
                break;
            case 'decimal':
                this.inputHandler.processDecimal();
                break;
            case 'operator':
                this.inputHandler.processOperator(data.operation, data.button);
                break;
            case 'equals':
                this.inputHandler.processEquals();
                break;
            case 'clear':
                this.inputHandler.processClear();
                break;
            case 'function':
                this.inputHandler.processFunction(data.action);
                break;
            default:
                console.warn(`Unknown input type: ${type}`);
        }
    }

    /**
     * Map keyboard key to input type and data
     * @param {string} key - Keyboard key
     * @returns {Object|null} Input type and data, or null if not a calculator key
     * @private
     */
    getInputTypeFromKey(key) {
        // Digits
        if (/^[0-9]$/.test(key)) {
            return { type: 'digit', data: { digit: key } };
        }

        // Decimal point
        if (key === '.') {
            return { type: 'decimal', data: {} };
        }

        // Operators
        if (['+', '-', '*', '/'].includes(key)) {
            return { type: 'operator', data: { operation: key } };
        }

        // Equals
        if (key === 'Enter' || key === '=') {
            return { type: 'equals', data: {} };
        }

        // Clear
        if (key === 'Escape') {
            return { type: 'clear', data: {} };
        }

        // Percentage
        if (key === '%') {
            return { type: 'function', data: { action: 'percentage' } };
        }

        return null;
    }

    /**
     * Toggle sound on/off
     * @private
     */
    toggleSound() {
        if (!this.audioManager) return;

        const isEnabled = this.audioManager.toggle();

        if (this.soundToggle) {
            if (isEnabled) {
                this.soundToggle.classList.remove('muted');
            } else {
                this.soundToggle.classList.add('muted');
            }
        }

        console.log(`Sound ${isEnabled ? 'enabled' : 'disabled'}`);
    }
}
