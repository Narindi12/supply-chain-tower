import { useState } from "react";
import { useControlTower } from "./hooks/useControlTower";
import KpiCard from "./components/KpiCard";
import ShipmentTable from "./components/ShipmentTable";
import AlertFeed from "./components/AlertFeed";
import SupplierChart from "./components/SupplierChart";
import InventoryPanel from "./components/InventoryPanel";

export default function App() {
  const { data, loading, usingMock, refresh } = useControlTower();
  const [modeFilter, setModeFilter] = useState("All");

  if (loading && !data) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh", color: "#888" }}>
        Loading control tower…
      </div>
    );
  }

  const { kpis, shipments, alerts, suppliers, inventory } = data;
  const filteredShipments = modeFilter === "All"
    ? shipments
    : shipments.filter((s) => s.mode === modeFilter);

  return (
    <div style={{ maxWidth: 1200, margin: "0 auto", padding: "24px 20px", fontFamily: "system-ui, sans-serif" }}>

      {/* Header */}
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 600, margin: 0 }}>Supply Chain Control Tower</h1>
          {usingMock && (
            <span style={{ fontSize: 12, color: "#f59e0b", background: "#fef3c7", padding: "2px 8px", borderRadius: 4, marginTop: 4, display: "inline-block" }}>
              Demo mode — start backend for live data
            </span>
          )}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ fontSize: 12, color: "#22c55e", display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#22c55e", display: "inline-block", animation: "pulse 2s infinite" }} />
            Live
          </span>
          <button onClick={refresh} style={{ fontSize: 13, padding: "6px 14px", borderRadius: 8, border: "1px solid #e2e8f0", background: "white", cursor: "pointer" }}>
            ↻ Refresh
          </button>
        </div>
      </header>

      {/* KPI row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 20 }}>
        <KpiCard label="Active shipments"   value={kpis.active_shipments}                  delta="+8 vs yesterday"    positive />
        <KpiCard label="On-time rate"        value={`${kpis.on_time_rate}%`}                delta="+2.1% this week"    positive />
        <KpiCard label="Active alerts"       value={kpis.active_alerts}                     delta={`${kpis.delayed_count} delayed`} positive={false} />
        <KpiCard label="Cost per unit"       value={`$${kpis.cost_per_unit_usd}`}           delta="-$0.14 vs target"   positive />
      </div>

      {/* Main 2-column */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        <ShipmentTable
          shipments={filteredShipments}
          modeFilter={modeFilter}
          onModeChange={setModeFilter}
        />
        <AlertFeed alerts={alerts} />
      </div>

      {/* Bottom 2-column */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <SupplierChart suppliers={suppliers} />
        <InventoryPanel inventory={inventory} />
      </div>
    </div>
  );
}
