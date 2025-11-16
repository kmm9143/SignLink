import React from "react";

/**
 * Simple layout wrapper for translator UIs.
 * Keeps components focused on logic and delegates structure here.
 */
export default function TranslatorLayout({ left, right }) {
    return (
        <div
            style={{ padding: "2rem", display: "flex", alignItems: "flex-start" }}
            role="region"
            aria-label="Translator Layout Container"
        >
            <div
                style={{ flex: 1, minWidth: 0 }}
                role="region"
                aria-label="Primary Content Area"
            >
                {left}
            </div>

            {right && (
                <div
                    style={{
                        marginLeft: "2rem",
                        minWidth: "300px",
                        maxWidth: "1100px",
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "flex-end",
                    }}
                    role="region"
                    aria-label="Side Panel"
                >
                    {right}
                </div>
            )}
        </div>
    );
}