// src/components/sarvamTranslate.js
// Sarvam AI Translate API — https://api.sarvam.ai/translate
// Uses VITE_SARVAM_API_KEY from frontend .env

const SARVAM_ENDPOINT = 'https://api.sarvam.ai/translate';

// Map our short language codes to Sarvam BCP-47 codes
const SARVAM_LANG_MAP = {
  en:  'en-IN',
  hi:  'hi-IN',
  ta:  'ta-IN',
  te:  'te-IN',
  kn:  'kn-IN',
  ml:  'ml-IN',
  bn:  'bn-IN',
  mr:  'mr-IN',
  gu:  'gu-IN',
  pa:  'pa-IN',
  or:  'od-IN',   // Odia
  as:  'as-IN',
  ur:  'ur-IN',
  sa:  'sa-IN',
  // Fallback for unsupported codes — route through English
};

/**
 * Translate text using Sarvam AI.
 *
 * @param {string} text         Text to translate
 * @param {string} targetCode   Short language code (e.g. 'hi', 'ta') for output
 * @param {string} sourceCode   Short language code for input (e.g. 'en', 'hi')
 * @returns {Promise<string>}   Translated text (or original on failure)
 */
export async function sarvamTranslate(text, targetCode = 'en', sourceCode = 'en') {
  const apiKey = import.meta.env.VITE_SARVAM_API_KEY;

  if (!apiKey) {
    console.warn('[Sarvam] VITE_SARVAM_API_KEY not set — skipping translation');
    return text;
  }

  const sourceLang = SARVAM_LANG_MAP[sourceCode] ?? 'en-IN';
  const targetLang = SARVAM_LANG_MAP[targetCode] ?? 'en-IN';

  // No-op if source == target
  if (sourceLang === targetLang) return text;

  try {
    const res = await fetch(SARVAM_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'api-subscription-key': apiKey,
      },
      body: JSON.stringify({
        input: text,
        source_language_code: sourceLang,
        target_language_code: targetLang,
        speaker_gender: 'Male',
        mode: 'formal',
        model: 'mayura:v1',
        enable_preprocessing: true,
      }),
    });

    if (!res.ok) {
      const err = await res.text();
      console.error('[Sarvam] Translation failed:', res.status, err);
      return text; // Graceful fallback
    }

    const data = await res.json();
    return data.translated_text ?? text;
  } catch (err) {
    console.error('[Sarvam] Network error during translation:', err);
    return text; // Graceful fallback
  }
}

/**
 * Check if a given language code is supported by Sarvam translation.
 */
export function isSarvamSupported(code) {
  return code in SARVAM_LANG_MAP && SARVAM_LANG_MAP[code] !== 'en-IN';
}
