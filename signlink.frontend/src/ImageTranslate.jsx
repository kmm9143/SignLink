// DESCRIPTION:  This component implements the frontend for image-based ASL (American Sign Language) translation.
//               It lets a user upload an image, previews it, sends it to a backend API for classification, and
//               displays the predicted ASL letter(s) with confidence. It also keeps a log of recent translations.
// LANGUAGE:     JAVASCRIPT / React (using functional components, hooks, and axios for HTTP requests)

import { useState } from 'react';
import axios from 'axios';

export default function ImageTranslate() {
    // -----------------------------------------------------------------------------------
    // Step: React state declarations
    // -----------------------------------------------------------------------------------
    const [file, setFile] = useState(null);               // The selected file object
    const [previewUrl, setPreviewUrl] = useState(null);   // URL to preview the selected image
    const [prediction, setPrediction] = useState(null);   // Received prediction result from backend
    const [loading, setLoading] = useState(false);        // Loading flag during API call
    const [error, setError] = useState(null);             // Error message, if any
    const [log, setLog] = useState([]);                   // Log of past translations

    // -----------------------------------------------------------------------------------
    // Handler: when user selects (or changes) an image file
    // -----------------------------------------------------------------------------------
    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        setPrediction(null);
        setError(null);

        if (selectedFile) {
            const validTypes = ['image/png', 'image/jpeg', 'image/jpg'];
            if (!validTypes.includes(selectedFile.type)) {
                // Invalid file type → reset and show error
                setFile(null);
                setPreviewUrl(null);
                setError('Invalid file type. Please upload a PNG or JPG image.');
                return;
            }
            setFile(selectedFile);
            const url = URL.createObjectURL(selectedFile);
            setPreviewUrl(url);
        } else {
            // No file selected → clear state
            setFile(null);
            setPreviewUrl(null);
        }
        console.log('Selected file:', selectedFile);
    };

    // -----------------------------------------------------------------------------------
    // Handler: when user clicks “Translate” / submit
    // -----------------------------------------------------------------------------------
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

            // Add this translation to the log (keep only the last 10 entries)
            setLog((prevLog) => {
                const newEntry = {
                    imageUrl: previewUrl,
                    prediction: response.data,
                    timestamp: new Date().toLocaleString(),
                };
                const updatedLog = [newEntry, ...prevLog];
                return updatedLog.slice(0, 10);
            });
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

    // -----------------------------------------------------------------------------------
    // Handler: clear the translation log entirely
    // -----------------------------------------------------------------------------------
    const handleClearLog = () => {
        setLog([]);
    };

    // -----------------------------------------------------------------------------------
    // Handler: remove a specific log entry by index
    // -----------------------------------------------------------------------------------
    const handleRemoveLogEntry = (idxToRemove) => {
        setLog((prevLog) => prevLog.filter((_, idx) => idx !== idxToRemove));
    };

    // -----------------------------------------------------------------------------------
    // Helper: render predictions (with class + confidence) from received data
    // -----------------------------------------------------------------------------------
    const renderPrediction = (prediction) => {
        if (Array.isArray(prediction)) {
            return prediction.map((item, idx) =>
                item.predictions && item.predictions.predictions
                    ? item.predictions.predictions.map((pred, pidx) =>
                        pred.class && pred.confidence !== undefined ? (
                            <div key={`${idx}-${pidx}`}>
                                {pred.class}: {(pred.confidence * 100).toFixed(1)}%
                            </div>
                        ) : null
                    )
                    : null
            );
        }
        return null;
    };

    // -----------------------------------------------------------------------------------
    // Render the UI
    // -----------------------------------------------------------------------------------
    return (
        <div style={{ padding: '2rem', display: 'flex', alignItems: 'flex-start' }}>
            <div style={{ flex: 1, minWidth: 0 }}>
                {/* File input and Translate button */}
                <input type="file" accept="image/*" onChange={handleFileChange} />
                <button
                    onClick={handleSubmit}
                    disabled={loading || !file}
                    style={{ marginLeft: '1rem' }}
                >
                    {loading ? 'Translating...' : 'Translate'}
                </button>

                {/* Preview of selected image */}
                {previewUrl && (
                    <div style={{ marginTop: '1rem' }}>
                        <img
                            src={previewUrl}
                            alt="Preview"
                            style={{ maxWidth: '300px', maxHeight: '300px', border: '1px solid #ccc' }}
                        />
                    </div>
                )}

                {/* Show error message */}
                {error && <p style={{ color: 'red' }}>{error}</p>}

                {/* Show prediction result */}
                {prediction && (
                    <div style={{ marginTop: '1rem' }}>
                        <h3>Prediction:</h3>
                        {renderPrediction(prediction)}
                    </div>
                )}
            </div>

            {/* Translation log (if any) */}
            {log.length > 0 && (
                <div style={{
                    marginLeft: '2rem',
                    minWidth: '540px',
                    maxWidth: '600px',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'flex-end'
                }}>
                    <div style={{
                        width: '100%',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '1rem'
                    }}>
                        <h3 style={{ margin: 0 }}>Translation Log (last 10)</h3>
                        <button onClick={handleClearLog} style={{ background: '#e74c3c', color: '#fff' }}>
                            Clear Log
                        </button>
                    </div>
                    <div
                        style={{
                            width: '100%',
                            display: 'grid',
                            gridTemplateColumns: 'repeat(5, 1fr)',
                            gap: '1rem'
                        }}
                    >
                        {log.map((entry, idx) => (
                            <div key={idx} style={{
                                border: '1px solid #ccc',
                                padding: '0.5rem',
                                borderRadius: '8px',
                                background: 'transparent',
                                maxWidth: '110px',
                                position: 'relative',
                                minHeight: '170px',
                                boxSizing: 'border-box'
                            }}>
                                <div style={{ position: 'relative', width: '100%', display: 'flex', justifyContent: 'center' }}>
                                    <img
                                        src={entry.imageUrl}
                                        alt={`Log Preview ${idx + 1}`}
                                        style={{
                                            maxWidth: '100%',
                                            maxHeight: '80px',
                                            display: 'block',
                                            borderRadius: '4px'
                                        }}
                                    />
                                    <button
                                        onClick={() => handleRemoveLogEntry(idx)}
                                        style={{
                                            position: 'absolute',
                                            top: '6px',
                                            right: '6px',
                                            background: '#e74c3c',
                                            color: '#fff',
                                            border: 'none',
                                            borderRadius: '4px',
                                            padding: '2px 8px',
                                            cursor: 'pointer',
                                            fontSize: '0.9em',
                                            boxShadow: '0 1px 4px rgba(0,0,0,0.15)',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center'
                                        }}
                                        title="Remove this entry"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24">
                                            <path fill="currentColor" d="M7 21a2 2 0 0 1-2-2V7H3V5h5V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v1h5v2h-2v12a2 2 a 0 0 1-2 2H7zm10-14H7v12h10V7zm-6 2h2v8h-2V9z" />
                                        </svg>
                                    </button>
                                </div>
                                <div style={{ fontSize: '0.8em', color: '#555', margin: '0.25rem 0' }}>
                                    {entry.timestamp}
                                </div>
                                <div>
                                    {renderPrediction(entry.prediction)}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
