"use client";

import { useEffect, useState, type KeyboardEvent } from "react";
import { MapContainer, TileLayer, Marker, useMap, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

export type LatLng = { lat: number; lng: number };

type NominatimResult = { lat: string; lon: string; display_name: string };

// API gratuita de OpenStreetMap. Política de uso: máximo 1 petición por segundo y sin
// autocompletado, por eso solo buscamos al pulsar el botón o Enter.
const NOMINATIM_URL = "https://nominatim.openstreetmap.org/search";

//Correcion para el icocno por defecto de Leaflet, en Next.js
const defaultIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

//Componente interno que detecta los clics en el mapa. COnsiguiendo la latitud y longitud dentro de varibles.
function LocationMarker({ position, setPosition }: { position: LatLng | null; setPosition: (pos: LatLng) => void }) {
  useMapEvents({
    click(e) {
      setPosition({ lat: e.latlng.lat, lng: e.latlng.lng });
    },
  });

  return position === null ? null : <Marker position={position} icon={defaultIcon} />;
}

//useMap solo funciona dentro de MapContainer, por eso el "vuelo" vive en su propio componente.
//Solo reacciona a las búsquedas, no a los clics, para no mover la cámara cada vez que se marca un punto.
function FlyToTarget({ target }: { target: LatLng | null }) {
  const map = useMap();

  useEffect(() => {
    if (target) {
      map.flyTo([target.lat, target.lng], 16, { duration: 1.2 });
    }
  }, [map, target]);

  return null;
}

//Funcion que generara el "lienzo" donde con la funcion de location Marker se posicionara dentro de un
//Maps pequeño
export default function MapPicker({
  position,
  setPosition,
  onAddressFound,
}: {
  position: LatLng | null;
  setPosition: (pos: LatLng) => void;
  onAddressFound?: (address: string) => void;
}) {
  // Coordenadas por defecto: Quito, Ecuador
  const defaultCenter = { lat: -0.180653, lng: -78.467834 };
  //Es lo mas al centro de Quito, Ecuador que pude encontrar.
  const center = position || defaultCenter;

  const [query, setQuery] = useState("");
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [flyTarget, setFlyTarget] = useState<LatLng | null>(null);

  async function handleSearch() {
    const term = query.trim();
    if (!term || searching) return;

    setSearching(true);
    setSearchError("");

    try {
      const params = new URLSearchParams({
        q: term,
        format: "jsonv2",
        limit: "1",
        countrycodes: "ec", // Solo resultados dentro de Ecuador
        "accept-language": "es",
      });
      const response = await fetch(`${NOMINATIM_URL}?${params}`);
      if (!response.ok) throw new Error(`Nominatim respondió ${response.status}`);

      const results: NominatimResult[] = await response.json();
      if (results.length === 0) {
        setSearchError(`No encontramos "${term}". Prueba con el sector y la ciudad, ej. "La Carolina, Quito".`);
        return;
      }

      const found = { lat: parseFloat(results[0].lat), lng: parseFloat(results[0].lon) };
      setFlyTarget(found);
      setPosition(found);
      onAddressFound?.(results[0].display_name);
    } catch {
      setSearchError("No se pudo consultar el buscador de direcciones. Intenta de nuevo o marca el punto manualmente.");
    } finally {
      setSearching(false);
    }
  }

  // El buscador vive dentro del <form> del modal: Enter debe buscar, no enviar el formulario.
  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") {
      e.preventDefault();
      void handleSearch();
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <svg className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fillRule="evenodd" d="M9 3.5a5.5 5.5 0 1 0 3.36 9.86l3.64 3.64a.75.75 0 1 0 1.06-1.06l-3.64-3.64A5.5 5.5 0 0 0 9 3.5ZM5 9a4 4 0 1 1 8 0 4 4 0 0 1-8 0Z" clipRule="evenodd" />
          </svg>
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder='Buscar sector, ej. "La Carolina, Quito"'
            aria-label="Buscar sector en el mapa"
            className="w-full rounded-lg border border-slate-300 py-2.5 pl-9 pr-3 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
          />
        </div>
        <button
          type="button"
          onClick={() => void handleSearch()}
          disabled={searching || !query.trim()}
          className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {searching ? "Buscando..." : "Buscar"}
        </button>
      </div>

      {searchError && <p role="alert" className="text-xs text-red-600">{searchError}</p>}

      <div className="relative z-0 rounded-lg overflow-hidden border border-slate-300">
        <MapContainer
          /*Hace que el centro seea con los ddatos de la latitud y el longitud */
          /*El tamaño dle mini mapa*/
          center={[center.lat, center.lng]}
          zoom={13}
          style={{ height: "320px", width: "100%", zIndex: 0 }}>

          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          />
          <LocationMarker position={position} setPosition={setPosition} />
          <FlyToTarget target={flyTarget} />
        </MapContainer>
      </div>
    </div>
  );
}
