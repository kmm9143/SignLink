// DESCRIPTION:  This React component streams webcam video, sends frames to a backend WebSocket server,
//               and displays both annotated output (drawn on canvas) and live predictions of ASL signs.
//               It maintains the connection state, handles cleanup on unmount, and shows the top prediction.
// LANGUAGE:     JAVASCRIPT / React (hooks, WebSocket API, HTML5 video & canvas)

import React, { useEffect, useRef, useState } from "react";

const WebcamTranslator = () => {
    // -----------------------------------------------------------------------------------
    // References & State
    // -----------------------------------------------------------------------------------
    const videoRef = useRef(null);       // DOM ref for webcam video element
    const canvasRef = useRef(null);      // DOM ref for annotated canvas
    const wsRef = useRef(null);          // WebSocket connection reference
    const [prediction, setPrediction] = useState(null);  // latest prediction from backend
    const [setConnected] = useState(false);              // connection status (true/false)

    // -----------------------------------------------------------------------------------
    // Effect: Start webcam & establish WebSocket connection on mount
    // -----------------------------------------------------------------------------------
    useEffect(() => {
        // Request webcam access
        const startWebcam = async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                if (videoRef.current) videoRef.current.srcObject = stream;
            } catch (err) {
                console.error("Webcam access denied:", err);
            }
        };
        startWebcam();

        // Connect to backend WebSocket server
        const ws = new WebSocket("ws://localhost:8000/webcam/ws");
        wsRef.current = ws;

        // Handle open/close events
        ws.onopen = () => {
            setConnected(true);
            console.log("[WS] Connected");
        };
        ws.onclose = () => {
            setConnected(false);
            console.log("[WS] Disconnected");
        };

        // Handle incoming messages (string JSON or binary image frames)
        ws.onmessage = (event) => {
            if (typeof event.data === "string") {
                // Text → JSON prediction
                try {
                    const msg = JSON.parse(event.data);
                    if (msg.prediction) setPrediction(msg.prediction);
                } catch {
                    // Ignore malformed messages
                }
            } else {
                // Binary → annotated frame (image blob)
                const img = new Image();
                img.onload = () => {
                    const ctx = canvasRef.current.getContext("2d");
                    ctx.drawImage(img, 0, 0, canvasRef.current.width, canvasRef.current.height);
                    URL.revokeObjectURL(img.src);
                };
                img.src = URL.createObjectURL(event.data);
            }
        };

        // Cleanup on unmount: close socket + stop webcam tracks
        return () => {
            if (wsRef.current) wsRef.current.close();
            if (videoRef.current && videoRef.current.srcObject) {
                const tracks = videoRef.current.srcObject.getTracks();
                tracks.forEach((t) => t.stop());
            }
        };
    }, []);

    // -----------------------------------------------------------------------------------
    // Effect: Periodically send frames to backend (every 500ms)
    // -----------------------------------------------------------------------------------
    useEffect(() => {
        const interval = setInterval(() => {
            if (videoRef.current && wsRef.current?.readyState === WebSocket.OPEN) {
                // Draw current video frame to an offscreen canvas
                const canvas = document.createElement("canvas");
                canvas.width = videoRef.current.videoWidth || 640;
                canvas.height = videoRef.current.videoHeight || 480;
                const ctx = canvas.getContext("2d");
                ctx.drawImage(videoRef.current, 0, 0);
                // Convert to compressed JPEG data URL and send
                const dataUrl = canvas.toDataURL("image/jpeg", 0.6);
                wsRef.current.send(dataUrl);
            }
        }, 500);

        return () => clearInterval(interval);
    }, []);

    // -----------------------------------------------------------------------------------
    // Helper: Render top prediction (class + confidence)
    // -----------------------------------------------------------------------------------
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

    // -----------------------------------------------------------------------------------
    // Inline Styles for layout (side-by-side video & canvas)
    // -----------------------------------------------------------------------------------
    const rowStyle = {
        display: "flex",
        flexDirection: "row",
        gap: "24px",
        alignItems: "flex-start",
        flexWrap: "nowrap",       // keep side-by-side layout
        overflowX: "auto",        // allow horizontal scroll on smaller screens
    };
    const paneStyle = {
        flex: "0 0 auto",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
    };
    const mediaStyle = {
        width: "640px",
        height: "480px",
        borderRadius: "8px",
        border: "1px solid #ddd",
        objectFit: "cover",
        background: "#000",
    };

    // -----------------------------------------------------------------------------------
    // Render UI: Webcam feed, annotated output, and prediction text
    // -----------------------------------------------------------------------------------
    return (
        <div style={{ padding: "16px" }}>
            <div style={rowStyle}>
                {/* Webcam Input */}
                <div style={paneStyle}>
                    <h3 style={{ margin: "0 0 8px 0", fontWeight: 600 }}>Webcam Input</h3>
                    <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        style={mediaStyle}
                    />
                </div>

                {/* Annotated Output */}
                <div style={paneStyle}>
                    <h3 style={{ margin: "0 0 8px 0", fontWeight: 600 }}>Annotated Output</h3>
                    <canvas
                        ref={canvasRef}
                        width={640}
                        height={480}
                        style={{ ...mediaStyle, display: "block" }}
                    />
                </div>
            </div>

            {/* Prediction (below video/canvas) */}
            <div style={{ marginTop: "16px" }}>
                <strong>Prediction:</strong> {renderPrediction()}
            </div>
        </div>
    );
};

export default WebcamTranslator;