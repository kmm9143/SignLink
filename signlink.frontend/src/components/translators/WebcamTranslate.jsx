import React from "react";
import SpeakerIcon from "../common/SpeakerIcon.jsx";
import useUserSettings from "../../hooks/useUserSettings";
import useSpeech from "../../hooks/useSpeech";
import TranslatorLayout from "./shared/TranslatorLayout.jsx";
import useWebcamStreamer from "../../hooks/useWebcamStreamer";

/**
 * WebcamTranslate refactored:
 * - Streamer logic extracted to useWebcamStreamer hook (SRP, DIP)
 * - Component focuses on rendering and speech behavior
 */
export default function WebcamTranslate({ userId = 1 }) {
    const settings = useUserSettings(userId);
    const { speaking, speakText } = useSpeech(settings);

    const { videoRef, canvasRef, connected, prediction } = useWebcamStreamer({
        wsUrl: "ws://localhost:8000/webcam/ws",
        enabled: !!(settings?.WEBCAM_ENABLED),
        sendIntervalMs: 500,
    });

    // speak when new prediction arrives
    React.useEffect(() => {
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
        // intentionally omit speakText from deps to avoid loops
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [prediction, settings?.SPEECH_ENABLED]);

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

    if (!settings) return <div>Loading settings...</div>;
    if (!settings.WEBCAM_ENABLED) return <div>⚠️ Webcam is disabled in your settings.</div>;

    const left = (
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

            <div style={{ marginTop: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
                <strong>Prediction:</strong> {renderPrediction()}
                <SpeakerIcon enabled={settings?.SPEECH_ENABLED} speaking={speaking} size={22} />
                <div style={{ marginLeft: "12px", color: connected ? "lightgreen" : "gray" }}>{connected ? "Connected" : "Disconnected"}</div>
            </div>
        </div>
    );

    return <TranslatorLayout left={left} />;
}