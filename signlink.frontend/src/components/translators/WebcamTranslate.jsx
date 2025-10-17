// DESCRIPTION:   React component for real-time ASL translation via webcam.
//                Streams video to a backend WebSocket, receives predictions
//                and annotated frames, and optionally outputs speech (TTS)
//                with a visual speaker icon indicator.
// LANGUAGE:      JAVASCRIPT (React.js)

import React, { useEffect, useRef, useState } from "react";
import SpeakerIcon from "../common/SpeakerIcon.jsx";

// ✅ Import shared logic hooks
import useUserSettings from "../../hooks/useUserSettings";
import useSpeech from "../../hooks/useSpeech";

const WebcamTranslator = ({ userId = 1 }) => {
    // -------------------------------------------------------------------------
    // Refs for video, canvas, and WebSocket
    // -------------------------------------------------------------------------
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const wsRef = useRef(null);

    // -------------------------------------------------------------------------
    // State variables
    // -------------------------------------------------------------------------
    const [prediction, setPrediction] = useState(null);
    const [connected, setConnected] = useState(false);

    // ✅ Use reusable hooks
    const settings = useUserSettings(userId);
    const { speaking, speakText } = useSpeech(settings);

    // -------------------------------------------------------------------------
    // Setup webcam stream and WebSocket
    // -------------------------------------------------------------------------
    useEffect(() => {
        if (!settings || !settings.WEBCAM_ENABLED) return;

        let stream;
        const startWebcam = async () => {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ video: true });
                if (videoRef.current) videoRef.current.srcObject = stream;
            } catch (err) {
                console.error("Webcam access denied:", err);
            }
        };
        startWebcam();

        // Connect to backend WebSocket
        const ws = new WebSocket("ws://localhost:8000/webcam/ws");
        wsRef.current = ws;

        ws.onopen = () => {
            setConnected(true);
            console.log("[WS] Connected");
        };

        ws.onclose = () => {
            setConnected(false);
            console.log("[WS] Disconnected");
        };

        ws.onmessage = (event) => {
            if (typeof event.data === "string") {
                try {
                    const msg = JSON.parse(event.data);
                    if (msg.prediction) setPrediction(msg.prediction);
                } catch (err) {
                    console.warn("Invalid JSON from WebSocket:", err);
                }
            } else {
                // Binary frame data → draw annotated image
                const img = new Image();
                img.onload = () => {
                    const ctx = canvasRef.current.getContext("2d");
                    ctx.drawImage(img, 0, 0, canvasRef.current.width, canvasRef.current.height);
                    URL.revokeObjectURL(img.src);
                };
                img.src = URL.createObjectURL(event.data);
            }
        };

        // Cleanup WebSocket + video
        return () => {
            if (wsRef.current) wsRef.current.close();
            if (stream) stream.getTracks().forEach((t) => t.stop());
        };
    }, [settings?.WEBCAM_ENABLED]); // depends only on webcam setting

    // -------------------------------------------------------------------------
    // Periodically send frames to backend
    // -------------------------------------------------------------------------
    useEffect(() => {
        if (!settings?.WEBCAM_ENABLED) return;

        const interval = setInterval(() => {
            if (videoRef.current && wsRef.current?.readyState === WebSocket.OPEN) {
                const canvas = document.createElement("canvas");
                canvas.width = videoRef.current.videoWidth || 640;
                canvas.height = videoRef.current.videoHeight || 480;
                const ctx = canvas.getContext("2d");
                ctx.drawImage(videoRef.current, 0, 0);
                wsRef.current.send(canvas.toDataURL("image/jpeg", 0.6));
            }
        }, 500);

        return () => clearInterval(interval);
    }, [settings?.WEBCAM_ENABLED]);

    // -------------------------------------------------------------------------
    // Speech output for new predictions
    // -------------------------------------------------------------------------
    useEffect(() => {
        if (!settings?.SPEECH_ENABLED || !prediction) return;

        try {
            const parsed = Array.isArray(prediction) ? prediction[0] : prediction;
            const preds = parsed?.predictions?.predictions || [];
            if (preds.length === 0) return;
            const top = preds[0];
            speakText(top.class);
        } catch (err) {
            console.warn("Failed to process speech output:", err);
        }
    }, [prediction]); // ✅ intentionally omits speakText to avoid stale closure loops

    // -------------------------------------------------------------------------
    // Format prediction for display
    // -------------------------------------------------------------------------
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

    // -------------------------------------------------------------------------
    // Render UI (identical)
    // -------------------------------------------------------------------------
    if (!settings) return <div>Loading settings...</div>;
    if (!settings.WEBCAM_ENABLED) return <div>⚠️ Webcam is disabled in your settings.</div>;

    return (
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

            {/* Prediction display with speaker icon */}
            <div
                style={{
                    marginTop: "16px",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                }}
            >
                <strong>Prediction:</strong> {renderPrediction()}
                <SpeakerIcon
                    enabled={settings?.SPEECH_ENABLED}
                    speaking={speaking}
                    size={22}
                />
            </div>
        </div>
    );
};

export default WebcamTranslator;
