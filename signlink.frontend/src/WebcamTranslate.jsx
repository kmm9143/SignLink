import { useEffect, useRef, useState } from "react";

export default function WebcamTranslate() {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [prediction, setPrediction] = useState(null);

    useEffect(() => {
        const ws = new WebSocket("ws://127.0.0.1:8000/webcam/ws");

        ws.binaryType = "arraybuffer";

        ws.onmessage = (event) => {
            // Try parsing JSON, otherwise assume frame
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

        const startVideo = async () => {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            videoRef.current.srcObject = stream;
            videoRef.current.play();

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
                requestAnimationFrame(sendFrame);
            };

            sendFrame();
        };

        startVideo();

        return () => ws.close();
    }, []);

    return (
        <div style={{ padding: "2rem" }}>
            <video ref={videoRef} style={{ display: "none" }} />
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
