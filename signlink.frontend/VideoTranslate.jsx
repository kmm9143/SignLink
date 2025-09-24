// src/components/VideoTranslate.jsx
import { useState } from "react";
import axios from "axios";

export default function VideoTranslate() {
    const [file, setFile] = useState(null);
    const [predictions, setPredictions] = useState([]);
    const [error, setError] = useState(null);

    const handleUpload = (e) => setFile(e.target.files[0]);

    const handleTranslate = async () => {
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await axios.post("http://127.0.0.1:8000/video/predict", formData);
            const data = res.data.predictions || [];

            // Extract first prediction of each frame
            const framePredictions = data.map((frame) => {
                const preds = frame?.predictions?.[0]?.predictions || [];
                return preds.length > 0 ? { label: preds[0].class, confidence: preds[0].confidence } : { label: "None", confidence: 0 };
            });

            setPredictions(framePredictions);
            setError(null);
        } catch (err) {
            console.error(err);
            setError("Error translating video.");
        }
    };

    return (
        <div>
            <h2>Video Translation</h2>
            <input type="file" accept="video/*" onChange={handleUpload} />
            <button onClick={handleTranslate}>Translate Video</button>

            {predictions.length > 0 && (
                <div>
                    <h3>Predictions:</h3>
                    <ul>
                        {predictions.map((p, i) => (
                            <li key={i}>
                                {p.label} ({(p.confidence * 100).toFixed(2)}%)
                                {p.confidence < 0.5 && <span style={{ color: "red" }}> - Low confidence!</span>}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
            {error && <p style={{ color: "red" }}>{error}</p>}
        </div>
    );
}
