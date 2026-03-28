// src/pages/AuthPage.jsx
import { useState, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';

/* ── tiny inline toast ── */
function Toast({ msg, type }) {
  if (!msg) return null;
  return (
    <div className={`auth-toast auth-toast--${type}`} role="alert">
      {type === 'error' ? '⚠️' : '✅'} {msg}
    </div>
  );
}

export default function AuthPage({ onSuccess }) {
  const { login, register } = useAuth();

  const [mode,     setMode]     = useState('login');   // 'login' | 'register'
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading,  setLoading]  = useState(false);
  const [toast,    setToast]    = useState({ msg: '', type: 'error' });

  const showToast = (msg, type = 'error') => {
    setToast({ msg, type });
    setTimeout(() => setToast({ msg: '', type: 'error' }), 3500);
  };

  const validate = () => {
    if (!username.trim()) return 'Username is required.';
    if (username.trim().length < 3) return 'Username must be at least 3 characters.';
    if (!password)        return 'Password is required.';
    if (password.length < 4) return 'Password must be at least 4 characters.';
    return null;
  };

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    const err = validate();
    if (err) return showToast(err);

    setLoading(true);
    try {
      if (mode === 'login') {
        await login(username.trim(), password);
        showToast('Welcome back! 🌾', 'success');
      } else {
        await register(username.trim(), password);
        showToast('Account created! 🌱', 'success');
      }
      setTimeout(() => onSuccess?.(), 600);
    } catch (err) {
      showToast(err.message);
    } finally {
      setLoading(false);
    }
  }, [mode, username, password, login, register, onSuccess]);

  return (
    <div className="auth-overlay">
      <div className="auth-card">

        {/* Brand */}
        <div className="auth-brand">
          <span className="brand-krishi">कृषि</span>
          <span className="brand-mitra">Mitra</span>
        </div>
        <p className="auth-tagline">AI Farm Assistant · किसान सहायक</p>

        {/* Mode toggle */}
        <div className="auth-toggle" role="tablist">
          <button
            role="tab"
            aria-selected={mode === 'login'}
            className={`auth-tab${mode === 'login' ? ' auth-tab--active' : ''}`}
            onClick={() => { setMode('login'); setToast({ msg: '' }); }}
          >
            Login
          </button>
          <button
            role="tab"
            aria-selected={mode === 'register'}
            className={`auth-tab${mode === 'register' ? ' auth-tab--active' : ''}`}
            onClick={() => { setMode('register'); setToast({ msg: '' }); }}
          >
            Register
          </button>
        </div>

        <Toast msg={toast.msg} type={toast.type} />

        {/* Form */}
        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <div className="auth-field">
            <label className="auth-label" htmlFor="km-username">
              Username · यूजरनेम
            </label>
            <input
              id="km-username"
              type="text"
              className="auth-input"
              placeholder={mode === 'login' ? 'Enter username' : 'Choose a username'}
              value={username}
              onChange={e => setUsername(e.target.value)}
              autoComplete="username"
              autoCapitalize="none"
              disabled={loading}
            />
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="km-password">
              Password · पासवर्ड
            </label>
            <input
              id="km-password"
              type="password"
              className="auth-input"
              placeholder={mode === 'login' ? 'Enter password' : 'Create a password (min 4 chars)'}
              value={password}
              onChange={e => setPassword(e.target.value)}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              disabled={loading}
            />
          </div>

          {mode === 'login' && (
            <p className="auth-hint">
              Demo: username <strong>farmer</strong> / password <strong>1234</strong>
            </p>
          )}

          <button type="submit" className="auth-submit" disabled={loading}>
            {loading
              ? <span className="auth-spinner" aria-label="Loading" />
              : mode === 'login' ? 'Login →' : 'Create Account →'}
          </button>
        </form>

        {/* Switch mode link */}
        <p className="auth-switch">
          {mode === 'login'
            ? <>New here? <button className="auth-switch-btn" onClick={() => setMode('register')}>Create account</button></>
            : <>Already have an account? <button className="auth-switch-btn" onClick={() => setMode('login')}>Login</button></>
          }
        </p>

      </div>
    </div>
  );
}