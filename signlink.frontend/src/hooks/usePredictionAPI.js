// FILE: src/hooks/usePredictionAPI.js
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
                timeout: 10000, // Optional: prevent hanging requests (10s)
            });

            const parsed = parsePredictions(res.data);
            setPredictions(parsed);
            return parsed;
        } catch (err) {
            console.error("Prediction API error:", err);

            // Handle different failure cases cleanly
            if (err.code === "ECONNABORTED") {
                setError("The server took too long to respond. Please try again later.");
            } else if (!err.response) {
                // No response = backend offline or network failure
                setError("Unable to connect to the server. Please check your connection.");
            } else if (err.response.status >= 500) {
                setError("Server error. Please try again later.");
            } else if (err.response.data?.detail) {
                setError(err.response.data.detail);
            } else {
                setError("An unexpected error occurred. Please try again.");
            }

            return null;
        } finally {
            setLoading(false);
        }
    };

    return { sendFile, predictions, loading, error };
}