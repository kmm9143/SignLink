// hooks/useSpeech.js
import { useState } from "react";
import { speak } from "../utils/speech";

export default function useSpeech(settings) {
    const [speaking, setSpeaking] = useState(false);

    const speakText = (text) => {
        if (!settings?.SPEECH_ENABLED || !text) return;
        speak(text, {
            onStart: () => setSpeaking(true),
            onEnd: () => setSpeaking(false),
            onError: () => setSpeaking(false),
        });
    };

    return { speaking, speakText };
}