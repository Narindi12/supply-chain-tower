/**
 * ShipmentMap — Leaflet.js map showing live shipment routes with animated arcs.
 * Install: npm install leaflet react-leaflet
 */
import { useEffect, useRef } from "react";

// Lat/lng centroids for known cities
const CITY_COORDS = {
  "Shanghai":      [31.2304, 121.4737],
  "Guangzhou":     [23.1291, 113.2644],
  "Mumbai":        [19.0760,  72.8777],
  "Dubai":         [25.2048,  55.2708],
  "Tokyo":         [35.6762, 139.6503],
  "Berlin":        [52.5200,  13.4050],
  "Houston":       [29.7604, -95.3698],
  "Chicago":       [41.8781, -87.6298],
  "Los Angeles":   [34.0522,-118.2437],
  "Rotterdam":     [51.9244,   4.4777],
  "Frankfurt":     [50.1109,   8.6821],
  "New York":      [40.7128, -74.0060],
  "Seattle":       [47.6062,-122.3321],
  "Dallas":        [32.7767, -96.7970],
  "Miami":         [25.7617, -80.1918],
  "Warsaw":        [52.2297,  21.0122],
};

const STATUS_COLOR = {
  "On time":   "#16a34a",
  "At risk":   "#d97706",
  "Delayed":   "#dc2626",
  "In transit":"#2563eb",
};

const MODE_ICON = { Sea: "🚢", Air: "✈️", Road: "🚛", Rail: "🚆" };

export default function ShipmentMap({ shipments = [] }) {
  const mapRef = useRef(null);
  const leafletMap = useRef(null);
  const layersRef = useRef([]);

  useEffect(() => {
    if (leafletMap.current) return; // already initialised

    // Dynamically load Leaflet CSS
    if (!document.getElementById("leaflet-css")) {
      const link = document.createElement("link");
      link.id = "leaflet-css";
      link.rel = "stylesheet";
      link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
      document.head.appendChild(link);
    }

    // Dynamically load Leaflet JS
    const script = document.createElement("script");
    script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
    script.onload = () => initMap();
    document.head.appendChild(script);

    function initMap() {
      const L = window.L;
      leafletMap.current = L.map(mapRef.current, {
        center: [20, 10],
        zoom: 2,
        zoomControl: true,
        attributionControl: false,
      });

      L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        { maxZoom: 18 }
      ).addTo(leafletMap.current);

      drawShipments(L, shipments);
    }

    return () => {
      if (leafletMap.current) {
        leafletMap.current.remove();
        leafletMap.current = null;
      }
    };
  }, []);

  // Redraw when shipments change
  useEffect(() => {
    if (!leafletMap.current || !window.L) return;
    const L = window.L;
    layersRef.current.forEach((l) => l.remove());
    layersRef.current = [];
    drawShipments(L, shipments);
  }, [shipments]);

  function drawShipments(L, ships) {
    ships.forEach((s) => {
      const from = CITY_COORDS[s.origin];
      const to   = CITY_COORDS[s.destination];
      if (!from || !to) return;

      const color = STATUS_COLOR[s.status] || "#64748b";

      // Curved arc via intermediate points
      const arcPoints = greatCircleArc(from, to, 20);
      const line = L.polyline(arcPoints, {
        color,
        weight: 1.5,
        opacity: 0.75,
        dashArray: s.status === "Delayed" ? "5, 6" : null,
      }).addTo(leafletMap.current);

      // Origin marker
      const originMarker = L.circleMarker(from, {
        radius: 4, fillColor: color, color: "white",
        weight: 1, fillOpacity: 1,
      }).addTo(leafletMap.current);

      // Destination marker
      const destMarker = L.circleMarker(to, {
        radius: 3, fillColor: color, color: "white",
        weight: 1, fillOpacity: 0.6,
      }).addTo(leafletMap.current);

      // Popup
      const popup = `
        <div style="font-family:system-ui;font-size:13px;min-width:180px">
          <strong>${s.id}</strong><br/>
          ${MODE_ICON[s.mode] || ""} ${s.mode} &nbsp;·&nbsp; ${s.route}<br/>
          ETA: <strong>${s.eta}</strong><br/>
          Status: <span style="color:${color};font-weight:600">${s.status}</span>
        </div>`;

      line.bindPopup(popup);
      originMarker.bindPopup(popup);

      layersRef.current.push(line, originMarker, destMarker);
    });
  }

  return (
    <div style={{ background: "white", border: "1px solid #e2e8f0", borderRadius: 12, padding: "16px 18px" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
        <h2 style={{ fontSize: 13, fontWeight: 500, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", margin: 0 }}>
          Live shipment map
        </h2>
        <div style={{ display: "flex", gap: 12, fontSize: 11, color: "#94a3b8" }}>
          {Object.entries(STATUS_COLOR).map(([status, color]) => (
            <span key={status} style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <span style={{ width: 8, height: 8, borderRadius: "50%", background: color, display: "inline-block" }} />
              {status}
            </span>
          ))}
        </div>
      </div>
      <div ref={mapRef} style={{ height: 340, borderRadius: 8, overflow: "hidden", background: "#1a1a2e" }} />
    </div>
  );
}

/** Generate points along a great-circle arc between two lat/lng pairs */
function greatCircleArc(from, to, steps = 20) {
  const toRad = (d) => (d * Math.PI) / 180;
  const toDeg = (r) => (r * 180) / Math.PI;
  const [lat1, lng1] = from.map(toRad);
  const [lat2, lng2] = to.map(toRad);
  const points = [];
  for (let i = 0; i <= steps; i++) {
    const f = i / steps;
    const A = Math.sin((1 - f) * Math.PI) / Math.sin(Math.PI);
    const B = Math.sin(f * Math.PI) / Math.sin(Math.PI);
    const x = A * Math.cos(lat1) * Math.cos(lng1) + B * Math.cos(lat2) * Math.cos(lng2);
    const y = A * Math.cos(lat1) * Math.sin(lng1) + B * Math.cos(lat2) * Math.sin(lng2);
    const z = A * Math.sin(lat1)                  + B * Math.sin(lat2);
    points.push([toDeg(Math.atan2(z, Math.sqrt(x * x + y * y))), toDeg(Math.atan2(y, x))]);
  }
  return points;
}
