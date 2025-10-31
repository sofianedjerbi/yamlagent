let currentExpression = '';
let currentResult = '0';

function updateDisplay() {
    document.getElementById('expression').textContent = currentExpression || '';
    document.getElementById('result').textContent = currentResult;
}

function appendNumber(num) {
    currentExpression += num;
    updateDisplay();
}

function appendOperator(op) {
    // Prevent adding operator if expression is empty
    if (currentExpression === '' && op !== '-') return;

    // Prevent consecutive operators
    const lastChar = currentExpression.slice(-1);
    if (['+', '-', '*', '/', '%', '^'].includes(lastChar)) {
        currentExpression = currentExpression.slice(0, -1);
    }

    currentExpression += op;
    updateDisplay();
}

function clearAll() {
    currentExpression = '';
    currentResult = '0';
    updateDisplay();
}

function deleteLast() {
    currentExpression = currentExpression.slice(0, -1);
    updateDisplay();
}

async function calculate() {
    if (currentExpression === '') return;

    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                expression: currentExpression
            })
        });

        const data = await response.json();

        if (response.ok) {
            currentResult = data.result.toString();
            currentExpression = '';
            updateDisplay();
        } else {
            currentResult = 'Error';
            updateDisplay();
            setTimeout(() => {
                currentResult = '0';
                currentExpression = '';
                updateDisplay();
            }, 2000);
        }
    } catch (error) {
        console.error('Calculation error:', error);
        currentResult = 'Error';
        updateDisplay();
        setTimeout(() => {
            currentResult = '0';
            currentExpression = '';
            updateDisplay();
        }, 2000);
    }
}

// Keyboard support
document.addEventListener('keydown', (event) => {
    const key = event.key;

    // Numbers
    if (key >= '0' && key <= '9') {
        appendNumber(key);
    }
    // Decimal point
    else if (key === '.') {
        appendNumber(key);
    }
    // Operators
    else if (key === '+' || key === '-' || key === '*' || key === '/') {
        appendOperator(key);
    }
    // Enter for equals
    else if (key === 'Enter') {
        event.preventDefault();
        calculate();
    }
    // Backspace for delete
    else if (key === 'Backspace') {
        event.preventDefault();
        deleteLast();
    }
    // Escape for clear
    else if (key === 'Escape') {
        clearAll();
    }
});

// Initialize display
updateDisplay();
