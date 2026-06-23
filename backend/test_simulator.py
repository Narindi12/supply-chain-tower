"""
Unit tests for simulator.py
Run: pytest test_simulator.py -v
"""
import pytest
from simulator import (
    generate_shipments,
    generate_alerts,
    generate_suppliers,
    generate_inventory,
    compute_kpis,
    generate_snapshot,
    MODES,
    SUPPLIERS,
    SKUS,
)


# ── generate_shipments ────────────────────────────────────────────────────────

class TestGenerateShipments:
    def test_returns_correct_count(self):
        result = generate_shipments(10)
        assert len(result) == 10

    def test_default_count(self):
        result = generate_shipments()
        assert len(result) == 142

    def test_required_fields(self):
        fields = {"id", "origin", "destination", "route", "mode", "eta", "status", "weight_kg", "value_usd"}
        for s in generate_shipments(5):
            assert fields.issubset(s.keys()), f"Missing fields in {s}"

    def test_valid_mode(self):
        for s in generate_shipments(20):
            assert s["mode"] in MODES

    def test_valid_status(self):
        valid = {"On time", "At risk", "Delayed", "In transit"}
        for s in generate_shipments(20):
            assert s["status"] in valid

    def test_route_format(self):
        for s in generate_shipments(5):
            assert "→" in s["route"]
            origin, dest = s["route"].split(" → ")
            assert origin == s["origin"]
            assert dest == s["destination"]

    def test_id_format(self):
        for s in generate_shipments(10):
            assert s["id"].startswith("SH-")
            num = int(s["id"][3:])
            assert 4000 <= num <= 6999

    def test_value_positive(self):
        for s in generate_shipments(10):
            assert s["value_usd"] > 0
            assert s["weight_kg"] > 0


# ── generate_alerts ───────────────────────────────────────────────────────────

class TestGenerateAlerts:
    def test_returns_requested_count(self):
        ids = ["SH-4001", "SH-4002"]
        result = generate_alerts(ids, count=5)
        assert len(result) == 5

    def test_required_fields(self):
        fields = {"id", "message", "category", "severity", "timestamp"}
        for a in generate_alerts(["SH-4001"], count=3):
            assert fields.issubset(a.keys())

    def test_valid_severity(self):
        valid = {"low", "medium", "high"}
        for a in generate_alerts(["SH-4001"], count=10):
            assert a["severity"] in valid

    def test_message_is_string(self):
        for a in generate_alerts(["SH-4001"], count=5):
            assert isinstance(a["message"], str)
            assert len(a["message"]) > 0

    def test_works_with_empty_ids(self):
        # Should not raise even with no shipment IDs
        result = generate_alerts([], count=3)
        assert len(result) == 3


# ── generate_suppliers ────────────────────────────────────────────────────────

class TestGenerateSuppliers:
    def test_count_matches_seed(self):
        result = generate_suppliers()
        assert len(result) == len(SUPPLIERS)

    def test_required_fields(self):
        fields = {"id", "name", "performance_score", "on_time_delivery", "quality_rating", "lead_time_days"}
        for s in generate_suppliers():
            assert fields.issubset(s.keys())

    def test_score_in_range(self):
        for s in generate_suppliers():
            assert 0 <= s["performance_score"] <= 100
            assert 0 <= s["on_time_delivery"] <= 100
            assert 0 <= s["quality_rating"] <= 100

    def test_lead_time_positive(self):
        for s in generate_suppliers():
            assert s["lead_time_days"] > 0


# ── generate_inventory ────────────────────────────────────────────────────────

class TestGenerateInventory:
    def test_count_matches_skus(self):
        result = generate_inventory()
        assert len(result) == len(SKUS)

    def test_required_fields(self):
        fields = {"sku", "name", "stock", "threshold", "health", "days_of_supply"}
        for item in generate_inventory():
            assert fields.issubset(item.keys())

    def test_health_values(self):
        valid = {"ok", "low", "critical"}
        for item in generate_inventory():
            assert item["health"] in valid

    def test_health_logic(self):
        """Health label must match stock vs threshold relationship."""
        for item in generate_inventory():
            stock, threshold = item["stock"], item["threshold"]
            if stock < threshold * 0.5:
                assert item["health"] == "critical", f"{item['sku']}: expected critical, got {item['health']}"
            elif stock < threshold:
                assert item["health"] == "low", f"{item['sku']}: expected low, got {item['health']}"
            else:
                assert item["health"] == "ok", f"{item['sku']}: expected ok, got {item['health']}"

    def test_days_of_supply_positive(self):
        for item in generate_inventory():
            assert item["days_of_supply"] > 0


# ── compute_kpis ──────────────────────────────────────────────────────────────

class TestComputeKpis:
    def _make_shipments(self, statuses):
        return [{"id": f"SH-{i}", "status": s, "value_usd": 1000} for i, s in enumerate(statuses)]

    def test_required_fields(self):
        ships = self._make_shipments(["On time", "Delayed"])
        kpis = compute_kpis(ships, [])
        fields = {"active_shipments", "on_time_rate", "delayed_count", "at_risk_count",
                  "active_alerts", "avg_shipment_value_usd", "cost_per_unit_usd", "total_value_in_transit_usd"}
        assert fields.issubset(kpis.keys())

    def test_on_time_rate_all_on_time(self):
        ships = self._make_shipments(["On time"] * 4)
        kpis = compute_kpis(ships, [])
        assert kpis["on_time_rate"] == 100.0

    def test_on_time_rate_none_on_time(self):
        ships = self._make_shipments(["Delayed"] * 4)
        kpis = compute_kpis(ships, [])
        assert kpis["on_time_rate"] == 0.0

    def test_on_time_rate_partial(self):
        ships = self._make_shipments(["On time", "On time", "Delayed", "At risk"])
        kpis = compute_kpis(ships, [])
        assert kpis["on_time_rate"] == 50.0

    def test_alert_count(self):
        ships = self._make_shipments(["On time"])
        kpis = compute_kpis(ships, [{"id": "a1"}, {"id": "a2"}])
        assert kpis["active_alerts"] == 2

    def test_total_value(self):
        ships = [{"id": "s1", "status": "On time", "value_usd": 5000},
                 {"id": "s2", "status": "On time", "value_usd": 3000}]
        kpis = compute_kpis(ships, [])
        assert kpis["total_value_in_transit_usd"] == 8000

    def test_empty_shipments(self):
        kpis = compute_kpis([], [])
        assert kpis["on_time_rate"] == 0
        assert kpis["active_shipments"] == 0


# ── generate_snapshot ─────────────────────────────────────────────────────────

class TestGenerateSnapshot:
    def test_top_level_keys(self):
        snap = generate_snapshot(10)
        assert {"generated_at", "kpis", "shipments", "alerts", "suppliers", "inventory"} == set(snap.keys())

    def test_shipment_count(self):
        snap = generate_snapshot(25)
        assert len(snap["shipments"]) == 25

    def test_generated_at_format(self):
        snap = generate_snapshot(5)
        assert snap["generated_at"].endswith("Z")
        assert "T" in snap["generated_at"]

    def test_kpis_active_shipments_matches(self):
        snap = generate_snapshot(30)
        assert snap["kpis"]["active_shipments"] == 30

    def test_deterministic_structure(self):
        """Two snapshots should have same shape even if different data."""
        s1 = generate_snapshot(5)
        s2 = generate_snapshot(5)
        assert set(s1.keys()) == set(s2.keys())
        assert len(s1["suppliers"]) == len(s2["suppliers"])
