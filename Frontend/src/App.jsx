// src/App.jsx
import { useState, useRef, useEffect, useCallback } from 'react'
import './App.css'
import soilNormal from './assets/soil_normal.svg'
import clouds from './assets/clouds.svg'
import rainDrops from './assets/placidplace-drops-13474.gif'
import navbarBottomBorder from './assets/navbar-bottom-border.svg'
import pond from './assets/pond.svg'
import LanguageSelect from './components/LanguageSelect.jsx'
import { useApp } from './context/AppContext.jsx'
import useSpeechRecognition from './components/useSpeechRecognition'
import { speakText } from './components/speakText'
import ChatPanel from './components/ChatPanel.jsx'   // NEW

/* ── Mock API responses (replace with real fetch later) ── */
const MOCK_RESPONSES = [
  "Hello farmer! Soil moisture is at 42% — optimal for wheat right now.",
  "Based on current weather, I recommend delaying irrigation by 24 hours.",
  "Rain is expected tonight. No irrigation needed today.",
  "Your wheat crop is at Stage 3. Fertilization is due in 3 days.",
  "Soil pH is 6.8 — excellent for wheat. Keep monitoring daily.",
  "High humidity today at 82%. Watch for fungal disease on leaves.",
  "Wind from North-East at 12 km/h — good conditions for pesticide spraying.",
];

/* ── Helpers ── */
function getTranscriptLines(text) {
  if (!text?.trim()) return [];
  const words = text.trim().split(' ');
  const lines = [];
  let cur = '';
  for (const w of words) {
    const test = cur ? `${cur} ${w}` : w;
    if (test.length > 42) { if (cur) lines.push(cur); cur = w; }
    else cur = test;
  }
  if (cur) lines.push(cur);
  return lines.slice(-5);
}

function formatTimer(secs) {
  const m = Math.floor(secs / 60).toString().padStart(2, '0');
  const s = (secs % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

function App() {
  const today       = new Date().getDate();
  const now         = new Date();
  const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();

  /* existing */
  const [selectedDate, setSelectedDate] = useState(today);
  const [isChatOpen,   setIsChatOpen]   = useState(false);
  const [isScrolled,   setIsScrolled]   = useState(false);
  const sliderRef       = useRef(null);
  const isUserScrolling = useRef(false);
  const scrollTimeout   = useRef(null);

  /* NEW */
  const [isChatPanelOpen, setIsChatPanelOpen] = useState(false);
  const [recordingTime,   setRecordingTime]   = useState(0);
  const [isProcessing,    setIsProcessing]    = useState(false);
  const [messages, setMessages] = useState([
    { id: 1, type: 'bot', text: 'Namaste! 🌾 I am KrishiBot. Speak or type to ask anything about your farm.', time: new Date() },
  ]);

  const { hasChosen, resetLanguage } = useApp();

  const { transcript, isListening, startListening, stopListening, resetTranscript } =
    useSpeechRecognition('en-IN');

  const dates = Array.from({ length: daysInMonth * 3 }, (_, i) => (i % daysInMonth) + 1);

  /* Navbar scroll shadow */
  useEffect(() => {
    const fn = () => setIsScrolled(window.scrollY > 10);
    window.addEventListener('scroll', fn, { passive: true });
    return () => window.removeEventListener('scroll', fn);
  }, []);

  /* Auto-scroll date to today */
  useEffect(() => {
    if (!sliderRef.current) return;
    const items = sliderRef.current.querySelectorAll('.date-item');
    items[daysInMonth + today - 1]?.scrollIntoView({ behavior: 'auto', block: 'nearest', inline: 'center' });
  }, [today, daysInMonth]);

  /* Recording timer */
  useEffect(() => {
    let iv;
    if (isListening) { setRecordingTime(0); iv = setInterval(() => setRecordingTime(t => t + 1), 1000); }
    else setRecordingTime(0);
    return () => clearInterval(iv);
  }, [isListening]);

  /* Send query when mic stops */
  useEffect(() => {
    if (!isListening && transcript.trim()) handleVoiceQuery(transcript.trim());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isListening]);

  const handleVoiceQuery = useCallback(async (text) => {
    setMessages(p => [...p, { id: Date.now(), type: 'user', text, time: new Date() }]);
    setIsProcessing(true);

    /* ── swap this block for real API ── */
    await new Promise(r => setTimeout(r, 1000 + Math.random() * 600));
    const reply = MOCK_RESPONSES[Math.floor(Math.random() * MOCK_RESPONSES.length)];
    /* ─────────────────────────────── */

    setMessages(p => [...p, { id: Date.now() + 1, type: 'bot', text: reply, time: new Date() }]);
    setIsProcessing(false);
    speakText(reply, 'en-IN');
    resetTranscript();
  }, [resetTranscript]);

  const handleScroll = () => {
    if (!sliderRef.current) return;
    isUserScrolling.current = true;
    clearTimeout(scrollTimeout.current);
    scrollTimeout.current = setTimeout(() => { isUserScrolling.current = false; }, 150);

    const slider = sliderRef.current;
    const mid    = slider.getBoundingClientRect().left + slider.getBoundingClientRect().width / 2;
    const items  = slider.querySelectorAll('.date-item');
    let closest  = selectedDate, minD = Infinity;
    items.forEach(item => {
      const d = Math.abs(item.getBoundingClientRect().left + item.getBoundingClientRect().width / 2 - mid);
      if (d < minD) { minD = d; closest = parseInt(item.querySelector('.date-number').innerText); }
    });
    if (closest !== selectedDate) setSelectedDate(closest);
  };

  const handleDateClick = (date, index) => {
    setSelectedDate(date);
    sliderRef.current?.querySelectorAll('.date-item')[index]
      ?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
  };

  const handleCloseVoice = () => {
    stopListening();
    setIsChatPanelOpen(false);
    setIsChatOpen(false);
  };

  return (
    <>
      {!hasChosen && <LanguageSelect />}

      {/* ── NAVBAR ── */}
      <nav className={`navbar${isScrolled ? ' navbar--scrolled' : ''}`}>
        <div className="brand-logo">
          <div className="brand-text">
            <span className="brand-krishi">कृषि</span><span className="brand-mitra">Mitra</span>
          </div>
        </div>
        <div className="navbar-center">
          <div className="location-chip">
            <span className="location-dot" /><span>Dehradun, IN</span>
          </div>
        </div>
        <button className="nav-icon-btn language-btn" onClick={resetLanguage} title="Change Language">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="2" y1="12" x2="22" y2="12"/>
            <path d="M12 2a15 15 0 0 1 0 20"/><path d="M12 2a15 15 0 0 0 0 20"/>
          </svg>
        </button>
        <div className="navbar-right">
          <button className="nav-icon-btn" aria-label="Notifications">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
            </svg>
            <span className="nav-badge">3</span>
          </button>
          <div className="hamburger">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
              <line x1="4" y1="6" x2="20" y2="6"/>
              <line x1="4" y1="12" x2="16" y2="12"/>
              <line x1="4" y1="18" x2="20" y2="18"/>
            </svg>
          </div>
        </div>
      </nav>

      <img src={navbarBottomBorder} alt="" className="navbar-bottom-border" aria-hidden="true" />

      <main className="dashboard-content">
        {/* HERO */}
        <section className="hero-section">
          <div className="hero">
            <img src={rainDrops}  alt="" className="rain-gif"    aria-hidden="true" />
            <img src={clouds}     alt="" className="clouds-img"  aria-hidden="true" />
            <img src={soilNormal} alt="" className="soil-img"    aria-hidden="true" />
            <div className="hero-center">
              <div className="hero-weather-badge"><span className="hero-weather-icon">🌧️</span><span>Light Rain</span></div>
              <div className="hero-temp">24°<span className="hero-temp-unit">C</span></div>
              <div className="hero-desc">Continuous showers · Feels like 21°C</div>
            </div>
            <div className="hero-widget weather-widget">
              <div className="widget-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0e6fa0" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/>
                </svg>
              </div>
              <div className="widget-info"><div className="widget-val">82%</div><div className="widget-label">Humidity</div></div>
            </div>
            <div className="hero-widget soil-widget">
              <div className="widget-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2e7d32" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>
                </svg>
              </div>
              <div className="widget-info"><div className="widget-val">42%</div><div className="widget-label">Moist Soil</div></div>
            </div>
            <div className="hero-widget wind-widget">
              <div className="widget-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5d4037" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9.59 4.59A2 2 0 1 1 11 8H2m10.59 11.41A2 2 0 1 0 14 16H2m15.73-8.27A2.5 2.5 0 1 1 19.5 12H2"/>
                </svg>
              </div>
              <div className="widget-info"><div className="widget-val">12 km/h</div><div className="widget-label">NE Wind</div></div>
            </div>
          </div>
        </section>

        {/* DATE STRIP */}
        <section className="timeline-section">
          <div className="section-divider" />
          <div className="date-slider-wrapper">
            <div className="date-slider-header">
              <div className="month-year">{now.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</div>
              <div className="slider-hint">Tap a date to view conditions</div>
            </div>
            <div className="date-slider" ref={sliderRef} onScroll={handleScroll}>
              {dates.map((date, index) => {
                const dayName = new Date(now.getFullYear(), now.getMonth(), date).toLocaleDateString('en-US', { weekday: 'short' }).toUpperCase();
                const isToday = date === today && index >= daysInMonth && index < daysInMonth * 2;
                let distance = Math.abs(selectedDate - date);
                if (distance > daysInMonth / 2) distance = daysInMonth - distance;
                let cls = 'date-item';
                if      (distance === 0) cls += ' active-date';
                else if (distance === 1) cls += ' near-date';
                else                     cls += ' far-date';
                return (
                  <div key={`${date}-${index}`} className={cls} onClick={() => handleDateClick(date, index)}>
                    <div className="day-label">{dayName}</div>
                    <div className="date-number">{date}</div>
                    {isToday && <div className="today-marker">TODAY</div>}
                  </div>
                );
              })}
            </div>
          </div>
          <div className="section-divider" />
        </section>

        {/* INSIGHTS */}
        <section className="insights-section">
          <div className="section-header">
            <h2 className="section-title">Farm Insights</h2>
            <p className="section-subtitle">Real-time status &amp; metrics</p>
          </div>
          <div className="updates">
            <div className="update-heading">Today's Activity</div>
            <div className="card card-weather">
              <div className="card-top"><div className="card-label"><span className="card-dot dot-blue"/>Weather Forecast</div><span className="card-badge badge-rain">🌧 Rain</span></div>
              <div className="card-metric">24°C</div>
              <div className="card-desc">Light showers throughout the day. Wind from North-East at 12 km/h. UV index: Low.</div>
              <div className="card-row"><div className="card-chip">💧 Humidity 82%</div><div className="card-chip">🌬 Wind 12 km/h</div><div className="card-chip">🌡 Feels 21°C</div></div>
            </div>
            <div className="card card-soil">
              <div className="card-top"><div className="card-label"><span className="card-dot dot-green"/>Soil Health</div><span className="card-badge badge-good">✅ Optimal</span></div>
              <div className="card-metric">pH 6.8</div>
              <div className="card-desc">Soil moisture at optimal levels for current wheat crop stage. No irrigation required today.</div>
              <div className="card-row"><div className="card-chip">💧 Moisture 42%</div><div className="card-chip">🌡 Soil 18°C</div><div className="card-chip">⚗️ N–P–K OK</div></div>
            </div>
            <div className="card card-advisory">
              <div className="card-top"><div className="card-label"><span className="card-dot dot-amber"/>Advisory</div><span className="card-badge badge-action">⚡ Action</span></div>
              <div className="card-metric">Irrigate</div>
              <div className="card-desc">Wheat crop needs irrigation within 24 hours. Rain today may reduce requirement — reassess tomorrow.</div>
              <div className="card-row"><div className="card-chip">📅 Fertilise in 3 days</div><div className="card-chip">🌾 Stage 3</div></div>
            </div>
            <div className="card card-scheme">
              <div className="card-top"><div className="card-label"><span className="card-dot dot-purple"/>Government Scheme</div><span className="card-badge badge-scheme">🏛 New</span></div>
              <div className="card-metric-sm">PM Fasal Bima</div>
              <div className="card-desc">Enroll in Pradhan Mantri Fasal Bima Yojana before the season deadline to protect your crop.</div>
              <div className="card-cta"><a href="https://pmfby.gov.in/" target="_blank" rel="noopener noreferrer" className="card-cta-btn">Apply Now →</a></div>
            </div>
          </div>
        </section>
      </main>

      {/* FOOTER */}
      <footer className="footer">
        <img src={pond} className="footer-pond" alt="" aria-hidden="true" />
        <div className="footer-content">
          <div className="footer-brand">
            <span className="brand-krishi">Krishi</span><span className="brand-mitra">Mitra</span>
          </div>
          <p className="footer-tagline">Empowering India's farmers with AI</p>
          <div className="footer-links">
            <a href="#about"   className="footer-link">About</a>
            <a href="#privacy" className="footer-link">Privacy</a>
            <a href="#terms"   className="footer-link">Terms</a>
            <a href="#contact" className="footer-link">Contact</a>
          </div>
          <div className="footer-divider" />
          <div className="footer-copyright">© 2026 कृषि Mitra · Made with 🌿 for Indian Farmers</div>
        </div>
      </footer>

      {/* CHATBOT FAB */}
      {!isChatOpen && (
        <div className="chatbot-container">
          <div className="chatbot-plant plant-1"><div className="plant-stem"/><div className="plant-flower">🌸</div></div>
          <div className="chatbot-plant plant-2"><div className="plant-stem"/><div className="plant-flower">🌻</div></div>
          <div className="chatbot-plant plant-3"><div className="plant-stem"/><div className="plant-flower">🌷</div></div>
          <button className="chatbot-fab" title="Chat with KrishiBot" onClick={() => setIsChatOpen(true)}>
            <div className="chatbot-fab-ring"/>
            <div className="chatbot-fab-icon">
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/>
                <path d="M2 14h2"/><path d="M20 14h2"/>
                <path d="M15 13v2"/><path d="M9 13v2"/>
              </svg>
            </div>
          </button>
          <div className="chatbot-fab-label">KrishiBot</div>
        </div>
      )}

      {/* ══════════════════════════════════════════════════════
          VOICE CHAT OVERLAY — full-screen separate experience
      ══════════════════════════════════════════════════════ */}
      {isChatOpen && (
        <div className="voice-chat-overlay">

          {/* Header */}
          <div className="chat-header">
            <div className="chat-header-left">
              <div className="chat-avatar">🌾</div>
              <div>
                <div className="chat-title">KrishiBot</div>
                <div className="chat-subtitle">AI Farm Assistant</div>
              </div>
            </div>
            <button className="close-chat" onClick={handleCloseVoice} aria-label="Close">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          {/* Visualizer */}
          <div className="voice-visualizer">
            <div className="nebula-blob"/>
            <div className="nebula-blob nebula-blob-2"/>
            <div className={`frequency-bars${isListening ? ' bars-active' : ''}`}>
              {[...Array(11)].map((_, i) => <div key={i} className={`freq-bar bar-${i + 1}`}/>)}
            </div>
          </div>

          {/* Transcript — Sarvam-style last-5-lines scroll */}
          <div className="chat-text-container">
            {isProcessing ? (
              <div className="processing-dots" aria-label="Processing">
                <span/><span/><span/>
              </div>
            ) : transcript.trim() ? (
              <div className="transcript-lines" aria-live="polite">
                {getTranscriptLines(transcript).map((line, i, arr) => {
                  const isLast = i === arr.length - 1;
                  return (
                    <div
                      key={i}
                      className={`transcript-line${isLast ? ' transcript-line--active' : ''}`}
                      style={{
                        opacity:    0.3 + (i / arr.length) * 0.7,
                        fontSize:   isLast ? '1.4rem' : '1.05rem',
                        fontWeight: isLast ? 600 : 400,
                      }}
                    >
                      {line}
                      {isLast && <span className="cursor" aria-hidden="true">|</span>}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="transcript-placeholder">
                {isListening ? 'Listening to you…' : 'Tap the mic to speak'}
              </div>
            )}
          </div>

          {/* Bottom row: status | mic | chat */}
          <div className="chat-action-row">

            <div className="bot-status">
              {isListening ? (
                <><span className="status-dot status-dot--recording"/><span className="recording-timer">{formatTimer(recordingTime)}</span></>
              ) : (
                <><span className="status-dot"/><span>{isProcessing ? 'Processing…' : 'Ready'}</span></>
              )}
            </div>

            {/* Mic — shows stop icon when recording */}
            <button
              className={`chat-mic-btn${isListening ? ' mic-active' : ''}`}
              onClick={() => isListening ? stopListening() : startListening()}
              aria-label={isListening ? 'Stop recording' : 'Start recording'}
            >
              {isListening ? (
                <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
                  <rect x="5" y="5" width="14" height="14" rx="2"/>
                </svg>
              ) : (
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="9" y="2" width="6" height="12" rx="3"/>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                  <line x1="12" y1="19" x2="12" y2="22"/>
                  <line x1="8" y1="22" x2="16" y2="22"/>
                </svg>
              )}
            </button>

            {/* Chat panel button — NEW */}
            <button
              className="chat-panel-btn"
              onClick={() => setIsChatPanelOpen(true)}
              aria-label="Open chat"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
              {messages.length > 1 && (
                <span className="chat-panel-badge">{messages.length - 1}</span>
              )}
            </button>

          </div>

          {/* Chat panel slides up inside overlay */}
          <ChatPanel
            isOpen={isChatPanelOpen}
            onClose={() => setIsChatPanelOpen(false)}
            messages={messages}
            setMessages={setMessages}
            isProcessing={isProcessing}
          />

        </div>
      )}
    </>
  );
}

export default App;