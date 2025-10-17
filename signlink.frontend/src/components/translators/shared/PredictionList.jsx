import React from "react";

/**
 * Renders a list of prediction items.
 * - predictions: array
 * - renderItem: (item, idx) => ReactNode
 */
export default function PredictionList({ predictions = [], renderItem }) {
    if (!predictions || predictions.length === 0) return null;
    return (
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
                    margin: 0,
                }}
            >
                Predictions:
            </h3>
            <div style={{ padding: "0.5rem" }}>
                {predictions.map((p, i) => (
                    <div key={i}>{renderItem ? renderItem(p, i) : JSON.stringify(p)}</div>
                ))}
            </div>
        </div>
    );
}