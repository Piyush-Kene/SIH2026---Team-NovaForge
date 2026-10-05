from fastapi import FastAPI, Query, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any

from models.schemas import (
    ClimateData, SolarPotentialRequest, SolarPotentialResponse,
    PanelOptimizerRequest, PanelOptimizerResponse,
    ThermalSimulationRequest, ThermalSimulationResponse,
    OptimizationRequest, OptimizerResponse,
    FinancialCalculationRequest, FinancialCalculationResponse,
    RankedLocationItem
)
from services.climate.climate_service import climate_service
from services.solar.solar_service import solar_service
from services.thermal.thermal_engine import thermal_engine
from services.optimization.optimizer_service import optimizer_service
from services.finance.finance_service import finance_service
from services.gis.gis_service import gis_service
from services.reports.report_generator import report_generator
from database.material_data import (
    MATERIALS_DATABASE, INSULATION_MATERIALS_DATABASE,
    GOVERNMENT_SUBSIDY_DATABASE, PREDEFINED_LOCATIONS
)

app = FastAPI(
    title="GEOTHERM SHIELD API",
    description="Climate-Aware Passive Shelter & Solar Optimization Platform API (SIH26051)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "GeoTherm Shield Backend",
        "version": "1.0.0",
        "scientific_engines": ["climate", "pvlib_solar", "rk4_thermal", "pareto_optimizer", "reportlab_pdf"]
    }

@app.get("/locations/predefined")
async def get_predefined_locations():
    return list(PREDEFINED_LOCATIONS.values())

@app.get("/materials")
async def get_materials_catalog():
    return {
        "envelope_materials": list(MATERIALS_DATABASE.values()),
        "insulation_materials": list(INSULATION_MATERIALS_DATABASE.values())
    }

@app.get("/subsidies")
async def get_subsidies():
    return GOVERNMENT_SUBSIDY_DATABASE

@app.get("/climate", response_model=ClimateData)
async def get_climate(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    location_name: Optional[str] = None
):
    return await climate_service.get_climate_data(latitude, longitude, location_name)

@app.post("/solar/potential", response_model=SolarPotentialResponse)
async def analyze_solar_potential(req: SolarPotentialRequest):
    return await solar_service.analyze_solar_potential(req)

@app.post("/solar/estimate", response_model=PanelOptimizerResponse)
async def estimate_solar_panels(req: PanelOptimizerRequest):
    return await solar_service.optimize_panel_placement(req)

@app.post("/thermal/simulate", response_model=ThermalSimulationResponse)
async def simulate_thermal(req: ThermalSimulationRequest):
    return await thermal_engine.run_24h_simulation(req)

@app.post("/optimizer/run", response_model=OptimizerResponse)
async def run_optimizer(req: OptimizationRequest):
    return await optimizer_service.run_optimization(req)

@app.post("/financial/calculate", response_model=FinancialCalculationResponse)
async def calculate_financials(req: FinancialCalculationRequest):
    return finance_service.calculate_financials(req)

@app.get("/locations/rank", response_model=List[RankedLocationItem])
async def rank_locations():
    return gis_service.rank_locations()

@app.post("/reports/generate")
async def generate_pdf(data: Dict[str, Any]):
    try:
        pdf_bytes = report_generator.generate_pdf_report(data)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=geotherm_shield_engineering_report.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compile report: {str(e)}")
