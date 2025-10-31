/**
 * Sound Manager for Calc3D
 * Handles interactive sound effects using Web Audio API
 */

class SoundManager {
    constructor() {
        this.audioContext = null;
        this.enabled = true;
        this.volume = 0.3;
        this.initAudioContext();
        this.loadSettings();
    }

    initAudioContext() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.warn('Web Audio API not supported:', e);
            this.enabled = false;
        }
    }

    loadSettings() {
        const savedEnabled = localStorage.getItem('calc3d_sound_enabled');
        if (savedEnabled !== null) {
            this.enabled = savedEnabled === 'true';
        }
    }

    saveSettings() {
        localStorage.setItem('calc3d_sound_enabled', this.enabled);
    }

    toggle() {
        this.enabled = !this.enabled;
        this.saveSettings();
        return this.enabled;
    }

    /**
     * Play a beep sound with specified frequency and duration
     */
    playBeep(frequency, duration = 0.05, type = 'sine') {
        if (!this.enabled || !this.audioContext) return;

        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);

        oscillator.type = type;
        oscillator.frequency.value = frequency;

        // Envelope for smooth sound
        gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(this.volume, this.audioContext.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);

        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + duration);
    }

    /**
     * Play a chord (multiple frequencies)
     */
    playChord(frequencies, duration = 0.1) {
        if (!this.enabled || !this.audioContext) return;

        frequencies.forEach(freq => {
            this.playBeep(freq, duration, 'sine');
        });
    }

    // Different sound types for different button categories
    playNumber() {
        this.playBeep(440, 0.04); // A4 note
    }

    playOperator() {
        this.playBeep(523.25, 0.05); // C5 note
    }

    playEquals() {
        // Play a pleasant chord for equals
        this.playChord([523.25, 659.25, 783.99], 0.15); // C-E-G major chord
    }

    playFunction() {
        this.playBeep(587.33, 0.06); // D5 note
    }

    playPower() {
        this.playBeep(698.46, 0.06); // F5 note
    }

    playClear() {
        // Descending tone for clear
        const osc = this.audioContext?.createOscillator();
        const gain = this.audioContext?.createGain();

        if (!osc || !gain || !this.enabled) return;

        osc.connect(gain);
        gain.connect(this.audioContext.destination);

        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, this.audioContext.currentTime);
        osc.frequency.exponentialRampToValueAtTime(220, this.audioContext.currentTime + 0.1);

        gain.gain.setValueAtTime(this.volume, this.audioContext.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.1);

        osc.start(this.audioContext.currentTime);
        osc.stop(this.audioContext.currentTime + 0.1);
    }

    playDelete() {
        this.playBeep(392, 0.03); // G4 note, short
    }

    playError() {
        // Dissonant chord for error
        this.playChord([200, 210], 0.2);
    }

    playSuccess() {
        // Ascending arpeggio for success
        if (!this.enabled || !this.audioContext) return;

        const notes = [523.25, 659.25, 783.99]; // C-E-G
        notes.forEach((freq, index) => {
            setTimeout(() => {
                this.playBeep(freq, 0.08);
            }, index * 50);
        });
    }
}

// Create global sound manager instance
const soundManager = new SoundManager();
