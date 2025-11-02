// DESCRIPTION: Displays the user's translation history across all modes (image, video, webcam).
// LANGUAGE:     JAVASCRIPT (React.js)

import React, { useEffect, useState } from "react";
import { Loader2, History } from "lucide-react";

export default function TranslationHistory({ userId }) {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await fetch(`http://localhost:8000/translations/${userId}`);
                const data = await response.json();
                setHistory(data);
            } catch (error) {
                console.error("Error fetching history:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, [userId]);

    return (
        <div
            style={{
                maxWidth: "700px",
                margin: "0 auto",
                padding: "1rem",
                color: "#111", // ✅ Ensure dark readable text
                backgroundColor: "#f9fafb", // ✅ Slight contrast background
                borderRadius: "12px",
            }}
        >
            {/* Header */}
            <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                    marginBottom: "1.5rem",
                }}
            >
                <History style={{ color: "#3b82f6" }} />
                <h2
                    style={{
                        fontSize: "1.5rem",
                        fontWeight: "bold",
                        color: "#111", // ✅ Strong text color
                    }}
                >
                    Translation History
                </h2>
            </div>

            {/* Loading state */}
            {loading ? (
                <div style={{ textAlign: "center", padding: "2rem", color: "#555" }}>
                    <Loader2 className="animate-spin" />
                    <p>Loading history...</p>
                </div>
            ) : history.length === 0 ? (
                <p style={{ textAlign: "center", color: "#666" }}>
                    No translation history found.
                </p>
            ) : (
                // History list
                <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                    {history.map((item) => (
                        <div
                            key={item.ID}
                            style={{
                                border: "1px solid #ddd",
                                borderRadius: "8px",
                                padding: "1rem",
                                boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
                                backgroundColor: "#fff", // ✅ Card background for contrast
                                color: "#222", // ✅ Readable text color
                            }}
                        >
                            <p style={{ marginBottom: "0.25rem" }}>
                                <strong>Type:</strong> {item.INPUT_TYPE}
                            </p>
                            <p style={{ marginBottom: "0.25rem" }}>{item.RECOGNIZED_TEXT}</p>
                            <p style={{ fontSize: "0.8rem", color: "#666", marginTop: "0.5rem" }}>
                                {new Date(item.CREATED_AT).toLocaleString()}
                            </p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
