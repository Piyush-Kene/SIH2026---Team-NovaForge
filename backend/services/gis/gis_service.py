from typing import List
from models.schemas import RankedLocationItem
from database.material_data import PREDEFINED_LOCATIONS

class GISRankingService:
    """
    Multi-Criteria GIS Site Suitability and Feasibility Ranking Service.
    """

    def rank_locations(self) -> List[RankedLocationItem]:
        items: List[RankedLocationItem] = []
        for key, loc in PREDEFINED_LOCATIONS.items():
            solar_score = loc["solar_suitability_score"]
            thermal_score = loc["shelter_suitability_score"]
            
            # Feasibility considerations: elevation, wind, access
            elev_penalty = max(0.0, (loc["elevation_m"] - 3000.0) * 0.003)
            feasibility = round(max(60.0, 95.0 - elev_penalty - (loc["avg_wind_speed_mps"] * 2.0)), 1)

            # Composite ranking score
            overall = round(
                0.40 * solar_score +
                0.35 * thermal_score +
                0.25 * feasibility,
                1
            )

            annual_yield = round(loc["annual_ghi_kwh_m2"] * 0.81, 1)

            summary = (
                f"High-altitude solar resource with {loc['avg_sunshine_hours_day']}h sunshine. "
                f"Requires high-thermal insulation envelope."
                if loc["elevation_m"] > 1500 else
                f"Temperate/warm climate with balanced heating & cooling requirements."
            )

            items.append(RankedLocationItem(
                rank=1,
                location_name=loc["name"],
                state_ut=loc["state_ut"],
                latitude=loc["latitude"],
                longitude=loc["longitude"],
                elevation_m=loc["elevation_m"],
                solar_score=solar_score,
                thermal_suitability_score=thermal_score,
                feasibility_score=feasibility,
                overall_rank_score=overall,
                annual_solar_yield_kwh_kw=annual_yield,
                climate_zone=loc["climate_zone"],
                recommendation_summary=summary
            ))

        items.sort(key=lambda x: x.overall_rank_score, reverse=True)
        for idx, item in enumerate(items, start=1):
            item.rank = idx

        return items

gis_service = GISRankingService()
