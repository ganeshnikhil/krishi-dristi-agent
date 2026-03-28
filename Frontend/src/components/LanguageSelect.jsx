// src/components/LanguageSelector/LanguageSelect.jsx

import { useState, useMemo } from 'react';
import { useApp } from '../context/AppContext';
import { PRIMARY_LANGUAGES, OTHER_LANGUAGES } from '../data/languages';
import './LanguageSelect.css';

export default function LanguageSelect() {
  const { setLanguage } = useApp();

  const [showOther, setShowOther] = useState(false);
  const [query, setQuery] = useState('');

  const filteredOther = useMemo(() => {
    if (!query.trim()) return OTHER_LANGUAGES;
    const q = query.toLowerCase();
    return OTHER_LANGUAGES.filter(
      l =>
        l.name.toLowerCase().includes(q) ||
        l.nativeName.toLowerCase().includes(q)
    );
  }, [query]);

  const handleSelect = (lang) => {
    console.log("CLICKED:", lang);
    setLanguage(lang);
  };

  return (
    <div className="ls-backdrop">
      <div className="ls-sheet">

        {/* Handle */}
        <div className="ls-handle" />

        {/* Header */}
        <div className="ls-header">
          <div className="ls-brand">
            <div className="ls-brand-icon">🌾</div>
            <div className="ls-brand-name">
              <span className="k">Krishi</span><span className="m">Mitra</span>
            </div>
          </div>

          <div className="ls-title">Choose your language</div>
          <div className="ls-subtitle">
            Select your preferred language for a better experience
          </div>
        </div>

        {/* Primary Languages */}
        <div className="ls-primary">
          {PRIMARY_LANGUAGES.map((lang) => (
            <button
              key={lang.code}
              onClick={() => handleSelect(lang)}
              className={`ls-primary-btn ${
                lang.code === 'hi' ? 'ls-btn-hindi' : 'ls-btn-english'
              }`}
            >
              <div className="ls-btn-flag">{lang.flag}</div>

              <div className="ls-btn-info">
                <div className="ls-btn-name">{lang.name}</div>
                <div className="ls-btn-native">{lang.nativeName}</div>
                <div className="ls-btn-script">{lang.script}</div>
              </div>

              <div className="ls-btn-arrow">→</div>
            </button>
          ))}
        </div>

        {/* Divider */}
        <div className="ls-divider">
          <div className="ls-divider-line" />
          <div className="ls-divider-text">or</div>
          <div className="ls-divider-line" />
        </div>

        {/* Other Languages Toggle */}
        <div
          className={`ls-other-toggle ${showOther ? 'open' : ''}`}
          onClick={() => {
            setShowOther(!showOther);
            setQuery('');
          }}
        >
          <div className="ls-other-toggle-left">
            <span className="ls-other-toggle-icon">🌐</span>
            <span className="ls-other-toggle-text">Other Languages</span>
            <span className="ls-other-toggle-count">
              {OTHER_LANGUAGES.length}
            </span>
          </div>

          <span className="ls-other-toggle-chevron">⌄</span>
        </div>

        {/* Other Languages Panel */}
        {showOther && (
          <div className="ls-other-panel">

            <div className="ls-search-wrap">
              <span className="ls-search-icon">🔍</span>
              <input
                type="text"
                placeholder="Search language..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="ls-search"
              />
            </div>

            <div className="ls-lang-grid">
              {filteredOther.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => handleSelect(lang)}
                  className="ls-lang-item"
                >
                  <div className="ls-lang-item-name">{lang.name}</div>
                  <div className="ls-lang-item-native">{lang.nativeName}</div>
                  <div className="ls-lang-item-greeting">{lang.greeting}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Footer Note */}
        <div className="ls-footer-note">
          <p>
            🌍 Supports 22 official Indian languages.<br />
            More languages can be enabled via API integration.
          </p>
        </div>

      </div>
    </div>
  );
}