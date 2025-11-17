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
            role="region"
            aria-label="Prediction results"
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
                id="predictionListHeader"
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

            <div
                role="list"
                aria-labelledby="predictionListHeader"
                style={{ padding: "0.5rem" }}
            >
                {predictions.map((p, i) => (
                    <div
                        key={i}
                        role="listitem"
                        aria-label={`Prediction ${i + 1}`}
                        tabIndex={0}
                        style={{
                            marginBottom: "0.5rem",
                            padding: "0.3rem",
                            borderRadius: "4px",
                            outline: "none",
                            transition: "background 0.2s ease",
                        }}
                        onFocus={(e) => (e.target.style.outline = "2px solid #3b82f6")}
                        onBlur={(e) => (e.target.style.outline = "none")}
                        onMouseEnter={(e) => (e.target.style.background = "rgba(255,255,255,0.08)")}
                        onMouseLeave={(e) => (e.target.style.background = "transparent")}
                    >
                        {renderItem ? renderItem(p, i) : JSON.stringify(p)}
                    </div>
                ))}
            </div>
        </div>
    );
}
