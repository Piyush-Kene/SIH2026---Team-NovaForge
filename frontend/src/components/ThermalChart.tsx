"use client";

import React from "react";
import { ThermalSimulationResponse } from "@/types/geotherm";
import { AlertTriangle, CheckCircle, ShieldAlert, Zap, TrendingDown, Sun } from "lucide-react";

interface ThermalChartProps {
  simulation: ThermalSimulationResponse;
}

export const ThermalChart: React.FC<ThermalChartProps> = ({ simulation }) => {
  const {
    hours,
    outside_temperature_c,
    indoor_temperature_c,
    solar_gain_w,
    peak_indoor_temp_c,
    min_indoor_temp_c,
    avg_indoor_temp_c,
    thermal_comfort_score,
    high_heat_loss_period,
    risk_level
  } = simulation;

  // Compute SVG plotting bounds
  const allTemps = [...outside_temperature_c, ...indoor_temperature_c];
  const minT = Math.min(...allTemps) - 2;
  const maxT = Math.max(...allTemps) + 4;
  const tempRange = maxT - minT || 1;

  const width = 640;
  const height = 260;
  const padding = { top: 20, right: 30, bottom: 40, left: 45 };
  const plotW = width - padding.left - padding.right;
  const plotH = height - padding.top - padding.bottom;

  const getX = (hour: number) => padding.left + (hour / 23) * plotW;
  const getY = (temp: number) => padding.top + plotH - ((temp - minT) / tempRange) * plotH;

  // Path generators
  const outsidePath = hours.reduce((acc, h, i) => {
    const x = getX(h);
    const y = getY(outside_temperature_c[i]);
    return i === 0 ? `M ${x} ${y}` : `${acc} L ${x} ${y}`;
  }, "");

  const indoorPath = hours.reduce((acc, h, i) => {
    const x = getX(h);
    const y = getY(indoor_temperature_c[i]);
    return i === 0 ? `M ${x} ${y}` : `${acc} L ${x} ${y}`;
  }, "");

  // Comfort zone band (18°C to 24°C)
  const yComfortMin = Math.max(padding.top, Math.min(padding.top + plotH, getY(18)));
  const yComfortMax = Math.max(padding.top, Math.min(padding.top + plotH, getY(24)));
  const comfortBandHeight = Math.abs(yComfortMin - yComfortMax);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            24-Hour Diurnal Thermal Simulation
            <span className="text-xs font-mono font-normal text-slate-400">
              (Runge-Kutta 4th Order RK4 Solvers)
            </span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time balance of envelope conduction, infiltration, passive window radiation, and thermal capacitance.
          </p>
        </div>

        {/* Comfort badge */}
        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-[10px] uppercase font-mono tracking-wider text-slate-400">GeoTherm Index</div>
            <div className="text-xl font-black text-cyan-400">{thermal_comfort_score} / 100</div>
          </div>
          <div className={`px-2.5 py-1 rounded-md text-xs font-bold uppercase flex items-center gap-1.5 ${
            risk_level === "low"
              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
              : risk_level === "caution"
              ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
              : "bg-red-500/20 text-red-300 border border-red-500/40"
          }`}>
            {risk_level === "low" ? <CheckCircle className="w-3.5 h-3.5" /> : <AlertTriangle className="w-3.5 h-3.5" />}
            {risk_level === "low" ? "Safe Thermal Zone" : risk_level === "caution" ? "Thermal Caution" : "Freezing Hazard"}
          </div>
        </div>
      </div>

      {/* SVG Chart */}
      <div className="w-full overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto max-h-[300px]">
          {/* Comfort Target Zone (18-24 C) */}
          <rect
            x={padding.left}
            y={Math.min(yComfortMin, yComfortMax)}
            width={plotW}
            height={comfortBandHeight}
            fill="#065f46"
            fillOpacity="0.15"
          />
          <text
            x={padding.left + 8}
            y={Math.min(yComfortMin, yComfortMax) + 14}
            fill="#34d399"
            fontSize="9"
            fontFamily="monospace"
          >
            Target Thermal Comfort Band (18°C – 24°C)
          </text>

          {/* Grid lines */}
          {[0, 6, 12, 18, 23].map((h) => (
            <g key={h}>
              <line
                x1={getX(h)}
                y1={padding.top}
                x2={getX(h)}
                y2={padding.top + plotH}
                stroke="#1e293b"
                strokeDasharray="3 3"
              />
              <text
                x={getX(h)}
                y={padding.top + plotH + 16}
                fill="#64748b"
                fontSize="10"
                textAnchor="middle"
                fontFamily="monospace"
              >
                {h.toString().padStart(2, "0")}:00
              </text>
            </g>
          ))}

          {/* Temperature Y-Ticks */}
          {[Math.round(minT), Math.round((minT + maxT) / 2), Math.round(maxT)].map((t) => (
            <g key={t}>
              <line
                x1={padding.left}
                y1={getY(t)}
                x2={padding.left + plotW}
                y2={getY(t)}
                stroke="#1e293b"
              />
              <text
                x={padding.left - 8}
                y={getY(t) + 3}
                fill="#64748b"
                fontSize="10"
                textAnchor="end"
                fontFamily="monospace"
              >
                {t}°C
              </text>
            </g>
          ))}

          {/* Outside Temperature Curve */}
          <path
            d={outsidePath}
            fill="none"
            stroke="#64748b"
            strokeWidth="2"
            strokeDasharray="4 3"
          />

          {/* Indoor Temperature Curve */}
          <path
            d={indoorPath}
            fill="none"
            stroke="#00adb5"
            strokeWidth="3.5"
          />

          {/* Key Data Nodes on Indoor Curve */}
          <circle cx={getX(14)} cy={getY(indoor_temperature_c[14])} r="4" fill="#00adb5" stroke="#ffffff" strokeWidth="1.5" />
          <circle cx={getX(5)} cy={getY(indoor_temperature_c[5])} r="4" fill="#ef4444" stroke="#ffffff" strokeWidth="1.5" />
        </svg>
      </div>

      {/* Legend & Summary Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4 pt-3 border-t border-slate-800 text-xs">
        <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
          <div className="text-slate-400 text-[10px] uppercase font-mono">Min Indoor Temp</div>
          <div className="text-sm font-bold text-red-400 mt-0.5">{min_indoor_temp_c}°C</div>
          <div className="text-[10px] text-slate-500">Predicted at dawn (05:00)</div>
        </div>

        <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
          <div className="text-slate-400 text-[10px] uppercase font-mono">Peak Indoor Temp</div>
          <div className="text-sm font-bold text-cyan-400 mt-0.5">{peak_indoor_temp_c}°C</div>
          <div className="text-[10px] text-slate-500">Post solar soak (14:00)</div>
        </div>

        <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
          <div className="text-slate-400 text-[10px] uppercase font-mono">Critical Heat-Loss Period</div>
          <div className="text-sm font-bold text-amber-400 mt-0.5">{high_heat_loss_period}</div>
          <div className="text-[10px] text-slate-500">Peak thermal deficit window</div>
        </div>

        <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
          <div className="text-slate-400 text-[10px] uppercase font-mono">Heating Deficit Offset</div>
          <div className="text-sm font-bold text-emerald-400 mt-0.5">{simulation.heating_energy_required_kwh_day} kWh/day</div>
          <div className="text-[10px] text-slate-500">Supplemental energy required</div>
        </div>
      </div>
    </div>
  );
};
