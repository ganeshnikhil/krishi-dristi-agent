// src/main.jsx  — wrap your existing providers with AuthProvider
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import { AppProvider } from './context/AppContext.jsx'
import { AuthProvider } from './context/AuthContext.jsx'   // ← add this

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AppProvider>
      <AuthProvider>          {/* ← wrap App */}
        <App />
      </AuthProvider>
    </AppProvider>
  </StrictMode>,
)