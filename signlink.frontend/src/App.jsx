// DESCRIPTION:  This is the top-level React component for the ASL translator app.  
//               It lets users switch between “Upload Image” mode and “Webcam” mode,  
//               and conditionally renders the appropriate translator component.  
// LANGUAGE:     JAVASCRIPT / React (functional components, hooks)

import { useState } from 'react';
import ImageTranslate from './ImageTranslate.jsx';
import WebcamTranslate from './WebcamTranslate.jsx';

export default function App() {
    // -----------------------------------------------------------------------------------
    // State: which translation mode is active
    // -----------------------------------------------------------------------------------
    const [mode, setMode] = useState('image');  // possible values: 'image' or 'webcam'

    // -----------------------------------------------------------------------------------
    // Render UI
    // -----------------------------------------------------------------------------------
    return (
        <div style={{ padding: '2rem' }}>
            <h1>ASL Translator</h1>

            {/* Mode selection buttons */}
            <div style={{ marginBottom: '1rem' }}>
                <button
                    onClick={() => setMode('image')}
                    style={{ marginRight: '1rem', backgroundColor: mode === 'image' ? '#ccc' : '' }}
                >
                    Upload Image
                </button>
                <button
                    onClick={() => setMode('webcam')}
                    style={{ backgroundColor: mode === 'webcam' ? '#ccc' : '' }}
                >
                    Webcam
                </button>
            </div>

            {/* Conditionally render either the image upload translator or the webcam translator */}
            {mode === 'image' && <ImageTranslate />}
            {mode === 'webcam' && <WebcamTranslate />}
        </div>
    );
}