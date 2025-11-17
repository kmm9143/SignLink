import React from "react";
import LoadingBar from "../../common/LoadingBar.jsx";

/**
 * UploadPanel: isolated file selection / preview / submit UI.
 * Props:
 *  - accept, previewUrl, loading, progress
 *  - onFileChange(event), onSubmit()
 *  - renderPreview(fileUrl)
 */
export default function UploadPanel({
    accept = "*/*",
    previewUrl,
    loading,
    progress,
    onFileChange,
    onSubmit,
    renderPreview,
    submitLabel = "Translate",
    disabled,
    children,
}) {
    return (
        <div
            role="region"
            aria-label="Upload Panel"
            style={{ color: "white" }}
        >
            {/* File Input */}
            <input
                type="file"
                accept={accept}
                onChange={onFileChange}
                aria-label="Select File to Upload"
                style={{
                    color: "white",
                    backgroundColor: "#222",
                    border: "1px solid #555",
                    padding: "0.4rem",
                    borderRadius: "6px",
                }}
            />

            {/* Submit Button */}
            <button
                onClick={onSubmit}
                disabled={disabled || loading}
                aria-label={loading ? "Processing Upload" : `${submitLabel} Button`}
                style={{
                    marginLeft: "1rem",
                    padding: "0.5rem 1rem",
                    backgroundColor: disabled || loading ? "#444" : "#1a1a1a",
                    color: "white",
                    border: "1px solid #555",
                    borderRadius: "6px",
                    cursor: disabled || loading ? "not-allowed" : "pointer",
                }}
            >
                {loading ? "Processing..." : submitLabel}
            </button>

            {children}

            {/* Loading Bar */}
            {loading && (
                <LoadingBar
                    progress={progress}
                    aria-label={`Upload Progress: ${progress}%`}
                />
            )}

            {/* Preview Section */}
            {previewUrl && (
                <div
                    style={{ marginTop: "1rem" }}
                    role="region"
                    aria-label="Preview Area"
                >
                    {renderPreview ? (
                        renderPreview(previewUrl)
                    ) : (
                        <img
                            src={previewUrl}
                            alt="Uploaded File Preview"
                            style={{
                                maxWidth: "300px",
                                maxHeight: "300px",
                                border: "1px solid #555", // updated contrast-safe border
                                borderRadius: "8px",
                            }}
                        />
                    )}
                </div>
            )}
        </div>
    );
}
