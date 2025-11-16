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
        >
            {/* File Input */}
            <input
                type="file"
                accept={accept}
                onChange={onFileChange}
                aria-label="Select File to Upload"
            />

            {/* Submit Button */}
            <button
                onClick={onSubmit}
                disabled={disabled || loading}
                style={{ marginLeft: "1rem" }}
                aria-label={loading ? "Processing Upload" : `${submitLabel} Button`}
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
                                border: "1px solid #ccc",
                            }}
                        />
                    )}
                </div>
            )}
        </div>
    );
}
