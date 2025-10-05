// DESCRIPTION:   React component that enables ASL translation from uploaded
//                images. It handles image file input, backend prediction via
//                API, user-specific settings retrieval, and optional speech
//                output (Text-to-Speech).
// LANGUAGE:      JAVASCRIPT (React.js)
// SOURCE(S):     
//    [1] React Docs. (n.d.). Using the Effect Hook. Retrieved October 4, 2025, from https://react.dev/reference/react/useEffect
//    [2] React Docs. (n.d.). Forms and Input Handling. Retrieved October 4, 2025, from https://react.dev/learn/forms
//    [3] Axios GitHub Repository. (n.d.). Axios Documentation. Retrieved October 4, 2025, from https://axios-http.com/docs/intro
//    [4] MDN Web Docs. (n.d.). Using the Web Speech API. Retrieved October 4, 2025, from https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API

// -----------------------------------------------------------------------------
// Step 1: Import dependencies and helper modules
// -----------------------------------------------------------------------------
import { useState, useEffect } from 'react';     // React Hooks for managing state and lifecycle
import axios from 'axios';                      // HTTP client for backend communication
import { speak } from './utils/speech.js';      // Local utility for text-to-speech output

// -----------------------------------------------------------------------------
// Step 2: Define ImageTranslate component
// -----------------------------------------------------------------------------
export default function ImageTranslate({ userId = 1 }) {

    // -------------------------------------------------------------------------
    // Step 3: Define state variables
    // -------------------------------------------------------------------------
    const [file, setFile] = useState(null);              // Stores the selected image file
    const [previewUrl, setPreviewUrl] = useState(null);  // Temporary image URL for preview display
    const [prediction, setPrediction] = useState(null);  // Holds prediction result from backend
    const [loading, setLoading] = useState(false);       // Boolean flag for loading state
    const [error, setError] = useState(null);            // Error message (if any)
    const [log, setLog] = useState([]);                  // List of previous translations
    const [settings, setSettings] = useState(null);      // User settings from backend (speech/webcam preferences)

    // -------------------------------------------------------------------------
    // Step 4: Fetch user settings from backend
    // -------------------------------------------------------------------------
    useEffect(() => {
        const fetchSettings = async () => {
            try {
                // Make GET request to retrieve user's settings by ID
                const res = await fetch(`http://localhost:8000/settings/${userId}`);
                if (res.ok) {
                    const data = await res.json();
                    setSettings(data); // Store fetched settings
                } else {
                    // If no settings found, default to speech disabled
                    console.warn("No settings found, defaulting speech to disabled.");
                    setSettings({ SPEECH_ENABLED: false });
                }
            } catch (err) {
                // Network or API error handling
                console.error("Error fetching settings:", err);
                setSettings({ SPEECH_ENABLED: false });
            }
        };
        fetchSettings(); // Call function once component mounts
    }, [userId]); // Rerun if userId changes

    // -------------------------------------------------------------------------
    // Step 5: Handle file selection and validation
    // -------------------------------------------------------------------------
    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0]; // Get first selected file
        setPrediction(null);
        setError(null);

        if (selectedFile) {
            const validTypes = ['image/png', 'image/jpeg', 'image/jpg'];
            // Validate allowed image formats
            if (!validTypes.includes(selectedFile.type)) {
                setFile(null);
                setPreviewUrl(null);
                setError('Invalid file type. Please upload a PNG or JPG image.');
                return;
            }
            // Create temporary preview URL
            setFile(selectedFile);
            setPreviewUrl(URL.createObjectURL(selectedFile));
        } else {
            // Reset states if no file is selected
            setFile(null);
            setPreviewUrl(null);
        }
        console.log('Selected file:', selectedFile);
    };

    // -------------------------------------------------------------------------
    // Step 6: Handle translation submission
    // -------------------------------------------------------------------------
    const handleSubmit = async () => {
        if (!file) {
            setError('Please select an image first.');
            return;
        }

        setLoading(true);
        setPrediction(null);
        setError(null);

        const formData = new FormData(); // Create form data for upload
        formData.append('file', file);   // Attach image file

        try {
            // Send POST request to backend model endpoint
            const response = await axios.post(
                'http://127.0.0.1:8000/image/predict',
                formData,
                { headers: { 'Content-Type': 'multipart/form-data' } }
            );
            const data = response.data;

            // Collect all predictions if backend returns multiple
            const allPredictions = [];
            if (Array.isArray(data)) {
                data.forEach(item => {
                    item.predictions?.predictions?.forEach(pred => allPredictions.push(pred));
                });
            }

            // Select prediction with highest confidence
            let highestPred = null;
            allPredictions.forEach(pred => {
                if (!highestPred || pred.confidence > highestPred.confidence)
                    highestPred = pred;
            });

            setPrediction(highestPred); // Store best result

            // -----------------------------------------------------------------
            // Optional Step: Trigger Text-to-Speech if enabled in settings
            // -----------------------------------------------------------------
            if (settings?.SPEECH_ENABLED && highestPred?.class) {
                speak(`Predicted letter is ${highestPred.class}`);
            }

            // -----------------------------------------------------------------
            // Step 7: Update translation log (keep last 10 entries)
            // -----------------------------------------------------------------
            setLog(prevLog => {
                const newEntry = {
                    imageUrl: previewUrl,
                    prediction: highestPred,
                    timestamp: new Date().toLocaleString(),
                };
                return [newEntry, ...prevLog].slice(0, 10);
            });

        } catch (err) {
            // -----------------------------------------------------------------
            // Step 8: Error handling for API request
            // -----------------------------------------------------------------
            console.error('Error during request:', err);
            if (err.response) setError(`Backend error: ${JSON.stringify(err.response.data)}`);
            else if (err.request) setError('No response received from backend.');
            else setError(`Request error: ${err.message}`);
        } finally {
            setLoading(false); // End loading state
        }
    };

    // -------------------------------------------------------------------------
    // Step 9: Clear all log entries
    // -------------------------------------------------------------------------
    const handleClearLog = () => setLog([]);

    // -------------------------------------------------------------------------
    // Step 10: Remove specific log entry by index
    // -------------------------------------------------------------------------
    const handleRemoveLogEntry = (idx) => setLog(prevLog => prevLog.filter((_, i) => i !== idx));

    // -------------------------------------------------------------------------
    // Step 11: Render prediction with confidence color coding
    // -------------------------------------------------------------------------
    const renderPrediction = (pred) => {
        if (!pred?.class || pred.confidence === undefined) return null;
        const lowConfidence = pred.confidence < 0.5;
        return (
            <div style={{ color: lowConfidence ? 'red' : 'white' }}>
                {pred.class}: {(pred.confidence * 100).toFixed(1)}%
                {lowConfidence && ' — Low confidence in recognition result.'}
            </div>
        );
    };

    // -------------------------------------------------------------------------
    // Step 12: Render UI
    // -------------------------------------------------------------------------
    if (!settings) return <div>Loading user settings...</div>;

    return (
        <div style={{ padding: '2rem', display: 'flex', alignItems: 'flex-start' }}>
            {/* ----------------------- Left Panel ----------------------- */}
            <div style={{ flex: 1, minWidth: 0 }}>
                {/* File input control */}
                <input type="file" accept="image/*" onChange={handleFileChange} />

                {/* Submit button */}
                <button
                    onClick={handleSubmit}
                    disabled={loading || !file}
                    style={{ marginLeft: '1rem' }}
                >
                    {loading ? 'Translating...' : 'Translate'}
                </button>

                {/* Image preview display */}
                {previewUrl && (
                    <div style={{ marginTop: '1rem' }}>
                        <img
                            src={previewUrl}
                            alt="Preview"
                            style={{ maxWidth: '300px', maxHeight: '300px', border: '1px solid #ccc' }}
                        />
                    </div>
                )}

                {/* Error message display */}
                {error && <p style={{ color: 'red' }}>{error}</p>}

                {/* Prediction output */}
                {prediction && (
                    <div style={{ marginTop: '1rem' }}>
                        <h3>Prediction:</h3>
                        {renderPrediction(prediction)}
                    </div>
                )}
            </div>

            {/* ----------------------- Right Panel (Log) ----------------------- */}
            {log.length > 0 && (
                <div style={{
                    marginLeft: '2rem',
                    minWidth: '540px',
                    maxWidth: '600px',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'flex-end'
                }}>
                    {/* Log header with clear button */}
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

                    {/* Grid layout for log items */}
                    <div style={{
                        width: '100%',
                        display: 'grid',
                        gridTemplateColumns: 'repeat(5, 1fr)',
                        gap: '1rem'
                    }}>
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
                                {/* Log entry preview image */}
                                <div style={{ position: 'relative', width: '100%', display: 'flex', justifyContent: 'center' }}>
                                    <img
                                        src={entry.imageUrl}
                                        alt={`Log Preview ${idx + 1}`}
                                        style={{ maxWidth: '100%', maxHeight: '80px', display: 'block', borderRadius: '4px' }}
                                    />
                                    {/* Delete log entry button */}
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
                                        ✖
                                    </button>
                                </div>

                                {/* Timestamp and prediction info */}
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