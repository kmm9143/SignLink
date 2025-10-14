// DESCRIPTION:   React component that enables ASL translation from uploaded
//                images. It handles image file input, backend prediction via
//                API, user-specific settings retrieval, and optional speech
//                output (Text-to-Speech) with a visual loading indicator
//                and speaker icon during speech playback.
// LANGUAGE:      JAVASCRIPT (React.js)

import { useState, useEffect } from "react";
import axios from "axios";
import { speak } from "./utils/speech.js";
import LoadingBar from "./utils/loadingBar.jsx";
import { Volume2, VolumeX } from "lucide-react"; // ✅ Speaker icons

export default function ImageTranslate({ userId = 1 }) {
    const [file, setFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [log, setLog] = useState([]);
    const [settings, setSettings] = useState(null);
    const [speaking, setSpeaking] = useState(false); // ✅ Track when speech is active

    // Fetch user settings
    useEffect(() => {
        const fetchSettings = async () => {
            try {
                const res = await fetch(`http://localhost:8000/settings/${userId}`);
                if (res.ok) {
                    const data = await res.json();
                    setSettings(data);
                } else {
                    console.warn("No settings found, defaulting speech to disabled.");
                    setSettings({ SPEECH_ENABLED: false });
                }
            } catch (err) {
                console.error("Error fetching settings:", err);
                setSettings({ SPEECH_ENABLED: false });
            }
        };
        fetchSettings();
    }, [userId]);

    // Handle file input
    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        setPrediction(null);
        setError(null);

        if (selectedFile) {
            const validTypes = ["image/png", "image/jpeg", "image/jpg"];
            if (!validTypes.includes(selectedFile.type)) {
                setFile(null);
                setPreviewUrl(null);
                setError("Invalid file type. Please upload a PNG or JPG image.");
                return;
            }
            setFile(selectedFile);
            setPreviewUrl(URL.createObjectURL(selectedFile));
        } else {
            setFile(null);
            setPreviewUrl(null);
        }
    };

    // Submit image for prediction
    const handleSubmit = async () => {
        if (!file) {
            setError("Please select an image first.");
            return;
        }

        setLoading(true);
        setPrediction(null);
        setError(null);

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await axios.post(
                "http://127.0.0.1:8000/image/predict",
                formData,
                { headers: { "Content-Type": "multipart/form-data" } }
            );

            const data = response.data;
            const allPredictions = [];
            if (Array.isArray(data)) {
                data.forEach((item) => {
                    item.predictions?.predictions?.forEach((pred) => allPredictions.push(pred));
                });
            }

            let highestPred = null;
            allPredictions.forEach((pred) => {
                if (!highestPred || pred.confidence > highestPred.confidence)
                    highestPred = pred;
            });

            setPrediction(highestPred);

            // ✅ Speech output with visual indicator
            if (settings?.SPEECH_ENABLED && highestPred?.class) {
                speak(`${highestPred.class}`, {
                    onStart: () => setSpeaking(true),
                    onEnd: () => setSpeaking(false),
                    onError: () => setSpeaking(false),
                });
            }

            // ✅ Add entry to the log
            setLog((prevLog) => {
                const newEntry = {
                    imageUrl: previewUrl,
                    prediction: highestPred,
                    timestamp: new Date().toLocaleString(),
                };
                return [newEntry, ...prevLog].slice(0, 10);
            });
        } catch (err) {
            console.error("Error during request:", err);
            if (err.response)
                setError(`Backend error: ${JSON.stringify(err.response.data)}`);
            else if (err.request)
                setError("No response received from backend.");
            else setError(`Request error: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const handleClearLog = () => setLog([]);
    const handleRemoveLogEntry = (idx) =>
        setLog((prev) => prev.filter((_, i) => i !== idx));

    const renderPrediction = (pred) => {
        if (!pred?.class || pred.confidence === undefined) return null;
        const lowConfidence = pred.confidence < 0.5;
        return (
            <div style={{ color: lowConfidence ? "red" : "white" }}>
                {pred.class}: {(pred.confidence * 100).toFixed(1)}%
                {lowConfidence && " — Low confidence in recognition result."}
            </div>
        );
    };

    if (!settings) return <div>Loading user settings...</div>;

    return (
        <div style={{ padding: "2rem", display: "flex", alignItems: "flex-start" }}>
            {/* Left Panel */}
            <div style={{ flex: 1, minWidth: 0 }}>
                <input type="file" accept="image/*" onChange={handleFileChange} />
                <button
                    onClick={handleSubmit}
                    disabled={loading || !file}
                    style={{ marginLeft: "1rem" }}
                >
                    Translate
                </button>

                {/* ✅ Speaker Icon for TTS */}
                {settings?.SPEECH_ENABLED && (
                    <span
                        style={{
                            marginLeft: "1rem",
                            verticalAlign: "middle",
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "0.25rem",
                        }}
                    >
                        {speaking ? (
                            <Volume2
                                size={22}
                                style={{ color: "#4CAF50", animation: "pulse 1s infinite" }}
                            />
                        ) : (
                            <VolumeX size={22} style={{ color: "#aaa" }} />
                        )}
                    </span>
                )}

                {/* ✅ Loading bar when processing */}
                {loading && (
                    <div style={{ marginTop: "1rem" }}>
                        <LoadingBar />
                    </div>
                )}

                {previewUrl && (
                    <div style={{ marginTop: "1rem" }}>
                        <img
                            src={previewUrl}
                            alt="Preview"
                            style={{
                                maxWidth: "300px",
                                maxHeight: "300px",
                                border: "1px solid #ccc",
                            }}
                        />
                    </div>
                )}

                {error && <p style={{ color: "red" }}>{error}</p>}

                {prediction && (
                    <div style={{ marginTop: "1rem" }}>
                        <h3>Prediction:</h3>
                        {renderPrediction(prediction)}
                    </div>
                )}
            </div>

            {/* Right Panel - Translation Log */}
            {log.length > 0 && (
                <div
                    style={{
                        marginLeft: "2rem",
                        minWidth: "540px",
                        maxWidth: "600px",
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "flex-end",
                    }}
                >
                    <div
                        style={{
                            width: "100%",
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            marginBottom: "1rem",
                        }}
                    >
                        <h3 style={{ margin: 0 }}>Translation Log (last 10)</h3>
                        <button
                            onClick={handleClearLog}
                            style={{ background: "#e74c3c", color: "#fff" }}
                        >
                            Clear Log
                        </button>
                    </div>

                    <div
                        style={{
                            width: "100%",
                            display: "grid",
                            gridTemplateColumns: "repeat(5, 1fr)",
                            gap: "1rem",
                        }}
                    >
                        {log.map((entry, idx) => (
                            <div
                                key={idx}
                                style={{
                                    border: "1px solid #ccc",
                                    padding: "0.5rem",
                                    borderRadius: "8px",
                                    background: "transparent",
                                    maxWidth: "110px",
                                    position: "relative",
                                    minHeight: "170px",
                                    boxSizing: "border-box",
                                }}
                            >
                                <div
                                    style={{
                                        position: "relative",
                                        width: "100%",
                                        display: "flex",
                                        justifyContent: "center",
                                    }}
                                >
                                    <img
                                        src={entry.imageUrl}
                                        alt={`Log Preview ${idx + 1}`}
                                        style={{
                                            maxWidth: "100%",
                                            maxHeight: "80px",
                                            display: "block",
                                            borderRadius: "4px",
                                        }}
                                    />
                                    <button
                                        onClick={() => handleRemoveLogEntry(idx)}
                                        style={{
                                            position: "absolute",
                                            top: "6px",
                                            right: "6px",
                                            background: "#e74c3c",
                                            color: "#fff",
                                            border: "none",
                                            borderRadius: "4px",
                                            padding: "2px 8px",
                                            cursor: "pointer",
                                            fontSize: "0.9em",
                                            boxShadow: "0 1px 4px rgba(0,0,0,0.15)",
                                        }}
                                        title="Remove this entry"
                                    >
                                        ✖
                                    </button>
                                </div>
                                <div
                                    style={{
                                        fontSize: "0.8em",
                                        color: "#555",
                                        margin: "0.25rem 0",
                                    }}
                                >
                                    {entry.timestamp}
                                </div>
                                <div>{renderPrediction(entry.prediction)}</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
