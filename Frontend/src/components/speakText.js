export function speakText(text, lang = "en-IN") {
  const speech = new SpeechSynthesisUtterance(text);

  speech.lang = lang;
  speech.rate = 1;
  speech.pitch = 1;

  const setVoiceAndSpeak = () => {
    const voices = window.speechSynthesis.getVoices();

    const voice = voices.find(v => v.lang === lang);

    if (voice) speech.voice = voice;

    window.speechSynthesis.speak(speech);
  };

  const voices = window.speechSynthesis.getVoices();

  if (voices.length === 0) {
    // 🔥 voices not ready yet → wait
    window.speechSynthesis.onvoiceschanged = () => {
      setVoiceAndSpeak();
    };
  } else {
    // ✅ voices already loaded
    setVoiceAndSpeak();
  }
}