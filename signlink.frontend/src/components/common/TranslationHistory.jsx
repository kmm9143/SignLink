// DESCRIPTION: Displays the user's translation history across all modes (image, video, webcam),
//               with filter options, sort order selection, and persistent preferences.
// LANGUAGE:     JAVASCRIPT (React.js)

import React, { useEffect, useState } from "react";
import { Loader2, History, Filter, ArrowUpDown } from "lucide-react";

export default function TranslationHistory({ userId }) {
    const [history, setHistory] = useState([]);
    const [filteredHistory, setFilteredHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    const [filter, setFilter] = useState(() => localStorage.getItem("historyFilter") || "All");
    const [sortOrder, setSortOrder] = useState(() => localStorage.getItem("historySortOrder") || "Newest");

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

    useEffect(() => {
        // Persist preferences
        localStorage.setItem("historyFilter", filter);
        localStorage.setItem("historySortOrder", sortOrder);

        // Filter
        let result =
            filter === "All"
                ? [...history]
                : history.filter((item) => item.INPUT_TYPE === filter);

        // Sort
        result.sort((a, b) =>
            sortOrder === "Newest"
                ? new Date(b.CREATED_AT) - new Date(a.CREATED_AT)
                : new Date(a.CREATED_AT) - new Date(b.CREATED_AT)
        );

        setFilteredHistory(result);
    }, [filter, sortOrder, history]);

    return (
        <div style={{ maxWidth: "700px", margin: "0 auto", padding: "1rem", color: "#111" }}>
            {/* Header */}
            <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    marginBottom: "1.5rem",
                }}
            >
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <History style={{ color: "#3b82f6" }} />
                    <h2 style={{ fontSize: "1.5rem", fontWeight: "bold", color: "white" }}>
                        Translation History
                    </h2>
                </div>

                {/* Controls */}
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                    {/* Filter Dropdown */}
                    <div style={{ display: "flex", alignItems: "center", gap: "0.3rem" }}>
                        <Filter size={18} style={{ color: "#555" }} />
                        <select
                            value={filter}
                            onChange={(e) => setFilter(e.target.value)}
                            style={{
                                padding: "0.4rem 0.6rem",
                                borderRadius: "6px",
                                border: "1px solid #ccc",
                                backgroundColor: "white",
                                color: "#111",
                                fontSize: "0.9rem",
                                cursor: "pointer",
                            }}
                        >
                            <option value="All">All</option>
                            <option value="image">Image</option>
                            <option value="video">Video</option>
                            <option value="webcam">Webcam</option>
                        </select>
                    </div>

                    {/* Sort Toggle */}
                    <button
                        onClick={() =>
                            setSortOrder((prev) =>
                                prev === "Newest" ? "Oldest" : "Newest"
                            )
                        }
                        style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "0.3rem",
                            padding: "0.4rem 0.6rem",
                            borderRadius: "6px",
                            border: "1px solid #ccc",
                            backgroundColor: "white",
                            color: "#111",
                            fontSize: "0.9rem",
                            cursor: "pointer",
                        }}
                        title="Toggle sort order"
                    >
                        <ArrowUpDown size={16} />
                        {sortOrder === "Newest" ? "Newest → Oldest" : "Oldest → Newest"}
                    </button>
                </div>
            </div>

            {/* Loading state */}
            {loading ? (
                <div style={{ textAlign: "center", padding: "2rem" }}>
                    <Loader2 className="animate-spin" />
                    <p>Loading history...</p>
                </div>
            ) : filteredHistory.length === 0 ? (
                <p style={{ textAlign: "center", color: "#777" }}>
                    No translation history found.
                </p>
            ) : (
                // History list
                <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                    {filteredHistory.map((item) => (
                        <div
                            key={item.ID}
                            style={{
                                border: "1px solid #ddd",
                                borderRadius: "8px",
                                padding: "1rem",
                                boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
                                backgroundColor: "white",
                            }}
                        >
                            <p>
                                <strong>Type:</strong> {item.INPUT_TYPE}
                            </p>
                            <p>{item.RECOGNIZED_TEXT}</p>
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