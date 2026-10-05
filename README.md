# GEOTHERM SHIELD
### Climate-Aware Passive Shelter & Solar Optimization Platform
**SIH Problem Statement SIH26051**: *“Software Based Model Development for Design of Area Specific Shelter for Thermal Comfort Maintenance.”*

---

## 🚀 Overview

**GEOTHERM SHIELD** is a production-grade defense and scientific research decision-support platform designed to solve shelter thermal habitability in extreme Indian climates (from -20°C high-altitude Ladakh cold deserts to +48°C Thar desert outposts).

By coupling **GIS geospatial intelligence**, **high-fidelity microclimate datasets**, **1D dynamic lumped RC thermal differential equations (Runge-Kutta 4th Order)**, **pvlib solar transposition modeling**, and a **Pareto multi-objective co-optimizer**, GeoTherm Shield replaces guesswork with empirical engineering precision.

---

## 🏗️ System Architecture

```
aryan SIH/
├── backend/
│   ├── api/                 # Endpoint routing
│   ├── database/            # Material thermophysical catalog & subsidy database
│   ├── models/              # Pydantic schemas
│   ├── services/
│   │   ├── climate/         # Open-Meteo & IMD/NASA baseline fallback service
│   │   ├── finance/         # Capex, DG offset, and MNRE subsidy engine
│   │   ├── gis/             # Multi-criteria site ranking service
│   │   ├── optimization/    # Pareto multi-objective co-optimizer
│   │   ├── reports/         # ReportLab technical PDF compiler
│   │   ├── solar/           # pvlib radiation, transposition, and pitch optimizer
│   │   └── thermal/         # Dynamic RK4 lumped capacitance thermal engine
│   ├── tests/               # Pytest automated test suite
│   ├── main.py              # FastAPI server
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router (Master Dashboard)
│   │   ├── components/      # GISMap (MapLibre), Shelter3D (Three.js), ThermalChart
│   │   ├── lib/             # API client & offline demo fallback dataset
│   │   └── types/           # TypeScript interfaces
│   ├── package.json
│   └── tsconfig.json
├── .env.example
├── ARCHITECTURE.md
├── DATA_SOURCES.md
└── DEMO_GUIDE.md
```

---

## ⚡ Quick Start & Running Locally

### 1. Start Python FastAPI Backend
```powershell
cd "c:\Users\HP\Desktop\Web Projects\aryan SIH\backend"
.\venv\Scripts\activate
$env:PYTHONPATH="."
uvicorn main:app --reload --port 8000
```
Backend will be live at `http://127.0.0.1:8000` with interactive Swagger docs at `http://127.0.0.1:8000/docs`.

### 2. Start Next.js Frontend
```powershell
cd "c:\Users\HP\Desktop\Web Projects\aryan SIH\frontend"
npm run dev
```
Frontend will be live at `http://localhost:3000`.

---

## 🔬 Core Scientific Engines

1. **Microclimate Service**: Fetches real-time temperature, radiation, and wind from Open-Meteo with automatic fallback to high-fidelity regional IMD/NASA POWER baselines.
2. **Solar Transposition Engine**: Uses pvlib anisotropic sky diffuse formulas with high-altitude atmospheric transmittance amplification and winter-solstice inter-row shadow-free spacing.
3. **Dynamic 1D Thermal Simulation**:
   $$\frac{dT_{in}}{dt} = \frac{\sum U_i A_i (T_{ext} - T_{in}) + \dot{m} C_p (T_{ext} - T_{in}) + Q_{solar} + Q_{internal}}{C_{total}}$$
   Solved via Runge-Kutta 4th Order numerical integration over 24-hour diurnal swings.
4. **Pareto Co-Optimizer**: Evaluates permutations of wall materials, insulation thickness, solar azimuth, and PV capacity to find the Pareto optimal balance.
5. **Government Subsidy & Financial Engine**: Calculates equipment costs, MNRE / LAHDC cold-desert capital grants, and diesel generator (DG) fuel offset savings.
6. **ReportLab PDF Generator**: Compiles downloadable multi-page technical feasibility reports.

---

## 🧪 Automated Testing
Backend tests can be executed via:
```powershell
cd backend
$env:PYTHONPATH="."
.\venv\Scripts\pytest -v tests/test_backend.py
```
Includes tests for health endpoints, climate resolution, solar transposition, thermal simulation, Pareto optimizer, subsidy ledger, and PDF binary output.
