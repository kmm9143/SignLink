// hooks/usePredictionAPI.js
import { useState } from "react";
import axios from "axios";

export default function usePredictionAPI(endpoint, parsePredictions) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [predictions, setPredictions] = useState([]);

    const sendFile = async (file, onProgress) => {
        setLoading(true);
        setError(null);
        setPredictions([]);

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await axios.post(endpoint, formData, {
                headers: { "Content-Type": "multipart/form-data" },
                onUploadProgress: onProgress,
            });

            const parsed = parsePredictions(res.data);
            setPredictions(parsed);
            return parsed;
        } catch (err) {
            setError(err.response?.data?.detail || err.message || "Error during upload");
        } finally {
            setLoading(false);
        }
    };

    return { sendFile, predictions, loading, error };
}