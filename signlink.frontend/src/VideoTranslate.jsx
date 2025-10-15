import { useState, useEffect } from 'react';
import axios from 'axios';
import { speak } from './utils/speech.js';
import LoadingBar from './utils/loadingBar.jsx';
import { Volume2, VolumeX } from 'lucide-react';

export default function VideoTranslate({ userId = 1 }) {
    const [file, setFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [predictions, setPredictions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [settings, setSettings] = useState(null);
    const [log, setLog] = useState([]);
    const [progress, setProgress] = useState(null);
    const [speaking, setSpeaking] = useState(false);

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

            const topPredsPerFrame = Object.values(
                allPreds.reduce((acc, p) => {
                    if (!acc[p.frame] || p.confidence > acc[p.frame].confidence) {
                        acc[p.frame] = p;
                    }
                    return acc;
                }, {})
            );

            setPredictions(topPredsPerFrame);

            if (settings?.SPEECH_ENABLED && topPredsPerFrame.length > 0) {
                const combinedText = topPredsPerFrame.map((p) => p.label).join(' ');
                speak(combinedText, {
                    onStart: () => setSpeaking(true),
                    onEnd: () => setSpeaking(false),
                    onError: () => setSpeaking(false),
                });
            }

            setLog((prevLog) => {
                const newEntry = {
                    videoUrl: previewUrl,
                    predictions: topPredsPerFrame,
                    timestamp: new Date().toLocaleString(),
                    fileName: file.name || 'prediction.mp4'
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

    const renderPrediction = (pred, index) => {
        const lowConfidence = pred.confidence < 0.5;
        return (
            <div key={index} style={{ color: lowConfidence ? 'red' : 'white', fontWeight: 'bold' }}>
                Frame {pred.frame}: {pred.label} ({(pred.confidence * 100).toFixed(1)}%)
                {lowConfidence && ' — Low confidence'}
            </div>
        );
    };

    // ✅ Download a log entry as .txt
    const downloadLog = (entry) => {
        let text = entry.predictions.map((p, i) =>
            `Frame ${p.frame}: ${p.label} (${(p.confidence * 100).toFixed(1)}%)`
        ).join('\n');

        const blob = new Blob([text], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;

        // Replace extension with .txt
        const name = entry.fileName.endsWith(".mp4") ? entry.fileName.replace(/\.mp4$/i, ".txt") : entry.fileName + ".txt";
        link.download = name;

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };

    if (!settings) return <div>Loading user settings...</div>;

    return (
        <div style={{ padding: '2rem', display: 'flex', alignItems: 'flex-start' }}>
            {/* Left Panel */}
            <div style={{ flex: 1, minWidth: 0 }}>
                <input type="file" accept="video/*" onChange={handleFileChange} />
                <button onClick={handleSubmit} disabled={loading || !file} style={{ marginLeft: '1rem' }}>
                    {loading ? 'Processing...' : 'Translate'}
                </button>

                {settings.SPEECH_ENABLED && (
                    <span style={{ marginLeft: '1rem', verticalAlign: 'middle', display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        {speaking ? (
                            <Volume2 size={22} style={{ color: '#4CAF50', animation: 'pulse 1s infinite' }} />
                        ) : (
                            <VolumeX size={22} style={{ color: '#aaa' }} />
                        )}
                    </span>
                )}

                {loading && <LoadingBar progress={progress} />}

                {previewUrl && (
                    <div style={{ marginTop: '1rem' }}>
                        <video src={previewUrl} controls style={{ maxWidth: '400px', border: '1px solid #ccc' }} />
                    </div>
                )}

                {error && <p style={{ color: 'red' }}>{error}</p>}

                {predictions.length > 0 && (
                    <div style={{ marginTop: '1rem', maxHeight: '250px', overflowY: 'auto', paddingRight: '0.5rem', border: '1px solid #444', borderRadius: '6px', background: 'rgba(0,0,0,0.2)' }}>
                        <h3 style={{ color: 'white', position: 'sticky', top: 0, background: 'rgba(0,0,0,0.6)', padding: '0.25rem' }}>Predictions:</h3>
                        <div style={{ padding: '0.5rem' }}>
                            {predictions.map((p, i) => renderPrediction(p, i))}
                        </div>
                    </div>
                )}
            </div>

            {/* Right Panel — Log */}
            {log.length > 0 && (
                <div style={{ marginLeft: '2rem', minWidth: '540px', maxWidth: '1100px', display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                    <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                        <h3 style={{ margin: 0, color: 'white' }}>Video Translation Log (last 3)</h3>
                        <button onClick={() => setLog([])} style={{ background: '#e74c3c', color: '#fff' }}>Clear Log</button>
                    </div>

                    <div style={{ width: '100%', border: '1px solid #444', borderRadius: '8px', background: 'rgba(0,0,0,0.2)', padding: '1rem', display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', boxSizing: 'border-box' }}>
                        {log.map((entry, idx) => (
                            <div key={idx} style={{ border: '1px solid #ccc', borderRadius: '8px', background: 'transparent', display: 'flex', flexDirection: 'column', height: '100%', padding: '0.5rem', boxSizing: 'border-box' }}>
                                <video src={entry.videoUrl} controls style={{ width: '100%', borderRadius: '6px', marginBottom: '0.4rem' }} />
                                <div style={{ fontSize: '0.8em', color: '#bbb', marginBottom: '0.5rem' }}>{entry.timestamp}</div>
                                <div style={{ flexGrow: 1, overflowY: 'auto', minHeight: '160px', maxHeight: '220px', borderTop: '1px solid #444', paddingTop: '0.5rem' }}>
                                    {entry.predictions.map((p, i) => renderPrediction(p, i))}
                                </div>
                                {/* ✅ Download transcript button */}
                                <button
                                    onClick={() => downloadLog(entry)}
                                    style={{ marginTop: '0.5rem', padding: '4px 8px', background: '#1976d2', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                                >
                                    Download Transcript
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
