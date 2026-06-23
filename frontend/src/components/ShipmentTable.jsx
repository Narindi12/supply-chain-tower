const MODES = ["All", "Sea", "Air", "Road", "Rail"];

const STATUS_COLORS = {
  "On time":   { bg: "#dcfce7", color: "#166534" },
  "Delayed":   { bg: "#fee2e2", color: "#991b1b" },
  "At risk":   { bg: "#fef9c3", color: "#854d0e" },
  "In transit":{ bg: "#dbeafe", color: "#1e40af" },
};

export default function ShipmentTable({ shipments, modeFilter, onModeChange }) {
  return (
    <div style={{ background: "white", border: "1px solid #e2e8f0", borderRadius: 12, padding: "16px 18px" }}>
      <h2 style={{ fontSize: 13, fontWeight: 500, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", margin: "0 0 12px" }}>
        Active shipments
      </h2>

      {/* Mode filter */}
      <div style={{ display: "flex", gap: 6, marginBottom: 12, flexWrap: "wrap" }}>
        {MODES.map((m) => (
          <button
            key={m}
            onClick={() => onModeChange(m)}
            style={{
              fontSize: 12, padding: "4px 10px", borderRadius: 6, cursor: "pointer",
              border: "1px solid",
              borderColor: modeFilter === m ? "#3b82f6" : "#e2e8f0",
              background: modeFilter === m ? "#eff6ff" : "white",
              color: modeFilter === m ? "#1d4ed8" : "#64748b",
              fontWeight: modeFilter === m ? 500 : 400,
            }}
          >
            {m}
          </button>
        ))}
      </div>

      {/* Table */}
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
        <thead>
          <tr style={{ borderBottom: "1px solid #f1f5f9" }}>
            {["ID", "Route", "Mode", "ETA", "Status"].map((h) => (
              <th key={h} style={{ textAlign: "left", padding: "6px 4px", color: "#94a3b8", fontWeight: 500, fontSize: 11 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {shipments.slice(0, 8).map((s) => {
            const sc = STATUS_COLORS[s.status] || { bg: "#f1f5f9", color: "#334155" };
            return (
              <tr key={s.id} style={{ borderBottom: "1px solid #f8fafc" }}>
                <td style={{ padding: "7px 4px", fontWeight: 500, color: "#0f172a" }}>{s.id}</td>
                <td style={{ padding: "7px 4px", color: "#64748b", maxWidth: 140, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{s.route}</td>
                <td style={{ padding: "7px 4px", color: "#64748b" }}>{s.mode}</td>
                <td style={{ padding: "7px 4px", color: "#64748b" }}>{s.eta}</td>
                <td style={{ padding: "7px 4px" }}>
                  <span style={{ background: sc.bg, color: sc.color, fontSize: 11, padding: "2px 8px", borderRadius: 4, fontWeight: 500 }}>
                    {s.status}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      {shipments.length > 8 && (
        <p style={{ fontSize: 12, color: "#94a3b8", marginTop: 10, textAlign: "center" }}>
          +{shipments.length - 8} more shipments
        </p>
      )}
    </div>
  );
}
