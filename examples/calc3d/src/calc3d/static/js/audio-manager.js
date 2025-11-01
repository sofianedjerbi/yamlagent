/**
 * Calc3D Audio Manager
 *
 * Manages sound effects using Web Audio API
 */

import { CONFIG } from './config.js';

export class AudioManager {
    constructor() {
        this.context = null;
        this.sounds = new Map();
        this.enabled = true;
        this.volume = CONFIG.audio.volume;
        this.gainNode = null;

        this.init();
    }

    /**
     * Initialize the Web Audio API context
     */
    init() {
        try {
            // Create audio context (Safari compatibility)
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            this.context = new AudioContext();

            // Create master gain node for volume control
            this.gainNode = this.context.createGain();
            this.gainNode.gain.value = this.volume;
            this.gainNode.connect(this.context.destination);

            // Add user interaction listener to resume context if suspended
            // Modern browsers require user interaction before playing audio
            this.setupUserInteractionHandler();

            console.log('AudioManager initialized');
        } catch (error) {
            console.warn('Web Audio API not supported:', error);
            this.enabled = false;
        }
    }

    /**
     * Set up handler to resume AudioContext on first user interaction
     * Required by modern browsers for autoplay policy compliance
     * @private
     */
    setupUserInteractionHandler() {
        const resumeContext = () => {
            if (this.context && this.context.state === 'suspended') {
                this.context.resume().then(() => {
                    console.log('AudioContext resumed after user interaction');
                });
            }
        };

        // Listen for first user interaction
        document.addEventListener('click', resumeContext, { once: true });
        document.addEventListener('touchstart', resumeContext, { once: true });
        document.addEventListener('keydown', resumeContext, { once: true });
    }

    /**
     * Preload a sound file
     * @param {string} name - Sound identifier
     * @param {string} url - URL to sound file
     */
    async loadSound(name, url) {
        if (!this.enabled) return;

        try {
            const response = await fetch(url);
            const arrayBuffer = await response.arrayBuffer();
            const audioBuffer = await this.context.decodeAudioData(arrayBuffer);

            this.sounds.set(name, audioBuffer);
            console.log(`Loaded sound: ${name}`);
        } catch (error) {
            console.warn(`Failed to load sound ${name}:`, error);
        }
    }

    /**
     * Preload all configured sounds
     */
    async loadAllSounds() {
        if (!this.enabled) return;

        const loadPromises = Object.entries(CONFIG.audio.sounds).map(([name, url]) =>
            this.loadSound(name, url)
        );

        await Promise.all(loadPromises);
        console.log('All sounds loaded');
    }

    /**
     * Play a sound effect
     * @param {string} name - Sound identifier
     * @param {number} playbackRate - Playback speed (default 1.0)
     */
    play(name, playbackRate = 1.0) {
        if (!this.enabled || !this.sounds.has(name)) {
            return;
        }

        // Resume context if suspended (required after user interaction)
        if (this.context.state === 'suspended') {
            this.context.resume();
        }

        try {
            // Create source node
            const source = this.context.createBufferSource();
            source.buffer = this.sounds.get(name);
            source.playbackRate.value = playbackRate;

            // Connect to gain node
            source.connect(this.gainNode);

            // Play sound
            source.start(0);
        } catch (error) {
            console.warn(`Failed to play sound ${name}:`, error);
        }
    }

    /**
     * Sound presets for different actions (DRY - centralized configuration)
     * @private
     */
    static SOUND_PRESETS = {
        digit: 1.0,
        operator: 0.9,
        equals: 1.1,
        clear: 0.8,
        error: 1.0
    };

    /**
     * Play digit button sound
     */
    playDigit() {
        this.playPreset('digit');
    }

    /**
     * Play operator button sound
     */
    playOperator() {
        this.playPreset('operator');
    }

    /**
     * Play equals button sound
     */
    playEquals() {
        this.playPreset('equals');
    }

    /**
     * Play clear button sound
     */
    playClear() {
        this.playPreset('clear');
    }

    /**
     * Play error sound
     */
    playError() {
        this.playPreset('error');
    }

    /**
     * Play sound using preset (DRY helper)
     * @param {string} preset - Preset name
     * @private
     */
    playPreset(preset) {
        const playbackRate = AudioManager.SOUND_PRESETS[preset] || 1.0;
        this.play(preset, playbackRate);
    }

    /**
     * Set master volume
     * @param {number} volume - Volume level (0.0 to 1.0)
     */
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));

        if (this.gainNode) {
            this.gainNode.gain.setTargetAtTime(
                this.volume,
                this.context.currentTime,
                CONFIG.audio.fadeTime
            );
        }
    }

    /**
     * Toggle sound on/off
     */
    toggle() {
        this.enabled = !this.enabled;
        return this.enabled;
    }

    /**
     * Enable sounds
     */
    enable() {
        this.enabled = true;
        if (this.context && this.context.state === 'suspended') {
            this.context.resume();
        }
    }

    /**
     * Disable sounds
     */
    disable() {
        this.enabled = false;
        if (this.context && this.context.state === 'running') {
            this.context.suspend();
        }
    }
}
