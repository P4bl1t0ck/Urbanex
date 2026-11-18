"use client";

import dynamic from "next/dynamic";
import { useEffect, useRef, useState } from "react";
import "leaflet/dist/leaflet.css";
import { propertyCoordinates } from "@/lib/propertyDetail";

type MapProps = { position: [number, number]; title: string; onReady: () => void };

// Leaflet needs the browser; neither the module nor its map is initialized during SSR.
const LocationMap = dynamic<MapProps>(async () => {
  const { MapContainer, TileLayer, Marker, Popup, ZoomControl } = await import("react-leaflet");
  const { divIcon } = await import("leaflet");
  const icon = divIcon({
    className: "urbanex-location-marker",
    html: '<span style="display:block;width:24px;height:24px;border:4px solid white;border-radius:50%;background:#1d4ed8;box-shadow:0 2px 8px #0f172a66"></span>',
    iconSize: [24, 24], iconAnchor: [12, 12],
  });
  return function Map({ position, title, onReady }: MapProps) {
    const [tileError, setTileError] = useState(false);
    return <>
      {tileError && <p role="status" className="bg-amber-50 px-4 py-3 text-sm text-amber-900">No se pudo cargar parte del mapa. Puedes abrir la ubicación en Google Maps.</p>}
      <MapContainer center={position} zoom={15} scrollWheelZoom={false} zoomControl={false}
      whenReady={onReady} className="h-72 w-full sm:h-96" style={{ zIndex: 0 }}>
      <ZoomControl position="bottomright" zoomInTitle="Acercar" zoomOutTitle="Alejar" />
      <TileLayer url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" maxZoom={19}
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        eventHandlers={{ tileerror: () => setTileError(true) }} />
      <Marker position={position} icon={icon} alt={`Ubicación de ${title}`}><Popup>{title}</Popup></Marker>
      </MapContainer>
    </>;
  };
}, { ssr: false, loading: () => <p className="flex h-72 items-center justify-center bg-slate-50 text-sm text-slate-500">Cargando mapa…</p> });

export default function PropertyLocationMap({ propertyId, latitude, longitude, title, location }: {
  propertyId: number; latitude: string | null; longitude: string | null; title: string; location: string;
}) {
  const position = propertyCoordinates(latitude, longitude);
  const container = useRef<HTMLDivElement>(null);
  const reported = useRef(false);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const element = container.current;
    if (!element) return;
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) { setVisible(true); observer.disconnect(); }
    }, { rootMargin: "100px" });
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  async function reportLoad() {
    if (reported.current) return;
    reported.current = true;
    // Metrics must never block the map. No identifier, cookie value or token is stored.
    const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    try {
      const csrf = await fetch(`${base}/api/auth/csrf/`, { credentials: "include", cache: "no-store" });
      if (!csrf.ok) return;
      const cookie = document.cookie.split(";").map((part) => part.trim()).find((part) => part.startsWith("csrftoken="));
      const token = cookie ? decodeURIComponent(cookie.slice("csrftoken=".length)) : null;
      if (!token) return;
      await fetch(`${base}/api/telemetry/map-loads/`, {
        method: "POST", credentials: "include",
        headers: { "Content-Type": "application/json", "X-CSRFToken": token },
        body: JSON.stringify({ property_id: propertyId, screen: "detail", provider: "leaflet" }),
      });
    } catch { /* Anonymous best-effort estimate; failures do not interrupt reading. */ }
  }

  return <section aria-labelledby="property-location">
    <div className="flex flex-wrap items-center justify-between gap-3">
      <h2 id="property-location" className="text-xl font-bold text-slate-900">Ubicación</h2>
      {position && <a href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(position.join(","))}`}
        target="_blank" rel="noopener noreferrer" className="text-sm font-semibold text-blue-700 hover:underline">Abrir en Google Maps</a>}
    </div>
    <p className="mt-2 text-sm text-slate-600">{location}</p>
    <div ref={container} className="relative z-0 mt-4 overflow-hidden rounded-2xl border border-slate-200 bg-slate-50">
      {!position ? <p className="p-6 text-sm text-slate-500">Ubicación en el mapa no disponible.</p>
        : visible ? <LocationMap position={position} title={title} onReady={reportLoad} />
        : <div className="h-72 sm:h-96" aria-hidden="true" />}
    </div>
  </section>;
}
