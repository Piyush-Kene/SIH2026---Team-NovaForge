import numpy as np
from typing import List, Dict, Any, Tuple
from models.schemas import ThermalSimulationRequest, ThermalSimulationResponse
from database.material_data import MATERIALS_DATABASE, INSULATION_MATERIALS_DATABASE
from services.climate.climate_service import climate_service

class ThermalSimulationEngine:
    """
    Dynamic 1D Lumped-Parameter Thermal Network (RC Equivalent Circuit).
    Models:
    - Envelope Conduction: Q_cond = sum(U_i * A_i * (T_out - T_in))
    - Window Solar Heat Gain (SHGC): Q_sol = A_win * GHI * SHGC * cos_factor
    - Infiltration / Ventilation: Q_vent = m_dot * Cp_air * (T_out - T_in)
    - Thermal Mass Capacitance: C * (dT_in / dt) = Q_cond + Q_sol + Q_vent + Q_int
    Solves 24-hour differential equations using Runge-Kutta 4th order (RK4) integration.
    """

    def _get_envelope_u_values(self, materials) -> Tuple[float, float, float, float]:
        # Wall U-value
        wall_mat = MATERIALS_DATABASE.get(materials.wall_material, MATERIALS_DATABASE["insulated_sandwich_panel"])
        ins_mat = INSULATION_MATERIALS_DATABASE.get(materials.insulation_material, INSULATION_MATERIALS_DATABASE["rock_wool"])

        # R = d1/k1 + d_ins/k_ins + R_si + R_se
        # Standard surface air film resistances: R_si = 0.13, R_se = 0.04 m2K/W
        r_wall_base = materials.wall_thickness_m / wall_mat["thermal_conductivity_w_mk"]
        r_ins = materials.insulation_thickness_m / ins_mat["thermal_conductivity_w_mk"]
        r_wall_total = r_wall_base + r_ins + 0.17
        u_wall = round(1.0 / max(0.1, r_wall_total), 3)

        # Roof U-value
        roof_mat = MATERIALS_DATABASE.get(materials.roof_material, MATERIALS_DATABASE["insulated_sandwich_panel"])
        r_roof_base = materials.roof_thickness_m / roof_mat["thermal_conductivity_w_mk"]
        r_roof_total = r_roof_base + r_ins + 0.14
        u_roof = round(1.0 / max(0.1, r_roof_total), 3)

        # Floor U-value (ground coupled with perimeter insulation)
        u_floor = 0.35 if "insulated" in materials.floor_material else 0.85

        # Thermal Capacitance per m2 floor area (J/K m2)
        # Concrete / Rammed earth has high density & specific heat
        cap_wall = wall_mat["density_kg_m3"] * wall_mat["specific_heat_j_kgk"] * materials.wall_thickness_m
        return u_wall, u_roof, u_floor, cap_wall

    async def run_24h_simulation(self, req: ThermalSimulationRequest) -> ThermalSimulationResponse:
        climate = await climate_service.get_climate_data(req.latitude, req.longitude, req.location_name)
        
        # Envelope Areas
        length = req.geometry.length_m
        width = req.geometry.width_m
        height = req.geometry.height_m
        floor_area = length * width
        volume = floor_area * height

        # Wall gross areas
        area_south_wall = length * height
        area_north_wall = length * height
        area_east_wall = width * height
        area_west_wall = width * height

        # Net opaque wall area
        total_window_area = (
            req.openings.window_area_south_m2 +
            req.openings.window_area_north_m2 +
            req.openings.window_area_east_m2 +
            req.openings.window_area_west_m2
        )
        total_wall_gross = 2 * (length + width) * height
        net_wall_area = max(10.0, total_wall_gross - total_window_area - req.openings.door_area_m2)

        # Roof area with pitch
        pitch_rad = np.radians(req.geometry.roof_angle_deg)
        roof_area = floor_area / np.cos(pitch_rad)

        u_wall, u_roof, u_floor, cap_wall_per_m2 = self._get_envelope_u_values(req.materials)
        u_win = req.openings.window_u_value
        u_door = 1.8  # Insulated draft-proofed door

        # Overall building heat loss coefficient UA (W/K)
        ua_envelope = (
            net_wall_area * u_wall +
            roof_area * u_roof +
            floor_area * u_floor +
            total_window_area * u_win +
            req.openings.door_area_m2 * u_door
        )

        # Infiltration & Ventilation heat loss rate (W/K): V * ACH / 3600 * rho_air * Cp_air
        # Air density ~1.05 kg/m3 at high altitude Leh, Cp ~ 1005 J/kg K => ~0.29 * V * ACH
        air_density = 1.225 * np.exp(-climate.elevation_m / 8500.0)
        h_vent = (volume * req.air_change_per_hour * air_density * 1005.0) / 3600.0

        total_ua = ua_envelope + h_vent

        # Lumped Thermal Capacitance C_tot (Joules / Kelvin)
        # Air thermal mass + internal walls/floors thermal mass
        c_air = volume * air_density * 1005.0
        c_structure = (net_wall_area * 0.4 + floor_area * 0.7) * cap_wall_per_m2
        c_total = max(5.0e5, c_air + c_structure)

        # 24-hour simulation vectors
        outside_temps = climate.hourly_temperatures if len(climate.hourly_temperatures) == 24 else [-10.0] * 24
        ghi_series = climate.hourly_ghi if len(climate.hourly_ghi) == 24 else [0.0] * 24

        # Initial indoor temperature: start near average external + 10C passive drift
        t_in = max(req.target_comfort_min_c - 4.0, np.mean(outside_temps) + 8.0)
        dt = 3600.0  # 1 hour timestep in seconds

        indoor_temps = []
        solar_gains = []
        heat_losses = []
        vent_losses = []
        net_flows = []

        def heat_derivative(t_curr, t_ext, q_sol, q_int):
            q_loss_env = ua_envelope * (t_ext - t_curr)
            q_loss_v = h_vent * (t_ext - t_curr)
            q_net = q_loss_env + q_loss_v + q_sol + q_int
            dt_dt = q_net / c_total
            return dt_dt, q_loss_env, q_loss_v, q_net

        for h in range(24):
            t_ext = outside_temps[h]
            ghi = ghi_series[h]

            # Solar gain through south windows (dominant in winter for passive heating)
            # Solar azimuth and incidence angle factor for vertical south aperture
            if 8 <= h <= 16 and ghi > 10:
                solar_factor = np.sin(np.pi * (h - 8) / 8.0)
                # Vertical south wall receives high radiation when winter sun is low in sky
                q_sol = (
                    req.openings.window_area_south_m2 * ghi * 1.25 * req.openings.window_shading_coefficient * solar_factor +
                    (req.openings.window_area_east_m2 + req.openings.window_area_west_m2) * ghi * 0.3 * req.openings.window_shading_coefficient
                )
            else:
                q_sol = 0.0

            q_int = req.internal_heat_gain_w

            # Runge-Kutta 4th Order numerical integration
            k1, _, _, _ = heat_derivative(t_in, t_ext, q_sol, q_int)
            k2, _, _, _ = heat_derivative(t_in + 0.5 * dt * k1, t_ext, q_sol, q_int)
            k3, _, _, _ = heat_derivative(t_in + 0.5 * dt * k2, t_ext, q_sol, q_int)
            k4, _, _, _ = heat_derivative(t_in + dt * k3, t_ext, q_sol, q_int)

            t_next = t_in + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

            # Record instantaneous flows at midpoint
            _, q_env, q_v, q_n = heat_derivative(t_in, t_ext, q_sol, q_int)

            indoor_temps.append(round(float(t_in), 2))
            solar_gains.append(round(float(q_sol), 1))
            heat_losses.append(round(float(abs(q_env)), 1))
            vent_losses.append(round(float(abs(q_v)), 1))
            net_flows.append(round(float(q_n), 1))

            t_in = t_next

        peak_t = round(float(np.max(indoor_temps)), 1)
        min_t = round(float(np.min(indoor_temps)), 1)
        avg_t = round(float(np.mean(indoor_temps)), 1)

        # Thermal comfort score (Comparative GeoTherm Index 0 - 100)
        # Ideal band: 19 - 23 deg C
        comfort_hours = sum(1 for t in indoor_temps if req.target_comfort_min_c <= t <= req.target_comfort_max_c)
        diurnal_swing = peak_t - min_t
        stability_score = max(0.0, 100.0 - diurnal_swing * 4.5)
        mean_deviation = abs(avg_t - 21.0)
        temp_score = max(0.0, 100.0 - mean_deviation * 6.0)
        comfort_fraction = (comfort_hours / 24.0) * 100.0

        overall_comfort_score = round(0.45 * comfort_fraction + 0.35 * temp_score + 0.20 * stability_score, 1)
        overall_comfort_score = max(10.0, min(99.0, overall_comfort_score))

        # Heating energy deficit if indoor drops below target_comfort_min_c
        deficit_kwh = sum(max(0.0, (req.target_comfort_min_c - t)) * total_ua * 1.0 for t in indoor_temps) / 1000.0

        # Critical night-time thermal risk detection
        cold_hazard = min_t < 10.0
        risk_level = "low"
        if min_t < 5.0:
            risk_level = "high_risk"
        elif min_t < 14.0:
            risk_level = "caution"

        # Identify worst cold period
        min_hour_idx = int(np.argmin(indoor_temps))
        start_h = max(0, min_hour_idx - 2)
        end_h = min(23, min_hour_idx + 1)
        period_str = f"{start_h:02d}:00–{end_h:02d}:00 (Min: {min_t}°C)"

        return ThermalSimulationResponse(
            hours=list(range(24)),
            outside_temperature_c=outside_temps,
            indoor_temperature_c=indoor_temps,
            solar_radiation_ghi_w_m2=ghi_series,
            solar_gain_w=solar_gains,
            envelope_heat_loss_w=heat_losses,
            ventilation_heat_loss_w=vent_losses,
            net_heat_flow_w=net_flows,
            peak_indoor_temp_c=peak_t,
            min_indoor_temp_c=min_t,
            avg_indoor_temp_c=avg_t,
            thermal_comfort_score=overall_comfort_score,
            thermal_stability_index=round(stability_score, 1),
            heating_energy_required_kwh_day=round(deficit_kwh, 2),
            high_heat_loss_period=period_str,
            status_summary=f"Envelope UA = {ua_envelope:.1f} W/K | Stability: {stability_score:.1f}% | Min Indoor: {min_t}°C",
            is_cold_hazard_predicted=cold_hazard,
            risk_level=risk_level,
            scientific_methodology="1D Dynamic Lumped RC Thermal Network with Runge-Kutta 4th Order Solvers & Transposition Solar Aperture Inflow"
        )

thermal_engine = ThermalSimulationEngine()
