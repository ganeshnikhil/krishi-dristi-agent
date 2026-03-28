// src/context/AppContext.jsx
import { createContext, useContext, useState } from 'react';

const AppContext = createContext(null);
const STORAGE_KEY = 'km_language';

export function AppProvider({ children }) {
  const [language, setLanguageState] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const setLanguage = (lang) => {
    console.log("SETTING LANGUAGE:", lang); // debug
    setLanguageState(lang);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(lang));
    } catch (e) {
      console.error("LocalStorage error:", e);
    }
  };

  const resetLanguage = () => {
    setLanguageState(null);
    localStorage.removeItem(STORAGE_KEY);
  };

  const hasChosen = language !== null;

  return (
    <AppContext.Provider
      value={{
        language,
        setLanguage,
        resetLanguage,
        hasChosen,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used inside AppProvider');
  return ctx;
}