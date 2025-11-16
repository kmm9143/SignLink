// DESCRIPTION:  Main entry point of ASL Translator.
//                Updated for US8: full keyboard accessibility, visible focus,
//                Enter/Space activation, ARIA labels, and consistent navigation.
//
// LANGUAGE:     JAVASCRIPT (React.js)

import { useState } from 'react';
import ImageTranslate from './components/translators/ImageTranslate.jsx';
import WebcamTranslate from './components/translators/WebcamTranslate.jsx';
import VideoTranslate from './components/translators/VideoTranslate.jsx';
import UserSettings from './components/common/UserSettings.jsx';
import TranslationHistory from './components/common/TranslationHistory.jsx';
import Auth from './Auth.jsx';

// Global a11y styles
import './styles/keyboardFocus.css';

export default function App() {
    const [user, setUser] = useState(null);
    const [mode, setMode] = useState('image');
    const [showSettings, setShowSettings] = useState(false);
    const [showHistory, setShowHistory] = useState(false);

    // -----------------------------
    // Accessibility Helper Function
    // -----------------------------
    const handleKeyActivate = (event, action) => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            action();
        }
    };

    if (!user) {
        return <Auth onLogin={(userData) => setUser(userData)} />;
    }

    return (
        <div style={{ padding: '2rem' }}>
            <h1 tabIndex="0" aria-label="ASL Translator Application Title">
                ASL Translator
            </h1>

            <p
                tabIndex="0"
                aria-label={`Logged in as ${user.username}`}
                style={{ fontSize: "0.9rem", color: "#666" }}
            >
                Logged in as <strong>{user.username}</strong>
            </p>

            {/* -------------------------------------
               Navigation Buttons (Keyboard Ready)
            -------------------------------------- */}
            <div style={{ marginBottom: '1rem' }}>

                {/* Upload Image */}
                <button
                    className="a11y-btn"
                    aria-label="Upload Image Button. Switch to image upload mode."
                    tabIndex="0"
                    onKeyDown={(e) =>
                        handleKeyActivate(e, () => {
                            setMode('image');
                            setShowSettings(false);
                            setShowHistory(false);
                        })
                    }
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

                {/* Webcam */}
                <button
                    className="a11y-btn"
                    aria-label="Webcam Translation Button. Open webcam mode."
                    tabIndex="0"
                    onKeyDown={(e) =>
                        handleKeyActivate(e, () => {
                            setMode('webcam');
                            setShowSettings(false);
                            setShowHistory(false);
                        })
                    }
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

                {/* Upload Video */}
                <button
                    className="a11y-btn"
                    aria-label="Upload Video Button. Switch to video upload mode."
                    tabIndex="0"
                    onKeyDown={(e) =>
                        handleKeyActivate(e, () => {
                            setMode('video');
                            setShowSettings(false);
                            setShowHistory(false);
                        })
                    }
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

                {/* Settings */}
                <button
                    className="a11y-btn"
                    aria-label="Open User Settings Panel"
                    tabIndex="0"
                    onKeyDown={(e) =>
                        handleKeyActivate(e, () => {
                            setShowSettings(!showSettings);
                            setShowHistory(false);
                        })
                    }
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

                {/* History */}
                <button
                    className="a11y-btn"
                    aria-label="Open Translation History Panel"
                    tabIndex="0"
                    onKeyDown={(e) =>
                        handleKeyActivate(e, () => {
                            setShowHistory(!showHistory);
                            setShowSettings(false);
                        })
                    }
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

            {/* -------------------------------------
                Conditional Translator Views
            -------------------------------------- */}
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
                    className="a11y-focus"
                    aria-label="User Settings Panel"
                    role="region"
                    tabIndex="0"
                    style={{
                        border: '1px solid #ccc',
                        padding: '1rem',
                        marginTop: '1rem'
                    }}
                >
                    <UserSettings userId={user.id} />

                    <button
                        className="a11y-btn"
                        aria-label="Close Settings Panel"
                        tabIndex="0"
                        onKeyDown={(e) =>
                            handleKeyActivate(e, () => setShowSettings(false))
                        }
                        onClick={() => setShowSettings(false)}
                        style={{ marginTop: '1rem' }}
                    >
                        Close Settings
                    </button>
                </div>
            )}

            {/* History Panel */}
            {showHistory && (
                <div
                    className="a11y-focus"
                    aria-label="Translation History Panel"
                    role="region"
                    tabIndex="0"
                    style={{
                        border: '1px solid #ccc',
                        padding: '1rem',
                        marginTop: '1rem'
                    }}
                >
                    <TranslationHistory userId={user.id} />

                    <button
                        className="a11y-btn"
                        aria-label="Close Translation History Panel"
                        tabIndex="0"
                        onKeyDown={(e) =>
                            handleKeyActivate(e, () => setShowHistory(false))
                        }
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
