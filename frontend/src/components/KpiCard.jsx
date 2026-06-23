export default function KpiCard({ label, value, delta, positive }) {
  return (
    <div style={{ background: "#f8fafc", borderRadius: 10, padding: "16px 18px" }}>
      <p style={{ fontSize: 12, color: "#64748b", margin: "0 0 6px" }}>{label}</p>
      <p style={{ fontSize: 24, fontWeight: 600, margin: "0 0 4px", color: "#0f172a" }}>{value}</p>
      <p style={{ fontSize: 12, margin: 0, color: positive ? "#16a34a" : "#dc2626" }}>
        {positive ? "↑" : "↓"} {delta}
      </p>
    </div>
  );
}
