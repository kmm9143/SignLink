import React, { useState } from "react";
import SpeakerIcon from "../common/SpeakerIcon.jsx";
import useUserSettings from "../../hooks/useUserSettings";
import useSpeech from "../../hooks/useSpeech";
import usePredictionAPI from "../../hooks/usePredictionAPI";

import TranslatorLayout from "./shared/TranslatorLayout.jsx";
import UploadPanel from "./shared/UploadPanel.jsx";
import PredictionList from "./shared/PredictionList.jsx";
import TranslationLog from "./shared/TranslationLog.jsx";
import { parseImagePredictions } from "../../services/parsers";

/**
 * ImageTranslate refactored:
 * - UI delegated to shared components
 * - Parsing delegated to parsers service
 * - Speech handled by useSpeech hook
 */
export default function ImageTranslate({ userId = 1 }) {
    const settings = useUserSettings(userId);
    const { speaking, speakText } = useSpeech(settings);

    const { sendFile, predictions, loading, error } = usePredictionAPI("/image/predict", parseImagePredictions);

    const [file, setFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [prediction, setPrediction] = useState(null);
    const [log, setLog] = useState([]);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files?.[0];
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
        <TranslatorLayout
            left={
                <>
                    <UploadPanel
                        accept="image/*"
                        previewUrl={previewUrl}
                        loading={loading}
                        onFileChange={handleFileChange}
                        onSubmit={handleSubmit}
                        submitLabel="Translate"
                        disabled={!file}
                    >
                        <SpeakerIcon enabled={settings?.SPEECH_ENABLED} speaking={speaking} size={22} style={{ marginLeft: "1rem" }} />
                        {error && <p style={{ color: "red" }}>{error}</p>}
                        {prediction && (
                            <div style={{ marginTop: "1rem" }}>
                                <h3>Prediction:</h3>
                                {renderPrediction(prediction)}
                            </div>
                        )}
                    </UploadPanel>
                </>
            }
            right={
                <TranslationLog
                    log={log}
                    onClear={handleClearLog}
                    renderEntry={(entry, idx) => (
                        <>
                            <div style={{ position: "relative", width: "100%", display: "flex", justifyContent: "center" }}>
                                <img src={entry.imageUrl} alt={`Log Preview ${idx + 1}`} style={{ maxWidth: "100%", maxHeight: "80px", display: "block", borderRadius: "4px" }} />
                                <button onClick={() => handleRemoveLogEntry(idx)} style={{ position: "absolute", top: "6px", right: "6px", background: "#e74c3c", color: "#fff", border: "none", borderRadius: "4px", padding: "2px 8px", cursor: "pointer", fontSize: "0.9em", boxShadow: "0 1px 4px rgba(0,0,0,0.15)" }} title="Remove this entry">✖</button>
                            </div>
                            <div style={{ fontSize: "0.8em", color: "#555", margin: "0.25rem 0" }}>{entry.timestamp}</div>
                            <div>{renderPrediction(entry.prediction)}</div>
                        </>
                    )}
                    containerStyle={{ minWidth: "540px", maxWidth: "600px" }}
                />
            }
        />
    );
}