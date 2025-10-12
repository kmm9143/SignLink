// DESCRIPTION:   React component that enables real-time ASL translation
//                using webcam input. It streams video frames to a backend
//                WebSocket, receives predictions and annotated frames,
//                and optionally outputs speech using Text-to-Speech.
// LANGUAGE:      JAVASCRIPT (React.js)
// SOURCE(S):     
//    [1] React Docs. (n.d.). Using the Effect Hook. Retrieved October 5, 2025, from https://react.dev/reference/react/useEffect
//    [2] React Docs. (n.d.). Refs and the DOM. Retrieved October 5, 2025, from https://react.dev/reference/react/useRef
//    [3] MDN Web Docs. (n.d.). MediaDevices.getUserMedia(). Retrieved October 5, 2025, from https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
//    [4] MDN Web Docs. (n.d.). WebSocket API. Retrieved October 5, 2025, from https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

// -----------------------------------------------------------------------------
// Step 1: Import dependencies and helper modules
// -----------------------------------------------------------------------------
import React, { useEffect, useRef, useState } from "react"; // React core and hooks
import { speak } from './utils/speech.js';                 // Local TTS utility

// -----------------------------------------------------------------------------
// Step 2: Define WebcamTranslator component
// -----------------------------------------------------------------------------
const WebcamTranslator = ({ userId = 1 }) => {

    // -------------------------------------------------------------------------
    // Step 3: Define refs and state variables
    // -------------------------------------------------------------------------
    const videoRef = useRef(null);      // Reference to video element
    const canvasRef = useRef(null);     // Reference to canvas element
    const wsRef = useRef(null);         // Reference to WebSocket connection

    const [prediction, setPrediction] = useState(null); // Latest prediction
    const [connected, setConnected] = useState(false);  // WebSocket connection state
    const [settings, setSettings] = useState(null);     // User settings from backend

    // -------------------------------------------------------------------------
    // Step 4: Fetch user settings from backend
    // -------------------------------------------------------------------------
    useEffect(() => {
        const fetchSettings = async () => {
            try {
                const res = await fetch(`http://localhost:8000/settings/${userId}`);
                if (res.ok) {
                    const data = await res.json();
                    setSettings(data); // Store fetched settings
                } else {
                    console.warn("No settings found, defaulting to disabled webcam and speech.");
                    setSettings({ WEBCAM_ENABLED: false, SPEECH_ENABLED: false });
                }
            } catch (err) {
                console.error("Error fetching settings:", err);
                setSettings({ WEBCAM_ENABLED: false, SPEECH_ENABLED: false });
            }
        };
        fetchSettings();
    }, [userId]);

    // -------------------------------------------------------------------------
    // Step 5: Setup webcam stream and WebSocket connection
    // -------------------------------------------------------------------------
    useEffect(() => {
        if (!settings?.WEBCAM_ENABLED) return;

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

        const ws = new WebSocket("ws://localhost:8000/webcam/ws");
        wsRef.current = ws;

        ws.onopen = () => { setConnected(true); console.log("[WS] Connected"); };
        ws.onclose = () => { setConnected(false); console.log("[WS] Disconnected"); };
        ws.onmessage = (event) => {
            if (typeof event.data === "string") {
                try {
                    const msg = JSON.parse(event.data);
                    if (msg.prediction) setPrediction(msg.prediction);
                } catch { }
            } else {
                const img = new Image();
                img.onload = () => {
                    const ctx = canvasRef.current.getContext("2d");
                    ctx.drawImage(img, 0, 0, canvasRef.current.width, canvasRef.current.height);
                    URL.revokeObjectURL(img.src);
                };
                img.src = URL.createObjectURL(event.data);
            }
        };

        return () => {
            if (wsRef.current) wsRef.current.close();               // Close WebSocket
            if (stream) stream.getTracks().forEach((t) => t.stop()); // Stop webcam tracks
        };
    }, [settings]);

    // -------------------------------------------------------------------------
    // Step 6: Periodically capture webcam frames and send to backend
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
                const dataUrl = canvas.toDataURL("image/jpeg", 0.6);
                wsRef.current.send(dataUrl);
            }
        }, 500);

        return () => clearInterval(interval);
    }, [settings]);

    // -------------------------------------------------------------------------
    // Step 7: Trigger Text-to-Speech for top prediction
    // -------------------------------------------------------------------------
    useEffect(() => {
        if (!settings?.SPEECH_ENABLED || !prediction) return;

        try {
            const parsed = Array.isArray(prediction) ? prediction[0] : prediction;
            const preds = parsed?.predictions?.predictions || [];
            if (preds.length === 0) return;
            const top = preds[0];
            speak(`${top.class}`);
        } catch {
            console.warn("Failed to parse prediction for speech output.");
        }
    }, [prediction, settings]);

    // -------------------------------------------------------------------------
    // Step 8: Format prediction text for display
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
    // Step 9: Render component UI
    // -------------------------------------------------------------------------
    if (!settings) return <div>Loading settings...</div>;
    if (!settings.WEBCAM_ENABLED) return <div>⚠️ Webcam is disabled in your settings.</div>;

    return (
        <div style={{ padding: "16px" }}>
            <div style={{ display: "flex", gap: "24px" }}>
                <div>
                    <h3>Webcam Input</h3>
                    <video ref={videoRef} autoPlay playsInline style={{ width: 640, height: 480, background: "#000" }} />
                </div>
                <div>
                    <h3>Annotated Output</h3>
                    <canvas ref={canvasRef} width={640} height={480} style={{ width: 640, height: 480, background: "#000" }} />
                </div>
            </div>
            <div style={{ marginTop: "16px" }}>
                <strong>Prediction:</strong> {renderPrediction()}
            </div>
        </div>
    );
};

export default WebcamTranslator;
