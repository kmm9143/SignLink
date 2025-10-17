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
        <div>
            <input type="file" accept={accept} onChange={onFileChange} />
            <button onClick={onSubmit} disabled={disabled || loading} style={{ marginLeft: "1rem" }}>
                {loading ? "Processing..." : submitLabel}
            </button>

            {children}

            {loading && <LoadingBar progress={progress} />}

            {previewUrl && (
                <div style={{ marginTop: "1rem" }}>
                    {renderPreview ? renderPreview(previewUrl) : <img src={previewUrl} alt="Preview" style={{ maxWidth: "300px", maxHeight: "300px", border: "1px solid #ccc" }} />}
                </div>
            )}
        </div>
    );
}