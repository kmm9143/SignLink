import { useState } from 'react';
import ImageTranslate from './ImageTranslate.jsx';
import WebcamTranslate from './WebcamTranslate.jsx';

export default function App() {
    const [mode, setMode] = useState('image'); // 'image' or 'webcam'

    return (
        <div style={{ padding: '2rem' }}>
            <h1>ASL Translator</h1>

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

            {mode === 'image' && <ImageTranslate />}
            {mode === 'webcam' && <WebcamTranslate />}
        </div>
    );
}
