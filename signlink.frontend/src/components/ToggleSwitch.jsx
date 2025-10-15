// ToggleSwitch.jsx
// Reusable accessible toggle switch.
// Props:
//  - label: string (text shown on left)
//  - checked: boolean
//  - onChange: function(e) or function() (called when toggled)
//  - id: optional string (for accessibility)
//  - disabled: optional boolean
//  - style / className: optional passthrough

import React from "react";

export default function ToggleSwitch({ label, checked, onChange, id, disabled = false, style, className }) {
    const inputId = id || `toggle-${label?.toLowerCase().replace(/\s+/g, "-") || Math.random().toString(36).slice(2, 8)}`;

    return (
        <div
            className={className}
            style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                margin: "1rem 0",
                ...style,
            }}
        >
            <label htmlFor={inputId} style={{ fontSize: "1rem", fontWeight: 500, cursor: disabled ? "not-allowed" : "pointer" }}>
                {label}
            </label>

            <label style={{ position: "relative", width: 50, height: 28, display: "inline-block", opacity: disabled ? 0.6 : 1 }}>
                <input
                    id={inputId}
                    type="checkbox"
                    checked={!!checked}
                    disabled={disabled}
                    onChange={onChange}
                    aria-checked={!!checked}
                    style={{ opacity: 0, width: 0, height: 0, position: "absolute", left: -9999 }}
                />

                {/* Track */}
                <span
                    aria-hidden
                    style={{
                        position: "absolute",
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        backgroundColor: checked ? "#4ade80" : "#ccc",
                        borderRadius: 999,
                        transition: "background-color 0.25s",
                    }}
                >
                    {/* Thumb */}
                    <span
                        style={{
                            position: "absolute",
                            height: 22,
                            width: 22,
                            left: checked ? 26 : 4,
                            bottom: 3,
                            backgroundColor: "white",
                            borderRadius: "50%",
                            boxShadow: "0 1px 3px rgba(0,0,0,0.2)",
                            transition: "left 0.25s",
                        }}
                    />
                </span>
            </label>
        </div>
    );
}