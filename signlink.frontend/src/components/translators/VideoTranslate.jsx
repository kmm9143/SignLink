import React, { useState } from "react";
import SpeakerIcon from "../common/SpeakerIcon.jsx";
import useUserSettings from "../../hooks/useUserSettings";
import useSpeech from "../../hooks/useSpeech";
import usePredictionAPI from "../../hooks/usePredictionAPI";

import TranslatorLayout from "./shared/TranslatorLayout.jsx";
import UploadPanel from "./shared/UploadPanel.jsx";
import PredictionList from "./shared/PredictionList.jsx";
import TranslationLog from "./shared/TranslationLog.jsx";
import { parseVideoPredictions } from "../../services/parsers";

/**
 * VideoTranslate refactored:
 * - parser moved to parsers service
 * - UI uses shared components
 */
export default function VideoTranslate({ userId = 1 }) {
    const settings = useUserSettings(userId);
    const { speaking, speakText } = useSpeech(settings);

    const { sendFile, predictions, loading, error } = usePredictionAPI("/video/translate", parseVideoPredictions);

    const [file, setFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [progress, setProgress] = useState(null);
    const [log, setLog] = useState([]);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files?.[0];
        if (!selectedFile) {
            setFile(null);
            setPreviewUrl(null);
            return;
        }

        const validTypes = ["video/mp4", "video/avi", "video/mov", "video/mpeg"];
        if (!validTypes.includes(selectedFile.type)) {
            alert("Invalid file type. Please upload an MP4, MOV, or AVI video.");
            setFile(null);
            setPreviewUrl(null);
            return;
        }

        setFile(selectedFile);
        setPreviewUrl(URL.createObjectURL(selectedFile));
    };

    const handleSubmit = async () => {
        if (!file) return alert("Please select a video first.");
        setProgress(0);
        const preds = await sendFile(file, (event) => {
            if (event.total) {
                const percent = Math.round((event.loaded * 100) / event.total);
                setProgress(percent);
            }
        });

        if (settings?.SPEECH_ENABLED && preds?.length > 0) {
            const combinedText = preds.map((p) => p.label).join(" ");
            speakText(combinedText);
        }

        setLog((prevLog) => {
            const newEntry = { videoUrl: previewUrl, predictions: preds, timestamp: new Date().toLocaleString(), fileName: file.name || "prediction.mp4" };
            return [newEntry, ...prevLog].slice(0, 3);
        });

        setProgress(null);
    };

    const downloadLog = (entry) => {
        const text = entry.predictions.map((p) => `Frame ${p.frame}: ${p.label} (${(p.confidence * 100).toFixed(1)}%)`).join("\n");
        const blob = new Blob([text], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        const name = entry.fileName.endsWith(".mp4") ? entry.fileName.replace(/\.mp4$/i, ".txt") : entry.fileName + ".txt";
        link.download = name;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };

    if (!settings) return <div>Loading user settings...</div>;

    const left = (
        <>
            {/* Pass renderPreview so UploadPanel renders a video element (not an <img>) */}
            <UploadPanel
                accept="video/*"
                previewUrl={previewUrl}
                loading={loading}
                progress={progress}
                onFileChange={handleFileChange}
                onSubmit={handleSubmit}
                submitLabel="Translate"
                disabled={!file}
                renderPreview={(url) => (
                    <div style={{ marginTop: "1rem" }}>
                        <video src={url} controls style={{ maxWidth: "400px", border: "1px solid #ccc" }} />
                    </div>
                )}
            >
                <SpeakerIcon enabled={settings?.SPEECH_ENABLED} speaking={speaking} size={22} style={{ marginLeft: "1rem" }} />
                {error && <p style={{ color: "red" }}>{error}</p>}

                <PredictionList
                    predictions={predictions}
                    renderItem={(p, i) => {
                        const lowConfidence = p.confidence < 0.5;
                        return (
                            <div key={i} style={{ color: lowConfidence ? "red" : "white", fontWeight: "bold" }}>
                                Frame {p.frame}: {p.label} ({(p.confidence * 100).toFixed(1)}%)
                                {lowConfidence && " — Low confidence"}
                            </div>
                        );
                    }}
                />
            </UploadPanel>
        </>
    );

    const right = (
        <TranslationLog
            log={log}
            onClear={() => setLog([])}
            renderEntry={(entry) => (
                <>
                    <video src={entry.videoUrl} controls style={{ width: "100%", borderRadius: "6px", marginBottom: "0.4rem" }} />
                    <div style={{ fontSize: "0.8em", color: "#bbb", marginBottom: "0.5rem" }}>{entry.timestamp}</div>
                    <div style={{ flexGrow: 1, overflowY: "auto", minHeight: "160px", maxHeight: "220px", borderTop: "1px solid #444", paddingTop: "0.5rem" }}>
                        {entry.predictions?.map((p, i) => (
                            <div key={i} style={{ color: p.confidence < 0.5 ? "red" : "white" }}>
                                Frame {p.frame}: {p.label} ({(p.confidence * 100).toFixed(1)}%)
                                {p.confidence < 0.5 && " — Low confidence"}
                            </div>
                        ))}
                    </div>
                    <button onClick={() => downloadLog(entry)} style={{ marginTop: "0.5rem", padding: "4px 8px", background: "#1976d2", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}>Download Transcript</button>
                </>
            )}
            containerStyle={{ minWidth: "540px", maxWidth: "1100px" }}
        />
    );

    return <TranslatorLayout left={left} right={right} />;
}