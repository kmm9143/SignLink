// Minimal TTS service wrapper — no UI alerts, returns boolean / invokes callbacks.
export async function hasAudioOutputDevice() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        return devices.some((d) => d.kind === "audiooutput");
    } catch (err) {
        console.error("Failed to enumerate devices for audio output check", err);
        return false;
    }
}

export async function speak(text, options = {}) {
    if (!text || typeof window === "undefined" || typeof window.speechSynthesis === "undefined") {
        options.onError?.(new Error("SpeechSynthesis unavailable"));
        return;
    }

    const audioAvailable = await hasAudioOutputDevice();
    if (!audioAvailable) {
        options.onError?.(new Error("No audio output device"));
        return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = options.lang || "en-US";
    utterance.rate = options.rate ?? 1;
    utterance.pitch = options.pitch ?? 1;
    utterance.volume = options.volume ?? 1;

    if (options.onStart) utterance.onstart = options.onStart;
    if (options.onEnd) utterance.onend = options.onEnd;
    if (options.onError) utterance.onerror = () => options.onError(new Error("Speech synthesis error"));

    try {
        window.speechSynthesis.cancel(); // stop any prior utterance optionally
        window.speechSynthesis.speak(utterance);
    } catch (err) {
        options.onError?.(err);
    }
}