import { useState, useEffect } from "react";

export default function useUserSettings(userId) {
    const [settings, setSettings] = useState(null);

    useEffect(() => {
        const fetchSettings = async () => {
            try {
                // use relative path so Vite proxy forwards to backend
                const res = await fetch(`/settings/${userId}`, { credentials: "include" });
                setSettings(res.ok ? await res.json() : { SPEECH_ENABLED: false });
            } catch {
                setSettings({ SPEECH_ENABLED: false });
            }
        };
        if (userId != null) fetchSettings();
    }, [userId]);

    return settings;
}