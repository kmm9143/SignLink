import React from 'react';

export default function LoadingBar({ progress = null, color = '#4caf50', height = '8px' }) {

    // Accessible text for screen readers
    const srLabel = progress === null
        ? "Loading, please wait"
        : `Loading progress: ${Math.round(progress)} percent`;

    return (
        <div
            role="progressbar"
            tabIndex={0}
            aria-valuenow={progress === null ? undefined : Math.round(progress)}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={srLabel}
            style={{
                width: '100%',
                height,
                background: '#333',
                borderRadius: '4px',
                overflow: 'hidden',
                marginTop: '1rem',
                position: 'relative',
                outline: 'none'
            }}
            onFocus={(e) => e.target.style.outline = "2px solid #3b82f6"}
            onBlur={(e) => e.target.style.outline = "none"}
        >

            {/* Visible progress indicator */}
            {progress === null ? (
                <>
                    <div
                        style={{
                            width: '100%',
                            height: '100%',
                            background: color,
                            animation: 'progressIndeterminate 1.5s infinite linear',
                        }}
                        aria-hidden="true"
                    />

                    <style>{`
                        @keyframes progressIndeterminate {
                            0% { transform: translateX(-100%); }
                            100% { transform: translateX(100%); }
                        }
                    `}</style>
                </>
            ) : (
                <div
                    style={{
                        width: `${progress}%`,
                        height: '100%',
                        background: color,
                        transition: 'width 0.3s ease',
                    }}
                    aria-hidden="true"
                />
            )}

            {/* Screen-reader-only text */}
            <span
                style={{
                    position: "absolute",
                    width: "1px",
                    height: "1px",
                    padding: 0,
                    margin: "-1px",
                    overflow: "hidden",
                    clip: "rect(0,0,0,0)",
                    whiteSpace: "nowrap",
                    border: 0
                }}
            >
                {srLabel}
            </span>
        </div>
    );
}
