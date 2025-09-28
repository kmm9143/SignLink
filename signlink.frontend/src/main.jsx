// DESCRIPTION:  Entry point for the React ASL Translator application.  
//               It loads global styles, mounts the root component (`App`),  
//               and wraps the app with React's StrictMode to highlight potential issues.  
// LANGUAGE:     JAVASCRIPT / React (application bootstrap)

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';   // global stylesheet
import App from './App.jsx';  // main application component

// -----------------------------------------------------------------------------------
// Create React root and render the application
// -----------------------------------------------------------------------------------
createRoot(document.getElementById('root')).render(
    <StrictMode>
        {/* Wrap App in StrictMode to catch unsafe lifecycles, warnings, etc. */}
        <App />
    </StrictMode>,
);