// SpeakerIcon.jsx
// Small reusable component that renders a speaker icon pair:
//  - a "speaking" icon when speaking is true
//  - a muted/inactive icon otherwise
//
// Props:
//  - enabled: boolean (if false, renders nothing)
//  - speaking: boolean
//  - size: number (optional, icon pixel size; default 22)
//  - className / style: optional passthrough

import React from "react";
import { Volume2, VolumeX } from "lucide-react";

export default function SpeakerIcon({ enabled = true, speaking = false, size = 22, style, className }) {
    if (!enabled) return null;

    const ariaLabel = speaking ? "Speech output active" : "Speech output muted";

    return (
        <span
            role="img"
            aria-label={ariaLabel}
            className={className}
            style={{
                marginLeft: "0.5rem",
                display: "inline-flex",
                alignItems: "center",
                gap: "0.25rem",
                ...style,
            }}
        >
            {speaking ? (
                <Volume2
                    size={size}
                    aria-hidden="true"
                    style={{
                        color: "#4CAF50",
                        animation: "speaker-pulse 1s infinite",
                    }}
                />
            ) : (
                <VolumeX
                    size={size}
                    aria-hidden="true"
                    style={{ color: "#aaa" }}
                />
            )}

            {/* Screen reader description (invisible to sighted users) */}
            <span style={{
                position: "absolute",
                width: "1px",
                height: "1px",
                padding: 0,
                margin: "-1px",
                overflow: "hidden",
                clip: "rect(0,0,0,0)",
                whiteSpace: "nowrap",
                border: 0
            }}>
                {ariaLabel}
            </span>

            {/* Simple CSS animation (kept local) */}
            <style>{`
                @keyframes speaker-pulse {
                  0% { transform: scale(1); opacity: 1; }
                  50% { transform: scale(1.08); opacity: 0.85; }
                  100% { transform: scale(1); opacity: 1; }
                }
            `}</style>
        </span>
    );
}
