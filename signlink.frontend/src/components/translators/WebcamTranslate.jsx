import React, { useState, useEffect, useRef } from "react";
import SpeakerIcon from "../common/SpeakerIcon.jsx";
import useUserSettings from "../../hooks/useUserSettings";
import useSpeech from "../../hooks/useSpeech";
import TranslatorLayout from "./shared/TranslatorLayout.jsx";
import useWebcamStreamer from "../../hooks/useWebcamStreamer";

export default function WebcamTranslate({ userId = 1 }) {
    const settings = useUserSettings(userId);
    const { speaking, speakText } = useSpeech(settings);
    const { videoRef, canvasRef, connected, prediction } = useWebcamStreamer({
        wsUrl: "ws://localhost:8000/webcam/ws",
        enabled: !!settings?.WEBCAM_ENABLED,
        sendIntervalMs: 500,
    });

    const [recording, setRecording] = useState(false);
    const [recordedLog, setRecordedLog] = useState([]);
    const bufferRef = useRef([]);

    const [showSaveModal, setShowSaveModal] = useState(false);
    const [pendingTranscript, setPendingTranscript] = useState("");
    const [serverError, setServerError] = useState(false);

    // 🕓 Give connection time before showing error
    useEffect(() => {
        const timer = setTimeout(() => {
            if (!connected) setServerError(true);
        }, 3000); // waits 3s before deciding it failed
        return () => clearTimeout(timer);
    }, [connected]);

    // Handle incoming predictions + recording
    useEffect(() => {
        if (!prediction) return;
        try {
            const parsed = Array.isArray(prediction) ? prediction[0] : prediction;
            const preds = parsed?.predictions?.predictions || [];
            if (preds.length === 0) return;

            const top = preds[0];
            if (settings?.SPEECH_ENABLED) speakText(top.class);

            if (recording && top?.class) {
                bufferRef.current.push(top.class);
            }
        } catch (err) {
            console.warn("Speech/record buffer error:", err);
        }
    }, [prediction, recording, settings?.SPEECH_ENABLED]);

    const handleStartRecording = () => {
        bufferRef.current = [];
        setRecording(true);
    };

    const handleStopRecording = () => {
        setRecording(false);
        const combined = bufferRef.current.join("");
        bufferRef.current = [];
        if (!combined) return;
        setPendingTranscript(combined);
        setShowSaveModal(true);
    };

    const saveTranscript = async () => {
        try {
            await fetch("http://localhost:8000/translations/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_id: userId,
                    input_type: "webcam",
                    recognized_text: pendingTranscript,
                }),
            });

            const timestamp = new Date().toLocaleString();
            setRecordedLog((prev) => {
                const newEntry = { text: pendingTranscript, timestamp };
                const updated = [newEntry, ...prev].slice(0, 3);
                return updated;
            });
        } catch (err) {
            console.warn("Failed to save webcam translation:", err);
        } finally {
            setShowSaveModal(false);
            setPendingTranscript("");
        }
    };

    const renderPrediction = () => {
        if (!prediction) return "None";
        try {
            const parsed = Array.isArray(prediction) ? prediction[0] : prediction;
            const preds = parsed?.predictions?.predictions || [];
            if (preds.length === 0) return "No hand detected";
            const top = preds[0];
            return `${top.class} (${(top.confidence * 100).toFixed(1)}%)`;
        } catch {
            return "Invalid prediction format";
        }
    };

    if (!settings) return <div>Loading settings...</div>;
    if (!settings.WEBCAM_ENABLED)
        return <div>⚠️ Webcam is disabled in your settings.</div>;

    // ✅ If server connection fails after retry window
    if (serverError && !connected) {
        return (
            <div style={{ color: "red", textAlign: "center", padding: "24px" }}>
                <h3>Server error. Please try again later.</h3>
            </div>
        );
    }

    const left = (
        <div style={{ padding: "16px" }}>
            <div style={{ display: "flex", gap: "24px" }}>
                <div>
                    <h3>Webcam Input</h3>
                    <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        style={{ width: 640, height: 480, background: "#000" }}
                    />
                </div>
                <div>
                    <h3>Annotated Output</h3>
                    <canvas
                        ref={canvasRef}
                        width={640}
                        height={480}
                        style={{ width: 640, height: 480, background: "#000" }}
                    />
                </div>
            </div>

            <div style={{ marginTop: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
                <strong>Prediction:</strong> {renderPrediction()}
                <SpeakerIcon enabled={settings?.SPEECH_ENABLED} speaking={speaking} size={22} />
                <div style={{ marginLeft: "12px", color: connected ? "lightgreen" : "gray" }}>
                    {connected ? "Connected" : "Connecting..."}
                </div>
            </div>

            <div style={{ marginTop: "24px", display: "flex", alignItems: "center", gap: "12px" }}>
                {!recording ? (
                    <button
                        onClick={handleStartRecording}
                        style={{
                            padding: "8px 16px",
                            background: "#2ecc71",
                            color: "#fff",
                            border: "none",
                            borderRadius: "6px",
                            cursor: "pointer",
                        }}
                    >
                        🎙️ Start Recording Transcript
                    </button>
                ) : (
                    <button
                        onClick={handleStopRecording}
                        style={{
                            padding: "8px 16px",
                            background: "#e74c3c",
                            color: "#fff",
                            border: "none",
                            borderRadius: "6px",
                            cursor: "pointer",
                        }}
                    >
                        ⏹️ Stop Recording Transcript
                    </button>
                )}
                {recording && <span style={{ color: "red" }}>Recording...</span>}
            </div>

            {recordedLog.length > 0 && (
                <div style={{ marginTop: "24px" }}>
                    <h4>Recent Webcam Translations (max 3):</h4>
                    {recordedLog.map((entry, idx) => (
                        <div
                            key={idx}
                            style={{
                                marginBottom: "8px",
                                background: "#222",
                                padding: "8px",
                                borderRadius: "4px",
                            }}
                        >
                            <div style={{ color: "#bbb", fontSize: "0.8em" }}>{entry.timestamp}</div>
                            <div style={{ color: "#fff", fontWeight: "bold" }}>{entry.text}</div>
                        </div>
                    ))}
                </div>
            )}

            {showSaveModal && (
                <div
                    style={{
                        position: "fixed",
                        top: 0,
                        left: 0,
                        width: "100%",
                        height: "100%",
                        backgroundColor: "rgba(0,0,0,0.5)",
                        display: "flex",
                        justifyContent: "center",
                        alignItems: "center",
                        zIndex: 1000,
                    }}
                >
                    <div
                        style={{
                            background: "#222",
                            padding: "24px",
                            borderRadius: "8px",
                            textAlign: "center",
                            maxWidth: "400px",
                            color: "#fff",
                        }}
                    >
                        <h3>Save Transcript?</h3>
                        <p
                            style={{
                                wordBreak: "break-word",
                                background: "#111",
                                padding: "8px",
                                borderRadius: "6px",
                            }}
                        >
                            {pendingTranscript}
                        </p>
                        <div style={{ marginTop: "16px" }}>
                            <button
                                onClick={saveTranscript}
                                style={{
                                    marginRight: "12px",
                                    padding: "8px 16px",
                                    background: "#2ecc71",
                                    border: "none",
                                    borderRadius: "6px",
                                    color: "#fff",
                                    cursor: "pointer",
                                }}
                            >
                                ✅ Save
                            </button>
                            <button
                                onClick={() => setShowSaveModal(false)}
                                style={{
                                    padding: "8px 16px",
                                    background: "#e74c3c",
                                    border: "none",
                                    borderRadius: "6px",
                                    color: "#fff",
                                    cursor: "pointer",
                                }}
                            >
                                ❌ Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );

    return <TranslatorLayout left={left} />;
}
