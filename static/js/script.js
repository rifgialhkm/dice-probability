document.addEventListener('DOMContentLoaded', function() {
    
    document.getElementById('calculatorForm').addEventListener('submit', (e) => {
        e.preventDefault();
        calculate();
    });

});

async function calculate() {
    hideMessages();
    document.getElementById('loadingIndicator').style.display = 'block';

    const soalText = document.getElementById('soalInput').value;
    const formData = {
        soal: soalText
    };
    
    if (!soalText.trim()) {
        showError("Soal tidak boleh kosong.");
        return;
    }

    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Terjadi kesalahan pada server');
        }
        
        displayResults(result);
        
    } catch (error) {
        showError(error.message);
    } finally {
        document.getElementById('loadingIndicator').style.display = 'none';
    }
}

function displayResults(result) {
    const stepsContainer = document.getElementById('stepsContainer');
    stepsContainer.innerHTML = '';
    result.steps.forEach(step => {
        const stepDiv = document.createElement('div');
        stepDiv.className = 'step';
        const contentHtml = step.content.map(line => `<div>${line}</div>`).join('');
        stepDiv.innerHTML = `<div class="step-title">${step.title}</div><div class="step-content">${contentHtml}</div>`;
        stepsContainer.appendChild(stepDiv);
    });
    document.getElementById('conclusionContainer').innerHTML = `<strong>Kesimpulan:</strong> ${result.conclusion}`;
    document.getElementById('resultSection').classList.add('show');
    document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function hideMessages() {
    document.getElementById('resultSection').classList.remove('show');
    document.getElementById('errorMessage').style.display = 'none';
    document.getElementById('loadingIndicator').style.display = 'none';
}

function showError(message) {
    document.getElementById('loadingIndicator').style.display = 'none';
    document.getElementById('errorText').textContent = message;
    document.getElementById('errorMessage').style.display = 'block';
    document.getElementById('errorMessage').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function resetForm() {
    document.getElementById('calculatorForm').reset();
    hideMessages();
}