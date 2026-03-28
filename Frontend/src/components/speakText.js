// src/components/speakText.js
// Uses Sarvam AI TTS (bulbul:v3 · shreya) when VITE_SARVAM_API_KEY is set.
// Falls back to the browser Web Speech API otherwise.

const SARVAM_TTS_ENDPOINT = 'https://api.sarvam.ai/text-to-speech';

// Module-level reference to the currently playing Sarvam audio element.
// Allows stopSpeech() to cancel it immediately.
let _currentAudio = null;

/**
 * Stop any in-progress speech — both Sarvam audio AND browser SpeechSynthesis.
 * Call this from the mute button or when the voice overlay closes.
 */
export function stopSpeech() {
  if (_currentAudio) {
    _currentAudio.pause();
    _currentAudio.currentTime = 0;
    _currentAudio = null;
  }
  window.speechSynthesis.cancel();
}


// Map short language codes → Sarvam BCP-47 codes for TTS
const TTS_LANG_MAP = {
  'en-IN': 'en-IN',
  'hi-IN': 'hi-IN',
  'ta-IN': 'ta-IN',
  'te-IN': 'te-IN',
  'kn-IN': 'kn-IN',
  'ml-IN': 'ml-IN',
  'bn-IN': 'bn-IN',
  'mr-IN': 'mr-IN',
  'gu-IN': 'gu-IN',
  'pa-IN': 'pa-IN',
  'od-IN': 'od-IN',
  'as-IN': 'as-IN',
  'ur-IN': 'ur-IN',
};

/**
 * Strip all special / non-speech characters from text before speaking.
 * Removes: emojis, markdown (**, __, ##, >, `), bullet symbols,
 *          arrows, currency symbols other than ₹, brackets, pipes, etc.
 */
export function cleanForSpeech(raw) {
  if (!raw) return '';

  return raw
    // Remove emoji (broad Unicode ranges)
    .replace(/[\u{1F300}-\u{1FFFF}]/gu, '')
    .replace(/[\u{2600}-\u{26FF}]/gu, '')
    .replace(/[\u{2700}-\u{27BF}]/gu, '')
    // Remove markdown formatting characters
    .replace(/[*_~`#>|]/g, '')
    // Remove bullet / arrow / special punctuation symbols
    .replace(/[•·→←↑↓⇒⇐✓✗✔✘◆◇○●■□▸▶◀▼▲]/g, '')
    // Remove brackets (but keep content inside)
    .replace(/[[\]{}()]/g, '')
    // Collapse multiple spaces / newlines into a single space
    .replace(/\s+/g, ' ')
    // Remove leading/trailing whitespace
    .trim();
}

/**
 * Speak text using Sarvam AI TTS (shreya voice) or fall back to the browser.
 *
 * @param {string} text  The text to speak (will be cleaned automatically)
 * @param {string} lang  BCP-47 language code, e.g. 'hi-IN', 'en-IN'
 */
export async function speakText(text, lang = 'en-IN') {
  const clean = cleanForSpeech(text);
  if (!clean) return;

  const apiKey = import.meta.env.VITE_SARVAM_API_KEY;
  const targetLang = TTS_LANG_MAP[lang] ?? 'en-IN';

  // ── Sarvam TTS path ──────────────────────────────────────────────────────
  if (apiKey) {
    try {
      const res = await fetch(SARVAM_TTS_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'api-subscription-key': apiKey,
        },
        body: JSON.stringify({
          inputs: [clean],
          target_language_code: targetLang,
          speaker: 'shreya',
          model: 'bulbul:v3',
          enable_preprocessing: true
        }),
      });

      if (res.ok) {
        const data = await res.json();
        const audioChunks = data.audios ?? [];
        if (audioChunks.length > 0) {
          for (const b64 of audioChunks) {
            const binary = atob(b64);
            const bytes = new Uint8Array(binary.length);
            for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
            const blob = new Blob([bytes], { type: 'audio/wav' });
            const url = URL.createObjectURL(blob);
            const audio = new Audio(url);
            _currentAudio = audio;
            await new Promise((resolve) => {
              audio.onended = () => { URL.revokeObjectURL(url); _currentAudio = null; resolve(); };
              audio.onerror = () => { URL.revokeObjectURL(url); _currentAudio = null; resolve(); };
              audio.play().catch(resolve);
            });
          }
          return; // Success
        }
      } else {
        const errText = await res.text();
        console.error('[Sarvam TTS] API Error:', res.status, errText);
        // If API key is present but it fails, we STOP here to avoid the "man" voice fallback
        // unless it's a critical failure where the user would prefer ANY voice.
        // But the user specifically asked for Shreya only.
        return; 
      }
    } catch (err) {
      console.error('[Sarvam TTS] Network failure:', err);
      return;
    }
  }

  // ── Browser Web Speech API fallback (Only if NO API KEY) ──────────────────
  const utterance = new SpeechSynthesisUtterance(clean);
  utterance.lang = lang;
  utterance.rate = 1;
  utterance.pitch = 1;

  const trySpeak = () => {
    const voices = window.speechSynthesis.getVoices();
    const voice = voices.find(v => v.lang === lang);
    if (voice) utterance.voice = voice;
    window.speechSynthesis.speak(utterance);
  };

  const voices = window.speechSynthesis.getVoices();
  if (voices.length === 0) {
    window.speechSynthesis.onvoiceschanged = trySpeak;
  } else {
    trySpeak();
  }
}