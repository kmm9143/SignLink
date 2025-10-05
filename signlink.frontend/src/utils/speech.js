// DESCRIPTION:  This utility provides reusable Text-to-Speech (TTS) functions
//               using the built-in Web Speech API. It allows the app to
//               audibly read out predictions, labels, and messages.
// LANGUAGE:     JAVASCRIPT
// SOURCE(S):    [1] MDN Web Docs. SpeechSynthesis API. Retrieved October 5, 2025, from
//                   https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis
//               [2] W3C Web Speech API Draft. Retrieved October 5, 2025, from
//                   https://wicg.github.io/speech-api/

// -------------------------------------------------------------------
// Step 1: Speak text aloud using the browser's SpeechSynthesis API
// -------------------------------------------------------------------
export function speak(text, options = {}) {
    if (!text || typeof window.speechSynthesis === "undefined") return;

    const utterance = new SpeechSynthesisUtterance(text);

    // Optional configuration
    utterance.lang = options.lang || "en-US";     // Language (default English)
    utterance.rate = options.rate || 1;           // Speed (1 = normal)
    utterance.pitch = options.pitch || 1;         // Pitch (1 = normal)
    utterance.volume = options.volume || 1;       // Volume (0–1)

    // Cancel any ongoing speech before starting a new one
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
}

// -------------------------------------------------------------------
// Step 2: Stop any currently playing speech
// -------------------------------------------------------------------
export function stopSpeech() {
    if (typeof window.speechSynthesis !== "undefined") {
        window.speechSynthesis.cancel();
    }
}

// -------------------------------------------------------------------
// Step 3: Check if speech is currently active
// -------------------------------------------------------------------
export function isSpeaking() {
    return typeof window.speechSynthesis !== "undefined" && window.speechSynthesis.speaking;
}