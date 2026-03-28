// src/context/AuthContext.jsx
import { createContext, useContext, useState, useCallback, useEffect } from 'react';

const AuthContext = createContext(null);

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/* ── Real API calls ── */
async function apiLogin(username, password) {
    const res = await fetch(`${API}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Login failed.');
    // data = { access_token, user: { id, username, ... } }
    return { token: data.access_token, user: data.user };
}

async function apiRegister(username, password) {
    const res = await fetch(`${API}/api/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Registration failed.');
    // After register, log them in to get a token
    return apiLogin(username, password);
}
/* ─────────────────────────────────────────────────────────── */

export function AuthProvider({ children }) {
    const [user, setUser]           = useState(null);
    const [token, setToken]         = useState(null);
    const [isAuthenticated, setIsAuth] = useState(false);
    const [pendingAction, setPendingAction] = useState(null); // 'mic' | 'chat' | null

    /* Rehydrate from localStorage on mount */
    useEffect(() => {
        try {
            const savedUser  = localStorage.getItem('km_user');
            const savedToken = localStorage.getItem('km_token');
            if (savedUser && savedToken) {
                setUser(JSON.parse(savedUser));
                setToken(savedToken);
                setIsAuth(true);
            }
        } catch { localStorage.removeItem('km_user'); localStorage.removeItem('km_token'); }
    }, []);

    const login = useCallback(async (username, password) => {
        const { token: jwt, user: userData } = await apiLogin(username, password);
        setUser(userData);
        setToken(jwt);
        setIsAuth(true);
        localStorage.setItem('km_user',  JSON.stringify(userData));
        localStorage.setItem('km_token', jwt);
        return userData;
    }, []);

    const register = useCallback(async (username, password) => {
        const { token: jwt, user: userData } = await apiRegister(username, password);
        setUser(userData);
        setToken(jwt);
        setIsAuth(true);
        localStorage.setItem('km_user',  JSON.stringify(userData));
        localStorage.setItem('km_token', jwt);
        return userData;
    }, []);

    const logout = useCallback(() => {
        setUser(null);
        setToken(null);
        setIsAuth(false);
        setPendingAction(null);
        localStorage.removeItem('km_user');
        localStorage.removeItem('km_token');
    }, []);

    return (
        <AuthContext.Provider value={{
            user,
            token,
            isAuthenticated,
            pendingAction,
            setPendingAction,
            login,
            register,
            logout,
        }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
    return ctx;
}