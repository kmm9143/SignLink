// DESCRIPTION:  This React component serves as the main entry point for the ASL Translator web application.
//                It manages user authentication, translation mode switching (image, webcam, or video),
//                and access to user-specific settings and translation history.
// LANGUAGE:     JAVASCRIPT (React.js)
// SOURCE(S):    [1] React Documentation. (n.d.). Using the State Hook. Retrieved September 27, 2025, from https://react.dev/reference/react/useState
//               [2] React Documentation. (n.d.). Conditional Rendering. Retrieved September 27, 2025, from https://react.dev/learn/conditional-rendering
//               [3] MDN Web Docs. (n.d.). JSX syntax and rendering logic. Retrieved September 27, 2025, from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/JSX

// -----------------------------------------------------------------------------
// Step 1: Import React dependencies and local components
// -----------------------------------------------------------------------------
import { useState } from 'react';
import ImageTranslate from './components/translators/ImageTranslate.jsx';    // Image-based ASL translation
import WebcamTranslate from './components/translators/WebcamTranslate.jsx';  // Webcam-based ASL translation
import VideoTranslate from './components/translators/VideoTranslate.jsx';    // Video-based ASL translation
import UserSettings from './components/common/UserSettings.jsx';             // User settings panel
import TranslationHistory from './components/common/TranslationHistory.jsx'; // Translation history panel
import Auth from './Auth.jsx';                                                // Authentication component

// -----------------------------------------------------------------------------
// Step 2: Define main App component
// -----------------------------------------------------------------------------
export default function App() {
    // -------------------------------------------------------------------------
    // State variables
    // -------------------------------------------------------------------------
    const [user, setUser] = useState(null);                // Logged-in user info
    const [mode, setMode] = useState('image');             // Current translation mode
    const [showSettings, setShowSettings] = useState(false); // Show/hide settings panel
    const [showHistory, setShowHistory] = useState(false);   // Show/hide translation history panel

    // -------------------------------------------------------------------------
    // Step 3: Conditional rendering - authentication check
    // -------------------------------------------------------------------------
    if (!user) {
        // If not logged in, render Auth component
        return <Auth onLogin={(userData) => setUser(userData)} />;
    }

    // -------------------------------------------------------------------------
    // Step 4: Render main application UI (after login)
    // -------------------------------------------------------------------------
    return (
        <div style={{ padding: '2rem' }}>
            <h1>ASL Translator</h1>

            {/* Display logged-in user information */}
            <p style={{ fontSize: "0.9rem", color: "#666" }}>
                Logged in as <strong>{user.username}</strong>
            </p>

            {/* -----------------------------------------------------------------
                Navigation Buttons: Switch translation modes, open settings/history
            ----------------------------------------------------------------- */}
            <div style={{ marginBottom: '1rem' }}>
                {/* Image Mode */}
                <button
                    onClick={() => {
                        setMode('image');
                        setShowSettings(false);
                        setShowHistory(false);
                    }}
                    style={{
                        marginRight: '1rem',
                        backgroundColor: mode === 'image' ? '#ccc' : ''
                    }}
                >
                    Upload Image
                </button>

                {/* Webcam Mode */}
                <button
                    onClick={() => {
                        setMode('webcam');
                        setShowSettings(false);
                        setShowHistory(false);
                    }}
                    style={{
                        marginRight: '1rem',
                        backgroundColor: mode === 'webcam' ? '#ccc' : ''
                    }}
                >
                    Webcam
                </button>

                {/* Video Mode */}
                <button
                    onClick={() => {
                        setMode('video');
                        setShowSettings(false);
                        setShowHistory(false);
                    }}
                    style={{
                        marginRight: '1rem',
                        backgroundColor: mode === 'video' ? '#ccc' : ''
                    }}
                >
                    Upload Video
                </button>

                {/* Settings Button */}
                <button
                    onClick={() => {
                        setShowSettings(!showSettings);
                        setShowHistory(false);
                    }}
                    style={{
                        marginRight: '1rem',
                        backgroundColor: showSettings ? '#ccc' : ''
                    }}
                >
                    Settings
                </button>

                {/* Translation History Button */}
                <button
                    onClick={() => {
                        setShowHistory(!showHistory);
                        setShowSettings(false);
                    }}
                    style={{
                        marginRight: '1rem',
                        backgroundColor: showHistory ? '#ccc' : ''
                    }}
                >
                    Translation History
                </button>
            </div>

            {/* -----------------------------------------------------------------
                Step 5: Conditional content rendering
            ----------------------------------------------------------------- */}

            {/* Translator views (only shown when settings/history are hidden) */}
            {!showSettings && !showHistory && (
                <>
                    {mode === 'image' && <ImageTranslate userId={user.id} />}
                    {mode === 'webcam' && <WebcamTranslate userId={user.id} />}
                    {mode === 'video' && <VideoTranslate userId={user.id} />}
                </>
            )}

            {/* Settings Panel */}
            {showSettings && (
                <div
                    style={{
                        border: '1px solid #ccc',
                        padding: '1rem',
                        marginTop: '1rem'
                    }}
                >
                    <UserSettings userId={user.id} />
                    <button
                        onClick={() => setShowSettings(false)}
                        style={{ marginTop: '1rem' }}
                    >
                        Close Settings
                    </button>
                </div>
            )}

            {/* Translation History Panel */}
            {showHistory && (
                <div
                    style={{
                        border: '1px solid #ccc',
                        padding: '1rem',
                        marginTop: '1rem'
                    }}
                >
                    <TranslationHistory userId={user.id} />
                    <button
                        onClick={() => setShowHistory(false)}
                        style={{ marginTop: '1rem' }}
                    >
                        Close History
                    </button>
                </div>
            )}
        </div>
    );
}
