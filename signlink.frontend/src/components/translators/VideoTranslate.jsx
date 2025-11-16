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

export default function VideoTranslate({ userId = 1 }) {
    const settings = useUserSettings(userId);
    const { speaking, speakText } = useSpeech(settings);

    const { sendFile, predictions, loading, error } = usePredictionAPI(
        "/video/translate",
        parseVideoPredictions
    );

    const [file, setFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null); // ✅ fixed line
    const [progress, setProgress] = useState(null);
    const [log, setLog] = useState([]);
    const [validationError, setValidationError] = useState(null);

    // ----------------------------------------------------------------------
    // Handle file selection and basic validation (only allow video formats)
    // ----------------------------------------------------------------------
    const handleFileChange = (e) => {
        const selectedFile = e.target.files?.[0];
        setValidationError(null);

        if (!selectedFile) {
            setFile(null);
            setPreviewUrl(null);
            return;
        }

        const validTypes = ["video/mp4", "video/avi", "video/quicktime", "video/mov", "video/mpeg"];
        if (!validTypes.includes(selectedFile.type)) {
            setValidationError("Invalid file type. Please upload an MP4, MOV, or AVI video.");
            setFile(null);
            setPreviewUrl(null);
            return;
        }

        setFile(selectedFile);
        setPreviewUrl(URL.createObjectURL(selectedFile));
    };

    // ----------------------------------------------------------------------
    // Handle upload and backend prediction request
    // ----------------------------------------------------------------------
    const handleSubmit = async () => {
        setValidationError(null);
        if (!file) {
            setValidationError("Please select a video first.");
            return;
        }

        setProgress(0);
        const preds = await sendFile(file, (event) => {
            if (event.total) {
                const percent = Math.round((event.loaded * 100) / event.total);
                setProgress(percent);
            }
        });

        if (error) {
            setValidationError(error);
            setProgress(null);
            return;
        }

        if (!preds || preds.length === 0) {
            setValidationError("No predictions were returned.");
            setProgress(null);
            return;
        }

        const combinedText = preds.map((p) => p.label).join(" ");

        if (settings?.SPEECH_ENABLED) {
            speakText(combinedText);
        }

        try {
            await fetch("http://localhost:8000/translations/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_id: userId,
                    input_type: "video",
                    recognized_text: combinedText,
                    filename: file?.name || null,
                }),
            });
        } catch (err) {
            console.warn("Failed to save video translation:", err);
        }

        setLog((prevLog) => {
            const newEntry = {
                videoUrl: previewUrl,
                predictions: preds,
                timestamp: new Date().toLocaleString(),
                fileName: file.name || "prediction.mp4",
                combinedText: combinedText,
            };
            return [newEntry, ...prevLog].slice(0, 3);
        });

        setProgress(null);
    };

    // ----------------------------------------------------------------------
    // Download transcript log as a .txt file
    // ----------------------------------------------------------------------
    const downloadLog = (entry) => {
        const text = entry.predictions
            .map((p) => `Frame ${p.frame}: ${p.label} (${(p.confidence * 100).toFixed(1)}%)`)
            .join("\n");

        const blob = new Blob([text], { type: "text/plain" });
        const url = URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.href = url;
        const name = entry.fileName.endsWith(".mp4")
            ? entry.fileName.replace(/\.mp4$/i, ".txt")
            : entry.fileName + ".txt";

        link.download = name;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };

    if (!settings)
        return <div role="status" aria-live="polite">Loading user settings...</div>;

    // ----------------------------------------------------------------------
    // LEFT PANE: Video upload, progress, prediction results, and error display
    // ----------------------------------------------------------------------
    const left = (
        <div role="region" aria-label="Video Translation Panel">
            <UploadPanel
                accept="video/*"
                aria-label="Video Upload Panel"
                previewUrl={previewUrl}
                loading={loading}
                progress={progress}
                onFileChange={handleFileChange}
                onSubmit={handleSubmit}
                submitLabel="Translate Video"
                disabled={!file}
                renderPreview={(url) => (
                    <div style={{ marginTop: "1rem" }}>
                        <video
                            src={url}
                            controls
                            aria-label="Uploaded video preview"
                            style={{ maxWidth: "400px", border: "1px solid #ccc" }}
                        />
                    </div>
                )}
            >
                <SpeakerIcon
                    enabled={settings?.SPEECH_ENABLED}
                    speaking={speaking}
                    size={22}
                    aria-label={
                        settings?.SPEECH_ENABLED
                            ? speaking
                                ? "Text to speech is currently speaking"
                                : "Text to speech enabled"
                            : "Text to speech disabled"
                    }
                    role="button"
                    style={{ marginLeft: "1rem" }}
                />

                {validationError && (
                    <p
                        style={{ color: "red", marginTop: "0.5rem" }}
                        role="alert"
                        aria-live="assertive"
                    >
                        {validationError}
                    </p>
                )}

                {error && !validationError && (
                    <p
                        style={{ color: "red", marginTop: "0.5rem" }}
                        role="alert"
                        aria-live="assertive"
                    >
                        {error}
                    </p>
                )}

                <PredictionList
                    aria-label="Prediction List"
                    predictions={predictions}
                    role="list"
                    aria-live="polite"
                    renderItem={(p, i) => {
                        const lowConfidence = p.confidence < 0.5;
                        return (
                            <div
                                key={i}
                                role="listitem"
                                aria-label={`Frame ${p.frame}: ${p.label}, confidence ${(p.confidence * 100).toFixed(1)} percent`}
                                style={{
                                    color: lowConfidence ? "red" : "white",
                                    fontWeight: "bold",
                                }}
                            >
                                Frame {p.frame}: {p.label} ({(p.confidence * 100).toFixed(1)}%)
                                {lowConfidence && " — Low confidence"}
                            </div>
                        );
                    }}
                />
            </UploadPanel>
        </div>
    );

    // ----------------------------------------------------------------------
    // RIGHT PANE: Recent translation logs and download functionality
    // ----------------------------------------------------------------------
    const right = (
        <TranslationLog
            log={log}
            aria-label="Recent Video Translations Log"
            role="region"
            onClear={() => setLog([])}
            renderEntry={(entry) => (
                <>
                    <video
                        src={entry.videoUrl}
                        controls
                        aria-label={`Video translation from ${entry.timestamp}`}
                        style={{ width: "100%", borderRadius: "6px", marginBottom: "0.4rem" }}
                    />

                    <div
                        style={{ fontSize: "0.8em", color: "#bbb", marginBottom: "0.5rem" }}
                        aria-label={`Translation timestamp: ${entry.timestamp}`}
                    >
                        {entry.timestamp}
                    </div>

                    <div
                        role="list"
                        aria-label="Prediction details for this video"
                        style={{
                            flexGrow: 1,
                            overflowY: "auto",
                            minHeight: "160px",
                            maxHeight: "220px",
                            borderTop: "1px solid #444",
                            paddingTop: "0.5rem",
                        }}
                    >
                        {entry.predictions?.map((p, i) => (
                            <div
                                key={i}
                                role="listitem"
                                aria-label={`Frame ${p.frame}: ${p.label}, confidence ${(p.confidence * 100).toFixed(1)} percent`}
                                style={{
                                    color: p.confidence < 0.5 ? "red" : "white",
                                }}
                            >
                                Frame {p.frame}: {p.label} ({(p.confidence * 100).toFixed(1)}%)
                                {p.confidence < 0.5 && " — Low confidence"}
                            </div>
                        ))}
                    </div>

                    <button
                        onClick={() => downloadLog(entry)}
                        aria-label={`Download transcript for video ${entry.fileName}`}
                        style={{
                            marginTop: "0.5rem",
                            padding: "4px 8px",
                            background: "#1976d2",
                            color: "#fff",
                            border: "none",
                            borderRadius: "4px",
                            cursor: "pointer",
                        }}
                    >
                        Download Transcript
                    </button>
                </>
            )}
            containerStyle={{ minWidth: "540px", maxWidth: "1100px" }}
        />
    );

    return <TranslatorLayout left={left} right={right} />;
}
