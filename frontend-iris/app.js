/**
 * Mapping species classes returned by KServe Model
 * Assuming Scikit-Learn RandomForest output where:
 * 0 = Setosa
 * 1 = Versicolor
 * 2 = Virginica
 */
const SPECIES_MAP = {
    0: { name: 'Iris Setosa', emoji: '🌸', theme: 'theme-setosa' },
    1: { name: 'Iris Versicolor', emoji: '🌺', theme: 'theme-versicolor' },
    2: { name: 'Iris Virginica', emoji: '🌻', theme: 'theme-virginica' }
};

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('predictionForm');
    const submitBtn = document.getElementById('submitBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultCard = document.getElementById('resultCard');
    const errorBanner = document.getElementById('errorBanner');

    // Result elements
    const flowerIcon = document.getElementById('flowerIcon');
    const speciesName = document.getElementById('speciesName');
    const classIndexEl = document.getElementById('classIndex');
    const errorMessage = document.getElementById('errorMessage');

    // Reset UI state
    const resetUI = () => {
        resultCard.classList.add('hidden');
        errorBanner.classList.add('hidden');
        document.body.className = ''; // Removing all theme classes
    };

    const setLoading = (isLoading) => {
        submitBtn.disabled = isLoading;
        if (isLoading) {
            loadingSpinner.classList.remove('hidden');
            submitBtn.querySelector('span').textContent = 'Predicting...';
            submitBtn.style.opacity = '0.8';
        } else {
            loadingSpinner.classList.add('hidden');
            submitBtn.querySelector('span').textContent = 'Predict Species';
            submitBtn.style.opacity = '1';
        }
    };

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        resetUI();
        setLoading(true);

        // 1. Hardcode exact native backend endpoint
        const apiUrl = '/v1/models/sklearn-iris:predict';

        // 2. Gather Features
        const sepalLength = parseFloat(document.getElementById('sepalLength').value);
        const sepalWidth = parseFloat(document.getElementById('sepalWidth').value);
        const petalLength = parseFloat(document.getElementById('petalLength').value);
        const petalWidth = parseFloat(document.getElementById('petalWidth').value);

        // 3. Construct Standard KServe Protocol Payload
        const payload = {
            instances: [
                [sepalLength, sepalWidth, petalLength, petalWidth]
            ]
        };

        try {
            // Parse URL to handle both absolute (local testing) and relative (cloud Native) paths
            let parsedUrl;
            let targetHost = undefined;
            
            // Checking if it's a relative URL (which means we are running natively on the ELB)
            if (apiUrl.startsWith('/')) {
                parsedUrl = new URL(apiUrl, window.location.origin);
            } else {
                parsedUrl = new URL(apiUrl);
                targetHost = parsedUrl.hostname;
                if (targetHost === 'localhost' || targetHost === '127.0.0.1') {
                    // Local proxy legacy support
                    targetHost = 'sklearn-iris.kserve-test.example.com';
                } else {
                    targetHost = undefined;
                }
            }

            const fetchHeaders = {
                'Content-Type': 'application/json'
            };
            if (targetHost) {
                fetchHeaders['Target-Host'] = targetHost;
            }

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: fetchHeaders,
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                let errorDetails = '';
                try {
                    const errorJson = await response.json();
                    errorDetails = JSON.stringify(errorJson);
                } catch (e) {
                    errorDetails = response.statusText;
                }
                throw new Error(`HTTP Error ${response.status}: ${errorDetails}`);
            }

            const data = await response.json();

            // 5. Parse output strictly following {"predictions": [...]}
            // Example response: {"predictions": [1]}
            if (!data.predictions || !Array.isArray(data.predictions) || data.predictions.length === 0) {
                throw new Error('Unexpected response format from KServe. Expected {"predictions": [...]}.');
            }

            const classIndex = data.predictions[0];

            // 6. Map to species info
            const speciesInfo = SPECIES_MAP[classIndex] || {
                name: 'Unknown Species',
                emoji: '❓',
                theme: ''
            };

            // 7. Update UI
            document.body.classList.add(speciesInfo.theme);
            flowerIcon.textContent = speciesInfo.emoji;
            speciesName.textContent = speciesInfo.name;
            classIndexEl.textContent = classIndex;

            resultCard.classList.remove('hidden');

        } catch (error) {
            console.error('Prediction Failed:', error);
            errorMessage.textContent = error.message.includes('fetch')
                ? 'Network connection error (CORS or server down). Please check the backend.'
                : error.message;
            errorBanner.classList.remove('hidden');
        } finally {
            setLoading(false);
        }
    });
});
