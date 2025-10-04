import { useState } from 'react';
import ImageTranslate from './ImageTranslate.jsx';
import WebcamTranslate from './WebcamTranslate.jsx';
import UserSettings from './UserSettings.jsx';
import Auth from './Auth.jsx';   // login/signup form

export default function App() {
    // -----------------------------------------------------------------------------------
    // State
    // -----------------------------------------------------------------------------------
    const [user, setUser] = useState(null);          // logged-in user info (from UserInformation table)
    const [mode, setMode] = useState('image');       // translation mode
    const [showSettings, setShowSettings] = useState(false); // toggle settings panel

    // -----------------------------------------------------------------------------------
    // If user is not logged in, show Auth component
    // -----------------------------------------------------------------------------------
    if (!user) {
        return <Auth onLogin={(userData) => setUser(userData)} />;
    }

    // -----------------------------------------------------------------------------------
    // Render Translator + Settings (once logged in)
    // -----------------------------------------------------------------------------------
    return (
        <div style={{ padding: '2rem' }}>
            <h1>ASL Translator</h1>
            <p style={{ fontSize: "0.9rem", color: "#666" }}>
                Logged in as <strong>{user.username}</strong>
            </p>

            {/* Top menu buttons */}
            <div style={{ marginBottom: '1rem' }}>
                <button
                    onClick={() => setMode('image')}
                    style={{ marginRight: '1rem', backgroundColor: mode === 'image' ? '#ccc' : '' }}
                >
                    Upload Image
                </button>
                <button
                    onClick={() => setMode('webcam')}
                    style={{ marginRight: '1rem', backgroundColor: mode === 'webcam' ? '#ccc' : '' }}
                >
                    Webcam
                </button>
                <button
                    onClick={() => setShowSettings(true)}
                    style={{ float: 'right' }}
                >
                    Settings
                </button>
            </div>

            {/* Conditionally render translator or settings */}
            {!showSettings && (
                <>
                    {mode === 'image' && <ImageTranslate userId={user.id} />}
                    {mode === 'webcam' && <WebcamTranslate userId={user.id} />}
                </>
            )}

            {showSettings && (
                <div style={{ border: '1px solid #ccc', padding: '1rem', marginTop: '1rem' }}>
                    {/* Pass the userId to settings so backend can fetch/update UserSettings */}
                    <UserSettings userId={user.id} />
                    <button onClick={() => setShowSettings(false)} style={{ marginTop: '1rem' }}>
                        Close Settings
                    </button>
                </div>
            )}
        </div>
    );
}
