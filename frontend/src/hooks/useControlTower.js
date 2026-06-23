/**
 * useControlTower — fetches & auto-refreshes the full dashboard snapshot.
 * Falls back to mock data so the UI works without a running backend.
 */
import { useState, useEffect, useCallback } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
const POLL_INTERVAL = 15_000; // 15s

function mockSnapshot() {
  const statuses = ["On time", "On time", "On time", "At risk", "Delayed"];
  const modes = ["Sea", "Air", "Road", "Rail"];
  const origins = ["Shanghai", "Dubai", "Mumbai", "Tokyo", "Berlin", "Houston"];
  const dests = ["Los Angeles", "Rotterdam", "Frankfurt", "New York", "Seattle"];
  const rand = (a) => a[Math.floor(Math.random() * a.length)];
  const shipments = Array.from({ length: 12 }, (_, i) => ({
    id: `SH-${4800 + i}`,
    origin: rand(origins),
    destination: rand(dests),
    route: `${rand(origins)} → ${rand(dests)}`,
    mode: rand(modes),
    eta: `Jun ${23 + Math.floor(Math.random() * 8)}`,
    status: rand(statuses),
    value_usd: Math.round(Math.random() * 200000 + 5000),
  }));
  return {
    generated_at: new Date().toISOString(),
    kpis: {
      active_shipments: 142,
      on_time_rate: 91.4,
      delayed_count: 12,
      at_risk_count: 8,
      active_alerts: 7,
      cost_per_unit_usd: 4.82,
      total_value_in_transit_usd: 4_820_000,
    },
    shipments,
    alerts: [
      { id: "a1", message: "SH-4822: Weather delay at Frankfurt hub — 18h expected", severity: "high",   category: "delay",    timestamp: "12 min ago" },
      { id: "a2", message: "SH-4824: Customs hold in Rotterdam — docs pending",      severity: "medium", category: "customs",  timestamp: "34 min ago" },
      { id: "a3", message: "Cold chain breach: Warehouse 3 temp above threshold",    severity: "high",   category: "quality",  timestamp: "51 min ago" },
      { id: "a4", message: "Demand spike: Electronics +22% in Southeast Asia",       severity: "low",    category: "demand",   timestamp: "2h ago" },
      { id: "a5", message: "Spot rate drop: APAC → EU lanes down 6%",               severity: "low",    category: "cost",     timestamp: "3h ago" },
    ],
    suppliers: [
      { id: "s1", name: "Acme Parts",     performance_score: 94 },
      { id: "s2", name: "StellarMFG",     performance_score: 87 },
      { id: "s3", name: "Pacific Source",  performance_score: 76 },
      { id: "s4", name: "TechFoundry",    performance_score: 61 },
      { id: "s5", name: "GlobalComp",     performance_score: 42 },
    ],
    inventory: [
      { sku: "IC-7701", name: "Microcontrollers",  stock: 8200,  threshold: 5000,  health: "ok" },
      { sku: "MB-2204", name: "Motor Bearings",    stock: 1100,  threshold: 2000,  health: "low" },
      { sku: "CS-0091", name: "Capacitors (50V)",  stock: 31000, threshold: 10000, health: "ok" },
      { sku: "LB-3310", name: "Li-Ion Cells",      stock: 380,   threshold: 1500,  health: "critical" },
      { sku: "CB-5502", name: "Control Boards",    stock: 2700,  threshold: 2000,  health: "ok" },
      { sku: "HS-1140", name: "Heat Sinks",        stock: 900,   threshold: 1200,  health: "low" },
    ],
  };
}

export function useControlTower() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [usingMock, setUsingMock] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/snapshot`, { signal: AbortSignal.timeout(5000) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setData(json);
      setUsingMock(false);
      setError(null);
    } catch {
      // Backend not running — use mock so the UI still works
      setData(mockSnapshot());
      setUsingMock(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const id = setInterval(fetchData, POLL_INTERVAL);
    return () => clearInterval(id);
  }, [fetchData]);

  const refresh = () => { setLoading(true); fetchData(); };

  return { data, loading, error, usingMock, refresh };
}
