/**
 * Calc3D - Main Application
 *
 * Orchestrates all components following SOLID principles
 * Refactored to reduce complexity and improve maintainability
 */

import { CONFIG } from './config.js';
import { CalculatorEngine } from './calculator-engine.js';
import { AudioManager } from './audio-manager.js';
import { Scene3D } from './scene3d.js';
import { EffectsController } from './effects.js';
import { DisplayManager } from './display-manager.js';
import { InputHandler } from './input-handler.js';
import { EventManager } from './event-manager.js';

class Calc3DApp {
    constructor() {
        // Core components
        this.engine = new CalculatorEngine();
        this.audio = new AudioManager();
        this.scene = null;
        this.effects = new EffectsController();

        // Managers (new modular architecture)
        this.displayManager = null;
        this.inputHandler = null;
        this.eventManager = null;
    }

    /**
     * Initialize the application
     */
    async init() {
        console.log('🚀 Initializing Calc3D...');

        await this.waitForDOM();

        const elements = this.getDOMElements();
        if (!elements.display) {
            console.error('Display element not found');
            return;
        }

        this.initializeManagers(elements);
        this.initializeScene();

        await this.audio.loadAllSounds();

        this.setupEventListeners(elements.soundToggle);
        this.effects.animateEntry();

        console.log('✅ Calc3D initialized successfully');
    }

    /**
     * Wait for DOM to be ready
     * @private
     */
    async waitForDOM() {
        if (document.readyState === 'loading') {
            await new Promise(resolve => {
                document.addEventListener('DOMContentLoaded', resolve);
            });
        }
    }

    /**
     * Get required DOM elements
     * @private
     * @returns {Object} DOM elements
     */
    getDOMElements() {
        return {
            display: document.getElementById('display'),
            expression: document.getElementById('expression'),
            soundToggle: document.getElementById('sound-toggle')
        };
    }

    /**
     * Initialize manager components
     * @private
     * @param {Object} elements - DOM elements
     */
    initializeManagers(elements) {
        // Set up effects controller
        this.effects.setDisplayElement(elements.display);

        // Initialize display manager
        this.displayManager = new DisplayManager(
            elements.display,
            elements.expression,
            this.effects
        );

        // Initialize input handler
        this.inputHandler = new InputHandler(
            this.engine,
            this.displayManager,
            this.audio,
            this.scene,
            this.effects
        );

        // Initialize event manager
        this.eventManager = new EventManager(
            this.inputHandler,
            this.effects
        );
    }

    /**
     * Initialize 3D scene
     * @private
     */
    initializeScene() {
        this.scene = new Scene3D('bg-canvas');

        // Update input handler with scene reference
        if (this.inputHandler) {
            this.inputHandler.scene = this.scene;
        }
    }

    /**
     * Set up event listeners
     * @private
     * @param {HTMLElement} soundToggle - Sound toggle button
     */
    setupEventListeners(soundToggle) {
        this.eventManager.setAudioManager(this.audio, soundToggle);
        this.eventManager.setupEventListeners();
    }
}

// Initialize app when script loads
const app = new Calc3DApp();
app.init().catch(error => {
    console.error('Failed to initialize Calc3D:', error);
});

// Export for debugging
window.Calc3D = app;
