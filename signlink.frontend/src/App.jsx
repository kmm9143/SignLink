// DESCRIPTION:  This React component serves as the main entry point for the ASL Translator web application.
//                It manages user authentication, translation mode switching (image or webcam),
//                and access to user-specific settings. The app integrates multiple child components,
//                including authentication, translation modules, and settings management.
// LANGUAGE:     JAVASCRIPT (React.js)
// SOURCE(S):    [1] React Documentation. (n.d.). Using the State Hook. Retrieved September 27, 2025, from https://react.dev/reference/react/useState
//               [2] React Documentation. (n.d.). Conditional Rendering. Retrieved September 27, 2025, from https://react.dev/learn/conditional-rendering
//               [3] MDN Web Docs. (n.d.). JSX syntax and rendering logic. Retrieved September 27, 2025, from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/JSX

// -----------------------------------------------------------------------------
// Step 1: Import React dependencies and local components
// -----------------------------------------------------------------------------
import { useState } from 'react';                    // Import React Hook for managing component state
import ImageTranslate from './ImageTranslate.jsx';   // Component for image-based ASL translation
import WebcamTranslate from './WebcamTranslate.jsx'; // Component for webcam-based ASL translation
import UserSettings from './UserSettings.jsx';       // Component for managing user preferences/settings
import Auth from './Auth.jsx';                       // Component for user login/signup functionality

// -----------------------------------------------------------------------------
// Step 2: Define main App component
// -----------------------------------------------------------------------------
export default function App() {
    // -------------------------------------------------------------------------
    // State variables
    // -------------------------------------------------------------------------
    const [user, setUser] = useState(null);          // Holds the logged-in user info (retrieved from backend)
    const [mode, setMode] = useState('image');       // Current translation mode: "image" or "webcam"
    const [showSettings, setShowSettings] = useState(false); // Boolean to toggle the settings panel visibility

    // -------------------------------------------------------------------------
    // Step 3: Conditional rendering - authentication check
    // -------------------------------------------------------------------------
    if (!user) {                                     // If no user is logged in
        // Render Auth component and pass callback to update user state after login
        return <Auth onLogin={(userData) => setUser(userData)} />;
    }

    // -------------------------------------------------------------------------
    // Step 4: Render main application UI (after login)
    // -------------------------------------------------------------------------
    return (
        <div style={{ padding: '2rem' }}>            {/* Container with consistent padding */}
            <h1>ASL Translator</h1>                  {/* Application title */}

            {/* Display logged-in user information */}
            <p style={{ fontSize: "0.9rem", color: "#666" }}>
                Logged in as <strong>{user.username}</strong>
            </p>

            {/* -----------------------------------------------------------------
                Top navigation buttons: switch translation modes and open settings
            ----------------------------------------------------------------- */}
            <div style={{ marginBottom: '1rem' }}>
                {/* Button to select image upload mode */}
                <button
                    onClick={() => setMode('image')}  // Change mode to 'image'
                    style={{ marginRight: '1rem', backgroundColor: mode === 'image' ? '#ccc' : '' }} // Highlight active mode
                >
                    Upload Image
                </button>

                {/* Button to select webcam mode */}
                <button
                    onClick={() => setMode('webcam')} // Change mode to 'webcam'
                    style={{ marginRight: '1rem', backgroundColor: mode === 'webcam' ? '#ccc' : '' }} // Highlight active mode
                >
                    Webcam
                </button>

                {/* Button to open settings panel */}
                <button
                    onClick={() => setShowSettings(true)} // Show settings section
                    style={{ float: 'right' }}           // Position on right side of menu
                >
                    Settings
                </button>
            </div>

            {/* -----------------------------------------------------------------
                Step 5: Conditional content rendering (translator or settings)
            ----------------------------------------------------------------- */}
            {/* Show translation components when settings are hidden */}
            {!showSettings && (
                <>
                    {/* Render image translation if image mode selected */}
                    {mode === 'image' && <ImageTranslate userId={user.id} />}

                    {/* Render webcam translation if webcam mode selected */}
                    {mode === 'webcam' && <WebcamTranslate userId={user.id} />}
                </>
            )}

            {/* Show settings panel when toggled on */}
            {showSettings && (
                <div style={{ border: '1px solid #ccc', padding: '1rem', marginTop: '1rem' }}>
                    {/* Pass userId to UserSettings so backend API can fetch/update related preferences */}
                    <UserSettings userId={user.id} />

                    {/* Button to close settings view and return to translator */}
                    <button onClick={() => setShowSettings(false)} style={{ marginTop: '1rem' }}>
                        Close Settings
                    </button>
                </div>
            )}
        </div>
    );
}