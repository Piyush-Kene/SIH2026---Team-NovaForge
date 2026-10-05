"""
Configurable Materials Database for Thermal & Structural Envelopes
Properties include:
- thermal_conductivity_w_mk (k)
- density_kg_m3 (rho)
- specific_heat_j_kgk (cp)
- embodied_carbon_kg_co2_kg
- cost_per_m2_at_standard_thickness_inr
"""

MATERIALS_DATABASE = {
    "insulated_sandwich_panel": {
        "id": "insulated_sandwich_panel",
        "name": "Polyurethane/PIR Sandwich Panel",
        "category": "High-Efficiency Composite",
        "default_thickness_m": 0.15,
        "thermal_conductivity_w_mk": 0.024,
        "density_kg_m3": 40.0,
        "specific_heat_j_kgk": 1400.0,
        "thermal_mass_rating": "Medium",
        "u_value_default": 0.16,
        "cost_per_m2_inr": 2800.0,
        "durability_years": 25,
        "suitability": "Extreme cold, rapid military/disaster deployment, high insulation"
    },
    "aerated_autoclaved_concrete": {
        "id": "aerated_autoclaved_concrete",
        "name": "Autoclaved Aerated Concrete (AAC Block)",
        "category": "Masonry & Thermal Mass",
        "default_thickness_m": 0.20,
        "thermal_conductivity_w_mk": 0.16,
        "density_kg_m3": 550.0,
        "specific_heat_j_kgk": 1050.0,
        "thermal_mass_rating": "High",
        "u_value_default": 0.72,
        "cost_per_m2_inr": 1850.0,
        "durability_years": 50,
        "suitability": "Moderate to cold climates with high thermal storage needs"
    },
    "composite_aerogel_panel": {
        "id": "composite_aerogel_panel",
        "name": "Aerogel Vacuum Insulated Panel (VIP)",
        "category": "Advanced Space/Defense Grade",
        "default_thickness_m": 0.08,
        "thermal_conductivity_w_mk": 0.014,
        "density_kg_m3": 160.0,
        "specific_heat_j_kgk": 1000.0,
        "thermal_mass_rating": "Low",
        "u_value_default": 0.17,
        "cost_per_m2_inr": 5500.0,
        "durability_years": 30,
        "suitability": "Sub-zero Himalayan altitude, weight-constrained air-transportable shelters"
    },
    "rammed_earth_stabilized": {
        "id": "rammed_earth_stabilized",
        "name": "Stabilized Rammed Earth (Trombe Wall Variant)",
        "category": "Indigenous Passive Solar Mass",
        "default_thickness_m": 0.35,
        "thermal_conductivity_w_mk": 0.85,
        "density_kg_m3": 1900.0,
        "specific_heat_j_kgk": 1260.0,
        "thermal_mass_rating": "Ultra High",
        "u_value_default": 1.60,
        "cost_per_m2_inr": 1200.0,
        "durability_years": 60,
        "suitability": "High diurnal swing regions (Ladakh, Spiti, Thar desert), solar passive capture"
    },
    "timber_cross_laminated": {
        "id": "timber_cross_laminated",
        "name": "Cross-Laminated Timber (CLT)",
        "category": "Bio-Composite & Low Carbon",
        "default_thickness_m": 0.12,
        "thermal_conductivity_w_mk": 0.13,
        "density_kg_m3": 500.0,
        "specific_heat_j_kgk": 1600.0,
        "thermal_mass_rating": "Medium-High",
        "u_value_default": 0.95,
        "cost_per_m2_inr": 3200.0,
        "durability_years": 40,
        "suitability": "Eco-sensitive high altitude, seismic-resistant modular structure"
    },
    "standard_brick_masonry": {
        "id": "standard_brick_masonry",
        "name": "Burnt Clay Brick Masonry with Plaster",
        "category": "Conventional Masonry",
        "default_thickness_m": 0.23,
        "thermal_conductivity_w_mk": 0.81,
        "density_kg_m3": 1800.0,
        "specific_heat_j_kgk": 840.0,
        "thermal_mass_rating": "High",
        "u_value_default": 2.10,
        "cost_per_m2_inr": 1400.0,
        "durability_years": 45,
        "suitability": "Temperate plains and baseline comparative benchmarking"
    }
}

INSULATION_MATERIALS_DATABASE = {
    "rock_wool": {
        "id": "rock_wool",
        "name": "Mineral Rock Wool Blanket / Board",
        "thermal_conductivity_w_mk": 0.038,
        "density_kg_m3": 60.0,
        "specific_heat_j_kgk": 840.0,
        "fire_resistance": "Class A1 (Non-combustible)",
        "cost_per_m2_100mm_inr": 650.0
    },
    "xps_extruded_polystyrene": {
        "id": "xps_extruded_polystyrene",
        "name": "Extruded Polystyrene (XPS)",
        "thermal_conductivity_w_mk": 0.029,
        "density_kg_m3": 35.0,
        "specific_heat_j_kgk": 1450.0,
        "fire_resistance": "Self-extinguishing Class B1",
        "cost_per_m2_100mm_inr": 820.0
    },
    "sheep_wool_local": {
        "id": "sheep_wool_local",
        "name": "Treated Himalayan Sheep Wool Insulation",
        "thermal_conductivity_w_mk": 0.039,
        "density_kg_m3": 25.0,
        "specific_heat_j_kgk": 1800.0,
        "fire_resistance": "Naturally flame-retardant (treated)",
        "cost_per_m2_100mm_inr": 500.0
    }
}

GOVERNMENT_SUBSIDY_DATABASE = [
    {
        "id": "pm_surya_ghar",
        "scheme_name": "PM Surya Ghar: Muft Bijli Yojana",
        "administering_body": "Ministry of New and Renewable Energy (MNRE), Govt of India",
        "state_or_ut": "All India",
        "eligible_categories": ["civilian_residential", "community_shelters"],
        "max_capacity_kw": 3.0,
        "subsidy_formula_description": "₹33,000 for 1 kW; ₹66,000 for 2 kW; ₹78,000 for 3 kW and above",
        "effective_date": "2024-02-15",
        "last_verified_date": "2026-03-01",
        "portal_url": "https://pmsuryaghar.gov.in",
        "base_rate_per_kw": 33000.0,
        "cap_amount_inr": 78000.0,
        "active": True
    },
    {
        "id": "mnre_ladakh_special",
        "scheme_name": "MNRE High Altitude Border & Himalayan Solar Cold-Desert Mission",
        "administering_body": "MNRE & Ladakh Autonomous Hill Development Council (LAHDC)",
        "state_or_ut": "Ladakh",
        "eligible_categories": ["defense_research", "remote_station", "civilian_residential"],
        "max_capacity_kw": 50.0,
        "subsidy_formula_description": "50% capital subsidy on hybrid battery-integrated solar microgrids for border and remote mountain facilities",
        "effective_date": "2023-08-01",
        "last_verified_date": "2026-02-15",
        "portal_url": "https://mnre.gov.in",
        "capital_subsidy_pct": 0.50,
        "cap_amount_inr": 350000.0,
        "active": True
    },
    {
        "id": "drdo_remote_shelter_grant",
        "scheme_name": "Defense Off-Grid Habitability & Passive Shelter R&D Incentive",
        "administering_body": "DRDO DIHAR / DTRL Sustainable High-Altitude Habitat Program",
        "state_or_ut": "All India",
        "eligible_categories": ["defense_research", "remote_station"],
        "max_capacity_kw": 100.0,
        "subsidy_formula_description": "35% equipment subsidy + zero-import tariff offset on aerogel composite envelopes and bifacial solar PV",
        "effective_date": "2024-01-10",
        "last_verified_date": "2026-01-20",
        "portal_url": "https://drdo.gov.in",
        "capital_subsidy_pct": 0.35,
        "cap_amount_inr": 450000.0,
        "active": True
    }
]

PREDEFINED_LOCATIONS = {
    "leh_ladakh": {
        "name": "Leh, Ladakh",
        "state_ut": "Ladakh",
        "latitude": 34.1526,
        "longitude": 77.5771,
        "elevation_m": 3524.0,
        "climate_zone": "Cold Semi-Arid / High-Altitude Alpine",
        "avg_annual_temp_c": 5.4,
        "min_temp_c": -18.2,
        "max_temp_c": 28.5,
        "annual_ghi_kwh_m2": 2180.0,
        "avg_daily_ghi_kwh_m2": 5.97,
        "avg_sunshine_hours_day": 8.7,
        "avg_wind_speed_mps": 3.8,
        "relative_humidity_pct": 32.0,
        "heating_degree_days": 4650.0,
        "cooling_degree_days": 80.0,
        "solar_suitability_score": 94.0,
        "shelter_suitability_score": 88.5,
        "optimal_tilt_deg": 35.0,
        "recommended_orientation": "True South (180° Azimuth)",
        "terrain_type": "High-altitude mountain valley plateau",
        "typical_winter_day_temps": [-12.0, -14.0, -15.5, -16.0, -15.0, -13.5, -9.0, -4.0, 0.5, 3.5, 4.8, 5.2, 4.9, 3.8, 1.2, -1.5, -4.2, -6.5, -8.0, -9.5, -10.2, -11.0, -11.8, -12.2]
    },
    "srinagar": {
        "name": "Srinagar, Jammu & Kashmir",
        "state_ut": "Jammu & Kashmir",
        "latitude": 34.0837,
        "longitude": 74.7973,
        "elevation_m": 1585.0,
        "climate_zone": "Humid Subtropical (Montane/Temperate)",
        "avg_annual_temp_c": 13.5,
        "min_temp_c": -6.5,
        "max_temp_c": 32.0,
        "annual_ghi_kwh_m2": 1720.0,
        "avg_daily_ghi_kwh_m2": 4.71,
        "avg_sunshine_hours_day": 6.9,
        "avg_wind_speed_mps": 2.2,
        "relative_humidity_pct": 68.0,
        "heating_degree_days": 2850.0,
        "cooling_degree_days": 320.0,
        "solar_suitability_score": 82.0,
        "shelter_suitability_score": 85.0,
        "optimal_tilt_deg": 33.0,
        "recommended_orientation": "South (180°)",
        "terrain_type": "Intermontane valley basin",
        "typical_winter_day_temps": [-2.0, -3.0, -3.5, -4.0, -3.8, -2.5, 0.0, 3.0, 6.0, 8.5, 9.8, 10.2, 9.5, 8.0, 5.5, 3.2, 1.5, 0.5, -0.5, -1.0, -1.5, -1.8, -2.0, -2.2]
    },
    "delhi": {
        "name": "New Delhi, NCR",
        "state_ut": "Delhi",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "elevation_m": 216.0,
        "climate_zone": "Composite / Semi-Arid",
        "avg_annual_temp_c": 25.1,
        "min_temp_c": 4.5,
        "max_temp_c": 45.2,
        "annual_ghi_kwh_m2": 1940.0,
        "avg_daily_ghi_kwh_m2": 5.31,
        "avg_sunshine_hours_day": 7.8,
        "avg_wind_speed_mps": 2.6,
        "relative_humidity_pct": 54.0,
        "heating_degree_days": 650.0,
        "cooling_degree_days": 2100.0,
        "solar_suitability_score": 86.0,
        "shelter_suitability_score": 79.0,
        "optimal_tilt_deg": 28.0,
        "recommended_orientation": "South (180°)",
        "terrain_type": "Gangetic alluvial plain",
        "typical_winter_day_temps": [9.0, 8.2, 7.5, 6.8, 6.5, 7.0, 9.5, 13.0, 17.5, 20.0, 21.5, 22.0, 21.8, 20.5, 18.0, 15.5, 13.0, 11.5, 10.8, 10.2, 9.8, 9.5, 9.2, 9.0]
    },
    "jaisalmer": {
        "name": "Jaisalmer, Rajasthan",
        "state_ut": "Rajasthan",
        "latitude": 26.9157,
        "longitude": 70.9083,
        "elevation_m": 225.0,
        "climate_zone": "Hot and Dry Desert (Thar)",
        "avg_annual_temp_c": 27.2,
        "min_temp_c": 5.0,
        "max_temp_c": 48.0,
        "annual_ghi_kwh_m2": 2250.0,
        "avg_daily_ghi_kwh_m2": 6.16,
        "avg_sunshine_hours_day": 9.2,
        "avg_wind_speed_mps": 4.5,
        "relative_humidity_pct": 28.0,
        "heating_degree_days": 420.0,
        "cooling_degree_days": 2850.0,
        "solar_suitability_score": 97.0,
        "shelter_suitability_score": 83.0,
        "optimal_tilt_deg": 26.0,
        "recommended_orientation": "South-Southwest (195°)",
        "terrain_type": "Desert sand dunes and rocky ridges",
        "typical_winter_day_temps": [11.0, 10.0, 9.0, 8.5, 8.0, 8.5, 11.0, 15.0, 19.5, 23.0, 25.0, 25.5, 25.0, 23.5, 21.0, 18.0, 15.0, 13.5, 12.8, 12.0, 11.8, 11.5, 11.2, 11.0]
    },
    "pune": {
        "name": "Pune, Maharashtra",
        "state_ut": "Maharashtra",
        "latitude": 18.5204,
        "longitude": 73.8567,
        "elevation_m": 560.0,
        "climate_zone": "Warm and Semi-Arid / Deccan Plateau",
        "avg_annual_temp_c": 24.8,
        "min_temp_c": 9.0,
        "max_temp_c": 39.5,
        "annual_ghi_kwh_m2": 2020.0,
        "avg_daily_ghi_kwh_m2": 5.53,
        "avg_sunshine_hours_day": 8.1,
        "avg_wind_speed_mps": 2.8,
        "relative_humidity_pct": 52.0,
        "heating_degree_days": 180.0,
        "cooling_degree_days": 1650.0,
        "solar_suitability_score": 89.0,
        "shelter_suitability_score": 88.0,
        "optimal_tilt_deg": 19.0,
        "recommended_orientation": "South (180°)",
        "terrain_type": "Deccan volcanic plateau / Western Ghats rain-shadow",
        "typical_winter_day_temps": [14.0, 13.2, 12.5, 11.8, 11.5, 12.0, 14.5, 18.0, 23.0, 27.0, 29.2, 30.0, 29.5, 28.0, 25.0, 22.0, 19.0, 17.5, 16.5, 15.8, 15.2, 14.8, 14.4, 14.0]
    }
}
