-- ============================================================
-- Supply Chain Control Tower — PostgreSQL Schema
-- ============================================================

-- ── Extensions ───────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- for fast text search on routes

-- ── Enum types ────────────────────────────────────────────────
CREATE TYPE transport_mode   AS ENUM ('Sea', 'Air', 'Road', 'Rail');
CREATE TYPE shipment_status  AS ENUM ('On time', 'At risk', 'Delayed', 'In transit', 'Delivered');
CREATE TYPE alert_severity   AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE inventory_health AS ENUM ('ok', 'low', 'critical');

-- ── Suppliers ─────────────────────────────────────────────────
CREATE TABLE suppliers (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name              TEXT NOT NULL,
    country           TEXT,
    contact_email     TEXT,
    base_score        NUMERIC(5,2) CHECK (base_score BETWEEN 0 AND 100),
    on_time_delivery  NUMERIC(5,2),
    quality_rating    NUMERIC(5,2),
    lead_time_days    INT,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);

-- ── Shipments ─────────────────────────────────────────────────
CREATE TABLE shipments (
    id              TEXT PRIMARY KEY,           -- e.g. SH-4821
    supplier_id     UUID REFERENCES suppliers(id),
    origin          TEXT NOT NULL,
    destination     TEXT NOT NULL,
    mode            transport_mode NOT NULL,
    status          shipment_status NOT NULL DEFAULT 'In transit',
    weight_kg       NUMERIC(10,2),
    value_usd       NUMERIC(12,2),
    eta             DATE,
    departed_at     TIMESTAMPTZ,
    arrived_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_shipments_status  ON shipments(status);
CREATE INDEX idx_shipments_mode    ON shipments(mode);
CREATE INDEX idx_shipments_eta     ON shipments(eta);
CREATE INDEX idx_shipments_route   ON shipments USING gin ((origin || ' → ' || destination) gin_trgm_ops);

-- ── SKUs / Inventory ──────────────────────────────────────────
CREATE TABLE skus (
    sku             TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    safety_stock    INT NOT NULL DEFAULT 1000,
    reorder_point   INT NOT NULL DEFAULT 2000,
    unit_cost_usd   NUMERIC(10,4),
    supplier_id     UUID REFERENCES suppliers(id),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE inventory_snapshots (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku             TEXT REFERENCES skus(sku),
    warehouse       TEXT NOT NULL,
    stock_qty       INT NOT NULL,
    health          inventory_health GENERATED ALWAYS AS (
                        CASE
                            WHEN stock_qty < (SELECT safety_stock * 0.5 FROM skus s WHERE s.sku = sku) THEN 'critical'::inventory_health
                            WHEN stock_qty < (SELECT safety_stock FROM skus s WHERE s.sku = sku)       THEN 'low'::inventory_health
                            ELSE 'ok'::inventory_health
                        END
                    ) STORED,
    recorded_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_inv_sku_time ON inventory_snapshots(sku, recorded_at DESC);

-- ── Alerts ────────────────────────────────────────────────────
CREATE TABLE alerts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shipment_id     TEXT REFERENCES shipments(id),
    sku             TEXT REFERENCES skus(sku),
    category        TEXT NOT NULL,  -- delay | customs | quality | demand | cost | inventory
    severity        alert_severity NOT NULL,
    message         TEXT NOT NULL,
    resolved        BOOLEAN DEFAULT FALSE,
    resolved_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alerts_unresolved ON alerts(created_at DESC) WHERE resolved = FALSE;
CREATE INDEX idx_alerts_shipment   ON alerts(shipment_id);

-- ── KPI snapshots (time-series) ───────────────────────────────
CREATE TABLE kpi_snapshots (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    active_shipments            INT,
    on_time_rate                NUMERIC(5,2),
    delayed_count               INT,
    at_risk_count               INT,
    active_alerts               INT,
    cost_per_unit_usd           NUMERIC(10,4),
    total_value_in_transit_usd  NUMERIC(16,2),
    recorded_at                 TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_kpi_time ON kpi_snapshots(recorded_at DESC);

-- ── Trigger: auto-update updated_at ──────────────────────────
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

CREATE TRIGGER trg_shipments_updated BEFORE UPDATE ON shipments
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_suppliers_updated BEFORE UPDATE ON suppliers
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ── Seed suppliers ────────────────────────────────────────────
INSERT INTO suppliers (id, name, base_score, lead_time_days) VALUES
    ('11111111-0000-0000-0000-000000000001', 'Acme Parts',     94, 5),
    ('11111111-0000-0000-0000-000000000002', 'StellarMFG',     87, 7),
    ('11111111-0000-0000-0000-000000000003', 'Pacific Source',  76, 10),
    ('11111111-0000-0000-0000-000000000004', 'TechFoundry',    61, 14),
    ('11111111-0000-0000-0000-000000000005', 'GlobalComp',     42, 21);

-- ── Seed SKUs ─────────────────────────────────────────────────
INSERT INTO skus (sku, name, safety_stock, reorder_point, unit_cost_usd) VALUES
    ('IC-7701', 'Microcontrollers',  5000, 8000,  2.40),
    ('MB-2204', 'Motor Bearings',    2000, 3500,  1.15),
    ('CS-0091', 'Capacitors (50V)', 10000,18000,  0.08),
    ('LB-3310', 'Li-Ion Cells',      1500, 3000, 12.75),
    ('CB-5502', 'Control Boards',    2000, 4000, 18.50),
    ('HS-1140', 'Heat Sinks',        1200, 2200,  3.20);

-- ── Useful views ──────────────────────────────────────────────
CREATE VIEW v_active_shipments AS
    SELECT * FROM shipments WHERE status != 'Delivered';

CREATE VIEW v_critical_alerts AS
    SELECT * FROM alerts WHERE resolved = FALSE AND severity IN ('high', 'critical')
    ORDER BY created_at DESC;

CREATE VIEW v_inventory_health AS
    SELECT DISTINCT ON (sku)
        i.sku, s.name, i.stock_qty, s.safety_stock,
        i.health, i.recorded_at
    FROM inventory_snapshots i
    JOIN skus s ON s.sku = i.sku
    ORDER BY sku, recorded_at DESC;
