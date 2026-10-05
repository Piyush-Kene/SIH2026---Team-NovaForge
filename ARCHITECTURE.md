# GEOTHERM SHIELD: Architecture Specification

## System Data Flow

```mermaid
graph TD
    User([User / Defense Engineer]) --> UI[Next.js App Interface]
    UI --> GIS[MapLibre Interactive GIS Map]
    UI --> ThreeJS[Three.js 3D Shelter Visualizer]
    UI --> Sandbox["What-If?" Interactive Sandbox]

    UI --> API[FastAPI Backend Engine]
    
    API --> ClimateService[Climate Data Service]
    ClimateService --> OpenMeteo[(Open-Meteo Global Reanalysis)]
    ClimateService --> FallbackDB[(Offline High-Fidelity IMD/NASA Baseline)]

    API --> SolarEngine[pvlib Solar Transposition & Pitch Sizer]
    API --> ThermalEngine[1D Dynamic Lumped RC Network / RK4 Solver]
    API --> Optimizer[Pareto Multi-Objective Co-Optimizer]
    API --> FinanceEngine[Capex, DG Offset & Subsidy Engine]
    API --> PDFEngine[ReportLab Technical PDF Compiler]

    ThermalEngine --> MaterialsDB[(Materials & Insulation Catalog)]
    FinanceEngine --> SubsidyDB[(MNRE / State Subsidy Database)]
```

## Scientific Methodology & Formulas

### 1. Thermal Envelope Conductance
$$UA_{total} = \sum_{i} U_i A_i + \dot{V} \cdot \rho_{air}(z) \cdot C_p$$
where air density varies with altitude:
$$\rho_{air}(z) = 1.225 \cdot \exp\left(-\frac{z}{8500}\right) \text{ kg/m}^3$$

### 2. Runge-Kutta 4th Order (RK4) Numerical Solvers
The differential temperature change is integrated numerically:
$$\Delta T = \frac{\Delta t}{6} (k_1 + 2k_2 + 2k_3 + k_4)$$
preventing numerical instability under rapid exterior diurnal shifts.

### 3. Solar Shading & Inter-Row Pitch
Row pitch to prevent winter solstice shading at noon:
$$\text{Spacing Multiplier} = 1.0 + \frac{\sin(\beta_{tilt})}{\tan(\alpha_{winter\_sun})} \cdot 0.4$$
