import { useState } from "react";
import LoadingBar from "./components/common/LoadingBar.jsx";
import SpeakerIcon from "./components/common/SpeakerIcon.jsx";

// ✅ Reusable hooks
import useUserSettings from "./hooks/useUserSettings";
import useSpeech from "./hooks/useSpeech";
import usePredictionAPI from "./hooks/usePredictionAPI";

export default function VideoTranslate({ userId = 1 }) {
    // Fetch user settings and initialize speech handling
    const settings = useUserSettings(userId);
    const { speaking, speakText } = useSpeech(settings);

    // Define how to parse backend predictions (video-specific)
    const parseVideoPredictions = (data) => {
        const allPreds = data.predictions.flatMap((frameData) => {
            const predictionArray = frameData.prediction || [];
            return predictionArray.flatMap((inner) => {
                const preds = inner.predictions?.predictions || [];
                return preds.map((p) => ({
                    frame: frameData.frame,
                    label: p.class || p.label || p.sign || "Unknown",
                    confidence: parseFloat(p.confidence ?? p.conf ?? p.probability ?? 0),
                }));
            });
        });

        const topPredsPerFrame = Object.values(
            allPreds.reduce((acc, p) => {
                if (!acc[p.frame] || p.confidence > acc[p.frame].confidence) {
                    acc[p.frame] = p;
                }
                return acc;
            }, {})
        );

        return topPredsPerFrame;
    };

    // ✅ Use shared backend logic (loading, error, upload)
    const { sendFile, predictions, loading, error } = usePredictionAPI(
        "http://127.0.0.1:8000/video/translate",
        parseVideoPredictions
    );

    // Local UI state
    const [file, setFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [progress, setProgress] = useState(null);
    const [log, setLog] = useState([]);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
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
        if (!file) {
            alert("Please select a video first.");
            return;
        }

        setProgress(0);
        const preds = await sendFile(file, (event) => {
            if (event.total) {
                const percent = Math.round((event.loaded * 100) / event.total);
                setProgress(percent);
            }
        });

        // ✅ Trigger speech
        if (settings?.SPEECH_ENABLED && preds?.length > 0) {
            const combinedText = preds.map((p) => p.label).join(" ");
            speakText(combinedText);
        }

        // ✅ Add to log
        setLog((prevLog) => {
            const newEntry = {
                videoUrl: previewUrl,
                predictions: preds,
                timestamp: new Date().toLocaleString(),
                fileName: file.name || "prediction.mp4",
            };
            return [newEntry, ...prevLog].slice(0, 3);
        });

        setProgress(null);
    };

    const renderPrediction = (pred, index) => {
        const lowConfidence = pred.confidence < 0.5;
        return (
            <div
                key={index}
                style={{ color: lowConfidence ? "red" : "white", fontWeight: "bold" }}
            >
                Frame {pred.frame}: {pred.label} ({(pred.confidence * 100).toFixed(1)}%)
                {lowConfidence && " — Low confidence"}
            </div>
        );
    };

    const downloadLog = (entry) => {
        const text = entry.predictions
            .map(
                (p) =>
                    `Frame ${p.frame}: ${p.label} (${(p.confidence * 100).toFixed(1)}%)`
            )
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

    if (!settings) return <div>Loading user settings...</div>;

    // -------------------------------------------------------------------------
    // ✅ UI identical to original
    // -------------------------------------------------------------------------
    return (
        <div style={{ padding: "2rem", display: "flex", alignItems: "flex-start" }}>
            {/* Left Panel */}
            <div style={{ flex: 1, minWidth: 0 }}>
                <input type="file" accept="video/*" onChange={handleFileChange} />
                <button
                    onClick={handleSubmit}
                    disabled={loading || !file}
                    style={{ marginLeft: "1rem" }}
                >
                    {loading ? "Processing..." : "Translate"}
                </button>

                {/* ✅ Speaker icon (unchanged) */}
                <SpeakerIcon
                    enabled={settings?.SPEECH_ENABLED}
                    speaking={speaking}
                    size={22}
                    style={{ marginLeft: "1rem" }}
                />

                {loading && <LoadingBar progress={progress} />}

                {previewUrl && (
                    <div style={{ marginTop: "1rem" }}>
                        <video
                            src={previewUrl}
                            controls
                            style={{ maxWidth: "400px", border: "1px solid #ccc" }}
                        />
                    </div>
                )}

                {error && <p style={{ color: "red" }}>{error}</p>}

                {predictions.length > 0 && (
                    <div
                        style={{
                            marginTop: "1rem",
                            maxHeight: "250px",
                            overflowY: "auto",
                            paddingRight: "0.5rem",
                            border: "1px solid #444",
                            borderRadius: "6px",
                            background: "rgba(0,0,0,0.2)",
                        }}
                    >
                        <h3
                            style={{
                                color: "white",
                                position: "sticky",
                                top: 0,
                                background: "rgba(0,0,0,0.6)",
                                padding: "0.25rem",
                            }}
                        >
                            Predictions:
                        </h3>
                        <div style={{ padding: "0.5rem" }}>
                            {predictions.map((p, i) => renderPrediction(p, i))}
                        </div>
                    </div>
                )}
            </div>

            {/* Right Panel — Log */}
            {log.length > 0 && (
                <div
                    style={{
                        marginLeft: "2rem",
                        minWidth: "540px",
                        maxWidth: "1100px",
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "flex-end",
                    }}
                >
                    <div
                        style={{
                            width: "100%",
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            marginBottom: "1rem",
                        }}
                    >
                        <h3 style={{ margin: 0, color: "white" }}>
                            Video Translation Log (last 3)
                        </h3>
                        <button
                            onClick={() => setLog([])}
                            style={{ background: "#e74c3c", color: "#fff" }}
                        >
                            Clear Log
                        </button>
                    </div>

                    <div
                        style={{
                            width: "100%",
                            border: "1px solid #444",
                            borderRadius: "8px",
                            background: "rgba(0,0,0,0.2)",
                            padding: "1rem",
                            display: "grid",
                            gridTemplateColumns: "repeat(3, 1fr)",
                            gap: "1rem",
                            boxSizing: "border-box",
                        }}
                    >
                        {log.map((entry, idx) => (
                            <div
                                key={idx}
                                style={{
                                    border: "1px solid #ccc",
                                    borderRadius: "8px",
                                    background: "transparent",
                                    display: "flex",
                                    flexDirection: "column",
                                    height: "100%",
                                    padding: "0.5rem",
                                    boxSizing: "border-box",
                                }}
                            >
                                <video
                                    src={entry.videoUrl}
                                    controls
                                    style={{
                                        width: "100%",
                                        borderRadius: "6px",
                                        marginBottom: "0.4rem",
                                    }}
                                />
                                <div
                                    style={{
                                        fontSize: "0.8em",
                                        color: "#bbb",
                                        marginBottom: "0.5rem",
                                    }}
                                >
                                    {entry.timestamp}
                                </div>
                                <div
                                    style={{
                                        flexGrow: 1,
                                        overflowY: "auto",
                                        minHeight: "160px",
                                        maxHeight: "220px",
                                        borderTop: "1px solid #444",
                                        paddingTop: "0.5rem",
                                    }}
                                >
                                    {entry.predictions.map((p, i) =>
                                        renderPrediction(p, i)
                                    )}
                                </div>
                                <button
                                    onClick={() => downloadLog(entry)}
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
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
