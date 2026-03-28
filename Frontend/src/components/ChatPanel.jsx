// src/components/ChatPanel.jsx
import { useState, useRef, useEffect } from 'react';
import './ChatPanel.css';

const MOCK_RESPONSES = [
  "Hello farmer! Soil moisture is at 42% — optimal for wheat right now.",
  "Based on current weather, I recommend delaying irrigation by 24 hours.",
  "Rain is expected tonight. No irrigation needed today.",
  "Your wheat crop is at Stage 3. Fertilization is due in 3 days.",
  "Soil pH is 6.8 — excellent for wheat. Keep monitoring daily.",
  "High humidity today (82%). Watch for fungal disease on leaves.",
  "Wind is from North-East at 12 km/h. Good conditions for spraying.",
];

// Called by parent when voice query needs a bot reply.
// Parent (App.jsx) manages the `messages` array.
export default function ChatPanel({
  isOpen, onClose, messages, setMessages, isProcessing,
  isListening, startListening, stopListening
}) {
  const [input, setInput] = useState('');
  const [localTyping, setLocalTyping] = useState(false);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isProcessing, localTyping]);

  // Focus input on open
  useEffect(() => {
    if (isOpen) setTimeout(() => inputRef.current?.focus(), 350);
  }, [isOpen]);

  // ── Send typed message ────────────────────────────────────────────────────
  const handleSend = () => {
    const text = input.trim();
    if (!text || localTyping || isProcessing) return;

    setInput('');

    // Add user message
    setMessages(prev => [
      ...prev,
      { id: Date.now(), type: 'user', text, time: new Date() },
    ]);

    // Simulate bot reply
    setLocalTyping(true);
    const delay = 900 + Math.random() * 700;
    setTimeout(() => {
      const reply = MOCK_RESPONSES[Math.floor(Math.random() * MOCK_RESPONSES.length)];
      setMessages(prev => [
        ...prev,
        { id: Date.now() + 1, type: 'bot', text: reply, time: new Date() },
      ]);
      setLocalTyping(false);
    }, delay);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const fmt = (d) =>
    d instanceof Date
      ? d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
      : '';

  if (!isOpen) return null;

  return (
    <div
      className="cp-overlay"
      onClick={(e) => e.target === e.currentTarget && onClose()}
      role="dialog"
      aria-modal="true"
      aria-label="KrishiBot Chat"
    >
      <div className="cp-panel">

        {/* ── Header ── */}
        <div className="cp-header">
          <div className="cp-header-left">
            <div className="cp-avatar" aria-hidden="true">🌾</div>
            <div>
              <div className="cp-title">KrishiBot</div>
              <div className="cp-subtitle">
                <span className="cp-status-dot" />
                AI Farm Assistant
              </div>
            </div>
          </div>
          <button className="cp-close" onClick={onClose} aria-label="Close chat">✕</button>
        </div>

        {/* ── Messages ── */}
        <div className="cp-messages" role="log" aria-live="polite">
          {messages.map((msg) => (
            <div key={msg.id} className={`cp-msg cp-msg--${msg.type}`}>
              {msg.type === 'bot' && (
                <div className="cp-msg-avatar" aria-hidden="true">🌾</div>
              )}
              <div className="cp-msg-body">
                <div className="cp-msg-bubble">{msg.text}</div>
                <div className="cp-msg-time">{fmt(msg.time)}</div>
              </div>
            </div>
          ))}

          {/* Typing indicator — shown during voice processing OR local text reply */}
          {(isProcessing || localTyping) && (
            <div className="cp-msg cp-msg--bot">
              <div className="cp-msg-avatar" aria-hidden="true">🌾</div>
              <div className="cp-msg-body">
                <div className="cp-typing-bubble" aria-label="KrishiBot is typing">
                  <span /><span /><span />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* ── Input row ── */}
        <div className="cp-input-row">
          <input
            ref={inputRef}
            className="cp-input"
            type="text"
            placeholder="Type your question…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            aria-label="Chat input"
          />

          {/* Voice input button inside chat panel */}
          <button
            className={`cp-mic-btn${isListening ? ' cp-mic-active' : ''}`}
            onClick={() => isListening ? stopListening() : startListening()}
            aria-label={isListening ? 'Stop recording' : 'Start recording'}
          >
            {isListening ? (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <rect x="5" y="5" width="14" height="14" rx="2" />
              </svg>
            ) : (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <rect x="9" y="2" width="6" height="12" rx="3" />
                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                <line x1="12" y1="19" x2="12" y2="22" />
                <line x1="8" y1="22" x2="16" y2="22" />
              </svg>
            )}
          </button>

          <button
            className="cp-send"
            onClick={handleSend}
            disabled={!input.trim() || localTyping || isProcessing}
            aria-label="Send message"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>

      </div>
    </div>
  );
}