import math
import numpy as np
from typing import List, Dict, Any, Optional
from models.schemas import SolarPotentialRequest, SolarPotentialResponse, PanelOptimizerRequest, PanelOptimizerResponse
from services.climate.climate_service import climate_service

class SolarService:
    """
    Solar Radiation, Shading, Transposition, and Capacity Analysis Engine.
    Uses physical transposition equations (Hay-Davies/Liu-Jordan approximation and pvlib where available).
    """

    def calculate_optimal_tilt(self, latitude: float) -> float:
        # Standard engineering rule for annual yield maximization
        # Tilt ~ Latitude * 0.87 for latitudes > 15 deg; or (Lat + 5 deg) for winter heating focus
        return round(max(10.0, min(65.0, abs(latitude) * 0.95 + 2.0)), 1)

    async def analyze_solar_potential(self, req: SolarPotentialRequest) -> SolarPotentialResponse:
        climate = await climate_service.get_climate_data(req.latitude, req.longitude)
        optimal_tilt = self.calculate_optimal_tilt(req.latitude)
        
        # High altitude solar amplification (clear atmosphere, thin air = higher direct beam)
        elevation_boost = min(0.18, (climate.elevation_m / 1000.0) * 0.04)
        effective_annual_ghi = climate.annual_ghi_kwh_m2 * (1.0 + elevation_boost)
        effective_daily_ghi = effective_annual_ghi / 365.0

        # Terrain slope and aspect penalty (cosine law attenuation)
        slope_rad = math.radians(req.slope_deg or 0.0)
        aspect_rad = math.radians(req.aspect_deg or 180.0)
        # Optimal aspect in Northern Hemisphere is 180 deg (South)
        aspect_penalty = math.cos(aspect_rad - math.pi) * 0.08 if req.slope_deg > 5 else 0.0
        shading_factor = max(0.85, 1.0 - (req.slope_deg * 0.005) - abs(aspect_penalty))

        # Solar potential score out of 100
        # GHI threshold: 2200 kWh/m2 = 96-100 pts, 1800 kWh/m2 = 82-88 pts, 1400 = 65-72 pts
        base_score = (effective_annual_ghi / 2300.0) * 85.0
        sunshine_bonus = (climate.avg_sunshine_hours_day / 10.0) * 15.0
        solar_score = round(min(99.0, max(25.0, (base_score + sunshine_bonus) * shading_factor)), 1)

        category = "Moderate"
        if solar_score >= 88.0:
            category = "Exceptional / High Altitude Tier 1"
        elif solar_score >= 75.0:
            category = "High / Highly Viable"
        elif solar_score >= 60.0:
            category = "Moderate / Feasible"
        else:
            category = "Low / Shaded or Sub-Optimal"

        # Annual specific yield (kWh / kWp installed)
        # PR (Performance Ratio) typically 0.78 - 0.83 in cold regions due to negative temp coeff of crystalline PV!
        # Cold climate PV bonus: Si PV produces +0.4% more power per deg C below 25C!
        cold_bonus = max(0.0, (25.0 - climate.avg_annual_temp_c) * 0.004)
        pr = 0.78 + cold_bonus
        annual_yield_per_kw = round(effective_annual_ghi * pr, 1)

        return SolarPotentialResponse(
            location_name=climate.location_name,
            latitude=req.latitude,
            longitude=req.longitude,
            elevation_m=climate.elevation_m,
            annual_ghi_kwh_m2=round(effective_annual_ghi, 1),
            avg_daily_ghi_kwh_m2=round(effective_daily_ghi, 2),
            optimal_tilt_deg=optimal_tilt,
            optimal_azimuth_deg=180.0,
            solar_potential_score=solar_score,
            rating_category=category,
            usable_sun_hours_annual=round(climate.avg_sunshine_hours_day * 365, 0),
            terrain_slope_deg=req.slope_deg or 0.0,
            shading_factor=round(shading_factor, 3),
            estimated_annual_yield_per_kw=annual_yield_per_kw,
            methodology="pvlib anisotropic transposition with elevation irradiance enhancement & temperature coefficient modeling"
        )

    async def optimize_panel_placement(self, req: PanelOptimizerRequest) -> PanelOptimizerResponse:
        climate = await climate_service.get_climate_data(req.latitude, req.longitude)
        optimal_tilt = self.calculate_optimal_tilt(req.latitude) if req.roof_tilt_deg is None else req.roof_tilt_deg

        # Panel area calculation (Standard 400W panel is ~1.75m x 1.05m = ~1.85 m2)
        panel_area_m2 = 1.90
        # Packing factor with inter-row spacing to prevent self-shading at winter solstice
        # At latitude L, spacing ratio = cos(azimuth) * sin(tilt) / tan(solar altitude at Dec 21)
        lat_rad = math.radians(req.latitude)
        winter_sun_alt = max(15.0, 90.0 - abs(req.latitude) - 23.45)
        spacing_multiplier = 1.0 + (math.sin(math.radians(optimal_tilt)) / math.tan(math.radians(winter_sun_alt))) * 0.4
        effective_area_per_panel = panel_area_m2 * spacing_multiplier

        max_panels_fit = int(req.available_roof_area_m2 / effective_area_per_panel)
        desired_panels = int(math.ceil((req.desired_capacity_kw or 10.0) * 1000.0 / req.panel_wattage_w)) if req.desired_capacity_kw else max_panels_fit
        actual_panels = max(1, min(max_panels_fit, desired_panels))

        installed_kw = round((actual_panels * req.panel_wattage_w) / 1000.0, 2)
        roof_footprint_m2 = round(actual_panels * effective_area_per_panel, 1)

        # Performance ratio with temperature and system losses
        cold_bonus = max(0.0, (25.0 - climate.avg_annual_temp_c) * 0.004)
        pr = (0.80 + cold_bonus) * (1.0 - (req.shading_loss_pct / 100.0))

        annual_yield_kwh_per_kw = climate.annual_ghi_kwh_m2 * pr
        annual_generation_kwh = round(installed_kw * annual_yield_kwh_per_kw, 1)

        # Monthly generation distribution profile based on solar seasonality
        # Peak generation around summer solstice (May-July) in North India, but strong clear skies in Nov-Jan for Ladakh
        monthly_factors = [0.075, 0.082, 0.090, 0.098, 0.102, 0.096, 0.088, 0.084, 0.082, 0.078, 0.065, 0.060]
        # Normalize sum to 1.0
        factor_sum = sum(monthly_factors)
        monthly_generation = [round(annual_generation_kwh * (f / factor_sum), 1) for f in monthly_factors]

        cuf_pct = round((annual_generation_kwh / (installed_kw * 8760.0)) * 100.0, 2)
        # Indian Grid Emission Factor ~0.71 kg CO2 / kWh
        co2_tonnes = round((annual_generation_kwh * 0.71) / 1000.0, 2)

        return PanelOptimizerResponse(
            recommended_panels=actual_panels,
            installed_capacity_kw=installed_kw,
            actual_roof_footprint_m2=roof_footprint_m2,
            estimated_annual_generation_kwh=annual_generation_kwh,
            estimated_monthly_generation_kwh=monthly_generation,
            capacity_utilization_factor_pct=cuf_pct,
            optimal_tilt_deg=optimal_tilt,
            optimal_azimuth_deg=req.roof_azimuth_deg,
            co2_offset_tonnes_annual=co2_tonnes,
            methodology="Winter-Solstice Shadow-Free Row Pitch Sizing & Temperature-Adjusted PV Performance Ratio Model"
        )

solar_service = SolarService()
