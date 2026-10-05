from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class LocationQuery(BaseModel):
    name: Optional[str] = "Leh, Ladakh"
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")
    elevation: Optional[float] = None

class ClimateData(BaseModel):
    location_name: str
    latitude: float
    longitude: float
    elevation_m: float
    climate_zone: str
    avg_annual_temp_c: float
    min_temp_c: float
    max_temp_c: float
    annual_ghi_kwh_m2: float
    avg_daily_ghi_kwh_m2: float
    avg_sunshine_hours_day: float
    avg_wind_speed_mps: float
    relative_humidity_pct: float
    heating_degree_days: float
    cooling_degree_days: float
    hourly_temperatures: List[float] = []
    hourly_ghi: List[float] = []
    data_source: str
    is_fallback: bool = False

class SolarPotentialRequest(BaseModel):
    latitude: float
    longitude: float
    elevation_m: Optional[float] = None
    slope_deg: Optional[float] = 0.0
    aspect_deg: Optional[float] = 180.0  # 180 = South facing

class SolarPotentialResponse(BaseModel):
    location_name: str
    latitude: float
    longitude: float
    elevation_m: float
    annual_ghi_kwh_m2: float
    avg_daily_ghi_kwh_m2: float
    optimal_tilt_deg: float
    optimal_azimuth_deg: float
    solar_potential_score: float = Field(..., ge=0, le=100)
    rating_category: str
    usable_sun_hours_annual: float
    terrain_slope_deg: float
    shading_factor: float
    estimated_annual_yield_per_kw: float
    methodology: str = "Perez/pvlib anisotropic sky diffuse & geometric transposition models"

class PanelOptimizerRequest(BaseModel):
    latitude: float
    longitude: float
    available_roof_area_m2: float = 60.0
    panel_wattage_w: int = 400
    desired_capacity_kw: Optional[float] = 10.0
    roof_tilt_deg: Optional[float] = None
    roof_azimuth_deg: float = 180.0
    shading_loss_pct: float = 3.0

class PanelOptimizerResponse(BaseModel):
    recommended_panels: int
    installed_capacity_kw: float
    actual_roof_footprint_m2: float
    estimated_annual_generation_kwh: float
    estimated_monthly_generation_kwh: List[float]
    capacity_utilization_factor_pct: float
    optimal_tilt_deg: float
    optimal_azimuth_deg: float
    co2_offset_tonnes_annual: float
    methodology: str

class ShelterGeometry(BaseModel):
    length_m: float = 8.0
    width_m: float = 6.0
    height_m: float = 3.0
    roof_type: str = "pitched"  # flat, pitched, shed
    roof_angle_deg: float = 30.0
    orientation_deg: float = 180.0  # azimuth, 180 is South

class ShelterOpenings(BaseModel):
    window_area_south_m2: float = 4.0
    window_area_north_m2: float = 0.5
    window_area_east_m2: float = 1.0
    window_area_west_m2: float = 1.0
    door_area_m2: float = 2.0
    window_shading_coefficient: float = 0.65
    window_u_value: float = 2.4  # Double glazing W/m2K

class MaterialLayer(BaseModel):
    material_id: str
    thickness_m: float
    conductivity_w_mk: float
    density_kg_m3: float
    specific_heat_j_kgk: float

class ShelterMaterials(BaseModel):
    wall_material: str = "insulated_sandwich_panel"
    wall_thickness_m: float = 0.15
    wall_u_value: Optional[float] = None
    roof_material: str = "insulated_sandwich_panel"
    roof_thickness_m: float = 0.15
    roof_u_value: Optional[float] = None
    floor_material: str = "concrete_slab_insulated"
    floor_thickness_m: float = 0.20
    floor_u_value: Optional[float] = None
    insulation_material: str = "rock_wool"
    insulation_thickness_m: float = 0.10
    thermal_mass_rating: str = "high"

class ThermalSimulationRequest(BaseModel):
    location_name: str = "Leh, Ladakh"
    latitude: float = 34.1526
    longitude: float = 77.5771
    geometry: ShelterGeometry = ShelterGeometry()
    materials: ShelterMaterials = ShelterMaterials()
    openings: ShelterOpenings = ShelterOpenings()
    air_change_per_hour: float = 0.6
    internal_heat_gain_w: float = 250.0  # Occupants + lighting
    target_comfort_min_c: float = 18.0
    target_comfort_max_c: float = 24.0

class ThermalSimulationResponse(BaseModel):
    hours: List[int]
    outside_temperature_c: List[float]
    indoor_temperature_c: List[float]
    solar_radiation_ghi_w_m2: List[float]
    solar_gain_w: List[float]
    envelope_heat_loss_w: List[float]
    ventilation_heat_loss_w: List[float]
    net_heat_flow_w: List[float]
    peak_indoor_temp_c: float
    min_indoor_temp_c: float
    avg_indoor_temp_c: float
    thermal_comfort_score: float
    thermal_stability_index: float
    heating_energy_required_kwh_day: float
    high_heat_loss_period: str
    status_summary: str
    is_cold_hazard_predicted: bool
    risk_level: str  # low, caution, high_risk
    scientific_methodology: str

class OptimizationRequest(BaseModel):
    location_name: str = "Leh, Ladakh"
    latitude: float = 34.1526
    longitude: float = 77.5771
    budget_max_inr: Optional[float] = 1200000.0
    user_category: str = "defense_research"  # defense_research, civilian_residential, remote_station
    floor_area_m2: float = 48.0
    prioritize_solar: bool = True
    prioritize_passive_thermal: bool = True

class RecommendedDesign(BaseModel):
    rank: int
    name: str
    orientation_deg: float
    orientation_label: str
    wall_material: str
    wall_insulation_thickness_cm: float
    roof_angle_deg: float
    window_to_wall_ratio_pct: float
    solar_capacity_kw: float
    thermal_score: float
    solar_score: float
    energy_score: float
    cost_score: float
    overall_score: float
    estimated_project_cost_inr: float
    estimated_subsidy_inr: float
    net_cost_inr: float
    annual_solar_generation_kwh: float
    annual_heating_deficit_kwh: float
    key_advantage: str

class OptimizerResponse(BaseModel):
    top_designs: List[RecommendedDesign]
    best_overall_design: RecommendedDesign
    optimization_method: str = "Multi-Objective Pareto Tradeoff Engine (SciPy/Heuristic Search)"
    pareto_tradeoff_notes: str

class FinancialCalculationRequest(BaseModel):
    system_capacity_kw: float = 10.0
    shelter_floor_area_m2: float = 48.0
    installation_type: str = "rooftop_stand_alone_hybrid"
    state_or_ut: str = "Ladakh"
    user_category: str = "defense_research"
    grid_tariff_inr_kwh: float = 6.5
    diesel_generator_replacement: bool = True

class FinancialCalculationResponse(BaseModel):
    equipment_cost_inr: float
    installation_and_civil_cost_inr: float
    shelter_construction_cost_inr: float
    total_project_cost_inr: float
    applicable_schemes: List[Dict[str, Any]]
    total_estimated_support_inr: float
    net_payable_cost_inr: float
    annual_electricity_savings_inr: float
    diesel_fuel_offset_liters_annual: float
    diesel_fuel_savings_inr_annual: float
    total_annual_monetary_benefit_inr: float
    simple_payback_years: float
    ten_year_net_savings_inr: float
    co2_reduction_tonnes_10y: float
    disclaimer: str

class RankedLocationItem(BaseModel):
    rank: int
    location_name: str
    state_ut: str
    latitude: float
    longitude: float
    elevation_m: float
    solar_score: float
    thermal_suitability_score: float
    feasibility_score: float
    overall_rank_score: float
    annual_solar_yield_kwh_kw: float
    climate_zone: str
    recommendation_summary: str
