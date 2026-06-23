# Supply Chain Logistics Control Tower

A full-stack real-time logistics monitoring dashboard built with **React + FastAPI + PostgreSQL**.

## Stack

| Layer    | Tech                              |
|----------|-----------------------------------|
| Frontend | React 18, Vite                    |
| Backend  | Python 3.11, FastAPI, Uvicorn     |
| Database | PostgreSQL 15                     |
| Simulate | Pure Python (no external deps)    |

---

## Quick start

### 1. Backend

```bash
cd backend
pip install fastapi uvicorn
python simulator.py          # test the simulator
uvicorn main:app --reload    # start API on :8000
```

API docs auto-open at http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev                  # starts on :5173
```

> The frontend **falls back to mock data** automatically if the backend isn't running — great for demos.

### 3. Database (optional)

```bash
psql -U postgres -c "CREATE DATABASE supply_chain;"
psql -U postgres -d supply_chain -f database/schema.sql
```

---

## API endpoints

| Method | Path               | Description                          |
|--------|--------------------|--------------------------------------|
| GET    | /api/snapshot      | Full dashboard snapshot              |
| GET    | /api/kpis          | KPI metrics only                     |
| GET    | /api/shipments     | Paginated list, filter by mode/status|
| GET    | /api/shipments/:id | Single shipment detail               |
| GET    | /api/alerts        | Active alerts, filter by severity    |
| GET    | /api/suppliers     | Supplier performance scores          |
| GET    | /api/inventory     | Inventory health by SKU              |
| POST   | /api/refresh       | Force fresh simulation               |

---

## Project structure

```
supply-chain-tower/
├── backend/
│   ├── main.py          ← FastAPI app & all routes
│   └── simulator.py     ← Synthetic data generator
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── hooks/
│       │   └── useControlTower.js   ← API polling hook
│       └── components/
│           ├── KpiCard.jsx
│           ├── ShipmentTable.jsx
│           ├── AlertFeed.jsx
│           ├── SupplierChart.jsx
│           └── InventoryPanel.jsx
└── database/
    └── schema.sql       ← PostgreSQL schema + seed data
```

---

## Resume talking points

- **Real-time data pipeline**: simulated IoT-style event stream (shipment status, temp sensors, port congestion)
- **REST API design**: paginated endpoints, query-param filters, 10s cache layer
- **Database design**: normalized schema with indexes, generated columns, time-series KPI snapshots
- **Anomaly detection**: rule-based alert generation for delays, cold chain breaches, demand spikes
- **Frontend state**: custom React hook with polling, error handling, and graceful mock fallback
