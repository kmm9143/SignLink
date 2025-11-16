import React from "react";

/**
 * Generic log presenter used by Image/Video translators.
 * Props:
 *  - log: array
 *  - renderEntry: (entry, idx) => ReactNode
 *  - onClear, containerStyle
 */
export default function TranslationLog({ log = [], renderEntry, onClear, containerStyle }) {
    if (!log || log.length === 0) return null;

    return (
        <div
            style={{ ...containerStyle }}
            role="region"
            aria-label="Translation log section"
        >
            <div
                style={{
                    width: "100%",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "1rem"
                }}
            >
                <h3 id="translationLogHeader" style={{ margin: 0, color: "white" }}>
                    Translation Log
                </h3>

                <button
                    onClick={onClear}
                    aria-label="Clear translation log"
                    style={{
                        background: "#e74c3c",
                        color: "#fff",
                        padding: "0.4rem 0.75rem",
                        borderRadius: "6px",
                        border: "none",
                        cursor: "pointer"
                    }}
                >
                    Clear Log
                </button>
            </div>

            <div
                role="list"
                aria-labelledby="translationLogHeader"
                style={{
                    width: "100%",
                    border: "1px solid #444",
                    borderRadius: "8px",
                    background: "rgba(0,0,0,0.2)",
                    padding: "1rem",
                    display: "grid",
                    gridTemplateColumns: "repeat(3, 1fr)",
                    gap: "1rem",
                    boxSizing: "border-box"
                }}
            >
                {log.map((entry, idx) => (
                    <div
                        key={idx}
                        role="listitem"
                        aria-label={`Log entry ${idx + 1}`}
                        tabIndex={0}
                        style={{
                            border: "1px solid #ccc",
                            borderRadius: "8px",
                            background: "transparent",
                            display: "flex",
                            flexDirection: "column",
                            height: "100%",
                            padding: "0.5rem",
                            boxSizing: "border-box",
                            outline: "none"
                        }}
                        onFocus={(e) => (e.target.style.outline = "2px solid #3b82f6")}
                        onBlur={(e) => (e.target.style.outline = "none")}
                    >
                        {renderEntry
                            ? renderEntry(entry, idx)
                            : (
                                <pre style={{ whiteSpace: "pre-wrap", color: "white" }}>
                                    {JSON.stringify(entry, null, 2)}
                                </pre>
                            )}
                    </div>
                ))}
            </div>
        </div>
    );
}