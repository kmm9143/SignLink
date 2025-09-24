import { useState } from 'react';
import axios from 'axios';

export default function ImageTranslate() {
    const [file, setFile] = useState(null);
    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setPrediction(null);
        setError(null);
        console.log('Selected file:', e.target.files[0]);
    };

    const handleSubmit = async () => {
        if (!file) {
            setError('Please select an image first.');
            console.warn('No file selected.');
            return;
        }

        setLoading(true);
        setPrediction(null);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);
        console.log('FormData prepared:', formData.get('file'));

        try {
            console.log('Sending request to backend...');
            const response = await axios.post(
                'http://127.0.0.1:8000/image/predict',
                formData,
                {
                    headers: { 'Content-Type': 'multipart/form-data' },
                }
            );
            console.log('Backend response:', response);
            setPrediction(response.data);
        } catch (err) {
            console.error('Error during request:', err);
            if (err.response) {
                console.error('Backend error response:', err.response.data);
                setError(`Backend error: ${JSON.stringify(err.response.data)}`);
            } else if (err.request) {
                console.error('No response received:', err.request);
                setError('No response received from backend.');
            } else {
                setError(`Request error: ${err.message}`);
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: '2rem' }}>
            <input type="file" accept="image/*" onChange={handleFileChange} />
            <button
                onClick={handleSubmit}
                disabled={loading}
                style={{ marginLeft: '1rem' }}
            >
                {loading ? 'Translating...' : 'Translate'}
            </button>

            {error && <p style={{ color: 'red' }}>{error}</p>}

            {prediction && (
                <div style={{ marginTop: '1rem' }}>
                    <h3>Prediction:</h3>
                    <pre>{JSON.stringify(prediction, null, 2)}</pre>
                </div>
            )}
        </div>
    );
}
