import { useState, useEffect } from 'react';
import axios from 'axios';
import { speak } from './utils/speech.js';

export default function VideoTranslate({ userId = 1 }) {
    const [file, setFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [predictions, setPredictions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [settings, setSettings] = useState(null);
    const [log, setLog] = useState([]);

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

    const handleSubmit = async () => {
        if (!file) {
            setError('Please select a video first.');
            return;
        }

        setLoading(true);
        setPredictions([]);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post(
                'http://127.0.0.1:8000/video/translate',
                formData,
                { headers: { 'Content-Type': 'multipart/form-data' } }
            );

            const data = response.data;

            // Flatten all predictions first
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

            // Keep only top confidence per frame
            const topPredsPerFrame = Object.values(
                allPreds.reduce((acc, p) => {
                    if (!acc[p.frame] || p.confidence > acc[p.frame].confidence) {
                        acc[p.frame] = p;
                    }
                    return acc;
                }, {})
            );

            setPredictions(topPredsPerFrame);

            // Speak predictions if enabled
            if (settings?.SPEECH_ENABLED && topPredsPerFrame.length > 0) {
                const combinedText = topPredsPerFrame.map((p) => p.label).join(' ');
                speak(combinedText);
            }

            // Log last 3 results
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
        }
    };

    const renderPrediction = (pred, index) => {
        const lowConfidence = pred.confidence < 0.5;
        return (
            <div
                key={index}
                style={{
                    color: lowConfidence ? 'red' : 'white',
                    fontWeight: 'bold',
                }}
            >
                Frame {pred.frame}: {pred.label} ({(pred.confidence * 100).toFixed(1)}%)
                {lowConfidence && ' — Low confidence'}
            </div>
        );
    };

    if (!settings) return <div>Loading user settings...</div>;

    return (
        <div style={{ padding: '2rem', display: 'flex', alignItems: 'flex-start' }}>
            {/* Left Panel */}
            <div style={{ flex: 1, minWidth: 0 }}>
                <input type="file" accept="video/*" onChange={handleFileChange} />
                <button
                    onClick={handleSubmit}
                    disabled={loading || !file}
                    style={{ marginLeft: '1rem' }}
                >
                    {loading ? 'Processing...' : 'Translate'}
                </button>

                {previewUrl && (
                    <div style={{ marginTop: '1rem' }}>
                        <video
                            src={previewUrl}
                            controls
                            style={{ maxWidth: '400px', border: '1px solid #ccc' }}
                        />
                    </div>
                )}

                {error && <p style={{ color: 'red' }}>{error}</p>}

                {predictions.length > 0 && (
                    <div style={{ marginTop: '1rem' }}>
                        <h3 style={{ color: 'white' }}>Predictions:</h3>
                        {predictions.map((p, i) => renderPrediction(p, i))}
                    </div>
                )}
            </div>

            {/* Right Panel (Video Log) */}
            {log.length > 0 && (
                <div
                    style={{
                        marginLeft: '2rem',
                        minWidth: '540px',
                        maxWidth: '600px',
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

                    <div
                        style={{
                            width: '100%',
                            display: 'grid',
                            gridTemplateColumns: 'repeat(3, 1fr)',
                            gap: '1rem',
                        }}
                    >
                        {log.map((entry, idx) => (
                            <div
                                key={idx}
                                style={{
                                    border: '1px solid #ccc',
                                    padding: '0.5rem',
                                    borderRadius: '8px',
                                    background: 'transparent',
                                }}
                            >
                                <video
                                    src={entry.videoUrl}
                                    controls
                                    style={{ width: '100%', borderRadius: '6px' }}
                                />
                                <div style={{ fontSize: '0.8em', color: '#555', marginTop: '0.25rem' }}>
                                    {entry.timestamp}
                                </div>
                                <div style={{ marginTop: '0.25rem' }}>
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
