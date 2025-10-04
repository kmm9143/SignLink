import React, { useEffect, useRef, useState } from "react";

const WebcamTranslator = ({ userId = 1 }) => {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const wsRef = useRef(null);

    const [prediction, setPrediction] = useState(null);
    const [connected, setConnected] = useState(false);
    const [settings, setSettings] = useState(null);

    // -----------------------------
    // Fetch settings
    // -----------------------------
    useEffect(() => {
        const fetchSettings = async () => {
            try {
                const res = await fetch(`http://localhost:8000/settings/${userId}`);
                if (res.ok) {
                    const data = await res.json();
                    setSettings(data);
                } else {
                    console.warn("No settings found, defaulting to disabled webcam.");
                    setSettings({ WEBCAM_ENABLED: false, SPEECH_ENABLED: false });
                }
            } catch (err) {
                console.error("Error fetching settings:", err);
                setSettings({ WEBCAM_ENABLED: false, SPEECH_ENABLED: false });
            }
        };
        fetchSettings();
    }, [userId]);

    // -----------------------------
    // Webcam + WebSocket setup
    // -----------------------------
    useEffect(() => {
        if (!settings || !settings.WEBCAM_ENABLED) {
            console.log("[Webcam] Disabled by settings");
            return;
        }

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
            if (wsRef.current) wsRef.current.close();
            if (stream) {
                stream.getTracks().forEach((t) => t.stop());
            }
        };
    }, [settings]);

    // -----------------------------
    // Frame sending loop
    // -----------------------------
    useEffect(() => {
        if (!settings || !settings.WEBCAM_ENABLED) return;
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

    // -----------------------------
    // Format prediction (same as before)
    // -----------------------------
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

    // -----------------------------
    // Render
    // -----------------------------
    if (!settings) {
        return <div>Loading settings...</div>;
    }

    if (!settings.WEBCAM_ENABLED) {
        return <div>⚠️ Webcam is disabled in your settings.</div>;
    }

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