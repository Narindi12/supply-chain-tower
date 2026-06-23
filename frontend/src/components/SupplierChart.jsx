function scoreColor(score) {
  if (score >= 85) return "#16a34a";
  if (score >= 65) return "#ca8a04";
  return "#dc2626";
}

export default function SupplierChart({ suppliers }) {
  return (
    <div style={{ background: "white", border: "1px solid #e2e8f0", borderRadius: 12, padding: "16px 18px" }}>
      <h2 style={{ fontSize: 13, fontWeight: 500, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", margin: "0 0 14px" }}>
        Supplier performance
      </h2>
      {suppliers.map((s) => (
        <div key={s.id} style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
          <span style={{ minWidth: 108, fontSize: 13, fontWeight: 500, color: "#0f172a" }}>{s.name}</span>
          <div style={{ flex: 1, background: "#f1f5f9", borderRadius: 4, height: 7, overflow: "hidden" }}>
            <div style={{ width: `${s.performance_score}%`, height: "100%", background: scoreColor(s.performance_score), borderRadius: 4, transition: "width 0.6s ease" }} />
          </div>
          <span style={{ fontSize: 13, color: "#64748b", minWidth: 34, textAlign: "right" }}>{s.performance_score}%</span>
        </div>
      ))}
    </div>
  );
}
