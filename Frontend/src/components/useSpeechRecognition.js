// src/components/useSpeechRecognition.js
//
// FIX: Chrome kills recognition after ~10s of silence or network hiccups.
// Solution: use shouldListenRef to auto-restart in onend if we still want to listen.

import { useEffect, useRef, useState, useCallback } from "react";

export default function useSpeechRecognition(selectedLanguage = "en-IN") {
  const [isListening, setIsListening]   = useState(false);
  const [transcript,  setTranscript]    = useState("");

  const recognitionRef  = useRef(null);
  const shouldListenRef = useRef(false);   // desired state — survives re-renders
  const transcriptRef   = useRef("");      // accumulate finals across restarts

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.error("❌ SpeechRecognition not supported in this browser.");
      return;
    }

    const recognition       = new SpeechRecognition();
    recognition.continuous      = true;
    recognition.interimResults  = true;
    recognition.lang            = selectedLanguage;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsListening(true);
    };

    // KEY FIX: auto-restart if we still want to listen
    recognition.onend = () => {
      if (shouldListenRef.current) {
        try { recognition.start(); } catch { /* already starting */ }
      } else {
        setIsListening(false);
      }
    };

    recognition.onresult = (event) => {
      let interim = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const t = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          transcriptRef.current += t + " ";
        } else {
          interim = t;
        }
      }

      setTranscript(transcriptRef.current + interim);
    };

    recognition.onerror = (e) => {
      // "no-speech" is normal — let onend handle the restart
      if (e.error === "no-speech") return;

      // For real errors, stop cleanly
      console.error("🎤 Recognition error:", e.error);
      shouldListenRef.current = false;
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      shouldListenRef.current = false;
      try { recognition.stop(); } catch {}
    };
  }, [selectedLanguage]);

  // ── Start ────────────────────────────────────────────────────────────────
  const startListening = useCallback(() => {
    if (!recognitionRef.current) return;

    // Clear previous transcript
    transcriptRef.current = "";
    setTranscript("");

    shouldListenRef.current = true;

    try { recognitionRef.current.abort(); } catch {}

    // Small delay so abort() resolves before start()
    setTimeout(() => {
      if (!shouldListenRef.current) return;
      try { recognitionRef.current.start(); } catch (err) {
        console.log("Start error (safe to ignore):", err.message);
      }
    }, 120);
  }, []);

  // ── Stop ─────────────────────────────────────────────────────────────────
  const stopListening = useCallback(() => {
    shouldListenRef.current = false;
    try { recognitionRef.current?.stop(); } catch {}
  }, []);

  // ── Reset transcript ─────────────────────────────────────────────────────
  const resetTranscript = useCallback(() => {
    transcriptRef.current = "";
    setTranscript("");
  }, []);

  return { transcript, isListening, startListening, stopListening, resetTranscript };
}