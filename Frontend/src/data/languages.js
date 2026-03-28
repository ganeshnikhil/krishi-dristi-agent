// src/data/languages.js
// India's 22 official languages from the 8th Schedule of the Constitution

export const PRIMARY_LANGUAGES = [
  {
    code: 'hi',
    name: 'Hindi',
    nativeName: 'हिन्दी',
    greeting: 'नमस्ते',
    flag: '🌾',
    script: 'Devanagari',
    color: '#e8f5e9',
    accent: '#2e7d32',
  },
  {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    greeting: 'Welcome',
    flag: '🌍',
    script: 'Latin',
    color: '#e3f2fd',
    accent: '#1565c0',
  },
];

export const OTHER_LANGUAGES = [
  { code: 'as',  name: 'Assamese',  nativeName: 'অসমীয়া',      greeting: 'নমস্কাৰ'         },
  { code: 'bn',  name: 'Bengali',   nativeName: 'বাংলা',         greeting: 'নমস্কার'          },
  { code: 'brx', name: 'Bodo',      nativeName: 'बड़ो',           greeting: 'नमस्कार'          },
  { code: 'doi', name: 'Dogri',     nativeName: 'डोगरी',          greeting: 'नमस्कार'          },
  { code: 'gu',  name: 'Gujarati',  nativeName: 'ગુજરાતી',        greeting: 'નમસ્તે'           },
  { code: 'kn',  name: 'Kannada',   nativeName: 'ಕನ್ನಡ',         greeting: 'ನಮಸ್ಕಾರ'         },
  { code: 'ks',  name: 'Kashmiri',  nativeName: 'कॉशुर',          greeting: 'آداب'             },
  { code: 'kok', name: 'Konkani',   nativeName: 'कोंकणी',         greeting: 'नमस्कार'          },
  { code: 'mai', name: 'Maithili',  nativeName: 'मैथिली',         greeting: 'प्रणाम'           },
  { code: 'ml',  name: 'Malayalam', nativeName: 'മലയാളം',         greeting: 'നമസ്കാരം'        },
  { code: 'mni', name: 'Manipuri',  nativeName: 'মৈতৈলোন্',       greeting: 'নমস্কার'          },
  { code: 'mr',  name: 'Marathi',   nativeName: 'मराठी',           greeting: 'नमस्कार'          },
  { code: 'ne',  name: 'Nepali',    nativeName: 'नेपाली',          greeting: 'नमस्ते'           },
  { code: 'or',  name: 'Odia',      nativeName: 'ଓଡ଼ିଆ',          greeting: 'ନମସ୍କାର'         },
  { code: 'pa',  name: 'Punjabi',   nativeName: 'ਪੰਜਾਬੀ',         greeting: 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ'  },
  { code: 'sa',  name: 'Sanskrit',  nativeName: 'संस्कृतम्',       greeting: 'नमस्ते'           },
  { code: 'sat', name: 'Santali',   nativeName: 'ᱥᱟᱱᱛᱟᱲᱤ',       greeting: 'ᱡᱚᱦᱟᱨ'         },
  { code: 'sd',  name: 'Sindhi',    nativeName: 'سنڌي',            greeting: 'ادب'              },
  { code: 'ta',  name: 'Tamil',     nativeName: 'தமிழ்',           greeting: 'வணக்கம்'         },
  { code: 'te',  name: 'Telugu',    nativeName: 'తెలుగు',          greeting: 'నమస్కారం'        },
  { code: 'ur',  name: 'Urdu',      nativeName: 'اردو',            greeting: 'السلام عليکم'     },
];

export const ALL_LANGUAGES = [...PRIMARY_LANGUAGES, ...OTHER_LANGUAGES];

// ─── API Configuration ─────────────────────────────────────────────────────
// Replace with your key to enable live translation.
// Recommended: Bhashini (bhashini.gov.in) — free for Indian languages
// Alternative: Google Cloud Translation API
export const TRANSLATION_API_KEY = null; // 'YOUR_API_KEY_HERE'