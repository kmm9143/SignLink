// DESCRIPTION:   React component that allows users to view and update their personal
//                application settings (speech and webcam features). The component
//                fetches user preferences from the backend, displays toggle switches
//                for each configurable option, and synchronizes changes with the API.
// LANGUAGE:      JAVASCRIPT (React.js)
// SOURCE(S):     
//    [1] React Docs. (n.d.). Using the Effect Hook. Retrieved October 4, 2025, from https://react.dev/reference/react/useEffect
//    [2] React Docs. (n.d.). State: useState Hook. Retrieved October 4, 2025, from https://react.dev/reference/react/useState
//    [3] MDN Web Docs. (n.d.). Fetch API. Retrieved October 4, 2025, from https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
//    [4] W3Schools. (n.d.). CSS Transitions. Retrieved October 4, 2025, from https://www.w3schools.com/css/css3_transitions.asp

// -----------------------------------------------------------------------------
// Step 1: Import dependencies
// -----------------------------------------------------------------------------
import { useState, useEffect } from 'react';

// -----------------------------------------------------------------------------
// Step 2: Define Toggle component
// -----------------------------------------------------------------------------
function Toggle({ label, checked, onChange }) {
    // Custom toggle switch UI for enabling/disabling settings
    return (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', margin: '1rem 0' }}>
            <span style={{ fontSize: '1rem', fontWeight: 500 }}>{label}</span>
            <label style={{ position: 'relative', display: 'inline-block', width: 50, height: 24 }}>
                <input
                    type="checkbox"
                    checked={checked}
                    onChange={onChange}
                    style={{ opacity: 0, width: 0, height: 0 }}
                />
                <span
                    style={{
                        position: 'absolute',
                        cursor: 'pointer',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        backgroundColor: checked ? '#4ade80' : '#ccc',
                        borderRadius: 24,
                        transition: '0.3s',
                    }}
                >
                    <span
                        style={{
                            position: 'absolute',
                            height: 18,
                            width: 18,
                            left: checked ? 26 : 4,
                            bottom: 3,
                            backgroundColor: 'white',
                            borderRadius: '50%',
                            transition: '0.3s',
                        }}
                    ></span>
                </span>
            </label>
        </div>
    );
}

// -----------------------------------------------------------------------------
// Step 3: Define UserSettings component
// -----------------------------------------------------------------------------
export default function UserSettings({ userId }) {
    // -------------------------------------------------------------------------
    // Step 4: Initialize state variables
    // -------------------------------------------------------------------------
    const [settings, setSettings] = useState({
        speech_enabled: false,
        webcam_enabled: true,
    });
    const [loading, setLoading] = useState(true); // Flag for loading indicator

    // -------------------------------------------------------------------------
    // Step 5: Fetch user settings from backend (on mount)
    // -------------------------------------------------------------------------
    useEffect(() => {
        async function fetchSettings() {
            try {
                // GET request: attempt to retrieve existing settings
                const res = await fetch(`http://127.0.0.1:8000/settings/${userId}`);
                if (res.ok) {
                    const data = await res.json();
                    setSettings({
                        speech_enabled: data.SPEECH_ENABLED,
                        webcam_enabled: data.WEBCAM_ENABLED,
                    });
                }
                // If no settings exist, create default ones
                else if (res.status === 404) {
                    const createRes = await fetch(`http://127.0.0.1:8000/settings/`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            user_id: userId,
                            speech_enabled: false,
                            webcam_enabled: true
                        })
                    });
                    if (createRes.ok) {
                        const defaultData = await createRes.json();
                        setSettings({
                            speech_enabled: defaultData.SPEECH_ENABLED,
                            webcam_enabled: defaultData.WEBCAM_ENABLED,
                        });
                    }
                }
            } catch (err) {
                // Network or server error handling
                console.error('Error fetching/creating user settings:', err);
            } finally {
                // Hide loading spinner after fetch attempt
                setLoading(false);
            }
        }

        fetchSettings(); // Trigger once when component mounts
    }, [userId]);

    // -------------------------------------------------------------------------
    // Step 6: Toggle individual setting and update backend
    // -------------------------------------------------------------------------
    const toggleSetting = async (field) => {
        const updatedSettings = { ...settings, [field]: !settings[field] };
        setSettings(updatedSettings); // Optimistic UI update

        try {
            // PUT request: update user settings in backend
            const res = await fetch(`http://127.0.0.1:8000/settings/${userId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    speech_enabled: updatedSettings.speech_enabled,
                    webcam_enabled: updatedSettings.webcam_enabled
                }),
            });
            if (!res.ok) throw new Error('Failed to update settings');
        } catch (err) {
            console.error(err);
        }
    };

    // -------------------------------------------------------------------------
    // Step 7: Render loading state
    // -------------------------------------------------------------------------
    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '150px' }}>
                <div className="spinner" style={{
                    border: "4px solid #f3f3f3",
                    borderTop: "4px solid #3498db",
                    borderRadius: "50%",
                    width: "30px",
                    height: "30px",
                    animation: "spin 1s linear infinite"
                }} />
                <style>
                    {`@keyframes spin { 
                        0% { transform: rotate(0deg); } 
                        100% { transform: rotate(360deg); } 
                    }`}
                </style>
            </div>
        );
    }

    // -------------------------------------------------------------------------
    // Step 8: Render settings UI (toggles for speech & webcam)
    // -------------------------------------------------------------------------
    return (
        <div style={{
            maxWidth: '400px',
            margin: '0 auto',
            padding: '1.5rem',
            borderRadius: '12px',
            boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
            background: 'gray'
        }}>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', textAlign: 'center' }}>User Settings</h2>

            {/* Toggle for Speech Feature */}
            <Toggle
                label="Enable Speech"
                checked={settings.speech_enabled}
                onChange={() => toggleSetting('speech_enabled')}
            />

            {/* Toggle for Webcam Feature */}
            <Toggle
                label="Enable Webcam"
                checked={settings.webcam_enabled}
                onChange={() => toggleSetting('webcam_enabled')}
            />
        </div>
    );
}