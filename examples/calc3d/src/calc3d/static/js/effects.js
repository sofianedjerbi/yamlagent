/**
 * Calc3D UI Effects Controller
 *
 * Manages animations, transitions, and visual effects for the UI
 */

import { CONFIG } from './config.js';

export class EffectsController {
    constructor() {
        this.displayElement = null;
        this.activeButton = null;
    }

    /**
     * Set the display element reference
     * @param {HTMLElement} element - Display element
     */
    setDisplayElement(element) {
        this.displayElement = element;
    }

    /**
     * Animate display update
     * @param {string} value - New display value
     */
    updateDisplay(value) {
        if (!this.displayElement) return;

        // Add update animation class
        this.displayElement.classList.add('updating');

        // Update text
        this.displayElement.textContent = value;

        // Remove animation class after duration
        setTimeout(() => {
            this.displayElement.classList.remove('updating');
        }, CONFIG.animation.displayUpdateDuration);
    }

    /**
     * Animate button press
     * @param {HTMLElement} button - Button element
     * @param {string} type - Button type (digit, operator, equals, etc.)
     */
    pressButton(button, type) {
        if (!button) return;

        this.clearPreviousActiveButton();
        this.activateButton(button);
        this.createRipple(button);
        this.scheduleButtonDeactivation(button, type);
    }

    /**
     * Clear previous active button
     * @private
     */
    clearPreviousActiveButton() {
        if (this.activeButton) {
            this.activeButton.classList.remove('active');
        }
    }

    /**
     * Activate button with pressed state
     * @param {HTMLElement} button - Button element
     * @private
     */
    activateButton(button) {
        button.classList.add('active', 'pressed');
        this.activeButton = button;
    }

    /**
     * Schedule button deactivation based on type
     * @param {HTMLElement} button - Button element
     * @param {string} type - Button type
     * @private
     */
    scheduleButtonDeactivation(button, type) {
        // Remove pressed class after duration
        setTimeout(() => {
            button.classList.remove('pressed');
        }, CONFIG.animation.buttonPressDuration);

        // For operators, keep active until next press
        if (type !== 'operator') {
            setTimeout(() => {
                button.classList.remove('active');
                if (this.activeButton === button) {
                    this.activeButton = null;
                }
            }, CONFIG.animation.buttonPressDuration * 2);
        }
    }

    /**
     * Create ripple effect on button
     * @param {HTMLElement} button - Button element
     */
    createRipple(button) {
        const ripple = document.createElement('span');
        ripple.classList.add('ripple');

        // Position ripple at button center
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        ripple.style.width = ripple.style.height = `${size}px`;

        button.appendChild(ripple);

        // Remove ripple after animation
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    /**
     * Show error animation
     */
    showError() {
        if (!this.displayElement) return;

        // Add error class
        this.displayElement.classList.add('error');

        // Shake animation
        const calculator = this.displayElement.closest('.calculator');
        if (calculator) {
            calculator.classList.add('shake');

            setTimeout(() => {
                calculator.classList.remove('shake');
            }, CONFIG.animation.errorShakeDuration);
        }

        // Remove error class after animation
        setTimeout(() => {
            this.displayElement.classList.remove('error');
        }, CONFIG.animation.errorShakeDuration);
    }

    /**
     * Pulse glow effect
     * @param {string} color - Glow color
     */
    pulseGlow(color) {
        if (!this.displayElement) return;

        const calculator = this.displayElement.closest('.calculator');
        if (!calculator) return;

        // Set custom glow color
        calculator.style.setProperty('--glow-color', color);
        calculator.classList.add('pulse-glow');

        setTimeout(() => {
            calculator.classList.remove('pulse-glow');
        }, CONFIG.animation.glowPulseDuration);
    }

    /**
     * Highlight operator button
     * @param {HTMLElement} button - Operator button to highlight
     */
    highlightOperator(button) {
        // Clear previous operator highlight
        document.querySelectorAll('.btn-operator.active').forEach(btn => {
            if (btn !== button) {
                btn.classList.remove('active');
            }
        });

        if (button) {
            button.classList.add('active');
            this.activeButton = button;
        }
    }

    /**
     * Clear operator highlights
     */
    clearOperatorHighlight() {
        document.querySelectorAll('.btn-operator.active').forEach(btn => {
            btn.classList.remove('active');
        });
        this.activeButton = null;
    }

    /**
     * Animate calculator entry
     */
    animateEntry() {
        const calculator = document.querySelector('.calculator');
        if (!calculator) return;

        calculator.classList.add('entering');

        setTimeout(() => {
            calculator.classList.remove('entering');
        }, 1000);
    }

    /**
     * Create floating particles effect
     * @param {HTMLElement} container - Container element
     */
    createFloatingParticles(container) {
        if (!container) return;

        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.classList.add('floating-particle');

            // Random position and delay
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.animationDelay = `${Math.random() * 3}s`;
            particle.style.animationDuration = `${3 + Math.random() * 4}s`;

            container.appendChild(particle);
        }
    }

    /**
     * Add keyboard press effect
     * @param {string} key - Key pressed
     */
    showKeyPress(key) {
        // Find corresponding button
        const button = document.querySelector(`[data-key="${key}"]`);
        if (button) {
            this.pressButton(button, button.dataset.type);
        }
    }

    /**
     * Smooth number transition effect
     * @param {HTMLElement} element - Element to animate
     * @param {number} start - Start value
     * @param {number} end - End value
     * @param {number} duration - Animation duration in ms
     */
    animateNumber(element, start, end, duration = 500) {
        if (!element) return;

        const startTime = performance.now();
        const delta = end - start;

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Ease out cubic
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            const current = start + (delta * easeProgress);

            element.textContent = Math.round(current).toString();

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }
}
