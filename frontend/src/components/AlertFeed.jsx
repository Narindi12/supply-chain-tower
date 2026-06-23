const SEV_COLORS = {
  high:   { icon: "⚠️", color: "#dc2626" },
  medium: { icon: "🔶", color: "#d97706" },
  low:    { icon: "ℹ️", color: "#2563eb" },
};

export default function AlertFeed({ alerts }) {
  return (
    <div style={{ background: "white", border: "1px solid #e2e8f0", borderRadius: 12, padding: "16px 18px" }}>
      <h2 style={{ fontSize: 13, fontWeight: 500, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", margin: "0 0 12px" }}>
        Alerts & exceptions
      </h2>
      {alerts.map((a) => {
        const sev = SEV_COLORS[a.severity] || SEV_COLORS.low;
        return (
          <div key={a.id} style={{ display: "flex", gap: 10, padding: "8px 0", borderBottom: "1px solid #f8fafc" }}>
            <span style={{ fontSize: 16, flexShrink: 0, marginTop: 1 }}>{sev.icon}</span>
            <div style={{ flex: 1 }}>
              <p style={{ fontSize: 13, color: "#0f172a", margin: "0 0 2px" }}>{a.message}</p>
              <span style={{ fontSize: 11, color: "#94a3b8" }}>{a.timestamp}</span>
            </div>
            <span style={{ fontSize: 11, padding: "2px 8px", borderRadius: 4, background: "#f1f5f9", color: sev.color, fontWeight: 500, alignSelf: "flex-start", whiteSpace: "nowrap" }}>
              {a.severity}
            </span>
          </div>
        );
      })}
    </div>
  );
}
