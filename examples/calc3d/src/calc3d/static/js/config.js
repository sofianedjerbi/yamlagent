/**
 * Calc3D Configuration
 *
 * Central configuration for colors, settings, and constants
 */

export const CONFIG = {
    // Color Palette - Cyberpunk/Futuristic Theme
    colors: {
        // Primary neon colors
        neonBlue: '#00d9ff',
        neonPurple: '#b744ff',
        neonPink: '#ff2a6d',
        neonGreen: '#05ffa1',
        neonYellow: '#fffb00',

        // Background colors
        darkBg: '#0a0a0f',
        darkBg2: '#12121a',
        darkBg3: '#1a1a2e',

        // UI colors
        displayBg: 'rgba(0, 217, 255, 0.1)',
        displayText: '#00d9ff',
        buttonBg: 'rgba(255, 255, 255, 0.05)',
        buttonHover: 'rgba(255, 255, 255, 0.1)',

        // Special button colors
        operatorColor: '#ff2a6d',
        equalsColor: '#05ffa1',
        clearColor: '#b744ff',
        functionColor: '#fffb00',

        // 3D Scene colors
        particleColor: '#00d9ff',
        gridColor: '#b744ff',
        ambientLight: '#ffffff',
        pointLight: '#00d9ff',
    },

    // 3D Scene Settings
    scene: {
        fov: 75,
        near: 0.1,
        far: 1000,
        cameraZ: 5,

        // Particle system
        particleCount: 1000,
        particleSize: 0.05,
        particleSpread: 50,

        // Animation
        rotationSpeed: 0.001,
        waveSpeed: 0.0005,

        // Grid
        gridSize: 50,
        gridDivisions: 50,
    },

    // Audio Settings
    audio: {
        volume: 0.3,
        fadeTime: 0.1,
        sounds: {
            digit: '/static/sounds/digit.wav',
            operator: '/static/sounds/operator.wav',
            equals: '/static/sounds/equals.wav',
            clear: '/static/sounds/clear.wav',
            error: '/static/sounds/error.wav',
        },
    },

    // Animation Settings
    animation: {
        buttonPressDuration: 150,
        buttonScalePress: 0.95,
        displayUpdateDuration: 300,
        errorShakeDuration: 500,
        glowPulseDuration: 2000,
    },

    // Calculator Settings
    calculator: {
        maxDisplayLength: 12,
        decimalPlaces: 10,
    },

    // Button Layout (4x5 grid)
    buttons: [
        [
            { label: 'AC', type: 'clear', action: 'clearAll' },
            { label: '+/-', type: 'function', action: 'toggleSign' },
            { label: '%', type: 'function', action: 'percentage' },
            { label: '÷', type: 'operator', action: 'divide', operation: '/' }
        ],
        [
            { label: '7', type: 'digit', action: 'digit' },
            { label: '8', type: 'digit', action: 'digit' },
            { label: '9', type: 'digit', action: 'digit' },
            { label: '×', type: 'operator', action: 'multiply', operation: '*' }
        ],
        [
            { label: '4', type: 'digit', action: 'digit' },
            { label: '5', type: 'digit', action: 'digit' },
            { label: '6', type: 'digit', action: 'digit' },
            { label: '-', type: 'operator', action: 'subtract', operation: '-' }
        ],
        [
            { label: '1', type: 'digit', action: 'digit' },
            { label: '2', type: 'digit', action: 'digit' },
            { label: '3', type: 'digit', action: 'digit' },
            { label: '+', type: 'operator', action: 'add', operation: '+' }
        ],
        [
            { label: '0', type: 'digit', action: 'digit', span: 2 },
            { label: '.', type: 'decimal', action: 'decimal' },
            { label: '=', type: 'equals', action: 'equals' }
        ]
    ],

    // Input Types - Centralized constants for validation
    inputTypes: {
        DIGIT: 'digit',
        DECIMAL: 'decimal',
        OPERATOR: 'operator',
        EQUALS: 'equals',
        CLEAR: 'clear',
        FUNCTION: 'function'
    }
};
