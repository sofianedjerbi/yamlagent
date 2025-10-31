let displayValue = '0';
const display = document.getElementById('display');

function updateDisplay() {
    display.textContent = displayValue;
}

/**
 * Add visual feedback to button press
 */
function addButtonFeedback(event) {
    const button = event.target.closest('.btn');
    if (!button) return;

    button.classList.add('active');
    setTimeout(() => {
        button.classList.remove('active');
    }, 600);
}

function appendToDisplay(value) {
    if (displayValue === '0' || displayValue === 'Error') {
        displayValue = value;
    } else {
        displayValue += value;
    }
    updateDisplay();

    // Play appropriate sound based on input type
    if (/\d/.test(value) || value === '.') {
        soundManager.playNumber();
    } else if (['+', '-', '*', '/'].includes(value)) {
        soundManager.playOperator();
    } else if (value === '(' || value === ')') {
        soundManager.playFunction();
    } else if (value.includes('**')) {
        soundManager.playPower();
    }
}

function clearDisplay() {
    displayValue = '0';
    updateDisplay();
    soundManager.playClear();
}

function deleteLast() {
    if (displayValue.length > 1) {
        displayValue = displayValue.slice(0, -1);
    } else {
        displayValue = '0';
    }
    updateDisplay();
    soundManager.playDelete();
}

async function calculate() {
    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                expression: displayValue
            })
        });

        const data = await response.json();

        if (response.ok) {
            displayValue = String(data.result);
            soundManager.playEquals();

            // Add success animation
            display.classList.remove('error');
            display.classList.add('success');
            setTimeout(() => {
                display.classList.remove('success');
            }, 600);
        } else {
            displayValue = 'Error';
            soundManager.playError();
            console.error(data.error);

            // Add error animation
            display.classList.remove('success');
            display.classList.add('error');
            setTimeout(() => {
                display.classList.remove('error');
            }, 500);
        }
    } catch (error) {
        displayValue = 'Error';
        soundManager.playError();
        console.error('Failed to calculate:', error);

        // Add error animation
        display.classList.remove('success');
        display.classList.add('error');
        setTimeout(() => {
            display.classList.remove('error');
        }, 500);
    }

    updateDisplay();
}

// Keyboard support
document.addEventListener('keydown', (event) => {
    const key = event.key;

    if (key >= '0' && key <= '9') {
        appendToDisplay(key);
    } else if (key === '.') {
        appendToDisplay(key);
    } else if (key === '+' || key === '-' || key === '*' || key === '/') {
        appendToDisplay(key);
    } else if (key === 'Enter' || key === '=') {
        event.preventDefault();
        calculate();
    } else if (key === 'Escape' || key === 'c' || key === 'C') {
        clearDisplay();
    } else if (key === 'Backspace') {
        event.preventDefault();
        deleteLast();
    } else if (key === '(' || key === ')') {
        appendToDisplay(key);
    }
});

// Initialize display
updateDisplay();

// Add visual feedback to all buttons
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('click', addButtonFeedback);
});

// Sound toggle functionality
const soundToggle = document.getElementById('soundToggle');

function updateSoundToggleUI() {
    if (soundManager.enabled) {
        soundToggle.classList.remove('muted');
        soundToggle.querySelector('.sound-icon').textContent = '🔊';
    } else {
        soundToggle.classList.add('muted');
        soundToggle.querySelector('.sound-icon').textContent = '🔇';
    }
}

soundToggle.addEventListener('click', () => {
    soundManager.toggle();
    updateSoundToggleUI();

    // Play a test sound when enabling
    if (soundManager.enabled) {
        soundManager.playSuccess();
    }
});

// Initialize sound toggle UI
updateSoundToggleUI();
