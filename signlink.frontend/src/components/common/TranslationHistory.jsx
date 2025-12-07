import React from "react";
import {
    Loader2,
    History,
    Filter,
    ArrowUpDown,
    Edit2,
    Trash2,
} from "lucide-react";

import useTranslationHistory from "../../hooks/useTranslationHistory";

export default function TranslationHistory({ userId }) {
    const {
        loading,
        history,
        filter,
        setFilter,
        sortOrder,
        setSortOrder,
        editMode,
        setEditMode,
        selectedIds,
        toggleSelect,
        selectAll,
        deleteSelected,
    } = useTranslationHistory(userId);

    return (
        <div
            style={{ maxWidth: "700px", margin: "0 auto", padding: "1rem", color: "#111" }}
            role="region"
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
                            onChange={(e) => setFilter(e.target.value)}
                            style={{
                                padding: "0.4rem 0.6rem",
                                borderRadius: "6px",
                                border: "1px solid #ccc",
                                backgroundColor: "white",
                                color: "#111",
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
                        onClick={() =>
                            setSortOrder((prev) => (prev === "Newest" ? "Oldest" : "Newest"))
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
                        }}
                    >
                        <ArrowUpDown aria-hidden="true" size={16} />
                        {sortOrder === "Newest" ? "Newest → Oldest" : "Oldest → Newest"}
                    </button>

                    {/* Edit */}
                    <button
                        aria-label="Toggle edit mode"
                        aria-pressed={editMode}
                        onClick={() => setEditMode((prev) => !prev)}
                        style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "0.3rem",
                            padding: "0.4rem 0.6rem",
                            borderRadius: "6px",
                            border: "1px solid #ccc",
                            backgroundColor: "white",
                        }}
                    >
                        <Edit2 aria-hidden="true" size={16} />
                        {editMode ? "Cancel" : "Edit"}
                    </button>

                    {editMode && (
                        <>
                            <button
                                aria-label="Select all"
                                onClick={selectAll}
                                style={{
                                    padding: "0.4rem 0.6rem",
                                    borderRadius: "6px",
                                    border: "1px solid #ccc",
                                    backgroundColor: "white",
                                }}
                            >
                                {selectedIds.length === history.length
                                    ? "Deselect All"
                                    : "Select All"}
                            </button>

                            <button
                                aria-label="Delete selected"
                                disabled={!selectedIds.length}
                                onClick={deleteSelected}
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: "0.3rem",
                                    padding: "0.4rem 0.6rem",
                                    borderRadius: "6px",
                                    border: "1px solid #e74c3c",
                                    backgroundColor: "#e74c3c",
                                    color: "white",
                                }}
                            >
                                <Trash2 aria-hidden="true" size={16} /> Delete Selected
                            </button>
                        </>
                    )}
                </div>
            </div>

            {/* List */}
            {loading ? (
                <div style={{ textAlign: "center", padding: "2rem" }} aria-live="polite">
                    <Loader2 className="animate-spin" />
                    <p>Loading history...</p>
                </div>
            ) : history.length === 0 ? (
                <p style={{ textAlign: "center", color: "#777" }} aria-live="polite">
                    No translation history found.
                </p>
            ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                    {history.map((item) => (
                        <div
                            key={item.ID}
                            role="listitem"
                            tabIndex={0}
                            style={{
                                border: "1px solid #ddd",
                                borderRadius: "8px",
                                padding: "1rem",
                                backgroundColor: "white",
                                display: "flex",
                                gap: "0.5rem",
                            }}
                            onKeyDown={(e) => {
                                if (editMode && (e.key === "Enter" || e.key === " ")) {
                                    e.preventDefault();
                                    toggleSelect(item.ID);
                                }
                            }}
                        >
                            {editMode && (
                                <input
                                    type="checkbox"
                                    checked={selectedIds.includes(item.ID)}
                                    onChange={() => toggleSelect(item.ID)}
                                />
                            )}

                            <div>
                                <p><strong>Type:</strong> {item.INPUT_TYPE}</p>
                                <p>{item.RECOGNIZED_TEXT}</p>
                                <p style={{ fontSize: "0.8rem", color: "#666" }}>
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