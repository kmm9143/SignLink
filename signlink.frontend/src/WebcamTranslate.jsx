import React, { useEffect, useRef, useState } from "react";

const WebcamTranslator = () => {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const wsRef = useRef(null);
    const [prediction, setPrediction] = useState(null);
    const [connected, setConnected] = useState(false);

    useEffect(() => {
        const startWebcam = async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
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
                } catch {
                    // ignore malformed text messages
                }
            } else {
                // binary annotated frame
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
            // stop webcam tracks when unmounting
            if (videoRef.current && videoRef.current.srcObject) {
                const tracks = videoRef.current.srcObject.getTracks();
                tracks.forEach((t) => t.stop());
            }
        };
    }, []);

    // Send frame every 500ms
    useEffect(() => {
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
    }, []);

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

    // Inline styles to force side-by-side layout regardless of global CSS
    const rowStyle = {
        display: "flex",
        flexDirection: "row",
        gap: "24px",
        alignItems: "flex-start",
        flexWrap: "nowrap",       // prevent wrapping into vertical stack
        overflowX: "auto",       // allow horizontal scroll on small screens
    };
    const paneStyle = {
        flex: "0 0 auto",        // don't shrink, fixed width set on children
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

            {/* Prediction below */}
            <div style={{ marginTop: "16px" }}>
                <strong>Prediction:</strong> {renderPrediction()}
            </div>
        </div>
    );
};

export default WebcamTranslator;
