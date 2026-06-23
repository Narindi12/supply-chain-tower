"""
Supply Chain Control Tower — Data Simulator
Generates realistic synthetic events: shipments, alerts, demand spikes, delays.
Run standalone or import generate_snapshot() for API use.
"""

import random
import json
from datetime import datetime, timedelta

# ── Seed data ─────────────────────────────────────────────────────────────────

ORIGINS = ["Shanghai", "Guangzhou", "Mumbai", "Dubai", "Tokyo", "Berlin", "Houston", "Chicago"]
DESTINATIONS = ["Los Angeles", "Rotterdam", "Frankfurt", "New York", "Seattle", "Dallas", "Miami", "Warsaw"]
MODES = ["Sea", "Air", "Road", "Rail"]
MODE_WEIGHTS = [0.45, 0.25, 0.20, 0.10]

SUPPLIERS = [
    {"id": "SUP-001", "name": "Acme Parts",     "base_score": 94},
    {"id": "SUP-002", "name": "StellarMFG",     "base_score": 87},
    {"id": "SUP-003", "name": "Pacific Source",  "base_score": 76},
    {"id": "SUP-004", "name": "TechFoundry",    "base_score": 61},
    {"id": "SUP-005", "name": "GlobalComp",     "base_score": 42},
]

SKUS = [
    {"sku": "IC-7701", "name": "Microcontrollers",   "min": 5000,  "max": 15000, "threshold": 5000},
    {"sku": "MB-2204", "name": "Motor Bearings",     "min": 500,   "max": 3000,  "threshold": 2000},
    {"sku": "CS-0091", "name": "Capacitors (50V)",   "min": 10000, "max": 50000, "threshold": 10000},
    {"sku": "LB-3310", "name": "Li-Ion Cells",       "min": 200,   "max": 4000,  "threshold": 1500},
    {"sku": "CB-5502", "name": "Control Boards",     "min": 1000,  "max": 5000,  "threshold": 2000},
    {"sku": "HS-1140", "name": "Heat Sinks",         "min": 400,   "max": 2500,  "threshold": 1200},
]

ALERT_TEMPLATES = [
    ("{sid}: Weather delay at {dest} hub — {hours}h expected",       "delay",   "high"),
    ("{sid}: Customs hold in {dest} — documentation pending",        "customs", "medium"),
    ("Cold chain breach: {warehouse} temp above threshold",          "quality", "high"),
    ("{sid}: Driver hours limit reached — rescheduling needed",      "compliance", "medium"),
    ("Demand spike detected: {category} +{pct}% in {region}",       "demand",  "low"),
    ("Spot rate drop: {lane} lanes down {pct}% — opportunity",      "cost",    "low"),
    ("{sid}: Port congestion at {dest} — 24–48h additional wait",   "delay",   "medium"),
    ("Inventory reorder triggered: {sku} below safety stock",       "inventory","medium"),
]

WAREHOUSES = ["Warehouse 3", "Warehouse 7", "Warehouse 12", "Cold Store A"]
CATEGORIES = ["Electronics", "Automotive parts", "Pharmaceuticals", "Consumer goods"]
REGIONS = ["Southeast Asia", "EU", "North America", "APAC", "LATAM"]
LANES = ["APAC → EU", "APAC → NA", "EU → NA", "ME → EU"]

# ── Helpers ───────────────────────────────────────────────────────────────────

def rand_shipment_id():
    return f"SH-{random.randint(4000, 6999)}"

def rand_eta(mode: str) -> str:
    days = {"Sea": random.randint(3, 14), "Air": random.randint(1, 3),
            "Road": random.randint(0, 2), "Rail": random.randint(1, 4)}
    dt = datetime.now() + timedelta(days=days[mode])
    return dt.strftime("%b %d")

def rand_status() -> str:
    return random.choices(
        ["On time", "At risk", "Delayed", "In transit"],
        weights=[0.62, 0.18, 0.12, 0.08]
    )[0]

def rand_alert(shipment_ids: list[str]) -> dict:
    template, category, severity = random.choice(ALERT_TEMPLATES)
    sid = random.choice(shipment_ids) if shipment_ids else rand_shipment_id()
    dest = random.choice(DESTINATIONS)
    message = template.format(
        sid=sid, dest=dest,
        hours=random.randint(6, 36),
        warehouse=random.choice(WAREHOUSES),
        category=random.choice(CATEGORIES),
        region=random.choice(REGIONS),
        pct=random.randint(8, 32),
        lane=random.choice(LANES),
        sku=random.choice(SKUS)["sku"],
    )
    mins_ago = random.randint(1, 240)
    if mins_ago < 60:
        time_str = f"{mins_ago} min ago"
    else:
        time_str = f"{mins_ago // 60}h {mins_ago % 60}m ago"

    return {"id": f"ALT-{random.randint(1000,9999)}", "message": message,
            "category": category, "severity": severity, "timestamp": time_str}

# ── Core generators ───────────────────────────────────────────────────────────

def generate_shipments(count: int = 142) -> list[dict]:
    shipments = []
    for _ in range(count):
        mode = random.choices(MODES, weights=MODE_WEIGHTS)[0]
        origin = random.choice(ORIGINS)
        dest = random.choice([d for d in DESTINATIONS])
        status = rand_status()
        shipments.append({
            "id": rand_shipment_id(),
            "origin": origin,
            "destination": dest,
            "route": f"{origin} → {dest}",
            "mode": mode,
            "eta": rand_eta(mode),
            "status": status,
            "weight_kg": round(random.uniform(50, 5000), 1),
            "value_usd": random.randint(500, 250000),
        })
    return shipments


def generate_alerts(shipment_ids: list[str], count: int = 8) -> list[dict]:
    return [rand_alert(shipment_ids) for _ in range(count)]


def generate_suppliers() -> list[dict]:
    result = []
    for s in SUPPLIERS:
        noise = random.uniform(-4, 4)
        score = max(0, min(100, round(s["base_score"] + noise, 1)))
        result.append({
            "id": s["id"],
            "name": s["name"],
            "performance_score": score,
            "on_time_delivery": round(score * 0.95 + random.uniform(-2, 2), 1),
            "quality_rating": round(score * 0.98 + random.uniform(-3, 3), 1),
            "lead_time_days": random.randint(3, 21),
        })
    return result


def generate_inventory() -> list[dict]:
    result = []
    for item in SKUS:
        stock = random.randint(item["min"], item["max"])
        if stock < item["threshold"] * 0.5:
            health = "critical"
        elif stock < item["threshold"]:
            health = "low"
        else:
            health = "ok"
        result.append({
            "sku": item["sku"],
            "name": item["name"],
            "stock": stock,
            "threshold": item["threshold"],
            "health": health,
            "days_of_supply": round(stock / random.randint(80, 400), 1),
        })
    return result


def compute_kpis(shipments: list[dict], alerts: list[dict]) -> dict:
    total = len(shipments)
    on_time = sum(1 for s in shipments if s["status"] == "On time")
    delayed = sum(1 for s in shipments if s["status"] == "Delayed")
    at_risk = sum(1 for s in shipments if s["status"] == "At risk")
    avg_value = sum(s["value_usd"] for s in shipments) / total if total else 0
    cost_per_unit = round(random.uniform(4.50, 5.20), 2)
    return {
        "active_shipments": total,
        "on_time_rate": round(on_time / total * 100, 1) if total else 0,
        "delayed_count": delayed,
        "at_risk_count": at_risk,
        "active_alerts": len(alerts),
        "avg_shipment_value_usd": round(avg_value, 2),
        "cost_per_unit_usd": cost_per_unit,
        "total_value_in_transit_usd": sum(s["value_usd"] for s in shipments),
    }


# ── Main snapshot ─────────────────────────────────────────────────────────────

def generate_snapshot(shipment_count: int = 142) -> dict:
    """Return a full simulated snapshot. Call this from the API."""
    shipments = generate_shipments(shipment_count)
    ids = [s["id"] for s in shipments]
    alerts = generate_alerts(ids)
    suppliers = generate_suppliers()
    inventory = generate_inventory()
    kpis = compute_kpis(shipments, alerts)
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "kpis": kpis,
        "shipments": shipments,
        "alerts": alerts,
        "suppliers": suppliers,
        "inventory": inventory,
    }


if __name__ == "__main__":
    snapshot = generate_snapshot()
    print(json.dumps(snapshot, indent=2))
    print(f"\n✓ Snapshot generated at {snapshot['generated_at']}")
    print(f"  {snapshot['kpis']['active_shipments']} shipments | "
          f"{snapshot['kpis']['on_time_rate']}% on-time | "
          f"{snapshot['kpis']['active_alerts']} alerts")
