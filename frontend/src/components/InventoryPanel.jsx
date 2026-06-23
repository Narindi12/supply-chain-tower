const HEALTH = {
  ok:       { icon: "✓", color: "#16a34a", label: "OK" },
  low:      { icon: "!", color: "#d97706", label: "Low" },
  critical: { icon: "✕", color: "#dc2626", label: "Critical" },
};

export default function InventoryPanel({ inventory }) {
  return (
    <div style={{ background: "white", border: "1px solid #e2e8f0", borderRadius: 12, padding: "16px 18px" }}>
      <h2 style={{ fontSize: 13, fontWeight: 500, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", margin: "0 0 12px" }}>
        Inventory health
      </h2>
      {inventory.map((item) => {
        const h = HEALTH[item.health] || HEALTH.ok;
        return (
          <div key={item.sku} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid #f8fafc" }}>
            <div>
              <p style={{ fontSize: 13, fontWeight: 500, color: "#0f172a", margin: 0 }}>{item.name}</p>
              <p style={{ fontSize: 11, color: "#94a3b8", margin: 0 }}>{item.sku}</p>
            </div>
            <div style={{ textAlign: "right" }}>
              <p style={{ fontSize: 13, fontWeight: 500, color: h.color, margin: 0 }}>
                {h.icon} {item.stock.toLocaleString()}
              </p>
              <p style={{ fontSize: 11, color: "#94a3b8", margin: 0 }}>of {item.threshold.toLocaleString()} min</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
