// DESCRIPTION:  This utility provides reusable Text-to-Speech (TTS) functions
//               using the built-in Web Speech API. It allows the app to
//               audibly read out predictions, labels, and messages. It also
//               includes audio device detection to ensure speech output
//               functions gracefully when no speakers/headphones are connected.
// LANGUAGE:     JAVASCRIPT
// SOURCE(S):    [1] MDN Web Docs. SpeechSynthesis API. Retrieved October 5, 2025, from
//                   https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis
//               [2] W3C Web Speech API Draft. Retrieved October 5, 2025, from
//                   https://wicg.github.io/speech-api/
//               [3] Stack Overflow. (2023). Check for available audio output devices in JavaScript.
//                   Retrieved October 5, 2025, from https://stackoverflow.com/questions/59797352

// -------------------------------------------------------------------
// Step 1: Check for available audio output devices
// -------------------------------------------------------------------
export async function hasAudioOutputDevice() {
    try {
        // Enumerate all available media devices (input/output)
        const devices = await navigator.mediaDevices.enumerateDevices();

        // Look specifically for devices capable of audio output
        const hasOutput = devices.some((d) => d.kind === "audiooutput");

        if (!hasOutput) {
            console.warn("[ERROR] No audio output device detected.");
            alert("No audio device detected. Speech output unavailable."); // Required for TC-US7-04
            return false;
        }

        return true;
    } catch (err) {
        console.error("[ERROR] Failed to check audio devices:", err);
        alert("Unable to verify audio device availability.");
        return false;
    }
}

// -------------------------------------------------------------------
// Step 2: Speak text aloud using the browser's SpeechSynthesis API
// -------------------------------------------------------------------
export async function speak(text, options = {}) {
    if (!text || typeof window.speechSynthesis === "undefined") return;

    // ✅ Run audio device check before speaking (TC-US7-04)
    const audioAvailable = await hasAudioOutputDevice();
    if (!audioAvailable) return;

    const utterance = new SpeechSynthesisUtterance(text);

    // Optional configuration
    utterance.lang = options.lang || "en-US";     // Language (default English)
    utterance.rate = options.rate || 1;           // Speed (1 = normal)
    utterance.pitch = options.pitch || 1;         // Pitch (1 = normal)
    utterance.volume = options.volume || 1;       // Volume (0–1)

    if (options.onStart) utterance.onstart = options.onStart;
    if (options.onEnd) utterance.onend = options.onEnd;
    if (options.onError) utterance.onerror = options.onError;

    // Cancel any ongoing speech before starting a new one
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
}

// -------------------------------------------------------------------
// Step 3: Stop any currently playing speech
// -------------------------------------------------------------------
export function stopSpeech() {
    if (typeof window.speechSynthesis !== "undefined") {
        window.speechSynthesis.cancel();
    }
}

// -------------------------------------------------------------------
// Step 4: Check if speech is currently active
// -------------------------------------------------------------------
export function isSpeaking() {
    return (
        typeof window.speechSynthesis !== "undefined" &&
        window.speechSynthesis.speaking
    );
}