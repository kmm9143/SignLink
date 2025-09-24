import { useEffect, useRef, useState } from "react";
import { Hands } from "@mediapipe/hands";

export default function WebcamTranslate() {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [prediction, setPrediction] = useState(null);
    const intervalIdRef = useRef(null);
    const handPresentRef = useRef(false);

    useEffect(() => {
        let ws;
        let hands;
        let animationId;

        const setupWebSocket = () => {
            ws = new WebSocket("ws://127.0.0.1:8000/webcam/ws");
            ws.binaryType = "arraybuffer";
            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    setPrediction(data.prediction);
                } catch {
                    const blob = new Blob([event.data], { type: "image/jpeg" });
                    const url = URL.createObjectURL(blob);
                    const img = new Image();
                    img.onload = () => {
                        const canvas = canvasRef.current;
                        const ctx = canvas.getContext("2d");
                        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                        URL.revokeObjectURL(url);
                    };
                    img.src = url;
                }
            };
            ws.onclose = () => console.log("WebSocket closed");
        };

        const startVideo = async () => {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            videoRef.current.srcObject = stream;
            videoRef.current.onloadedmetadata = () => {
                videoRef.current.play();
            };
        };

        const sendFrame = () => {
            if (videoRef.current && ws.readyState === WebSocket.OPEN) {
                const canvas = document.createElement("canvas");
                canvas.width = videoRef.current.videoWidth;
                canvas.height = videoRef.current.videoHeight;
                const ctx = canvas.getContext("2d");
                ctx.drawImage(videoRef.current, 0, 0);
                canvas.toBlob((blob) => {
                    if (blob) ws.send(blob);
                }, "image/jpeg");
            }
        };

        const updateInterval = (handPresent) => {
            if (handPresent && !intervalIdRef.current) {
                intervalIdRef.current = setInterval(sendFrame, 1000);
            } else if (!handPresent && intervalIdRef.current) {
                clearInterval(intervalIdRef.current);
                intervalIdRef.current = null;
            }
        };

        hands = new Hands({
            locateFile: (file) =>
                `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
        });
        hands.setOptions({
            maxNumHands: 1,
            modelComplexity: 1,
            minDetectionConfidence: 0.7,
            minTrackingConfidence: 0.7,
        });

        hands.onResults((results) => {
            const handPresent = results.multiHandLandmarks && results.multiHandLandmarks.length > 0;
            if (handPresentRef.current !== handPresent) {
                handPresentRef.current = handPresent;
                updateInterval(handPresent);
            }
        });

        const detectHand = async () => {
            const canvas = document.createElement("canvas");
            const video = videoRef.current;
            if (video && video.videoWidth > 0 && video.videoHeight > 0) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext("2d");
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                await hands.send({ image: canvas });
            }
            animationId = requestAnimationFrame(detectHand);
        };

        setupWebSocket();
        startVideo();
        detectHand();

        return () => {
            if (ws) ws.close();
            if (intervalIdRef.current) clearInterval(intervalIdRef.current);
            if (animationId) cancelAnimationFrame(animationId);
        };
    }, []);

    return (
        <div style={{ padding: "2rem" }}>
            <video ref={videoRef} width={640} height={480} autoPlay style={{ display: "block", marginBottom: "1rem" }} />
            <canvas ref={canvasRef} width={640} height={480} style={{ border: "1px solid black" }} />
            {prediction && (
                <div style={{ marginTop: "1rem" }}>
                    <h3>Prediction:</h3>
                    <pre>{JSON.stringify(prediction, null, 2)}</pre>
                </div>
            )}
        </div>
    );
}
