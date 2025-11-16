import React, { useEffect, useState } from "react";
import { Loader2, History, Filter, ArrowUpDown, Edit2, Trash2 } from "lucide-react";

export default function TranslationHistory({ userId }) {
    const [history, setHistory] = useState([]);
    const [filteredHistory, setFilteredHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    const [filter, setFilter] = useState(() => localStorage.getItem("historyFilter") || "All");
    const [sortOrder, setSortOrder] = useState(() => localStorage.getItem("historySortOrder") || "Newest");

    const [editMode, setEditMode] = useState(false);
    const [selectedIds, setSelectedIds] = useState([]);

    //
    // Fetch translation history
    //
    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await fetch(`http://localhost:8000/translations/${userId}`, { credentials: "include" });
                if (!response.ok) throw new Error(`Failed to fetch history (${response.status})`);
                const data = await response.json();
                setHistory(data || []);
            } catch (error) {
                console.error("Error fetching history:", error);
            } finally {
                setLoading(false);
            }
        };
        if (userId != null) fetchHistory();
    }, [userId]);

    //
    // Apply filter & sort
    //
    useEffect(() => {
        localStorage.setItem("historyFilter", filter);
        localStorage.setItem("historySortOrder", sortOrder);

        let result = filter === "All"
            ? [...history]
            : history.filter(item => (item.INPUT_TYPE ?? item.input_type) === filter);

        result.sort((a, b) =>
            sortOrder === "Newest"
                ? new Date(b.CREATED_AT) - new Date(a.CREATED_AT)
                : new Date(a.CREATED_AT) - new Date(b.CREATED_AT)
        );

        setFilteredHistory(result);
    }, [filter, sortOrder, history]);

    //
    // Toggle selection
    //
    const toggleSelect = (id) => {
        setSelectedIds(prev =>
            prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
        );
    };

    const selectAll = () => {
        if (selectedIds.length === filteredHistory.length) {
            setSelectedIds([]);
        } else {
            setSelectedIds(filteredHistory.map(item => item.ID));
        }
    };

    //
    // Delete selected
    //
    const deleteSelected = async () => {
        if (!selectedIds.length) return;

        if (!window.confirm(`Are you sure you want to delete ${selectedIds.length} log(s)?`)) return;

        try {
            const payload = { log_ids: selectedIds };

            const response = await fetch(
                `http://localhost:8000/translations/${userId}/logs`,
                {
                    method: "DELETE",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                    credentials: "include",
                }
            );

            if (!response.ok) {
                const errorDetail = await response.json().catch(() => null);
                throw new Error(errorDetail?.detail || "Failed to delete logs");
            }

            setHistory(prev => prev.filter(item => !selectedIds.includes(item.ID)));
            setSelectedIds([]);
            setEditMode(false);
        } catch (error) {
            console.error("Error deleting logs:", error);
            alert(error.message || "Failed to delete selected logs");
        }
    };

    return (
        <div
            style={{ maxWidth: "700px", margin: "0 auto", padding: "1rem", color: "#111" }}
            aria-label="Translation history section"
        >
            {/* Header */}
            <div
                style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}
                aria-label="History controls"
            >
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <History aria-hidden="true" style={{ color: "#3b82f6" }} />
                    <h2 id="history-title" style={{ fontSize: "1.5rem", fontWeight: "bold", color: "white" }}>
                        Translation History
                    </h2>
                </div>

                <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                    {/* Filter */}
                    <div style={{ display: "flex", alignItems: "center", gap: "0.3rem" }}>
                        <Filter aria-hidden="true" size={18} style={{ color: "#555" }} />
                        <select
                            aria-label="Filter translation history"
                            value={filter}
                            onChange={e => setFilter(e.target.value)}
                            onFocus={(e) => (e.target.style.outline = "2px solid #3b82f6")}
                            onBlur={(e) => (e.target.style.outline = "none")}
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

                    {/* Sort */}
                    <button
                        aria-label="Toggle sort order"
                        aria-pressed={sortOrder === "Newest"}
                        tabIndex={0}
                        onClick={() => setSortOrder(prev => prev === "Newest" ? "Oldest" : "Newest")}
                        onFocus={(e) => (e.target.style.outline = "2px solid #3b82f6")}
                        onBlur={(e) => (e.target.style.outline = "none")}
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
                    >
                        <ArrowUpDown aria-hidden="true" size={16} />
                        {sortOrder === "Newest" ? "Newest → Oldest" : "Oldest → Newest"}
                    </button>

                    {/* Edit Button */}
                    <button
                        aria-label="Toggle edit mode"
                        aria-pressed={editMode}
                        tabIndex={0}
                        onClick={() => setEditMode(prev => !prev)}
                        onFocus={(e) => (e.target.style.outline = "2px solid #3b82f6")}
                        onBlur={(e) => (e.target.style.outline = "none")}
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
                    >
                        <Edit2 aria-hidden="true" size={16} />
                        {editMode ? "Cancel" : "Edit"}
                    </button>

                    {editMode && (
                        <>
                            {/* Select All */}
                            <button
                                aria-label="Select or deselect all logs"
                                tabIndex={0}
                                onClick={selectAll}
                                onFocus={(e) => (e.target.style.outline = "2px solid #3b82f6")}
                                onBlur={(e) => (e.target.style.outline = "none")}
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
                                {selectedIds.length === filteredHistory.length ? "Deselect All" : "Select All"}
                            </button>

                            {/* Delete Selected */}
                            <button
                                aria-label="Delete selected history logs"
                                tabIndex={0}
                                onClick={deleteSelected}
                                disabled={!selectedIds.length}
                                onFocus={(e) => (e.target.style.outline = "2px solid #3b82f6")}
                                onBlur={(e) => (e.target.style.outline = "none")}
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: "0.3rem",
                                    padding: "0.4rem 0.6rem",
                                    borderRadius: "6px",
                                    border: "1px solid #e74c3c",
                                    backgroundColor: "#e74c3c",
                                    color: "white",
                                    fontSize: "0.9rem",
                                    cursor: selectedIds.length ? "pointer" : "not-allowed",
                                }}
                            >
                                <Trash2 aria-hidden="true" size={16} /> Delete Selected
                            </button>
                        </>
                    )}
                </div>
            </div>

            {/* History List */}
            {loading ? (
                <div style={{ textAlign: "center", padding: "2rem" }} aria-live="polite">
                    <Loader2 className="animate-spin" aria-hidden="true" />
                    <p>Loading history...</p>
                </div>
            ) : filteredHistory.length === 0 ? (
                <p style={{ textAlign: "center", color: "#777" }} aria-live="polite">
                    No translation history found.
                </p>
            ) : (
                <div
                    style={{ display: "flex", flexDirection: "column", gap: "1rem" }}
                    aria-label="List of translation history records"
                    role="list"
                >
                    {filteredHistory.map(item => (
                        <div
                            key={item.ID}
                            role="listitem"
                            tabIndex={0}
                            className="history-card"
                            aria-label={`History entry: ${item.RECOGNIZED_TEXT}. Created ${new Date(item.CREATED_AT).toLocaleString()}`}
                            onKeyDown={(e) => {
                                if (editMode && (e.key === "Enter" || e.key === " ")) {
                                    e.preventDefault();
                                    toggleSelect(item.ID);
                                }
                            }}
                            onFocus={(e) => (e.target.style.outline = "2px solid #3b82f6")}
                            onBlur={(e) => (e.target.style.outline = "none")}
                            style={{
                                border: "1px solid #ddd",
                                borderRadius: "8px",
                                padding: "1rem",
                                boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
                                backgroundColor: "white",
                                display: "flex",
                                alignItems: "center",
                                gap: "0.5rem",
                            }}
                        >
                            {editMode && (
                                <input
                                    type="checkbox"
                                    aria-label={`Select translation entry ${item.RECOGNIZED_TEXT}`}
                                    checked={selectedIds.includes(item.ID)}
                                    onChange={() => toggleSelect(item.ID)}
                                />
                            )}
                            <div>
                                <p><strong>Type:</strong> {item.INPUT_TYPE}</p>
                                <p>{item.RECOGNIZED_TEXT}</p>
                                <p style={{ fontSize: "0.8rem", color: "#666", marginTop: "0.5rem" }}>
                                    {new Date(item.CREATED_AT).toLocaleString()}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
