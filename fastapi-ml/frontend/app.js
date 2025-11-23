document.getElementById('predictionForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const apiUrl = document.getElementById('apiUrl').value.replace(/\/$/, '');
    const resultDiv = document.getElementById('result');
    const speciesName = document.getElementById('speciesName');
    const probability = document.getElementById('probability');
    const flowerIcon = document.getElementById('flowerIcon');

    const data = {
        sepal_length: parseFloat(document.getElementById('sepalLength').value),
        sepal_width: parseFloat(document.getElementById('sepalWidth').value),
        petal_length: parseFloat(document.getElementById('petalLength').value),
        petal_width: parseFloat(document.getElementById('petalWidth').value)
    };

    try {
        const response = await fetch(`${apiUrl}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const result = await response.json();

        speciesName.textContent = result.class_name;
        probability.textContent = `Confidence: ${(result.probability * 100).toFixed(2)}%`;

        // Set icon and theme based on species
        // Reset themes
        document.body.className = '';

        switch (result.class_name) {
            case 'setosa':
                flowerIcon.textContent = '🌸'; // Cherry Blossom for Setosa
                document.body.classList.add('theme-setosa');
                break;
            case 'versicolor':
                flowerIcon.textContent = '🌺'; // Hibiscus for Versicolor
                document.body.classList.add('theme-versicolor');
                break;
            case 'virginica':
                flowerIcon.textContent = '🌻'; // Sunflower for Virginica
                document.body.classList.add('theme-virginica');
                break;
            default:
                flowerIcon.textContent = '❓';
        }

        resultDiv.classList.remove('hidden');
    } catch (error) {
        alert('Error connecting to API. Please check the URL and try again.');
        console.error('Error:', error);
    }
});
