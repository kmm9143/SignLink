// DESCRIPTION:  This React component handles the "Upload Video" translation mode for the ASL Translator app.
//                It allows users to upload video files containing sign language gestures, sends the video
//                to the backend for frame-by-frame inference, displays top predictions per frame, and logs
//                the last three processed videos for quick reference. The component also integrates optional
//                text-to-speech output for recognized signs when enabled in user settings.
// LANGUAGE:     JAVASCRIPT (React.js)
// SOURCE(S):    [1] React Documentation. (n.d.). useState and useEffect Hooks. Retrieved October 11, 2025, from https://react.dev/reference/react
//               [2] Axios Documentation. (n.d.). Handling POST requests with multipart/form-data. Retrieved October 11, 2025, from https://axios-http.com
//               [3] MDN Web Docs. (n.d.). FormData API and File Uploads. Retrieved October 11, 2025, from https://developer.mozilla.org/en-US/docs/Web/API/FormData
//               [4] MDN Web Docs. (n.d.). Using object URLs for local media previews. Retrieved October 11, 2025, from https://developer.mozilla.org/en-US/docs/Web/API/URL/createObjectURL

// -----------------------------------------------------------------------------
// Step 1: Import dependencies and utility functions
// -----------------------------------------------------------------------------
import { useState, useEffect } from 'react';
import axios from 'axios';
import { speak } from './utils/speech.js';     // Custom utility for optional TTS output
import LoadingBar from './utils/loadingBar.jsx'; // Reusable loading bar component
import { Volume2, VolumeX } from 'lucide-react'; // ✅ Speaker icons

// -----------------------------------------------------------------------------
// Step 2: Define the VideoTranslate component
// -----------------------------------------------------------------------------
export default function VideoTranslate({ userId = 1 }) {
    // -------------------------------------------------------------------------
    // State variables
    // -------------------------------------------------------------------------
    const [file, setFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [predictions, setPredictions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [settings, setSettings] = useState(null);
    const [log, setLog] = useState([]);
    const [progress, setProgress] = useState(null); // Optional upload progress tracker
    const [speaking, setSpeaking] = useState(false); // ✅ Track TTS playback

    // -------------------------------------------------------------------------
    // Step 3: Fetch user settings on mount
    // -------------------------------------------------------------------------
    useEffect(() => {
        const fetchSettings = async () => {
            try {
                const res = await fetch(`http://127.0.0.1:8000/settings/${userId}`);
                if (res.ok) {
                    const data = await res.json();
                    setSettings(data);
                } else {
                    setSettings({ SPEECH_ENABLED: false });
                }
            } catch {
                setSettings({ SPEECH_ENABLED: false });
            }
        };
        fetchSettings();
    }, [userId]);

    // -------------------------------------------------------------------------
    // Step 4: Handle video file selection and validation
    // -------------------------------------------------------------------------
    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        setPredictions([]);
        setError(null);

        if (selectedFile) {
            const validTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/mpeg'];
            if (!validTypes.includes(selectedFile.type)) {
                setError('Invalid file type. Please upload an MP4, MOV, or AVI video.');
                setFile(null);
                setPreviewUrl(null);
                return;
            }
            setFile(selectedFile);
            setPreviewUrl(URL.createObjectURL(selectedFile));
        } else {
            setFile(null);
            setPreviewUrl(null);
        }
    };

    // -------------------------------------------------------------------------
    // Step 5: Handle video upload and backend translation
    // -------------------------------------------------------------------------
    const handleSubmit = async () => {
        if (!file) {
            setError('Please select a video first.');
            return;
        }

        setLoading(true);
        setPredictions([]);
        setError(null);
        setProgress(0);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post(
                'http://127.0.0.1:8000/video/translate',
                formData,
                {
                    headers: { 'Content-Type': 'multipart/form-data' },
                    onUploadProgress: (event) => {
                        if (event.total) {
                            const percent = Math.round((event.loaded * 100) / event.total);
                            setProgress(percent);
                        }
                    },
                }
            );

            const data = response.data;

            // Flatten and normalize predictions
            const allPreds = data.predictions.flatMap((frameData) => {
                const predictionArray = frameData.prediction || [];
                return predictionArray.flatMap((inner) => {
                    const preds = inner.predictions?.predictions || [];
                    return preds.map((p) => ({
                        frame: frameData.frame,
                        label: p.class || p.label || p.sign || "Unknown",
                        confidence: parseFloat(p.confidence ?? p.conf ?? p.probability ?? 0),
                    }));
                });
            });

            // Keep only highest confidence prediction per frame
            const topPredsPerFrame = Object.values(
                allPreds.reduce((acc, p) => {
                    if (!acc[p.frame] || p.confidence > acc[p.frame].confidence) {
                        acc[p.frame] = p;
                    }
                    return acc;
                }, {})
            );

            setPredictions(topPredsPerFrame);

            // ✅ Optional speech synthesis with speaking state
            if (settings?.SPEECH_ENABLED && topPredsPerFrame.length > 0) {
                const combinedText = topPredsPerFrame.map((p) => p.label).join(' ');
                speak(combinedText, {
                    onStart: () => setSpeaking(true),
                    onEnd: () => setSpeaking(false),
                    onError: () => setSpeaking(false),
                });
            }

            // Log last three sessions
            setLog((prevLog) => {
                const newEntry = {
                    videoUrl: previewUrl,
                    predictions: topPredsPerFrame,
                    timestamp: new Date().toLocaleString(),
                };
                return [newEntry, ...prevLog].slice(0, 3);
            });

        } catch (err) {
            if (err.response)
                setError(`Backend error: ${err.response.data.detail || JSON.stringify(err.response.data)}`);
            else if (err.request)
                setError('No response received from backend.');
            else
                setError(`Request error: ${err.message}`);
        } finally {
            setLoading(false);
            setProgress(null);
        }
    };

    // -------------------------------------------------------------------------
    // Step 6: Render a single prediction row
    // -------------------------------------------------------------------------
    const renderPrediction = (pred, index) => {
        const lowConfidence = pred.confidence < 0.5;
        return (
            <div key={index} style={{ color: lowConfidence ? 'red' : 'white', fontWeight: 'bold' }}>
                Frame {pred.frame}: {pred.label} ({(pred.confidence * 100).toFixed(1)}%)
                {lowConfidence && ' — Low confidence'}
            </div>
        );
    };

    // -------------------------------------------------------------------------
    // Step 7: Loading settings
    // -------------------------------------------------------------------------
    if (!settings) return <div>Loading user settings...</div>;

    // -------------------------------------------------------------------------
    // Step 8: Render the full UI
    // -------------------------------------------------------------------------
    return (
        <div style={{ padding: '2rem', display: 'flex', alignItems: 'flex-start' }}>
            {/* Left Panel — Upload & Predictions */}
            <div style={{ flex: 1, minWidth: 0 }}>
                <input type="file" accept="video/*" onChange={handleFileChange} />
                <button
                    onClick={handleSubmit}
                    disabled={loading || !file}
                    style={{ marginLeft: '1rem' }}
                >
                    {loading ? 'Processing...' : 'Translate'}
                </button>

                {/* ✅ Speaker icon showing TTS state */}
                {settings.SPEECH_ENABLED && (
                    <span style={{ marginLeft: '1rem', verticalAlign: 'middle', display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        {speaking ? (
                            <Volume2 size={22} style={{ color: '#4CAF50', animation: 'pulse 1s infinite' }} />
                        ) : (
                            <VolumeX size={22} style={{ color: '#aaa' }} />
                        )}
                    </span>
                )}

                {/* 🔹 Loading bar displayed during upload or processing */}
                {loading && <LoadingBar progress={progress} />}

                {/* Video preview */}
                {previewUrl && (
                    <div style={{ marginTop: '1rem' }}>
                        <video
                            src={previewUrl}
                            controls
                            style={{ maxWidth: '400px', border: '1px solid #ccc' }}
                        />
                    </div>
                )}

                {/* Error message */}
                {error && <p style={{ color: 'red' }}>{error}</p>}

                {/* Predictions list */}
                {predictions.length > 0 && (
                    <div
                        style={{
                            marginTop: '1rem',
                            maxHeight: '250px',
                            overflowY: 'auto',
                            paddingRight: '0.5rem',
                            border: '1px solid #444',
                            borderRadius: '6px',
                            background: 'rgba(0,0,0,0.2)',
                        }}
                    >
                        <h3 style={{
                            color: 'white',
                            position: 'sticky',
                            top: 0,
                            background: 'rgba(0,0,0,0.6)',
                            padding: '0.25rem'
                        }}>
                            Predictions:
                        </h3>
                        <div style={{ padding: '0.5rem' }}>
                            {predictions.map((p, i) => renderPrediction(p, i))}
                        </div>
                    </div>
                )}
            </div>

            {/* Right Panel — Translation Log */}
            {log.length > 0 && (
                <div
                    style={{
                        marginLeft: '2rem',
                        minWidth: '540px',
                        maxWidth: '1100px',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'flex-end',
                    }}
                >
                    <div
                        style={{
                            width: '100%',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            marginBottom: '1rem',
                        }}
                    >
                        <h3 style={{ margin: 0, color: 'white' }}>Video Translation Log (last 3)</h3>
                        <button
                            onClick={() => setLog([])}
                            style={{ background: '#e74c3c', color: '#fff' }}
                        >
                            Clear Log
                        </button>
                    </div>

                    {/* Grid of last 3 translated videos */}
                    <div
                        style={{
                            width: '100%',
                            border: '1px solid #444',
                            borderRadius: '8px',
                            background: 'rgba(0,0,0,0.2)',
                            padding: '1rem',
                            display: 'grid',
                            gridTemplateColumns: 'repeat(3, 1fr)',
                            gap: '1rem',
                            boxSizing: 'border-box',
                        }}
                    >
                        {log.map((entry, idx) => (
                            <div
                                key={idx}
                                style={{
                                    border: '1px solid #ccc',
                                    borderRadius: '8px',
                                    background: 'transparent',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    height: '100%',
                                    padding: '0.5rem',
                                    boxSizing: 'border-box',
                                }}
                            >
                                <video
                                    src={entry.videoUrl}
                                    controls
                                    style={{
                                        width: '100%',
                                        borderRadius: '6px',
                                        marginBottom: '0.4rem',
                                    }}
                                />
                                <div
                                    style={{
                                        fontSize: '0.8em',
                                        color: '#bbb',
                                        marginBottom: '0.5rem',
                                    }}
                                >
                                    {entry.timestamp}
                                </div>
                                <div
                                    style={{
                                        flexGrow: 1,
                                        overflowY: 'auto',
                                        minHeight: '160px',
                                        maxHeight: '220px',
                                        borderTop: '1px solid #444',
                                        paddingTop: '0.5rem',
                                    }}
                                >
                                    {entry.predictions.map((p, i) => renderPrediction(p, i))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}