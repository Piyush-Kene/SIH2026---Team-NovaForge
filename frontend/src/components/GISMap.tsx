"use client";

import React, { useEffect, useRef, useState } from "react";
import * as maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { Layers, Compass, Eye, ShieldCheck, Sun, Thermometer, Mountain } from "lucide-react";
import { DEMO_LOCATIONS } from "@/lib/api";

interface GISMapProps {
  selectedLocation: { lat: number; lon: number; name: string };
  onSelectLocation: (loc: { lat: number; lon: number; name: string }) => void;
  activeLayer: string;
  setActiveLayer: (layer: string) => void;
}

export const GISMap: React.FC<GISMapProps> = ({
  selectedLocation,
  onSelectLocation,
  activeLayer,
  setActiveLayer
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<maplibregl.Map | null>(null);
  const markerRef = useRef<maplibregl.Marker | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
    if (!mapContainer.current) return;

    // Use free public OpenStreetMap vector/raster tile style
    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          osm: {
            type: "raster",
            tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
            tileSize: 256,
            attribution: "&copy; OpenStreetMap contributors"
          }
        },
        layers: [
          {
            id: "osm-layer",
            type: "raster",
            source: "osm",
            minzoom: 0,
            maxzoom: 19
          }
        ]
      },
      center: [selectedLocation.lon, selectedLocation.lat],
      zoom: 7
    });

    map.addControl(new maplibregl.NavigationControl({ showCompass: true }), "top-right");

    map.on("load", () => {
      setMapLoaded(true);

      // Create persistent marker
      const el = document.createElement("div");
      el.className = "geotherm-marker";
      el.style.width = "24px";
      el.style.height = "24px";
      el.style.borderRadius = "50%";
      el.style.backgroundColor = "#00adb5";
      el.style.border = "3px solid #ffffff";
      el.style.boxShadow = "0 0 15px rgba(0, 173, 181, 0.9)";
      el.style.cursor = "pointer";

      markerRef.current = new maplibregl.Marker({ element: el })
        .setLngLat([selectedLocation.lon, selectedLocation.lat])
        .addTo(map);
    });

    map.on("click", (e) => {
      const { lng, lat } = e.lngLat;
      const customName = `Custom Site (${lat.toFixed(3)}°N, ${lng.toFixed(3)}°E)`;
      if (markerRef.current) {
        markerRef.current.setLngLat([lng, lat]);
      }
      onSelectLocation({ lat, lon: lng, name: customName });
    });

    mapInstance.current = map;

    return () => {
      map.remove();
    };
  }, []);

  // Update map center and marker when selectedLocation changes
  useEffect(() => {
    if (!mapInstance.current || !markerRef.current) return;
    mapInstance.current.flyTo({
      center: [selectedLocation.lon, selectedLocation.lat],
      zoom: 9,
      essential: true
    });
    markerRef.current.setLngLat([selectedLocation.lon, selectedLocation.lat]);
  }, [selectedLocation]);

  return (
    <div className="relative w-full h-[520px] rounded-xl overflow-hidden border border-slate-800 shadow-2xl bg-slate-950">
      <div ref={mapContainer} className="w-full h-full" />

      {/* Layer Control Bar */}
      <div className="absolute top-4 left-4 z-10 flex flex-wrap gap-2 bg-slate-900/90 backdrop-blur-md p-2 rounded-lg border border-slate-700 text-xs shadow-lg">
        <button
          onClick={() => setActiveLayer("solar")}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded transition ${
            activeLayer === "solar" ? "bg-amber-500 text-slate-950 font-bold" : "text-slate-300 hover:bg-slate-800"
          }`}
        >
          <Sun className="w-3.5 h-3.5" /> Solar Potential
        </button>
        <button
          onClick={() => setActiveLayer("temperature")}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded transition ${
            activeLayer === "temperature" ? "bg-cyan-500 text-slate-950 font-bold" : "text-slate-300 hover:bg-slate-800"
          }`}
        >
          <Thermometer className="w-3.5 h-3.5" /> Thermal Zone
        </button>
        <button
          onClick={() => setActiveLayer("terrain")}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded transition ${
            activeLayer === "terrain" ? "bg-emerald-500 text-slate-950 font-bold" : "text-slate-300 hover:bg-slate-800"
          }`}
        >
          <Mountain className="w-3.5 h-3.5" /> Elevation / Contour
        </button>
      </div>

      {/* Quick Predefined Location Selector */}
      <div className="absolute bottom-4 left-4 z-10 bg-slate-900/90 backdrop-blur-md p-3 rounded-lg border border-slate-700 shadow-xl max-w-sm">
        <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1">
          <Compass className="w-3.5 h-3.5 text-cyan-400" /> Strategic SIH Test Sites
        </div>
        <div className="flex flex-wrap gap-1.5">
          {DEMO_LOCATIONS.map((loc) => (
            <button
              key={loc.name}
              onClick={() => onSelectLocation({ lat: loc.lat, lon: loc.lon, name: loc.name })}
              className={`text-xs px-2.5 py-1 rounded transition border ${
                selectedLocation.name === loc.name
                  ? "bg-cyan-500/20 border-cyan-400 text-cyan-200 font-semibold"
                  : "bg-slate-800/80 border-slate-700 text-slate-300 hover:bg-slate-700"
              }`}
            >
              {loc.name.split(",")[0]}
            </button>
          ))}
        </div>
      </div>

      {/* Coordinate & GIS HUD Badge */}
      <div className="absolute bottom-4 right-4 z-10 bg-slate-900/95 backdrop-blur-md px-3.5 py-2.5 rounded-lg border border-slate-700 shadow-xl text-right">
        <div className="text-[10px] uppercase font-mono text-cyan-400 tracking-wider flex items-center justify-end gap-1">
          <ShieldCheck className="w-3.5 h-3.5" /> GIS TARGET LOCKED
        </div>
        <div className="text-sm font-bold text-slate-100">{selectedLocation.name}</div>
        <div className="text-xs font-mono text-slate-400">
          {selectedLocation.lat.toFixed(4)}°N, {selectedLocation.lon.toFixed(4)}°E
        </div>
      </div>
    </div>
  );
};
