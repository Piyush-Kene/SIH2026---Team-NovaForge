"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldCheck, Sun, Thermometer, Sliders, FileText, Download,
  Compass, Award, RefreshCw, AlertCircle, Layers, CheckCircle2,
  DollarSign, Sparkles, TrendingUp
} from "lucide-react";
import { GISMap } from "@/components/GISMap";
import { Shelter3D } from "@/components/Shelter3D";
import { ThermalChart } from "@/components/ThermalChart";
import {
  fetchClimateData,
  fetchSolarPotential,
  runThermalSimulation,
  runOptimizer,
  calculateFinancials,
  downloadReportPdf,
  DEMO_LOCATIONS
} from "@/lib/api";
import {
  ClimateData,
  SolarPotentialResponse,
  ThermalSimulationResponse,
  OptimizerResponse,
  FinancialCalculationResponse
} from "@/types/geotherm";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"dashboard" | "gis" | "thermal" | "solar" | "optimizer" | "finance">("dashboard");
  const [selectedLocation, setSelectedLocation] = useState({
    name: "Leh, Ladakh",
    lat: 34.1526,
    lon: 77.5771
  });
  const [activeMapLayer, setActiveMapLayer] = useState("solar");

  // State for modules
  const [climate, setClimate] = useState<ClimateData | null>(null);
  const [solar, setSolar] = useState<SolarPotentialResponse | null>(null);
  const [simulation, setSimulation] = useState<ThermalSimulationResponse | null>(null);
  const [optimizer, setOptimizer] = useState<OptimizerResponse | null>(null);
  const [finance, setFinance] = useState<FinancialCalculationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [downloadingReport, setDownloadingReport] = useState(false);

  // What-If Simulator Inputs
  const [wallInsulationCm, setWallInsulationCm] = useState(12);
  const [orientationDeg, setOrientationDeg] = useState(180);
  const [solarCapacityKw, setSolarCapacityKw] = useState(10);
  const [windowAreaSouthM2, setWindowAreaSouthM2] = useState(5.0);

  // Initial load & when location changes
  useEffect(() => {
    loadLocationIntelligence(selectedLocation.lat, selectedLocation.lon, selectedLocation.name);
  }, [selectedLocation]);

  const loadLocationIntelligence = async (lat: number, lon: number, name: string) => {
    setLoading(true);
    try {
      const climData = await fetchClimateData(lat, lon, name);
      setClimate(climData);

      const solData = await fetchSolarPotential(lat, lon);
      setSolar(solData);

      // Trigger thermal simulation
      const simData = await runThermalSimulation({
        location_name: name,
        latitude: lat,
        longitude: lon,
        geometry: {
          length_m: 8.0,
          width_m: 6.0,
          height_m: 3.0,
          roof_angle_deg: solData.optimal_tilt_deg,
          orientation_deg: orientationDeg
        },
        materials: {
          wall_material: "insulated_sandwich_panel",
          wall_thickness_m: 0.15,
          insulation_thickness_m: wallInsulationCm / 100.0,
          roof_material: "insulated_sandwich_panel",
          roof_thickness_m: 0.15
        },
        openings: {
          window_area_south_m2: windowAreaSouthM2,
          window_area_north_m2: 0.4,
          window_area_east_m2: 1.0,
          window_area_west_m2: 1.0
        }
      });
      setSimulation(simData);

      // Multi-Objective Optimizer
      const optData = await runOptimizer({
        location_name: name,
        latitude: lat,
        longitude: lon,
        floor_area_m2: 48.0
      });
      setOptimizer(optData);

      // Financials
      const finData = await calculateFinancials({
        system_capacity_kw: solarCapacityKw,
        shelter_floor_area_m2: 48.0,
        state_or_ut: lat > 31 ? "Ladakh" : "All India"
      });
      setFinance(finData);
    } catch (err) {
      console.error("Pipeline intelligence error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Immediate "What-If?" Simulation update
  const handleWhatIfUpdate = async () => {
    setLoading(true);
    try {
      const simData = await runThermalSimulation({
        location_name: selectedLocation.name,
        latitude: selectedLocation.lat,
        longitude: selectedLocation.lon,
        geometry: {
          length_m: 8.0,
          width_m: 6.0,
          height_m: 3.0,
          roof_angle_deg: solar?.optimal_tilt_deg || 35,
          orientation_deg: orientationDeg
        },
        materials: {
          wall_material: "insulated_sandwich_panel",
          wall_thickness_m: 0.15,
          insulation_thickness_m: wallInsulationCm / 100.0,
          roof_material: "insulated_sandwich_panel",
          roof_thickness_m: 0.15
        },
        openings: {
          window_area_south_m2: windowAreaSouthM2,
          window_area_north_m2: 0.4,
          window_area_east_m2: 1.0,
          window_area_west_m2: 1.0
        }
      });
      setSimulation(simData);

      const finData = await calculateFinancials({
        system_capacity_kw: solarCapacityKw,
        shelter_floor_area_m2: 48.0,
        state_or_ut: selectedLocation.lat > 31 ? "Ladakh" : "All India"
      });
      setFinance(finData);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    setDownloadingReport(true);
    try {
      const payload = {
        location_name: selectedLocation.name,
        latitude: selectedLocation.lat,
        longitude: selectedLocation.lon,
        elevation_m: climate?.elevation_m || 3524,
        climate_zone: climate?.climate_zone || "Alpine Cold Desert",
        annual_ghi_kwh_m2: solar?.annual_ghi_kwh_m2 || 2180,
        solar_score: solar?.solar_potential_score || 94.0,
        min_temp_c: climate?.min_temp_c || -18.2,
        max_temp_c: climate?.max_temp_c || 28.5,
        thermal_score: simulation?.thermal_comfort_score || 91.5,
        min_indoor_temp_c: simulation?.min_indoor_temp_c || 15.6,
        peak_indoor_temp_c: simulation?.peak_indoor_temp_c || 23.5,
        avg_indoor_temp_c: simulation?.avg_indoor_temp_c || 19.3,
        high_heat_loss_period: simulation?.high_heat_loss_period || "03:00–06:00",
        thermal_stability_index: simulation?.thermal_stability_index || 87.2,
        heating_energy_required_kwh_day: simulation?.heating_energy_required_kwh_day || 5.8,
        wall_material: "Insulated Polyurethane Sandwich Panel (12cm PIR)",
        solar_capacity_kw: solarCapacityKw,
        optimal_tilt_deg: solar?.optimal_tilt_deg || 35.0,
        annual_solar_generation_kwh: solarCapacityKw * 1550,
        co2_tonnes_annual: roundNumber((solarCapacityKw * 1550 * 0.71) / 1000, 1),
        roof_area_m2: 48.0,
        total_project_cost_inr: finance?.total_project_cost_inr || 1312000,
        estimated_subsidy_inr: finance?.total_estimated_support_inr || 350000,
        net_cost_inr: finance?.net_payable_cost_inr || 962000,
        annual_benefit_inr: finance?.total_annual_monetary_benefit_inr || 556450,
        payback_years: finance?.simple_payback_years || 2.4,
        diesel_offset_liters: finance?.diesel_fuel_offset_liters_annual || 4340,
        ten_year_net_inr: finance?.ten_year_net_savings_inr || 2850000
      };
      await downloadReportPdf(payload);
    } catch (e) {
      alert("Error generating PDF report. Ensure backend is running.");
    } finally {
      setDownloadingReport(false);
    }
  };

  const roundNumber = (val: number, decimals: number) => {
    return Number(Math.round(Number(val + "e" + decimals)) + "e-" + decimals);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-cyan-500 selection:text-slate-950">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-teal-700 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <ShieldCheck className="w-6 h-6 text-slate-950" />
            </div>
            <div>
              <div className="text-lg font-black tracking-wider text-slate-100 flex items-center gap-2">
                GEOTHERM SHIELD
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                  SIH26051
                </span>
              </div>
              <div className="text-[11px] text-slate-400 font-mono">
                Climate-Aware Passive Shelter & Solar Optimization Platform
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1 text-xs">
            <button
              onClick={() => setActiveTab("dashboard")}
              className={`px-3 py-1.5 rounded-lg transition ${
                activeTab === "dashboard" ? "bg-cyan-500 text-slate-950 font-bold" : "text-slate-300 hover:bg-slate-800"
              }`}
            >
              Master Dashboard
            </button>
            <button
              onClick={() => setActiveTab("gis")}
              className={`px-3 py-1.5 rounded-lg transition ${
                activeTab === "gis" ? "bg-cyan-500 text-slate-950 font-bold" : "text-slate-300 hover:bg-slate-800"
              }`}
            >
              GIS Intelligence
            </button>
            <button
              onClick={() => setActiveTab("thermal")}
              className={`px-3 py-1.5 rounded-lg transition ${
                activeTab === "thermal" ? "bg-cyan-500 text-slate-950 font-bold" : "text-slate-300 hover:bg-slate-800"
              }`}
            >
              Thermal Simulation
            </button>
            <button
              onClick={() => setActiveTab("optimizer")}
              className={`px-3 py-1.5 rounded-lg transition ${
                activeTab === "optimizer" ? "bg-cyan-500 text-slate-950 font-bold" : "text-slate-300 hover:bg-slate-800"
              }`}
            >
              Co-Optimizer
            </button>
            <button
              onClick={() => setActiveTab("finance")}
              className={`px-3 py-1.5 rounded-lg transition ${
                activeTab === "finance" ? "bg-cyan-500 text-slate-950 font-bold" : "text-slate-300 hover:bg-slate-800"
              }`}
            >
              Financial & Subsidies
            </button>
          </nav>

          {/* Export Report Action */}
          <button
            onClick={handleDownloadReport}
            disabled={downloadingReport}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-teal-500 to-cyan-500 text-slate-950 text-xs font-bold hover:brightness-110 shadow-lg shadow-cyan-500/20 disabled:opacity-50"
          >
            <Download className="w-4 h-4" />
            {downloadingReport ? "Compiling PDF..." : "Export Report (PDF)"}
          </button>
        </div>
      </header>

      {/* Main Content Container */}
      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Hero KPI Strip */}
        <section className="grid grid-cols-2 md:grid-cols-6 gap-3">
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 shadow-md">
            <div className="text-[10px] uppercase font-mono text-slate-400">Target Location</div>
            <div className="text-sm font-bold text-slate-100 truncate mt-1">{selectedLocation.name}</div>
            <div className="text-[10px] font-mono text-cyan-400">{climate?.elevation_m || 3524}m AMSL</div>
          </div>

          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 shadow-md">
            <div className="text-[10px] uppercase font-mono text-slate-400">Solar Potential</div>
            <div className="text-sm font-bold text-amber-400 mt-1">{solar?.solar_potential_score || 94.0} / 100</div>
            <div className="text-[10px] text-slate-400">{solar?.annual_ghi_kwh_m2 || 2180} kWh/m² GHI</div>
          </div>

          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 shadow-md">
            <div className="text-[10px] uppercase font-mono text-slate-400">Thermal Comfort</div>
            <div className="text-sm font-bold text-cyan-400 mt-1">{simulation?.thermal_comfort_score || 91.5} / 100</div>
            <div className="text-[10px] text-emerald-400 font-mono">Min {simulation?.min_indoor_temp_c || 15.6}°C</div>
          </div>

          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 shadow-md">
            <div className="text-[10px] uppercase font-mono text-slate-400">Solar PV Sizing</div>
            <div className="text-sm font-bold text-slate-100 mt-1">{solarCapacityKw} kWp Array</div>
            <div className="text-[10px] text-slate-400">{roundNumber(solarCapacityKw * 1550, 0)} kWh/yr Yield</div>
          </div>

          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 shadow-md">
            <div className="text-[10px] uppercase font-mono text-slate-400">Government Support</div>
            <div className="text-sm font-bold text-emerald-400 mt-1">₹{finance?.total_estimated_support_inr?.toLocaleString() || "3,50,000"}</div>
            <div className="text-[10px] text-slate-400">MNRE Ladakh Grant</div>
          </div>

          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 shadow-md">
            <div className="text-[10px] uppercase font-mono text-slate-400">Net Project Cost</div>
            <div className="text-sm font-bold text-teal-300 mt-1">₹{finance?.net_payable_cost_inr?.toLocaleString() || "9,62,000"}</div>
            <div className="text-[10px] text-cyan-400 font-mono">{finance?.simple_payback_years || 2.4} Yr Payback</div>
          </div>
        </section>

        {/* Master Row: GIS Map & 3D Shelter Visualizer */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-7 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
                <Compass className="w-4 h-4 text-cyan-400" />
                Location & GIS Multi-Layer Intelligence
              </h2>
              <span className="text-xs text-slate-400 font-mono">
                Click map to lock arbitrary coordinate
              </span>
            </div>
            <GISMap
              selectedLocation={selectedLocation}
              onSelectLocation={setSelectedLocation}
              activeLayer={activeMapLayer}
              setActiveLayer={setActiveMapLayer}
            />
          </div>

          <div className="lg:col-span-5 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
                <Layers className="w-4 h-4 text-teal-400" />
                3D Parametric Digital Twin
              </h2>
              <span className="text-xs text-slate-400 font-mono">
                Drag mouse to inspect azimuth
              </span>
            </div>
            <Shelter3D
              roofAngle={solar?.optimal_tilt_deg || 35}
              orientationDeg={orientationDeg}
              solarKw={solarCapacityKw}
            />
          </div>
        </section>

        {/* Dynamic 24-Hour Thermal Engine Simulation */}
        <section>
          {simulation ? (
            <ThermalChart simulation={simulation} />
          ) : (
            <div className="h-64 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-center text-slate-500">
              Running dynamic Runge-Kutta 4th Order thermal equation solvers...
            </div>
          )}
        </section>

        {/* "What-If?" Real-Time Engineering Sandbox */}
        <section className="bg-slate-900 border border-cyan-900/60 rounded-xl p-5 shadow-xl">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
            <div>
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Sliders className="w-5 h-5 text-cyan-400" />
                Real-Time "What-If?" Engineering Sandbox
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Modify envelope parameters, glazing aperture, or solar kilowatt sizing to instantly observe thermal comfort and economic impacts.
              </p>
            </div>
            <button
              onClick={handleWhatIfUpdate}
              disabled={loading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 text-xs font-semibold hover:bg-cyan-500/30 transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
              Recalculate Physics
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-xs">
            {/* Wall Insulation */}
            <div className="space-y-2">
              <div className="flex justify-between font-mono">
                <span className="text-slate-400">PIR Insulation Thickness:</span>
                <span className="text-cyan-400 font-bold">{wallInsulationCm} cm</span>
              </div>
              <input
                type="range"
                min="5"
                max="20"
                step="1"
                value={wallInsulationCm}
                onChange={(e) => setWallInsulationCm(Number(e.target.value))}
                className="w-full accent-cyan-500 cursor-pointer"
              />
              <div className="text-[10px] text-slate-500">Range: 5cm (Baseline) to 20cm (Arctic Passive)</div>
            </div>

            {/* Shelter Azimuth */}
            <div className="space-y-2">
              <div className="flex justify-between font-mono">
                <span className="text-slate-400">Shelter Orientation:</span>
                <span className="text-amber-400 font-bold">{orientationDeg}° {orientationDeg === 180 ? "(True South)" : ""}</span>
              </div>
              <input
                type="range"
                min="135"
                max="225"
                step="5"
                value={orientationDeg}
                onChange={(e) => setOrientationDeg(Number(e.target.value))}
                className="w-full accent-amber-500 cursor-pointer"
              />
              <div className="text-[10px] text-slate-500">180° = Optimal solar window gain in N. Hemisphere</div>
            </div>

            {/* South Glazing Aperture */}
            <div className="space-y-2">
              <div className="flex justify-between font-mono">
                <span className="text-slate-400">South Window Area:</span>
                <span className="text-teal-400 font-bold">{windowAreaSouthM2} m²</span>
              </div>
              <input
                type="range"
                min="1"
                max="10"
                step="0.5"
                value={windowAreaSouthM2}
                onChange={(e) => setWindowAreaSouthM2(Number(e.target.value))}
                className="w-full accent-teal-500 cursor-pointer"
              />
              <div className="text-[10px] text-slate-500">Daytime passive solar heat collection aperture</div>
            </div>

            {/* Solar PV Sizing */}
            <div className="space-y-2">
              <div className="flex justify-between font-mono">
                <span className="text-slate-400">Solar PV Capacity:</span>
                <span className="text-emerald-400 font-bold">{solarCapacityKw} kWp</span>
              </div>
              <input
                type="range"
                min="3"
                max="25"
                step="1"
                value={solarCapacityKw}
                onChange={(e) => setSolarCapacityKw(Number(e.target.value))}
                className="w-full accent-emerald-500 cursor-pointer"
              />
              <div className="text-[10px] text-slate-500">Roof capacity & DG genset fuel replacement</div>
            </div>
          </div>
        </section>

        {/* Multi-Objective Optimization Pareto Tradeoff Grid */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-amber-400" />
                Multi-Objective Co-Optimization: Top 3 Pareto Designs
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Simultaneous exploration of envelope thermal resistance, diurnal storage mass, and PV harvest.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {optimizer?.top_designs?.map((design) => (
              <div
                key={design.rank}
                className={`rounded-xl p-4 border transition ${
                  design.rank === 1
                    ? "bg-gradient-to-b from-slate-900 to-cyan-950/40 border-cyan-500/60 shadow-xl shadow-cyan-950/20"
                    : "bg-slate-900/90 border-slate-800"
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className={`text-[10px] font-bold font-mono px-2 py-0.5 rounded ${
                    design.rank === 1 ? "bg-cyan-500 text-slate-950" : "bg-slate-800 text-slate-300"
                  }`}>
                    {design.rank === 1 ? "★ RANK 1 RECOMMENDED" : `RANK ${design.rank}`}
                  </span>
                  <div className="text-right">
                    <span className="text-xs text-slate-400">Composite Score: </span>
                    <span className="text-base font-black text-cyan-400">{design.overall_score}</span>
                  </div>
                </div>

                <h4 className="text-sm font-bold text-slate-100 mb-2">{design.name}</h4>
                <p className="text-xs text-slate-400 mb-4 line-clamp-2">{design.key_advantage}</p>

                <div className="space-y-2 text-xs border-t border-slate-800 pt-3">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Envelope Material:</span>
                    <span className="font-semibold text-slate-200">{design.wall_material}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Insulation / Pitch:</span>
                    <span className="font-semibold text-slate-200">{design.wall_insulation_thickness_cm}cm / {design.roof_angle_deg}°</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Solar Array Capacity:</span>
                    <span className="font-semibold text-amber-400">{design.solar_capacity_kw} kW</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Thermal Comfort Score:</span>
                    <span className="font-semibold text-cyan-400">{design.thermal_score} / 100</span>
                  </div>
                  <div className="flex justify-between border-t border-slate-800 pt-2 font-mono">
                    <span className="text-slate-400">Net Estimated Cost:</span>
                    <span className="font-bold text-emerald-400">₹{design.net_cost_inr?.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Government Scheme & Financial Support Breakdown */}
        <section className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-emerald-400" />
              Government Scheme Verification & Financial Payback
            </h3>
            <span className="text-xs text-slate-400 font-mono">
              Calculations based on verified MNRE / LAHDC subsidy guidelines
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2 space-y-3">
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                Applicable Government Policies
              </div>
              {finance?.applicable_schemes?.map((scheme) => (
                <div key={scheme.id} className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-emerald-400">{scheme.name}</span>
                    <span className="text-xs font-mono font-bold bg-emerald-950 text-emerald-300 px-2 py-0.5 rounded border border-emerald-800">
                      ₹{scheme.estimated_benefit_inr?.toLocaleString()}
                    </span>
                  </div>
                  <div className="text-xs text-slate-300 font-mono">{scheme.authority}</div>
                  <p className="text-xs text-slate-400">{scheme.formula}</p>
                  <div className="text-[10px] text-slate-500 flex justify-between pt-1">
                    <span>Verified Date: {scheme.verified_date}</span>
                    <a href={scheme.portal} target="_blank" rel="noreferrer" className="text-cyan-400 hover:underline">
                      Official Government Portal ↗
                    </a>
                  </div>
                </div>
              ))}
            </div>

            {/* Financial Ledger */}
            <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 space-y-3 text-xs">
              <div className="text-xs font-bold uppercase tracking-wider text-slate-300 border-b border-slate-800 pb-2">
                Project Investment Ledger
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Total Project Gross Cost:</span>
                <span className="font-semibold text-slate-200">₹{finance?.total_project_cost_inr?.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-emerald-400">
                <span>Estimated Government Subsidy:</span>
                <span className="font-bold">- ₹{finance?.total_estimated_support_inr?.toLocaleString()}</span>
              </div>
              <div className="flex justify-between border-t border-slate-800 pt-2 text-sm font-bold">
                <span className="text-slate-200">Net Capital Outlay:</span>
                <span className="text-teal-400">₹{finance?.net_payable_cost_inr?.toLocaleString()}</span>
              </div>
              <div className="space-y-1.5 pt-2 border-t border-slate-800 text-[11px]">
                <div className="flex justify-between">
                  <span className="text-slate-400">Diesel Genset Offset:</span>
                  <span className="font-mono text-amber-300">{finance?.diesel_fuel_offset_liters_annual} Liters/yr</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Simple Payback Period:</span>
                  <span className="font-mono text-cyan-400 font-bold">{finance?.simple_payback_years} Years</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">10-Year Net Economic Return:</span>
                  <span className="font-mono text-emerald-400 font-bold">₹{finance?.ten_year_net_savings_inr?.toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Engineering Disclaimer */}
        <footer className="border-t border-slate-800/80 pt-4 text-center text-xs text-slate-500 space-y-1">
          <div>
            GeoTherm Shield — Software Based Model Development for Design of Area Specific Shelter for Thermal Comfort Maintenance (SIH26051).
          </div>
          <div className="text-[11px] text-slate-600">
            Preliminary software-based engineering estimates for research and hackathon feasibility. Results subject to on-site validation by licensed engineers and competent government authorities.
          </div>
        </footer>
      </main>
    </div>
  );
}
