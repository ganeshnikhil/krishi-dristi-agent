// src/components/AdvisoryTicker.jsx

const ADVISORY_ALERTS = [
  "🔴 HIGH RISK: Frost expected tonight — cover wheat crops before 6 PM",
  "⚠️ ALERT: Heavy rainfall (40mm+) predicted in next 24 hours — delay irrigation",
  "🔴 PEST WARNING: Aphid outbreak reported in Dehradun region — apply neem spray",
  "⚠️ ALERT: Soil moisture critically low in Zone B — irrigate within 12 hours",
  "🔴 HIGH RISK: Thunderstorm likely Friday evening — secure loose farm equipment",
  "⚠️ ALERT: PM Fasal Bima Yojana deadline in 3 days — enroll immediately",
  "🔴 DISEASE RISK: High humidity (82%) increases fungal risk — inspect leaves daily",
];

export default function AdvisoryTicker() {
  const text = ADVISORY_ALERTS.join("          •          ");
  const doubled = text + "          •          " + text;

  return (
    <div style={{
      background: "linear-gradient(90deg, #b71c1c, #c62828, #b71c1c)",
      overflow: "hidden",
      padding: "11px 0",
      borderTop: "1.5px solid #e53935",
      borderBottom: "1.5px solid #e53935",
      borderRadius: "0 0 18px 18px",
      position: "relative",
    }}>
      {/* Left fade mask */}
      <div style={{
        position: "absolute", left: 0, top: 0, bottom: 0, width: 48,
        background: "linear-gradient(to right, #c62828, transparent)",
        zIndex: 2, pointerEvents: "none",
      }} />
      {/* Right fade mask */}
      <div style={{
        position: "absolute", right: 0, top: 0, bottom: 0, width: 48,
        background: "linear-gradient(to left, #c62828, transparent)",
        zIndex: 2, pointerEvents: "none",
      }} />

      <div style={{
        display: "inline-block",
        whiteSpace: "nowrap",
        animation: "advisory-scroll 55s linear infinite",
        fontSize: "0.85rem",
        fontWeight: 600,
        color: "#ffebee",
        fontFamily: "'Outfit', system-ui, sans-serif",
        letterSpacing: "0.025em",
        lineHeight: 1.4,
      }}>
        {doubled}
      </div>

      <style>{`
        @keyframes advisory-scroll {
          0%   { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
      `}</style>
    </div>
  );
}