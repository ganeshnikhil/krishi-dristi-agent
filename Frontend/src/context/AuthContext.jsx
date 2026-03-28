// src/context/AuthContext.jsx
import { createContext, useContext, useState, useCallback, useEffect } from 'react';

const AuthContext = createContext(null);

/* ── Mock API — swap this function body for real fetch later ── */
async function mockLogin(username, password) {
    await new Promise(r => setTimeout(r, 800));
    if (username === 'farmer' && password === '1234') {
        return { id: 1, username, name: 'Ramesh Kumar', role: 'farmer' };
    }
    throw new Error('Invalid username or password.');
}

async function mockRegister(username, password) {
    await new Promise(r => setTimeout(r, 900));
    if (username.length < 3) throw new Error('Username must be at least 3 characters.');
    return { id: Date.now(), username, name: username, role: 'farmer' };
}
/* ─────────────────────────────────────────────────────────── */

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [isAuthenticated, setIsAuth] = useState(false);
    const [pendingAction, setPendingAction] = useState(null); // 'mic' | 'chat' | null

    /* Rehydrate from localStorage on mount */
    useEffect(() => {
        try {
            const saved = localStorage.getItem('km_user');
            if (saved) {
                const parsed = JSON.parse(saved);
                setUser(parsed);
                setIsAuth(true);
            }
        } catch { localStorage.removeItem('km_user'); }
    }, []);

    const login = useCallback(async (username, password) => {
        const userData = await mockLogin(username, password);
        setUser(userData);
        setIsAuth(true);
        localStorage.setItem('km_user', JSON.stringify(userData));
        return userData;
    }, []);

    const register = useCallback(async (username, password) => {
        const userData = await mockRegister(username, password);
        setUser(userData);
        setIsAuth(true);
        localStorage.setItem('km_user', JSON.stringify(userData));
        return userData;
    }, []);

    const logout = useCallback(() => {
        setUser(null);
        setIsAuth(false);
        setPendingAction(null);
        localStorage.removeItem('km_user');
    }, []);

    return (
        <AuthContext.Provider value={{
            user,
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