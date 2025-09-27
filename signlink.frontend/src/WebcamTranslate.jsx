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
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                }
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
                    if (msg.prediction) {
                        setPrediction(msg.prediction);
                    }
                } catch {
                    console.warn("Non-JSON message:", event.data);
                }
            } else {
                const img = new Image();
                img.onload = () => {
                    const ctx = canvasRef.current.getContext("2d");
                    ctx.drawImage(img, 0, 0, canvasRef.current.width, canvasRef.current.height);
                };
                img.src = URL.createObjectURL(event.data);
            }
        };

        return () => {
            if (wsRef.current) wsRef.current.close();
        };
    }, []);

    // Send frame every 500ms
    useEffect(() => {
        const interval = setInterval(() => {
            if (videoRef.current && wsRef.current?.readyState === WebSocket.OPEN) {
                const canvas = document.createElement("canvas");
                canvas.width = videoRef.current.videoWidth;
                canvas.height = videoRef.current.videoHeight;
                const ctx = canvas.getContext("2d");
                ctx.drawImage(videoRef.current, 0, 0);

                const dataUrl = canvas.toDataURL("image/jpeg", 0.6);
                wsRef.current.send(dataUrl);
            }
        }, 500);

        return () => clearInterval(interval);
    }, []);

    // Helper to format prediction
    const renderPrediction = () => {
        if (!prediction) return "None";

        try {
            const parsed = Array.isArray(prediction) ? prediction[0] : prediction;
            const preds = parsed?.predictions?.predictions || [];
            if (preds.length === 0) return "No hand detected";

            const top = preds[0]; // take highest confidence
            return `${top.class} (${(top.confidence * 100).toFixed(1)}%)`;
        } catch {
            return "Invalid prediction format";
        }
    };

    return (
        <div className="p-4">
            <h2 className="text-lg font-bold mb-2">Live ASL Translator</h2>
            <video ref={videoRef} autoPlay playsInline className="hidden" />
            <canvas ref={canvasRef} width={640} height={480} className="border rounded" />
            <div className="mt-2">
                <p>Prediction: {renderPrediction()}</p>
            </div>
        </div>
    );
};

export default WebcamTranslator;
