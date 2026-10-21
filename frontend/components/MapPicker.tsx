"use client";

import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

//Correcion para el icocno por defecto de Leaflet, en Next.js
const defaultIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

//Componente interno que detecta los clics en el mapa. COnsiguiendo la latitud y longitud dentro de varibles. 
function LocationMarker({ position, setPosition }: { position: {lat: number, lng: number} | null, setPosition: any }) {
  useMapEvents({
    click(e) {
      setPosition({ lat: e.latlng.lat, lng: e.latlng.lng });
    },
  });

  return position === null ? null : <Marker position={position} icon={defaultIcon} />;
}

//Funcion que generara el "lienzo" donde con la funcion de location Marker se posicionara dentro de un 
//Maps pequeño
export default function MapPicker({ position, setPosition }: { position: {lat: number, lng: number} | null, setPosition: any }) {
  // Coordenadas por defecto: Quito, Ecuador
  const defaultCenter = { lat: -0.180653, lng: -78.467834 };
  //Es lo mas al centro de Quito, Ecuador que pude encontrar.
  const center = position || defaultCenter;

    return (
    <div className="relative z-0 rounded-lg overflow-hidden border border-slate-300">
      <MapContainer 
        /*Hace que el centro seea con los ddatos de la latitud y el longitud */
        /*El tamaño dle mini mapa*/
        center={[center.lat, center.lng]} 
        zoom={13} 
        style={{ height: "300px", width: "100%", zIndex: 0 }}>
            
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />
        <LocationMarker position={position} setPosition={setPosition} />
      </MapContainer>
    </div>
    );
}

  


