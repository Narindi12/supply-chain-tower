"""
Supply Chain Control Tower — FastAPI Backend
Run: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import time

from simulator import generate_snapshot, generate_shipments, generate_alerts, generate_inventory

app = FastAPI(
    title="Supply Chain Control Tower API",
    description="Real-time logistics monitoring — shipments, alerts, suppliers, inventory",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory store (swap for PostgreSQL in production) ───────────────────────
_cache: dict = {}
_cache_ts: float = 0
CACHE_TTL = 10  # seconds — refresh simulation every 10s


def get_or_refresh() -> dict:
    global _cache, _cache_ts
    if not _cache or (time.time() - _cache_ts) > CACHE_TTL:
        _cache = generate_snapshot()
        _cache_ts = time.time()
    return _cache


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "service": "Supply Chain Control Tower API"}


@app.get("/api/snapshot")
def snapshot():
    """Full dashboard snapshot — KPIs, shipments, alerts, suppliers, inventory."""
    return get_or_refresh()


@app.get("/api/kpis")
def kpis():
    """Top-level KPI metrics only."""
    return get_or_refresh()["kpis"]


@app.get("/api/shipments")
def shipments(
    mode: Optional[str] = Query(None, description="Filter by mode: Air|Sea|Road|Rail"),
    status: Optional[str] = Query(None, description="Filter by status: On time|Delayed|At risk"),
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
):
    """Paginated shipment list with optional mode/status filters."""
    data = get_or_refresh()["shipments"]
    if mode:
        data = [s for s in data if s["mode"].lower() == mode.lower()]
    if status:
        data = [s for s in data if s["status"].lower() == status.lower()]
    return {
        "total": len(data),
        "limit": limit,
        "offset": offset,
        "results": data[offset: offset + limit],
    }


@app.get("/api/shipments/{shipment_id}")
def shipment_detail(shipment_id: str):
    """Single shipment by ID."""
    data = get_or_refresh()["shipments"]
    match = next((s for s in data if s["id"] == shipment_id), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Shipment {shipment_id} not found")
    return match


@app.get("/api/alerts")
def alerts(severity: Optional[str] = Query(None, description="low|medium|high")):
    """Active alerts and exceptions."""
    data = get_or_refresh()["alerts"]
    if severity:
        data = [a for a in data if a["severity"].lower() == severity.lower()]
    return {"count": len(data), "alerts": data}


@app.get("/api/suppliers")
def suppliers():
    """Supplier performance scores."""
    return get_or_refresh()["suppliers"]


@app.get("/api/inventory")
def inventory(health: Optional[str] = Query(None, description="ok|low|critical")):
    """Inventory health by SKU."""
    data = get_or_refresh()["inventory"]
    if health:
        data = [i for i in data if i["health"].lower() == health.lower()]
    return {"count": len(data), "items": data}


@app.post("/api/refresh")
def force_refresh():
    """Force a fresh simulation snapshot (for demo/testing)."""
    global _cache_ts
    _cache_ts = 0
    snap = get_or_refresh()
    return {"refreshed_at": snap["generated_at"], "kpis": snap["kpis"]}
