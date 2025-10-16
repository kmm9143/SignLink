// hooks/useUserSettings.js
import { useState, useEffect } from "react";

export default function useUserSettings(userId) {
    const [settings, setSettings] = useState(null);

    useEffect(() => {
        const fetchSettings = async () => {
            try {
                const res = await fetch(`http://localhost:8000/settings/${userId}`);
                setSettings(res.ok ? await res.json() : { SPEECH_ENABLED: false });
            } catch {
                setSettings({ SPEECH_ENABLED: false });
            }
        };
        fetchSettings();
    }, [userId]);

    return settings;
}