// src/components/HamburgerMenu.jsx
import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';

export default function HamburgerMenu({ onOpenAuth }) {
  const { isAuthenticated, user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const menuRef = useRef(null);

  /* Close on outside click */
  useEffect(() => {
    if (!open) return;
    const handler = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [open]);

  /* Close on Escape */
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') setOpen(false); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  return (
    <div className="hm-wrap" ref={menuRef}>
      {/* Hamburger trigger */}
      <button
        className={`hamburger${open ? ' hamburger--open' : ''}`}
        onClick={() => setOpen(v => !v)}
        aria-label="Open menu"
        aria-expanded={open}
      >
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
          {open ? (
            <>
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6"  y1="6" x2="18" y2="18" />
            </>
          ) : (
            <>
              <line x1="4" y1="6"  x2="20" y2="6"  />
              <line x1="4" y1="12" x2="16" y2="12" />
              <line x1="4" y1="18" x2="20" y2="18" />
            </>
          )}
        </svg>
      </button>

      {/* Drawer */}
      {open && (
        <div className="hm-drawer" role="dialog" aria-label="Menu">
          <div className="hm-drawer-inner">

            {/* User section */}
            {isAuthenticated ? (
              <div className="hm-profile">
                <div className="hm-avatar">
                  {user?.name?.[0]?.toUpperCase() ?? 'F'}
                </div>
                <div>
                  <div className="hm-username">{user?.name ?? user?.username}</div>
                  <div className="hm-role">🌾 Farmer</div>
                </div>
              </div>
            ) : (
              <div className="hm-auth-prompt">
                <div className="hm-auth-icon">🔒</div>
                <p className="hm-auth-text">Login to access voice assistant &amp; AI chat</p>
              </div>
            )}

            <div className="hm-divider" />

            {/* Nav links */}
            <nav className="hm-nav">
              <a href="#about"   className="hm-link" onClick={() => setOpen(false)}>About</a>
              <a href="#privacy" className="hm-link" onClick={() => setOpen(false)}>Privacy Policy</a>
              <a href="#terms"   className="hm-link" onClick={() => setOpen(false)}>Terms</a>
              <a href="#contact" className="hm-link" onClick={() => setOpen(false)}>Contact</a>
            </nav>

            <div className="hm-divider" />

            {/* Auth CTA */}
            {isAuthenticated ? (
              <button
                className="hm-btn hm-btn--logout"
                onClick={() => { logout(); setOpen(false); }}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                  <polyline points="16 17 21 12 16 7"/>
                  <line x1="21" y1="12" x2="9" y2="12"/>
                </svg>
                Logout
              </button>
            ) : (
              <button
                className="hm-btn hm-btn--login"
                onClick={() => { onOpenAuth(); setOpen(false); }}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                  <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>
                  <polyline points="10 17 15 12 10 7"/>
                  <line x1="15" y1="12" x2="3" y2="12"/>
                </svg>
                Login / Register
              </button>
            )}

          </div>
        </div>
      )}
    </div>
  );
}