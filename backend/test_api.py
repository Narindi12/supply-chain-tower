"""
API integration tests for main.py
Run: pytest test_api.py -v
Install: pip install httpx pytest
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ── /api/snapshot ─────────────────────────────────────────────────────────────

class TestSnapshot:
    def test_status_200(self):
        r = client.get("/api/snapshot")
        assert r.status_code == 200

    def test_top_level_keys(self):
        data = client.get("/api/snapshot").json()
        assert {"generated_at", "kpis", "shipments", "alerts", "suppliers", "inventory"} <= data.keys()

    def test_shipments_list(self):
        data = client.get("/api/snapshot").json()
        assert isinstance(data["shipments"], list)
        assert len(data["shipments"]) > 0

    def test_kpis_present(self):
        kpis = client.get("/api/snapshot").json()["kpis"]
        assert "on_time_rate" in kpis
        assert "active_shipments" in kpis


# ── /api/kpis ─────────────────────────────────────────────────────────────────

class TestKpis:
    def test_status_200(self):
        assert client.get("/api/kpis").status_code == 200

    def test_on_time_rate_range(self):
        kpis = client.get("/api/kpis").json()
        assert 0 <= kpis["on_time_rate"] <= 100

    def test_cost_per_unit_positive(self):
        kpis = client.get("/api/kpis").json()
        assert kpis["cost_per_unit_usd"] > 0


# ── /api/shipments ────────────────────────────────────────────────────────────

class TestShipments:
    def test_status_200(self):
        assert client.get("/api/shipments").status_code == 200

    def test_pagination_structure(self):
        data = client.get("/api/shipments").json()
        assert "total" in data
        assert "results" in data
        assert "limit" in data
        assert "offset" in data

    def test_default_limit(self):
        data = client.get("/api/shipments").json()
        assert len(data["results"]) <= 50

    def test_custom_limit(self):
        data = client.get("/api/shipments?limit=5").json()
        assert len(data["results"]) <= 5

    def test_mode_filter_sea(self):
        data = client.get("/api/shipments?mode=Sea").json()
        for s in data["results"]:
            assert s["mode"] == "Sea"

    def test_mode_filter_air(self):
        data = client.get("/api/shipments?mode=Air").json()
        for s in data["results"]:
            assert s["mode"] == "Air"

    def test_status_filter_delayed(self):
        data = client.get("/api/shipments?status=Delayed").json()
        for s in data["results"]:
            assert s["status"] == "Delayed"

    def test_mode_filter_case_insensitive(self):
        r = client.get("/api/shipments?mode=sea")
        assert r.status_code == 200

    def test_offset_pagination(self):
        page1 = client.get("/api/shipments?limit=5&offset=0").json()["results"]
        page2 = client.get("/api/shipments?limit=5&offset=5").json()["results"]
        ids1 = {s["id"] for s in page1}
        ids2 = {s["id"] for s in page2}
        assert ids1.isdisjoint(ids2), "Pages should not overlap"

    def test_shipment_fields(self):
        results = client.get("/api/shipments?limit=3").json()["results"]
        for s in results:
            assert "id" in s
            assert "mode" in s
            assert "status" in s
            assert "route" in s


# ── /api/shipments/:id ────────────────────────────────────────────────────────

class TestShipmentDetail:
    def test_404_on_missing(self):
        r = client.get("/api/shipments/SH-9999999")
        assert r.status_code == 404

    def test_found_shipment(self):
        # Get any real ID first
        first = client.get("/api/shipments?limit=1").json()["results"]
        if not first:
            pytest.skip("No shipments available")
        sid = first[0]["id"]
        r = client.get(f"/api/shipments/{sid}")
        assert r.status_code == 200
        assert r.json()["id"] == sid


# ── /api/alerts ───────────────────────────────────────────────────────────────

class TestAlerts:
    def test_status_200(self):
        assert client.get("/api/alerts").status_code == 200

    def test_response_structure(self):
        data = client.get("/api/alerts").json()
        assert "count" in data
        assert "alerts" in data
        assert data["count"] == len(data["alerts"])

    def test_severity_filter_high(self):
        data = client.get("/api/alerts?severity=high").json()
        for a in data["alerts"]:
            assert a["severity"] == "high"

    def test_alert_fields(self):
        data = client.get("/api/alerts").json()
        for a in data["alerts"]:
            assert "message" in a
            assert "severity" in a


# ── /api/suppliers ────────────────────────────────────────────────────────────

class TestSuppliers:
    def test_status_200(self):
        assert client.get("/api/suppliers").status_code == 200

    def test_returns_list(self):
        data = client.get("/api/suppliers").json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_score_range(self):
        for s in client.get("/api/suppliers").json():
            assert 0 <= s["performance_score"] <= 100


# ── /api/inventory ────────────────────────────────────────────────────────────

class TestInventory:
    def test_status_200(self):
        assert client.get("/api/inventory").status_code == 200

    def test_response_structure(self):
        data = client.get("/api/inventory").json()
        assert "items" in data
        assert "count" in data

    def test_health_filter_critical(self):
        data = client.get("/api/inventory?health=critical").json()
        for item in data["items"]:
            assert item["health"] == "critical"

    def test_health_filter_ok(self):
        data = client.get("/api/inventory?health=ok").json()
        for item in data["items"]:
            assert item["health"] == "ok"


# ── /api/refresh ──────────────────────────────────────────────────────────────

class TestRefresh:
    def test_post_refresh(self):
        r = client.post("/api/refresh")
        assert r.status_code == 200
        data = r.json()
        assert "refreshed_at" in data
        assert "kpis" in data
