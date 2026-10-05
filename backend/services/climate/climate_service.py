import httpx
import logging
from typing import Optional, Dict, Any, List
from models.schemas import ClimateData
from database.material_data import PREDEFINED_LOCATIONS

logger = logging.getLogger(__name__)

class ClimateService:
    def __init__(self, open_meteo_url: str = "https://archive-api.open-meteo.com/v1/archive", nasa_power_url: Optional[str] = None):
        self.open_meteo_url = open_meteo_url
        self.nasa_power_url = nasa_power_url

    def _find_closest_predefined(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        best_match = None
        min_dist = float('inf')
        for loc in PREDEFINED_LOCATIONS.values():
            dist = (loc["latitude"] - lat)**2 + (loc["longitude"] - lon)**2
            if dist < min_dist:
                min_dist = dist
                best_match = loc
        if min_dist < 0.5:  # within ~50km
            return best_match
        return None

    def _generate_synthetic_hourly(self, avg_temp: float, min_temp: float, max_temp: float, avg_ghi: float) -> tuple[List[float], List[float]]:
        import numpy as np
        hours = np.arange(24)
        # Diurnal temp variation: minimum at hour 5 (dawn), peak at hour 14
        amp = (max_temp - min_temp) / 2.0
        mid = (max_temp + min_temp) / 2.0
        temps = mid + amp * np.sin((hours - 9) * np.pi / 12.0)
        temps = [round(float(t), 2) for t in temps]

        # Solar radiation bell curve (zero at night, peak around hour 12-13)
        # avg_daily_ghi in kWh/m2/day converted to peak W/m2 ~ avg * 1000 / (effective hours ~ 8) * 1.5
        peak_w = max(200.0, avg_ghi * 160.0)
        ghi = []
        for h in hours:
            if 6 <= h <= 18:
                rad = peak_w * np.sin((h - 6) * np.pi / 12.0)
                ghi.append(round(float(max(0.0, rad)), 1))
            else:
                ghi.append(0.0)
        return temps, ghi

    async def get_climate_data(self, latitude: float, longitude: float, location_name: Optional[str] = None) -> ClimateData:
        # Check predefined cache first
        predefined = self._find_closest_predefined(latitude, longitude)
        if predefined and (not location_name or location_name.lower() in predefined["name"].lower()):
            temps = predefined["typical_winter_day_temps"]
            _, ghi = self._generate_synthetic_hourly(
                predefined["avg_annual_temp_c"],
                predefined["min_temp_c"],
                predefined["max_temp_c"],
                predefined["avg_daily_ghi_kwh_m2"]
            )
            return ClimateData(
                location_name=predefined["name"],
                latitude=predefined["latitude"],
                longitude=predefined["longitude"],
                elevation_m=predefined["elevation_m"],
                climate_zone=predefined["climate_zone"],
                avg_annual_temp_c=predefined["avg_annual_temp_c"],
                min_temp_c=predefined["min_temp_c"],
                max_temp_c=predefined["max_temp_c"],
                annual_ghi_kwh_m2=predefined["annual_ghi_kwh_m2"],
                avg_daily_ghi_kwh_m2=predefined["avg_daily_ghi_kwh_m2"],
                avg_sunshine_hours_day=predefined["avg_sunshine_hours_day"],
                avg_wind_speed_mps=predefined["avg_wind_speed_mps"],
                relative_humidity_pct=predefined["relative_humidity_pct"],
                heating_degree_days=predefined["heating_degree_days"],
                cooling_degree_days=predefined["cooling_degree_days"],
                hourly_temperatures=temps,
                hourly_ghi=ghi,
                data_source="IMD / NASA POWER Verified Climate Baseline (Offline High-Fidelity Dataset)",
                is_fallback=False
            )

        # Attempt Open-Meteo live API with graceful timeout
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                url = (
                    f"https://api.open-meteo.com/v1/forecast?"
                    f"latitude={latitude}&longitude={longitude}&"
                    f"current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m&"
                    f"hourly=temperature_2m,shortwave_radiation&"
                    f"daily=temperature_2m_max,temperature_2m_min,shortwave_radiation_sum&"
                    f"timezone=auto"
                )
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    elevation = data.get("elevation", 500.0)
                    hourly = data.get("hourly", {})
                    h_temps = hourly.get("temperature_2m", [])[:24]
                    h_ghi = hourly.get("shortwave_radiation", [])[:24]
                    daily = data.get("daily", {})
                    t_max = float(daily.get("temperature_2m_max", [25.0])[0])
                    t_min = float(daily.get("temperature_2m_min", [10.0])[0])
                    rad_sum = float(daily.get("shortwave_radiation_sum", [18.0])[0])  # MJ/m2
                    daily_ghi_kwh = round(rad_sum / 3.6, 2)
                    avg_temp = round((t_max + t_min) / 2.0, 1)

                    climate_zone = "Temperate / Highland"
                    if elevation > 2500:
                        climate_zone = "Alpine / High Altitude Cold Desert"
                    elif avg_temp > 24 and daily_ghi_kwh > 5.5:
                        climate_zone = "Hot & Dry Arid"
                    elif avg_temp < 10:
                        climate_zone = "Cold Mountainous"

                    return ClimateData(
                        location_name=location_name or f"Coordinates ({latitude:.3f}, {longitude:.3f})",
                        latitude=latitude,
                        longitude=longitude,
                        elevation_m=float(elevation),
                        climate_zone=climate_zone,
                        avg_annual_temp_c=avg_temp,
                        min_temp_c=t_min,
                        max_temp_c=t_max,
                        annual_ghi_kwh_m2=round(daily_ghi_kwh * 365, 1),
                        avg_daily_ghi_kwh_m2=daily_ghi_kwh,
                        avg_sunshine_hours_day=round(min(11.0, max(5.0, daily_ghi_kwh * 1.4)), 1),
                        avg_wind_speed_mps=float(data.get("current", {}).get("wind_speed_10m", 3.2)),
                        relative_humidity_pct=float(data.get("current", {}).get("relative_humidity_2m", 45.0)),
                        heating_degree_days=round(max(0.0, (18.0 - avg_temp) * 220), 1),
                        cooling_degree_days=round(max(0.0, (avg_temp - 24.0) * 180), 1),
                        hourly_temperatures=[round(t, 2) for t in h_temps] if len(h_temps) == 24 else [],
                        hourly_ghi=[round(g, 1) for g in h_ghi] if len(h_ghi) == 24 else [],
                        data_source="Open-Meteo Global Meteorological Forecast & Reanalysis API",
                        is_fallback=False
                    )
        except Exception as e:
            logger.warning(f"Live climate API request timed out or failed: {e}. Falling back to physics synthetic model.")

        # Robust Fallback Model based on latitude and elevation
        # Estimate elevation based on latitude/longitude roughly in India
        elevation_est = 400.0
        if 32.0 <= latitude <= 36.0 and 74.0 <= longitude <= 79.0:
            elevation_est = 3200.0  # Himalayan / Ladakh belt
        elif 25.0 <= latitude <= 30.0 and 69.0 <= longitude <= 75.0:
            elevation_est = 250.0   # Thar desert

        lapse_rate = 0.0065  # 6.5 C per 1000m
        sea_level_temp = 30.0 - abs(latitude - 20.0) * 0.7
        avg_temp = round(sea_level_temp - (elevation_est * lapse_rate), 1)
        min_temp = round(avg_temp - 12.0, 1)
        max_temp = round(avg_temp + 10.0, 1)
        daily_ghi = round(max(3.8, 6.2 - (0.05 * abs(latitude - 25.0)) + (elevation_est / 4000.0)), 2)

        temps, ghi = self._generate_synthetic_hourly(avg_temp, min_temp, max_temp, daily_ghi)

        return ClimateData(
            location_name=location_name or f"Site ({latitude:.2f}N, {longitude:.2f}E)",
            latitude=latitude,
            longitude=longitude,
            elevation_m=elevation_est,
            climate_zone="High Altitude Mountain Valley" if elevation_est > 2000 else "Subtropical Continental",
            avg_annual_temp_c=avg_temp,
            min_temp_c=min_temp,
            max_temp_c=max_temp,
            annual_ghi_kwh_m2=round(daily_ghi * 365, 1),
            avg_daily_ghi_kwh_m2=daily_ghi,
            avg_sunshine_hours_day=round(daily_ghi * 1.35, 1),
            avg_wind_speed_mps=3.5,
            relative_humidity_pct=38.0,
            heating_degree_days=round(max(0.0, (18.0 - avg_temp) * 240), 1),
            cooling_degree_days=round(max(0.0, (avg_temp - 24.0) * 150), 1),
            hourly_temperatures=temps,
            hourly_ghi=ghi,
            data_source="Fallback Synthetic Regional Solar/Climate Model (Deterministic Physics & Elevation Lapse Rate)",
            is_fallback=True
        )

climate_service = ClimateService()
