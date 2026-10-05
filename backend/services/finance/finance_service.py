from typing import List, Dict, Any
from models.schemas import FinancialCalculationRequest, FinancialCalculationResponse
from database.material_data import GOVERNMENT_SUBSIDY_DATABASE

class FinanceService:
    """
    Project Cost, Government Scheme Eligibility, and Multi-Year Financial Payback Engine.
    """

    def calculate_financials(self, req: FinancialCalculationRequest) -> FinancialCalculationResponse:
        # Solar PV Cost Model (Standard Indian MNRE benchmark: ~₹48,000 to ₹58,000 per kW for high-altitude/bifacial)
        kw = req.system_capacity_kw
        solar_equipment_cost = kw * 38000.0  # Panels, Inverter, Protection
        solar_installation_cost = kw * 14000.0  # Cold-region structural mounting, ballast, cabling

        # Shelter Construction Cost Model
        # Standard composite thermal shelter costs ~₹14,000 to ₹18,000 per m2 floor area
        shelter_cost = req.shelter_floor_area_m2 * 16500.0

        total_project_cost = round(solar_equipment_cost + solar_installation_cost + shelter_cost, 2)

        # Subsidy / Grant Evaluation
        applicable_schemes = []
        total_support = 0.0

        for scheme in GOVERNMENT_SUBSIDY_DATABASE:
            if not scheme["active"]:
                continue

            matches_cat = (
                "All India" in scheme["state_or_ut"] or
                req.state_or_ut.lower() in scheme["state_or_ut"].lower()
            )
            matches_user = (
                req.user_category in scheme["eligible_categories"] or
                "civilian_residential" in scheme["eligible_categories"]
            )

            if matches_cat and matches_user:
                est_amount = 0.0
                if "base_rate_per_kw" in scheme:
                    eligible_kw = min(kw, scheme["max_capacity_kw"])
                    est_amount = eligible_kw * scheme["base_rate_per_kw"]
                    if "cap_amount_inr" in scheme:
                        est_amount = min(est_amount, scheme["cap_amount_inr"])
                elif "capital_subsidy_pct" in scheme:
                    eligible_pv_cost = solar_equipment_cost + solar_installation_cost
                    est_amount = eligible_pv_cost * scheme["capital_subsidy_pct"]
                    if "cap_amount_inr" in scheme:
                        est_amount = min(est_amount, scheme["cap_amount_inr"])

                if est_amount > 0:
                    applicable_schemes.append({
                        "id": scheme["id"],
                        "name": scheme["scheme_name"],
                        "authority": scheme["administering_body"],
                        "estimated_benefit_inr": round(est_amount, 2),
                        "formula": scheme["subsidy_formula_description"],
                        "portal": scheme["portal_url"],
                        "verified_date": scheme["last_verified_date"]
                    })
                    total_support += est_amount

        # Support capped to not exceed 60% of total solar expenditure
        total_support = min(total_support, (solar_equipment_cost + solar_installation_cost) * 0.70)
        net_payable = max(0.0, total_project_cost - total_support)

        # Energy Generation & Savings
        # Average yield in high altitude Ladakh is ~1550 kWh / kWp
        annual_kwh_gen = kw * 1550.0
        electricity_savings = annual_kwh_gen * req.grid_tariff_inr_kwh

        # Diesel Generator Replacement in remote/defense outposts
        # In Ladakh/Himalayas, DG sets consume ~0.30 liters diesel per kWh generated.
        # High-altitude diesel transport & kerosene blend logistics cost ~₹110/liter!
        diesel_offset_liters = 0.0
        diesel_savings = 0.0
        if req.diesel_generator_replacement:
            diesel_offset_liters = round(annual_kwh_gen * 0.28, 1)
            diesel_savings = round(diesel_offset_liters * 105.0, 2)

        total_annual_benefit = round(electricity_savings + diesel_savings, 2)

        # Payback period calculation
        solar_net_capex = max(1000.0, (solar_equipment_cost + solar_installation_cost) - total_support)
        payback_years = round(solar_net_capex / max(1000.0, total_annual_benefit), 1)

        # 10-Year cumulative cashflow with 0.7% annual PV degradation and 3% energy inflation
        ten_year_savings = 0.0
        for year in range(1, 11):
            deg_factor = (1.0 - 0.007)**year
            inflation_factor = (1.0 + 0.03)**year
            ten_year_savings += total_annual_benefit * deg_factor * inflation_factor

        ten_year_net = round(ten_year_savings - solar_net_capex, 2)
        co2_10y = round((annual_kwh_gen * 0.71 * 10) / 1000.0, 1)

        return FinancialCalculationResponse(
            equipment_cost_inr=round(solar_equipment_cost, 2),
            installation_and_civil_cost_inr=round(solar_installation_cost, 2),
            shelter_construction_cost_inr=round(shelter_cost, 2),
            total_project_cost_inr=total_project_cost,
            applicable_schemes=applicable_schemes,
            total_estimated_support_inr=round(total_support, 2),
            net_payable_cost_inr=round(net_payable, 2),
            annual_electricity_savings_inr=round(electricity_savings, 2),
            diesel_fuel_offset_liters_annual=diesel_offset_liters,
            diesel_fuel_savings_inr_annual=diesel_savings,
            total_annual_monetary_benefit_inr=total_annual_benefit,
            simple_payback_years=payback_years,
            ten_year_net_savings_inr=ten_year_net,
            co2_reduction_tonnes_10y=co2_10y,
            disclaimer="Estimated figures for preliminary feasibility. Official subsidies are subject to administrative scrutiny, sanction orders, and discom grid feasibility approvals."
        )

finance_service = FinanceService()
