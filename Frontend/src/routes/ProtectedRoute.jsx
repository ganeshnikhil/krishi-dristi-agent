// src/routes/ProtectedRoute.jsx
import { useAuth } from '../context/AuthContext';

/**
 * Wrap any action trigger (mic click, chat click) with this hook.
 * Returns a guarded version of the handler — if not authenticated,
 * sets pendingAction and calls onRedirect instead of running the action.
 *
 * Usage:
 *   const guardedOpen = useProtectedAction('mic', () => setIsChatOpen(true), () => setShowAuth(true));
 *   <button onClick={guardedOpen}>Mic</button>
 */
export function useProtectedAction(actionName, action, onRedirect) {
    const { isAuthenticated, setPendingAction } = useAuth();

    return function guardedHandler(...args) {
        if (isAuthenticated) {
            action(...args);
        } else {
            setPendingAction(actionName);
            onRedirect();
        }
    };
}

/**
 * Component wrapper — renders children only if authenticated,
 * otherwise renders fallback (or null).
 *
 * Usage:
 *   <ProtectedRoute fallback={<AuthPage />}>
 *     <SecretComponent />
 *   </ProtectedRoute>
 */
export default function ProtectedRoute({ children, fallback = null }) {
    const { isAuthenticated } = useAuth();
    return isAuthenticated ? children : fallback;
}