import React from 'react';

export default function LoadingBar({ progress = null, color = '#4caf50', height = '8px' }) {
    if (progress === null) {
        return (
            <div style={{
                width: '100%',
                height,
                background: '#333',
                borderRadius: '4px',
                overflow: 'hidden',
                marginTop: '1rem',
            }}>
                <div style={{
                    width: '100%',
                    height: '100%',
                    background: color,
                    animation: 'progressIndeterminate 1.5s infinite linear',
                }} />
                <style>
                    {`@keyframes progressIndeterminate {
              0% { transform: translateX(-100%); }
              100% { transform: translateX(100%); }
            }`}
                </style>
            </div>
        );
    }

    return (
        <div style={{
            width: '100%',
            height,
            background: '#333',
            borderRadius: '4px',
            overflow: 'hidden',
            marginTop: '1rem',
        }}>
            <div style={{
                width: `${progress}%`,
                height: '100%',
                background: color,
                transition: 'width 0.3s ease',
            }} />
        </div>
    );
}