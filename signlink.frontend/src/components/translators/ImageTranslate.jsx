// DESCRIPTION:   React component that enables ASL translation from uploaded
//                images using speaker icon component for TTS.
// LANGUAGE:      JAVASCRIPT (React.js)

import { useState } from "react";
import LoadingBar from "./components/common/LoadingBar.jsx";
import SpeakerIcon from "./components/common/SpeakerIcon.jsx";

// ✅ Reusable hooks
import useUserSettings from "./hooks/useUserSettings";
import useSpeech from "./hooks/useSpeech";
import usePredictionAPI from "./hooks/usePredictionAPI";

export default function ImageTranslate({ userId = 1 }) {
    const settings = useUserSettings(userId);
    const { speaking, speakText } = useSpeech(settings);

    // Parser function for image predictions
    const parseImagePredictions = (data) => {
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
        return highestPred;
    };

    // Shared backend logic
    const { sendFile, predictions, loading, error } = usePredictionAPI(
        "http://127.0.0.1:8000/image/predict",
        parseImagePredictions
    );

    const [file, setFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [prediction, setPrediction] = useState(null);
    const [log, setLog] = useState([]);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        setPrediction(null);

        if (!selectedFile) {
            setFile(null);
            setPreviewUrl(null);
            return;
        }

        const validTypes = ["image/png", "image/jpeg", "image/jpg"];
        if (!validTypes.includes(selectedFile.type)) {
            alert("Invalid file type. Please upload a PNG or JPG image.");
            setFile(null);
            setPreviewUrl(null);
            return;
        }

        setFile(selectedFile);
        setPreviewUrl(URL.createObjectURL(selectedFile));
    };

    const handleSubmit = async () => {
        if (!file) return alert("Please select an image first.");

        const pred = await sendFile(file);
        setPrediction(pred);

        if (settings?.SPEECH_ENABLED && pred?.class) speakText(pred.class);

        setLog((prevLog) => {
            const newEntry = {
                imageUrl: previewUrl,
                prediction: pred,
                timestamp: new Date().toLocaleString(),
            };
            return [newEntry, ...prevLog].slice(0, 10);
        });
    };

    const handleClearLog = () => setLog([]);
    const handleRemoveLogEntry = (idx) => setLog((prev) => prev.filter((_, i) => i !== idx));

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

                {/* ✅ Speaker Icon */}
                <SpeakerIcon
                    enabled={settings?.SPEECH_ENABLED}
                    speaking={speaking}
                    size={22}
                    style={{ marginLeft: "1rem" }}
                />

                {loading && <LoadingBar />}

                {previewUrl && (
                    <div style={{ marginTop: "1rem" }}>
                        <img
                            src={previewUrl}
                            alt="Preview"
                            style={{ maxWidth: "300px", maxHeight: "300px", border: "1px solid #ccc" }}
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

            {/* Right Panel — Translation Log */}
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