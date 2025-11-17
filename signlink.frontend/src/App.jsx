import { useState, useEffect, useRef } from 'react';
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
    const settingsRef = useRef(null);
    const historyRef = useRef(null);

    // -----------------------------
    // Accessibility Helper Function
    // -----------------------------
    const handleKeyActivate = (event, action) => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            action();
        }
    };

    // Focus panel when opened
    useEffect(() => {
        if (showSettings && settingsRef.current) {
            settingsRef.current.focus();
        }
    }, [showSettings]);

    useEffect(() => {
        if (showHistory && historyRef.current) {
            historyRef.current.focus();
        }
    }, [showHistory]);

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
            <nav aria-label="Main Navigation" style={{ marginBottom: '1rem' }}>
                {[
                    { label: 'Upload Image', key: 'image' },
                    { label: 'Webcam', key: 'webcam' },
                    { label: 'Upload Video', key: 'video' },
                    { label: 'Settings', key: 'settings' },
                    { label: 'Translation History', key: 'history' }
                ].map((btn) => {
                    const isActive = btn.key === mode ||
                        (btn.key === 'settings' && showSettings) ||
                        (btn.key === 'history' && showHistory);
                    const handleClick = () => {
                        setMode(btn.key === 'image' || btn.key === 'webcam' || btn.key === 'video' ? btn.key : mode);
                        setShowSettings(btn.key === 'settings' ? !showSettings : false);
                        setShowHistory(btn.key === 'history' ? !showHistory : false);
                    };
                    return (
                        <button
                            key={btn.key}
                            className="a11y-btn"
                            aria-label={`${btn.label} Button`}
                            tabIndex="0"
                            onKeyDown={(e) => handleKeyActivate(e, handleClick)}
                            onClick={handleClick}
                            style={{
                                marginRight: '1rem',
                                backgroundColor: isActive ? '#ccc' : ''
                            }}
                        >
                            {btn.label}
                        </button>
                    );
                })}
            </nav>

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
                <section
                    ref={settingsRef}
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
                        onKeyDown={(e) => handleKeyActivate(e, () => setShowSettings(false))}
                        onClick={() => setShowSettings(false)}
                        style={{ marginTop: '1rem' }}
                    >
                        Close Settings
                    </button>
                </section>
            )}

            {/* History Panel */}
            {showHistory && (
                <section
                    ref={historyRef}
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
                        onKeyDown={(e) => handleKeyActivate(e, () => setShowHistory(false))}
                        onClick={() => setShowHistory(false)}
                        style={{ marginTop: '1rem' }}
                    >
                        Close History
                    </button>
                </section>
            )}
        </div>
    );
}
