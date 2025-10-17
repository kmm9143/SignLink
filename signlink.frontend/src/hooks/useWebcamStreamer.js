import { useEffect, useRef, useState } from "react";

/**
 * useWebcamStreamer
 * - Manages camera access, websocket connection, frame sending and incoming messages.
 * - Returns refs for <video> and <canvas>, prediction data, connected flag, and stop() to force shutdown.
 *
 * Options:
 *  - wsUrl: websocket URL
 *  - enabled: boolean
 *  - sendIntervalMs: frame send interval (default 500)
 */
export default function useWebcamStreamer({ wsUrl = "ws://localhost:8000/webcam/ws", enabled = false, sendIntervalMs = 500 } = {}) {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const wsRef = useRef(null);
    const streamRef = useRef(null);
    const intervalRef = useRef(null);

    const [connected, setConnected] = useState(false);
    const [prediction, setPrediction] = useState(null);
    const [annotatedUrl, setAnnotatedUrl] = useState(null);

    useEffect(() => {
        if (!enabled) return;

        let mounted = true;

        const start = async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                streamRef.current = stream;
                if (videoRef.current) videoRef.current.srcObject = stream;
            } catch (err) {
                console.error("Webcam access denied:", err);
            }

            const ws = new WebSocket(wsUrl);
            wsRef.current = ws;

            ws.onopen = () => {
                if (!mounted) return;
                setConnected(true);
            };

            ws.onclose = () => {
                if (!mounted) return;
                setConnected(false);
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
                    // binary annotated frame
                    const blob = event.data;
                    // revoke previous annotatedUrl
                    if (annotatedUrl) {
                        URL.revokeObjectURL(annotatedUrl);
                    }
                    const url = URL.createObjectURL(blob);
                    setAnnotatedUrl(url);
                }
            };

            // send frames periodically
            intervalRef.current = setInterval(() => {
                if (!videoRef.current || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
                const canvas = document.createElement("canvas");
                canvas.width = videoRef.current.videoWidth || 640;
                canvas.height = videoRef.current.videoHeight || 480;
                const ctx = canvas.getContext("2d");
                ctx.drawImage(videoRef.current, 0, 0);
                try {
                    wsRef.current.send(canvas.toDataURL("image/jpeg", 0.6));
                } catch (err) {
                    console.warn("Failed to send frame", err);
                }
            }, sendIntervalMs);
        };

        start();

        return () => {
            mounted = false;
            if (intervalRef.current) clearInterval(intervalRef.current);
            if (wsRef.current) {
                try { wsRef.current.close(); } catch { }
                wsRef.current = null;
            }
            if (streamRef.current) {
                streamRef.current.getTracks().forEach((t) => t.stop());
                streamRef.current = null;
            }
            if (annotatedUrl) {
                URL.revokeObjectURL(annotatedUrl);
            }
        };
        // intentionally ignore annotatedUrl in deps to avoid tearing down on each frame
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [enabled, wsUrl, sendIntervalMs]);

    // allow consumer to draw annotatedUrl into provided canvasRef if desired
    useEffect(() => {
        if (!annotatedUrl || !canvasRef.current) return;
        const img = new Image();
        img.onload = () => {
            const ctx = canvasRef.current.getContext("2d");
            canvasRef.current.width = img.width;
            canvasRef.current.height = img.height;
            ctx.drawImage(img, 0, 0, canvasRef.current.width, canvasRef.current.height);
            URL.revokeObjectURL(img.src);
        };
        img.src = annotatedUrl;
    }, [annotatedUrl]);

    const stop = () => {
        if (intervalRef.current) clearInterval(intervalRef.current);
        if (wsRef.current) {
            try { wsRef.current.close(); } catch { }
            wsRef.current = null;
        }
        if (streamRef.current) {
            streamRef.current.getTracks().forEach((t) => t.stop());
            streamRef.current = null;
        }
        if (annotatedUrl) {
            URL.revokeObjectURL(annotatedUrl);
        }
        setConnected(false);
    };

    return {
        videoRef,
        canvasRef,
        connected,
        prediction,
        annotatedUrl,
        stop,
    };
}