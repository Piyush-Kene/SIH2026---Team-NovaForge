export interface ClimateData {
  location_name: string;
  latitude: number;
  longitude: number;
  elevation_m: number;
  climate_zone: string;
  avg_annual_temp_c: number;
  min_temp_c: number;
  max_temp_c: number;
  annual_ghi_kwh_m2: number;
  avg_daily_ghi_kwh_m2: number;
  avg_sunshine_hours_day: number;
  avg_wind_speed_mps: number;
  relative_humidity_pct: number;
  heating_degree_days: number;
  cooling_degree_days: number;
  hourly_temperatures: number[];
  hourly_ghi: number[];
  data_source: string;
  is_fallback: boolean;
}

export interface SolarPotentialResponse {
  location_name: string;
  latitude: number;
  longitude: number;
  elevation_m: number;
  annual_ghi_kwh_m2: number;
  avg_daily_ghi_kwh_m2: number;
  optimal_tilt_deg: number;
  optimal_azimuth_deg: number;
  solar_potential_score: number;
  rating_category: string;
  usable_sun_hours_annual: number;
  terrain_slope_deg: number;
  shading_factor: number;
  estimated_annual_yield_per_kw: number;
  methodology: string;
}

export interface ThermalSimulationResponse {
  hours: number[];
  outside_temperature_c: number[];
  indoor_temperature_c: number[];
  solar_radiation_ghi_w_m2: number[];
  solar_gain_w: number[];
  envelope_heat_loss_w: number[];
  ventilation_heat_loss_w: number[];
  net_heat_flow_w: number[];
  peak_indoor_temp_c: number;
  min_indoor_temp_c: number;
  avg_indoor_temp_c: number;
  thermal_comfort_score: number;
  thermal_stability_index: number;
  heating_energy_required_kwh_day: number;
  high_heat_loss_period: string;
  status_summary: string;
  is_cold_hazard_predicted: boolean;
  risk_level: "low" | "caution" | "high_risk";
  scientific_methodology: string;
}

export interface RecommendedDesign {
  rank: number;
  name: string;
  orientation_deg: number;
  orientation_label: string;
  wall_material: string;
  wall_insulation_thickness_cm: number;
  roof_angle_deg: number;
  window_to_wall_ratio_pct: number;
  solar_capacity_kw: number;
  thermal_score: number;
  solar_score: number;
  energy_score: number;
  cost_score: number;
  overall_score: number;
  estimated_project_cost_inr: number;
  estimated_subsidy_inr: number;
  net_cost_inr: number;
  annual_solar_generation_kwh: number;
  annual_heating_deficit_kwh: number;
  key_advantage: string;
}

export interface OptimizerResponse {
  top_designs: RecommendedDesign[];
  best_overall_design: RecommendedDesign;
  optimization_method: string;
  pareto_tradeoff_notes: string;
}

export interface FinancialCalculationResponse {
  equipment_cost_inr: number;
  installation_and_civil_cost_inr: number;
  shelter_construction_cost_inr: number;
  total_project_cost_inr: number;
  applicable_schemes: Array<{
    id: string;
    name: string;
    authority: string;
    estimated_benefit_inr: number;
    formula: string;
    portal: string;
    verified_date: string;
  }>;
  total_estimated_support_inr: number;
  net_payable_cost_inr: number;
  annual_electricity_savings_inr: number;
  diesel_fuel_offset_liters_annual: number;
  diesel_fuel_savings_inr_annual: number;
  total_annual_monetary_benefit_inr: number;
  simple_payback_years: number;
  ten_year_net_savings_inr: number;
  co2_reduction_tonnes_10y: number;
  disclaimer: string;
}

export interface RankedLocationItem {
  rank: number;
  location_name: string;
  state_ut: string;
  latitude: number;
  longitude: number;
  elevation_m: number;
  solar_score: number;
  thermal_suitability_score: number;
  feasibility_score: number;
  overall_rank_score: number;
  annual_solar_yield_kwh_kw: number;
  climate_zone: string;
  recommendation_summary: string;
}
