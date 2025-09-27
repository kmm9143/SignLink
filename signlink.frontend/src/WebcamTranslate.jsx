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
                } catch (e) {
                    console.warn("Non-JSON message:", event.data);
                }
            } else {
                // Annotated frame as binary → show in canvas
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

                // Convert to base64 and send
                const dataUrl = canvas.toDataURL("image/jpeg", 0.6); // compress for speed
                wsRef.current.send(dataUrl);
            }
        }, 500); // adjustable frequency

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="p-4">
            <h2 className="text-lg font-bold mb-2">Live ASL Translator</h2>
            <video ref={videoRef} autoPlay playsInline className="hidden" />
            <canvas ref={canvasRef} width={640} height={480} className="border rounded" />
            <div className="mt-2">
                <p>Status: {connected ? "🟢 Connected" : "🔴 Disconnected"}</p>
                <p>Prediction: {prediction ? JSON.stringify(prediction) : "None"}</p>
            </div>
        </div>
    );
};

export default WebcamTranslator;
