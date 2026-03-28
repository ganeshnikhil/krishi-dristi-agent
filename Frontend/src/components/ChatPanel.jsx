// src/components/ChatPanel.jsx
import { useState, useRef, useEffect, useCallback } from 'react';
import './ChatPanel.css';
import { useAuth } from '../context/AuthContext.jsx';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function ChatPanel({
  isOpen, onClose, messages, setMessages, isProcessing,
  isListening, startListening, stopListening
}) {
  const [input, setInput]         = useState('');
  const [localTyping, setLocalTyping] = useState(false);
  const [error, setError]         = useState(null);

  const messagesEndRef = useRef(null);
  const inputRef       = useRef(null);

  const { token } = useAuth();

  // Scroll to bottom whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isProcessing, localTyping]);

  // Focus input on open
  useEffect(() => {
    if (isOpen) setTimeout(() => inputRef.current?.focus(), 350);
  }, [isOpen]);

  // ── Send message to real backend ────────────────────────────
  const sendToBackend = useCallback(async (text) => {
    setLocalTyping(true);
    setError(null);

    try {
      const res = await fetch(`${API}/api/v1/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ message: text }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Failed to get a response from KrishiBot.');
      }

      setMessages(prev => [
        ...prev,
        { id: Date.now() + 1, type: 'bot', text: data.reply, time: new Date() },
      ]);
    } catch (err) {
      const errMsg = err.message || 'Network error. Please try again.';
      setError(errMsg);
      setMessages(prev => [
        ...prev,
        { id: Date.now() + 1, type: 'bot', text: `⚠️ ${errMsg}`, time: new Date() },
      ]);
    } finally {
      setLocalTyping(false);
    }
  }, [token, setMessages]);

  // ── Handle typed message send ────────────────────────────────
  const handleSend = useCallback(() => {
    const text = input.trim();
    if (!text || localTyping || isProcessing) return;

    setInput('');
    setMessages(prev => [
      ...prev,
      { id: Date.now(), type: 'user', text, time: new Date() },
    ]);

    sendToBackend(text);
  }, [input, localTyping, isProcessing, setMessages, sendToBackend]);

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

          {/* Typing indicator */}
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
            disabled={localTyping || isProcessing}
          />

          {/* Voice input button */}
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