// src/App.jsx
import { useState, useRef, useEffect, useCallback } from 'react'
import './App.css'
import './auth.css'

import soilNormal from './assets/soil_normal.svg'
import clouds from './assets/clouds.svg'
import rainDrops from './assets/placidplace-drops-13474.gif'
import navbarBottomBorder from './assets/navbar-bottom-border.svg'
import pond from './assets/pond.svg'
import farmerGif from './assets/farmer-avatar.gif'

import LanguageSelect from './components/LanguageSelect.jsx'
import ChatPanel from './components/ChatPanel.jsx'
import { useApp } from './context/AppContext.jsx'
import { useAuth } from './context/AuthContext.jsx'
import useSpeechRecognition from './components/useSpeechRecognition'
import { speakText, stopSpeech } from './components/speakText'
import AdvisoryTicker from './components/AdvisoryTicker.jsx'
import { sarvamTranslate, isSarvamSupported } from './components/sarvamTranslate.js'

/* ── inline sub-components (no extra files needed) ── */

/* HAMBURGER MENU */
function HamburgerMenu({ onOpenAuth }) {
  const { isAuthenticated, user, logout } = useAuth()
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    if (!open) return
    const fn = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', fn)
    return () => document.removeEventListener('mousedown', fn)
  }, [open])

  useEffect(() => {
    const fn = (e) => { if (e.key === 'Escape') setOpen(false) }
    window.addEventListener('keydown', fn)
    return () => window.removeEventListener('keydown', fn)
  }, [])

  return (
    <div ref={ref} style={{ position: 'relative' }}>

      {/* ── Trigger button ── */}
      <button
        className="nav-icon-btn"
        onClick={() => setOpen(v => !v)}
        aria-label="Open menu"
        style={{ width: 38, height: 38 }}
      >
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
          {open
            ? <><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></>
            : <><line x1="4" y1="6" x2="20" y2="6" /><line x1="4" y1="12" x2="16" y2="12" /><line x1="4" y1="18" x2="20" y2="18" /></>
          }
        </svg>
      </button>

      {/* ── Drawer ── */}
      {open && (
        <>
          {/* backdrop */}
          <div
            onClick={() => setOpen(false)}
            style={{
              position: 'fixed', inset: 0, zIndex: 5999,
              background: 'rgba(0,0,0,0.35)', backdropFilter: 'blur(4px)',
            }}
          />
          <div style={{
            position: 'fixed', top: 0, right: 0, bottom: 0, zIndex: 6000,
            width: 'min(300px, 82vw)',
            background: '#fff',
            boxShadow: '-8px 0 48px rgba(0,0,0,0.18)',
            display: 'flex', flexDirection: 'column',
            padding: '64px 20px 40px',
            gap: 16,
            animation: 'hmSlide .3s cubic-bezier(.165,.84,.44,1) both',
            overflowY: 'auto',
          }}>

            {/* User block */}
            {isAuthenticated ? (
              <div style={{
                display: 'flex', alignItems: 'center', gap: 14,
                background: '#e8f5e9', borderRadius: 16, padding: 14,
              }}>
                <div style={{
                  width: 46, height: 46, borderRadius: '50%',
                  background: 'linear-gradient(135deg,#2e7d32,#1b5e20)',
                  color: '#fff', fontSize: '1.2rem', fontWeight: 800,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  flexShrink: 0, boxShadow: '0 4px 14px rgba(46,125,50,.3)',
                }}>
                  {user?.name?.[0]?.toUpperCase() ?? 'F'}
                </div>
                <div>
                  <div style={{ fontSize: '.95rem', fontWeight: 700, color: '#1a1005' }}>
                    {user?.name ?? user?.username}
                  </div>
                  <div style={{ fontSize: '.72rem', color: '#2e7d32', fontWeight: 600, marginTop: 2 }}>
                    🌾 Farmer
                  </div>
                </div>
              </div>
            ) : (
              <div style={{
                display: 'flex', flexDirection: 'column', alignItems: 'center',
                gap: 8, padding: '20px 14px',
                background: '#fdf8f0', borderRadius: 16,
                border: '1.5px dashed rgba(192,96,16,.25)', textAlign: 'center',
              }}>
                <span style={{ fontSize: '1.8rem' }}>🔒</span>
                <p style={{ fontSize: '.8rem', color: 'rgba(26,16,5,.6)', lineHeight: 1.5, margin: 0, fontWeight: 500 }}>
                  Login to use voice assistant &amp; AI chat
                </p>
              </div>
            )}

            <div style={{ height: 1, background: 'rgba(0,0,0,.07)' }} />

            {/* Nav links */}
            <nav style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {['About', 'Privacy Policy', 'Terms', 'Contact'].map(label => (
                <a key={label} href={`#${label.toLowerCase().replace(' ', '')}`}
                  onClick={() => setOpen(false)}
                  style={{
                    display: 'block', padding: '11px 14px', borderRadius: 12,
                    fontSize: '.9rem', fontWeight: 600, color: '#1a1005',
                    textDecoration: 'none', transition: 'background .18s',
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = '#e8f5e9'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                  {label}
                </a>
              ))}
            </nav>

            <div style={{ height: 1, background: 'rgba(0,0,0,.07)' }} />

            {/* Auth CTA */}
            {isAuthenticated ? (
              <button
                onClick={() => { logout(); setOpen(false) }}
                style={{
                  width: '100%', padding: '13px 16px', borderRadius: 14,
                  background: 'rgba(229,57,53,.07)',
                  color: '#c62828', border: '1.5px solid rgba(229,57,53,.2)',
                  fontSize: '.9rem', fontWeight: 700, fontFamily: 'inherit',
                  cursor: 'pointer', display: 'flex', alignItems: 'center',
                  justifyContent: 'center', gap: 8, marginTop: 'auto',
                }}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                  <polyline points="16 17 21 12 16 7" />
                  <line x1="21" y1="12" x2="9" y2="12" />
                </svg>
                Logout
              </button>
            ) : (
              <button
                onClick={() => { onOpenAuth(); setOpen(false) }}
                style={{
                  width: '100%', padding: '13px 16px', borderRadius: 14,
                  background: 'linear-gradient(135deg,#2e7d32,#1b5e20)',
                  color: '#fff', border: 'none',
                  fontSize: '.9rem', fontWeight: 700, fontFamily: 'inherit',
                  cursor: 'pointer', display: 'flex', alignItems: 'center',
                  justifyContent: 'center', gap: 8, marginTop: 'auto',
                  boxShadow: '0 6px 20px rgba(27,94,32,.25)',
                }}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                  <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
                  <polyline points="10 17 15 12 10 7" />
                  <line x1="15" y1="12" x2="3" y2="12" />
                </svg>
                Login / Register
              </button>
            )}

          </div>
        </>
      )}
    </div>
  )
}

/* AUTH PAGE */
function AuthPage({ onSuccess, onClose }) {
  const { login, register } = useAuth()
  const [mode, setMode] = useState('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState({ msg: '', type: 'error' })

  const showToast = (msg, type = 'error') => {
    setToast({ msg, type })
    setTimeout(() => setToast({ msg: '', type: 'error' }), 3500)
  }

  const validate = () => {
    if (!username.trim()) return 'Username is required.'
    if (username.trim().length < 3) return 'Username must be at least 3 characters.'
    if (!password) return 'Password is required.'
    if (password.length < 4) return 'Password must be at least 4 characters.'
    return null
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const err = validate()
    if (err) return showToast(err)
    setLoading(true)
    try {
      if (mode === 'login') { await login(username.trim(), password); showToast('Welcome back! 🌾', 'success') }
      else { await register(username.trim(), password); showToast('Account created! 🌱', 'success') }
      setTimeout(() => onSuccess?.(), 500)
    } catch (err) {
      showToast(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    /* backdrop */
    <div
      style={{
        position: 'fixed', inset: 0, zIndex: 8000,
        background: 'rgba(10,20,10,.75)',
        backdropFilter: 'blur(14px)',
        display: 'flex', alignItems: 'flex-end', justifyContent: 'center',
      }}
      onClick={onClose}
    >
      {/* card — stops propagation so clicking inside doesn't close */}
      <div
        onClick={e => e.stopPropagation()}
        style={{
          background: '#fff', borderRadius: '28px 28px 0 0',
          padding: '32px 24px 48px',
          width: '100%', maxWidth: 420,
          display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 18,
          animation: 'authSlide .38s cubic-bezier(.165,.84,.44,1) both',
          boxShadow: '0 -8px 48px rgba(0,0,0,.18)',
        }}
      >
        {/* Brand */}
        <div style={{ fontFamily: "'Outfit',system-ui,sans-serif", fontSize: '1.7rem', letterSpacing: '-.03em', display: 'flex', gap: 4 }}>
          <span style={{ fontWeight: 800, color: '#2e7d32' }}>कृषि</span>
          <span style={{ fontWeight: 600, color: '#5d4037' }}>Mitra</span>
        </div>
        <p style={{ fontSize: '.72rem', fontWeight: 600, color: 'rgba(26,16,5,.6)', letterSpacing: '.04em', margin: '-10px 0 0', textAlign: 'center' }}>
          AI Farm Assistant · किसान सहायक
        </p>

        {/* Toggle */}
        <div style={{ display: 'flex', background: '#e8f5e9', borderRadius: 14, padding: 4, width: '100%', gap: 4 }}>
          {['login', 'register'].map(m => (
            <button key={m}
              onClick={() => { setMode(m); setToast({ msg: '' }) }}
              style={{
                flex: 1, padding: '9px', borderRadius: 10,
                fontSize: '.88rem', fontWeight: 700, fontFamily: 'inherit',
                border: 'none', cursor: 'pointer',
                background: mode === m ? '#fff' : 'transparent',
                color: mode === m ? '#2e7d32' : 'rgba(26,16,5,.6)',
                boxShadow: mode === m ? '0 2px 10px rgba(0,0,0,.08)' : 'none',
                transition: 'all .22s',
              }}
            >
              {m === 'login' ? 'Login' : 'Register'}
            </button>
          ))}
        </div>

        {/* Toast */}
        {toast.msg && (
          <div style={{
            width: '100%', padding: '10px 14px', borderRadius: 12,
            fontSize: '.82rem', fontWeight: 600,
            background: toast.type === 'error' ? 'rgba(229,57,53,.09)' : 'rgba(46,125,50,.09)',
            color: toast.type === 'error' ? '#c62828' : '#2e7d32',
            border: `1px solid ${toast.type === 'error' ? 'rgba(229,57,53,.2)' : 'rgba(46,125,50,.2)'}`,
          }}>
            {toast.type === 'error' ? '⚠️' : '✅'} {toast.msg}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: 14 }} noValidate>
          {[
            { id: 'km-user', label: 'Username · यूजरनेम', type: 'text', val: username, set: setUsername, ph: mode === 'login' ? 'Enter username' : 'Choose a username', ac: 'username' },
            { id: 'km-pass', label: 'Password · पासवर्ड', type: 'password', val: password, set: setPassword, ph: mode === 'login' ? 'Enter password' : 'Create a password (min 4 chars)', ac: mode === 'login' ? 'current-password' : 'new-password' },
          ].map(f => (
            <div key={f.id} style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              <label htmlFor={f.id} style={{ fontSize: '.75rem', fontWeight: 700, color: 'rgba(26,16,5,.6)', letterSpacing: '.02em' }}>
                {f.label}
              </label>
              <input
                id={f.id} type={f.type} value={f.val}
                onChange={e => f.set(e.target.value)}
                placeholder={f.ph} autoComplete={f.ac}
                autoCapitalize="none" disabled={loading}
                style={{
                  width: '100%', padding: '13px 16px', borderRadius: 12,
                  border: '1.5px solid rgba(0,0,0,.1)', background: '#f9f9f7',
                  fontSize: '.95rem', fontFamily: 'inherit', color: '#1a1005',
                  outline: 'none', transition: 'border-color .2s,box-shadow .2s',
                  opacity: loading ? .55 : 1,
                }}
                onFocus={e => { e.target.style.borderColor = '#2e7d32'; e.target.style.boxShadow = '0 0 0 3px rgba(46,125,50,.12)'; e.target.style.background = '#fff' }}
                onBlur={e => { e.target.style.borderColor = 'rgba(0,0,0,.1)'; e.target.style.boxShadow = 'none'; e.target.style.background = '#f9f9f7' }}
              />
            </div>
          ))}

          {mode === 'login' && (
            <p style={{ fontSize: '.72rem', color: 'rgba(26,16,5,.35)', textAlign: 'center', margin: 0 }}>
              Demo: username <strong>farmer</strong> / password <strong>1234</strong>
            </p>
          )}

          <button type="submit" disabled={loading}
            style={{
              width: '100%', padding: 14, borderRadius: 14,
              background: 'linear-gradient(135deg,#2e7d32,#1b5e20)',
              color: '#fff', fontSize: '.97rem', fontWeight: 700,
              fontFamily: 'inherit', border: 'none', cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 6px 20px rgba(27,94,32,.3)',
              opacity: loading ? .7 : 1, marginTop: 4,
              transition: 'all .2s',
            }}
          >
            {loading
              ? <span style={{ width: 20, height: 20, border: '2.5px solid rgba(255,255,255,.35)', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin .7s linear infinite', display: 'inline-block' }} />
              : mode === 'login' ? 'Login →' : 'Create Account →'
            }
          </button>
        </form>

        <p style={{ fontSize: '.8rem', color: 'rgba(26,16,5,.6)', textAlign: 'center', margin: 0 }}>
          {mode === 'login'
            ? <>New here? <button onClick={() => setMode('register')} style={{ background: 'none', border: 'none', color: '#2e7d32', fontWeight: 700, fontSize: 'inherit', cursor: 'pointer', fontFamily: 'inherit', textDecoration: 'underline', padding: '0 2px' }}>Create account</button></>
            : <>Already have an account? <button onClick={() => setMode('login')} style={{ background: 'none', border: 'none', color: '#2e7d32', fontWeight: 700, fontSize: 'inherit', cursor: 'pointer', fontFamily: 'inherit', textDecoration: 'underline', padding: '0 2px' }}>Login</button></>
          }
        </p>

      </div>
    </div>
  )
}

/* GATE TOAST */
function GateToast({ visible }) {
  if (!visible) return null
  return (
    <div role="status" style={{
      position: 'fixed', bottom: 108, left: '50%',
      transform: 'translateX(-50%)',
      zIndex: 7000, background: '#1a1005', color: '#fff',
      padding: '11px 20px', borderRadius: 40,
      fontSize: '.82rem', fontWeight: 600,
      whiteSpace: 'nowrap', boxShadow: '0 8px 28px rgba(0,0,0,.2)',
      animation: 'authSlide .3s ease both',
      pointerEvents: 'none', letterSpacing: '.01em',
    }}>
      🔒 Please login to use voice assistant
    </div>
  )
}

/* ── Keyframes injected once ── */
const STYLE = `
  @keyframes hmSlide   { from{transform:translateX(100%);opacity:0} to{transform:translateX(0);opacity:1} }
  @keyframes authSlide { from{transform:translateY(30px);opacity:0} to{transform:translateY(0);opacity:1} }
  @keyframes spin      { to{transform:rotate(360deg)} }
`

/* ── helpers ── */
const MOCK_RESPONSES = [
  "Hello farmer! Soil moisture is at 42% — optimal for wheat right now.",
  "Based on current weather, I recommend delaying irrigation by 24 hours.",
  "Rain is expected tonight. No irrigation needed today.",
  "Your wheat crop is at Stage 3. Fertilization is due in 3 days.",
  "Soil pH is 6.8 — excellent for wheat. Keep monitoring daily.",
  "High humidity today at 82%. Watch for fungal disease on leaves.",
  "Wind from North-East at 12 km/h — good conditions for pesticide spraying.",
]

function getTranscriptLines(text) {
  if (!text?.trim()) return []
  const words = text.trim().split(' ')
  const lines = []; let cur = ''
  for (const w of words) {
    const test = cur ? `${cur} ${w}` : w
    if (test.length > 42) { if (cur) lines.push(cur); cur = w } else cur = test
  }
  if (cur) lines.push(cur)
  return lines.slice(-5)
}
function formatTimer(secs) {
  return `${Math.floor(secs / 60).toString().padStart(2, '0')}:${(secs % 60).toString().padStart(2, '0')}`
}
function getWindDirection(deg) {
  if (deg >= 337.5 || deg < 22.5) return 'N'
  if (deg >= 22.5 && deg < 67.5) return 'NE'
  if (deg >= 67.5 && deg < 112.5) return 'E'
  if (deg >= 112.5 && deg < 157.5) return 'SE'
  if (deg >= 157.5 && deg < 202.5) return 'S'
  if (deg >= 202.5 && deg < 247.5) return 'SW'
  if (deg >= 247.5 && deg < 292.5) return 'W'
  if (deg >= 292.5 && deg < 337.5) return 'NW'
  return ''
}

/* ═══════════════════════════════════ APP ═══════════════════════════════════ */
export default function App() {
  const today = new Date().getDate()
  const now = new Date()
  const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate()

  const [selectedDate, setSelectedDate] = useState(today)
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)
  const [isChatPanelOpen, setIsChatPanelOpen] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [isProcessing, setIsProcessing] = useState(false)
  const [showAuth, setShowAuth] = useState(false)
  const [gateToast, setGateToast] = useState(false)
  const [pendingAction, setPendingAction] = useState(null) // 'chat' | 'mic'
  const [messages, setMessages] = useState([
    { id: 1, type: 'bot', text: 'Namaste! 🌾 I am KrishiBot. Speak or type to ask anything about your farm.', time: new Date() },
  ])
  const [locationText, setLocationText] = useState('Dehradun, IN')
  const [isUpdatingLocation, setIsUpdatingLocation] = useState(false)
  const [weatherData, setWeatherData] = useState(null)

  const sliderRef = useRef(null)
  const isUserScrolling = useRef(false)
  const scrollTimeout = useRef(null)

  const { hasChosen, resetLanguage, language, getSpeechCode } = useApp()
  const { isAuthenticated, token } = useAuth()

  // ── Voice UI Helpers ──
  const [isMuted, setIsMuted] = useState(false)
  const [frequencies] = useState(new Array(24).fill(8)) // Static visualizer bars
  const overlayEndRef = useRef(null)
  const [translating, setTranslating] = useState(false) // shows 🔄 badge
  const localLangCode = getSpeechCode(language?.code)
  const langShortCode = language?.code ?? 'en'


  /**
   * Translate text with Sarvam AI.
   * `to`   — short code of the TARGET language   (e.g. 'en' to send to the AI)
   * `from` — short code of the SOURCE language   (e.g. 'hi' if the user spoke Hindi)
   */
  const translateText = useCallback(async (text, to, from) => {
    if (!isSarvamSupported(from) && !isSarvamSupported(to)) return text
    setTranslating(true)
    try {
      const result = await sarvamTranslate(text, to, from)
      return result
    } finally {
      setTranslating(false)
    }
  }, [])

  const { transcript, isListening, startListening, stopListening, resetTranscript } =
    useSpeechRecognition(localLangCode)

  // Auto-scroll for voice transcript
  useEffect(() => {
    if (overlayEndRef.current) {
      overlayEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [transcript, messages])

  const dates = Array.from({ length: daysInMonth * 3 }, (_, i) => (i % daysInMonth) + 1)

  /* ── auth gate helper ── */
  const guardedAction = useCallback((actionName, action) => {
    if (isAuthenticated) {
      action()
    } else {
      setPendingAction(actionName)
      setGateToast(true)
      setTimeout(() => setGateToast(false), 2800)
      setTimeout(() => setShowAuth(true), 150)
    }
  }, [isAuthenticated])

  /* ── after login: resume pending action ── */
  const handleAuthSuccess = useCallback(() => {
    setShowAuth(false)
    if (pendingAction === 'chat' || pendingAction === 'mic') {
      setIsChatOpen(true)
      if (pendingAction === 'chat') setIsChatPanelOpen(true)
    }
    setPendingAction(null)
  }, [pendingAction])

  /* scroll shadow */
  useEffect(() => {
    const fn = () => setIsScrolled(window.scrollY > 10)
    window.addEventListener('scroll', fn, { passive: true })
    return () => window.removeEventListener('scroll', fn)
  }, [])

  /* auto-scroll date strip */
  useEffect(() => {
    if (!sliderRef.current) return
    sliderRef.current.querySelectorAll('.date-item')[daysInMonth + today - 1]
      ?.scrollIntoView({ behavior: 'auto', block: 'nearest', inline: 'center' })
  }, [today, daysInMonth])

  /* recording timer */
  useEffect(() => {
    let iv
    if (isListening) { setRecordingTime(0); iv = setInterval(() => setRecordingTime(t => t + 1), 1000) }
    else setRecordingTime(0)
    return () => clearInterval(iv)
  }, [isListening])

  /* send query when mic stops */
  useEffect(() => {
    if (!isListening && transcript.trim()) handleAppQuery(transcript.trim())
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isListening])

  const handleAppQuery = useCallback(async (rawText, isTextSource = false) => {
    setIsProcessing(true)
    resetTranscript()

    const userMsgId = Date.now()
    // Show user's spoken text in their language immediately
    setMessages(p => [...p, { id: userMsgId, type: 'user', text: rawText, isTranslating: langShortCode !== 'en', lang: language?.nativeName, time: new Date() }])

    // Translate user's message TO English for the backend
    let queryForBackend = rawText
    if (langShortCode !== 'en' && isSarvamSupported(langShortCode)) {
      queryForBackend = await translateText(rawText, 'en', langShortCode)
      // Update bubble: mark translation done
      setMessages(p => {
        const next = [...p]
        const idx = next.findIndex(m => m.id === userMsgId)
        if (idx !== -1) next[idx] = { ...next[idx], isTranslating: false }
        return next
      })
    } else {
      setMessages(p => {
        const next = [...p]
        const idx = next.findIndex(m => m.id === userMsgId)
        if (idx !== -1) next[idx] = { ...next[idx], isTranslating: false }
        return next
      })
    }

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const res = await fetch(`${apiUrl}/api/v1/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ message: queryForBackend }),
      })
      const data = await res.json()
      let reply = res.ok ? data.reply : (data.detail || 'Something went wrong.')

      // Translate bot reply back to user's language
      let displayReply = reply
      if (langShortCode !== 'en' && isSarvamSupported(langShortCode)) {
        displayReply = await translateText(reply, langShortCode, 'en')
      }

      setMessages(p => [...p, { id: Date.now() + 1, type: 'bot', text: displayReply, time: new Date() }])
      if (!isMuted && !isTextSource) speakText(displayReply, localLangCode)
    } catch {
      setMessages(p => [...p, { id: Date.now() + 1, type: 'bot', text: '⚠️ Network error. Please try again.', time: new Date() }])
    } finally {
      setIsProcessing(false)
      resetTranscript()
    }
  }, [resetTranscript, token, langShortCode, localLangCode, language, isMuted, translateText])

  const handleScroll = () => {
    if (!sliderRef.current) return
    isUserScrolling.current = true
    clearTimeout(scrollTimeout.current)
    scrollTimeout.current = setTimeout(() => { isUserScrolling.current = false }, 150)
    const slider = sliderRef.current
    const mid = slider.getBoundingClientRect().left + slider.getBoundingClientRect().width / 2
    const items = slider.querySelectorAll('.date-item')
    let closest = selectedDate, minD = Infinity
    items.forEach(item => {
      const d = Math.abs(item.getBoundingClientRect().left + item.getBoundingClientRect().width / 2 - mid)
      if (d < minD) { minD = d; closest = parseInt(item.querySelector('.date-number').innerText) }
    })
    if (closest !== selectedDate) setSelectedDate(closest)
  }

  const handleDateClick = (date, index) => {
    setSelectedDate(date)
    sliderRef.current?.querySelectorAll('.date-item')[index]
      ?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
  }

  const handleCloseVoice = () => {
    stopListening();
    stopSpeech();
    setIsChatPanelOpen(false);
    setIsChatOpen(false)
  }

  const handleLocationClick = useCallback(() => {
    if (!isAuthenticated) {
      guardedAction('location', () => { })
      return
    }

    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser");
      return
    }

    setIsUpdatingLocation(true)
    setLocationText('Locating...')

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const latitude = parseFloat(position.coords.latitude.toFixed(6))
        const longitude = parseFloat(position.coords.longitude.toFixed(6))
        try {
          // You just changed your backend endpoint in endpoints/user.py to prefix="/user"
          // but if it's included in router.py as api_router.include_router(user_router) 
          // then the path is /api/v1/user/location
          // Let's rely on standard v1 route setup
          const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
          const res = await fetch(`${apiUrl}/api/v1/user/location`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({ lat: latitude, lon: longitude }),
          })

          if (res.ok) {
            setLocationText('Location Synced')
            try {
              const geoRes = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`)
              const geoData = await geoRes.json()
              const city = geoData.address.city || geoData.address.town || geoData.address.village || geoData.address.county || 'Synced'
              const state = geoData.address.state ? geoData.address.state.substring(0, 2).toUpperCase() : 'IN'
              setLocationText(`${city}, ${state}`)
            } catch (e) {
              // Ignore reverse geocode failures
            }
            try {
              const owmKey = import.meta.env.VITE_OPENWEATHER_API_KEY;
              if (owmKey) {
                const wRes = await fetch(`https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=${owmKey}&units=metric`);
                if (wRes.ok) {
                  const wData = await wRes.json();
                  setWeatherData(wData);
                }
              }
            } catch (err) { }
          } else {
            setLocationText('Dehradun, IN')
            alert('Failed to update location on server.')
          }
        } catch {
          setLocationText('Dehradun, IN')
        } finally {
          setIsUpdatingLocation(false)
        }
      },
      (error) => {
        setLocationText('Dehradun, IN')
        setIsUpdatingLocation(false)
      }
    )
  }, [isAuthenticated, token, guardedAction])

  return (
    <>
      {/* inject keyframes once */}
      <style>{STYLE}</style>

      {!hasChosen && <LanguageSelect />}

      {/* AUTH PAGE */}
      {showAuth && (
        <AuthPage
          onSuccess={handleAuthSuccess}
          onClose={() => setShowAuth(false)}
        />
      )}

      {/* GATE TOAST */}
      <GateToast visible={gateToast} />

      {/* ── NAVBAR ── */}
      <nav className={`navbar${isScrolled ? ' navbar--scrolled' : ''}`}>
        <div className="brand-logo">
          <div className="brand-text">
            <span className="brand-krishi">कृषि</span>
            <span className="brand-mitra">Mitra</span>
          </div>
        </div>
        <div className="navbar-center">
          <div
            className="location-chip"
            onClick={handleLocationClick}
            style={{ cursor: isUpdatingLocation ? 'wait' : 'pointer', opacity: isUpdatingLocation ? 0.7 : 1 }}
            title="Update Location"
          >
            <span className="location-dot" />
            <span>{isUpdatingLocation ? '📡 Locating…' : locationText}</span>
          </div>
          {language && language.code !== 'en' && (
            <div
              className="lang-badge"
              onClick={resetLanguage}
              title={`Language: ${language.name} — click to change`}
            >
              <span>{language.flag || '🌐'}</span>
              <span>{language.nativeName}</span>
            </div>
          )}
        </div>
        <button className="nav-icon-btn language-btn" onClick={resetLanguage} title="Change Language">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="2" y1="12" x2="22" y2="12" />
            <path d="M12 2a15 15 0 0 1 0 20" /><path d="M12 2a15 15 0 0 0 0 20" />
          </svg>
        </button>
        <div className="navbar-right">
          <button className="nav-icon-btn" aria-label="Notifications">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
              <path d="M13.73 21a2 2 0 0 1-3.46 0" />
            </svg>
            <span className="nav-badge">3</span>
          </button>

          {/* ← HAMBURGER — now actually wired */}
          <HamburgerMenu onOpenAuth={() => setShowAuth(true)} />
        </div>
      </nav>

      <img src={navbarBottomBorder} alt="" className="navbar-bottom-border" aria-hidden="true" />

      <main className="dashboard-content">
        <section className="hero-section">
          <div className="hero">
            <img src={rainDrops} alt="" className="rain-gif" aria-hidden="true" />
            <img src={clouds} alt="" className="clouds-img" aria-hidden="true" />
            <img src={soilNormal} alt="" className="soil-img" aria-hidden="true" />
            <div className="hero-center">
              <div className="hero-weather-badge">
                <span className="hero-weather-icon">🌧️</span>
                <span>{weatherData?.weather?.[0]?.main || 'Light Rain'}</span>
              </div>
              <div className="hero-temp">
                {weatherData ? Math.round(weatherData.main.temp) : 24}°
                <span className="hero-temp-unit">C</span>
              </div>
              <div className="hero-desc">
                {weatherData?.weather?.[0]?.description
                  ? weatherData.weather[0].description.charAt(0).toUpperCase() + weatherData.weather[0].description.slice(1)
                  : 'Continuous showers'} · Feels like {weatherData ? Math.round(weatherData.main.feels_like) : 21}°C
              </div>
            </div>
            <div className="hero-widget weather-widget">
              <div className="widget-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0e6fa0" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z" />
                </svg>
              </div>
              <div className="widget-info">
                <div className="widget-val">{weatherData ? weatherData.main.humidity : 82}%</div>
                <div className="widget-label">Humidity</div>
              </div>
            </div>
            <div className="hero-widget soil-widget">
              <div className="widget-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2e7d32" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" />
                </svg>
              </div>
              <div className="widget-info"><div className="widget-val">42%</div><div className="widget-label">Moist Soil</div></div>
            </div>
            <div className="hero-widget wind-widget">
              <div className="widget-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5d4037" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9.59 4.59A2 2 0 1 1 11 8H2m10.59 11.41A2 2 0 1 0 14 16H2m15.73-8.27A2.5 2.5 0 1 1 19.5 12H2" />
                </svg>
              </div>
              <div className="widget-info">
                <div className="widget-val">
                  {weatherData?.wind ? Math.round(weatherData.wind.speed * 3.6) : 12} km/h
                </div>
                <div className="widget-label">
                  {weatherData?.wind ? getWindDirection(weatherData.wind.deg) : 'NE'} Wind
                </div>
              </div>
            </div>
          </div>
        </section>
        <AdvisoryTicker />

        <section className="timeline-section">
          <div className="section-divider" />
          <div className="date-slider-wrapper">
            <div className="date-slider-header">
              <div className="month-year">{now.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</div>
              <div className="slider-hint">Tap a date to view conditions</div>
            </div>
            <div className="date-slider" ref={sliderRef} onScroll={handleScroll}>
              {dates.map((date, index) => {
                const dayName = new Date(now.getFullYear(), now.getMonth(), date)
                  .toLocaleDateString('en-US', { weekday: 'short' }).toUpperCase()
                const isToday = date === today && index >= daysInMonth && index < daysInMonth * 2
                let distance = Math.abs(selectedDate - date)
                if (distance > daysInMonth / 2) distance = daysInMonth - distance
                let cls = 'date-item'
                if (distance === 0) cls += ' active-date'
                else if (distance === 1) cls += ' near-date'
                else cls += ' far-date'
                return (
                  <div key={`${date}-${index}`} className={cls} onClick={() => handleDateClick(date, index)}>
                    <div className="day-label">{dayName}</div>
                    <div className="date-number">{date}</div>
                    {isToday && <div className="today-marker">TODAY</div>}
                  </div>
                )
              })}
            </div>
          </div>
          <div className="section-divider" />
        </section>

        <section className="insights-section">
          <div className="section-header">
            <h2 className="section-title">Farm Insights</h2>
            <p className="section-subtitle">Real-time status &amp; metrics</p>
          </div>
          <div className="updates">
            <div className="update-heading">Today's Activity</div>
            <div className="card card-weather">
              <div className="card-top"><div className="card-label"><span className="card-dot dot-blue" />Weather Forecast</div><span className="card-badge badge-rain">🌧 Rain</span></div>
              <div className="card-metric">24°C</div>
              <div className="card-desc">Light showers throughout the day. Wind from North-East at 12 km/h. UV index: Low.</div>
              <div className="card-row"><div className="card-chip">💧 Humidity 82%</div><div className="card-chip">🌬 Wind 12 km/h</div><div className="card-chip">🌡 Feels 21°C</div></div>
            </div>
            <div className="card card-soil">
              <div className="card-top"><div className="card-label"><span className="card-dot dot-green" />Soil Health</div><span className="card-badge badge-good">✅ Optimal</span></div>
              <div className="card-metric">pH 6.8</div>
              <div className="card-desc">Soil moisture at optimal levels for current wheat crop stage. No irrigation required today.</div>
              <div className="card-row"><div className="card-chip">💧 Moisture 42%</div><div className="card-chip">🌡 Soil 18°C</div><div className="card-chip">⚗️ N–P–K OK</div></div>
            </div>
            <div className="card card-advisory">
              <div className="card-top"><div className="card-label"><span className="card-dot dot-amber" />Advisory</div><span className="card-badge badge-action">⚡ Action</span></div>
              <div className="card-metric">Irrigate</div>
              <div className="card-desc">Wheat crop needs irrigation within 24 hours. Rain today may reduce requirement — reassess tomorrow.</div>
              <div className="card-row"><div className="card-chip">📅 Fertilise in 3 days</div><div className="card-chip">🌾 Stage 3</div></div>
            </div>
            <div className="card card-scheme">
              <div className="card-top"><div className="card-label"><span className="card-dot dot-purple" />Government Scheme</div><span className="card-badge badge-scheme">🏛 New</span></div>
              <div className="card-metric-sm">PM Fasal Bima</div>
              <div className="card-desc">Enroll in Pradhan Mantri Fasal Bima Yojana before the season deadline to protect your crop.</div>
              <div className="card-cta"><a href="https://pmfby.gov.in/" target="_blank" rel="noopener noreferrer" className="card-cta-btn">Apply Now →</a></div>
            </div>
          </div>
        </section>
      </main>

      <footer className="footer">
        <img src={pond} className="footer-pond" alt="" aria-hidden="true" />
        <div className="footer-content">
          <div className="footer-brand">
            <span className="brand-krishi">Krishi</span><span className="brand-mitra">Mitra</span>
          </div>
          <p className="footer-tagline">Empowering India's farmers with AI</p>
          <div className="footer-links">
            <a href="#about" className="footer-link">About</a>
            <a href="#privacy" className="footer-link">Privacy</a>
            <a href="#terms" className="footer-link">Terms</a>
            <a href="#contact" className="footer-link">Contact</a>
          </div>
          <div className="footer-divider" />
          <div className="footer-copyright">© 2026 कृषि Mitra · Made with 🌿 for Indian Farmers</div>
        </div>
      </footer>

      {/* CHATBOT FAB — guarded */}
      {!isChatOpen && (
        <div className="chatbot-container">
          <button
            className="chatbot-fab"
            title={isAuthenticated ? 'Chat with KrishiBot' : 'Login to chat'}
            onClick={() => guardedAction('mic', () => { setIsChatOpen(true); setIsChatPanelOpen(false) })}
          >
            <div className="chatbot-fab-ring" />
            <img src={farmerGif} alt="Farmer" className="chatbot-avatar-img" />
          </button>
          <div className="chatbot-fab-label">KrishiBot</div>
        </div>
      )}

      {/* VOICE OVERLAY */}
      {isChatOpen && (
        <div className="voice-chat-overlay notranslate">
          <div className="chat-header">
            <div className="chat-header-left">
              <div className="chat-avatar">🌾</div>
              <div>
                <div className="chat-title">KrishiBot</div>
                <div className="chat-subtitle">
                  {translating
                    ? <><span className="translate-spinner">⟳</span> Translating…</>
                    : 'AI Farm Assistant'
                  }
                </div>
              </div>
            </div>
            <button className="close-chat" onClick={handleCloseVoice} aria-label="Close">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>

          {!isChatPanelOpen && (
            <div className="voice-overlay-content">
              {/* Visualizer at top */}
              <div className="voice-visualizer">
                <div className="nebula-blob" />
                <div className="nebula-blob nebula-blob-2" />
                <div className={`frequency-bars${isListening ? ' bars-active' : ''}`}>
                  {frequencies.map((freq, i) => (
                    <div
                      key={i}
                      className={`freq-bar bar-${i + 1}`}
                      style={{
                        height: isListening ? `${Math.max(8, freq / 2.5)}px` : '8px',
                        transition: 'height 0.05s linear'
                      }}
                    />
                  ))}
                </div>
              </div>

              {/* Focused Interaction Stage (No Scroll) */}
              <div className="voice-interaction-stage notranslate">
                {messages.length > 1 && messages.slice(-2).map((msg) => (
                  <div
                    key={msg.id}
                    className={`voice-bubble voice-bubble--${msg.type}`}
                  >
                    <span>{msg.text}</span>
                  </div>
                ))}

                {/* Live transcript while mic is on */}
                {isListening && transcript.trim() && (
                  <div className="voice-live-transcript" aria-live="polite">
                    {transcript.trim()}
                    <span className="cursor" aria-hidden="true">|</span>
                  </div>
                )}

                {/* Processing */}
                {isProcessing && (
                  <div className="voice-bubble voice-bubble--bot">
                    <div className="processing-dots" aria-label="Processing"><span /><span /><span /></div>
                  </div>
                )}

                {/* Empty state */}
                {messages.filter(m => m.type !== 'system').length === 0 && !transcript.trim() && !isProcessing && (
                  <div className="transcript-placeholder">
                    {isListening ? `🎤 Listening in ${language?.name || 'English'}…` : 'Tap the mic to speak'}
                  </div>
                )}
              </div>

              <div className="chat-action-row">
                <div className="bot-status">
                  {isListening
                    ? <><span className="status-dot status-dot--recording" /><span className="recording-timer">{formatTimer(recordingTime)}</span></>
                    : <><span className="status-dot" /><span>{isProcessing ? 'Processing…' : 'Ready'}</span></>
                  }
                </div>

                {/* mic — also guarded */}
                <button
                  className={`chat-mic-btn${isListening ? ' mic-active' : ''}`}
                  onClick={() => {
                    if (isListening) { stopListening(); return }
                    guardedAction('mic', startListening)
                  }}
                  aria-label={isListening ? 'Stop recording' : 'Start recording'}
                >
                  {isListening ? (
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><rect x="5" y="5" width="14" height="14" rx="2" /></svg>
                  ) : (
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="9" y="2" width="6" height="12" rx="3" />
                      <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                      <line x1="12" y1="19" x2="12" y2="22" />
                      <line x1="8" y1="22" x2="16" y2="22" />
                    </svg>
                  )}
                </button>

                <button
                  className={`chat-speaker-btn${isMuted ? ' muted' : ''}`}
                  onClick={() => {
                    setIsMuted(!isMuted);
                    if (!isMuted) stopSpeech(); // Silence instantly if muting
                  }}
                  aria-label={isMuted ? 'Unmute AI' : 'Mute AI'}
                >
                  {isMuted ? (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M11 5L6 9H2v6h4l5 4V5z" /><line x1="23" y1="9" x2="17" y2="15" /><line x1="17" y1="9" x2="23" y2="15" />
                    </svg>
                  ) : (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M11 5L6 9H2v6h4l5 4V5z" /><path d="M19.07 4.93a10 10 0 0 1 0 14.14" /><path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
                    </svg>
                  )}
                </button>
                <button className="chat-panel-btn" onClick={() => setIsChatPanelOpen(true)} aria-label="Open chat">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                  {messages.length > 1 && <span className="chat-panel-badge">{messages.length - 1}</span>}
                </button>
              </div>
            </div>
          )}

          <ChatPanel
            isOpen={isChatPanelOpen}
            onClose={() => setIsChatPanelOpen(false)}
            messages={messages}
            setMessages={setMessages}
            isProcessing={isProcessing}
            handleTextQuery={(text) => handleAppQuery(text, true)}
            onSwitchToVoice={() => { setIsChatPanelOpen(false); setIsChatOpen(true); }}
            onSpeak={(text) => speakText(text, localLangCode)}
          />
        </div>
      )}
    </>
  )
}