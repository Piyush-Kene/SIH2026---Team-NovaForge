import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from typing import Dict, Any

class ReportGenerator:
    """
    Automated Engineering & Feasibility PDF Report Generator for GEOTHERM SHIELD.
    """

    def generate_pdf_report(self, data: Dict[str, Any]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()
        primary_color = colors.HexColor("#0f3460")
        accent_color = colors.HexColor("#00adb5")
        dark_neutral = colors.HexColor("#1a1a2e")

        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=primary_color,
            spaceAfter=6
        )

        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#555555"),
            spaceAfter=14
        )

        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=13,
            leading=16,
            textColor=accent_color,
            spaceBefore=12,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=9,
            leading=13,
            textColor=dark_neutral
        )

        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Italic'],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#777777"),
            spaceBefore=14
        )

        elements = []

        # Header Title
        elements.append(Paragraph("GEOTHERM SHIELD", title_style))
        elements.append(Paragraph("Climate-Aware Passive Shelter & Solar Optimization Engineering Report — SIH26051", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=4, spaceAfter=12))

        # Location & Climate Metadata Table
        loc_name = data.get("location_name", "Leh, Ladakh")
        lat = data.get("latitude", 34.1526)
        lon = data.get("longitude", 77.5771)
        elev = data.get("elevation_m", 3524.0)

        elements.append(Paragraph("1. Geographic & Microclimate Profile", section_heading))
        geo_table_data = [
            ["Location", loc_name, "Latitude / Longitude", f"{lat:.4f}°N, {lon:.4f}°E"],
            ["Elevation", f"{elev} m AMSL", "Climate Classification", data.get("climate_zone", "Alpine Cold Semi-Arid")],
            ["Annual GHI", f"{data.get('annual_ghi_kwh_m2', 2180)} kWh/m²", "Solar Suitability Score", f"{data.get('solar_score', 94.0)} / 100"],
            ["Diurnal Temperature", f"{data.get('min_temp_c', -18.2)}°C to {data.get('max_temp_c', 28.5)}°C", "Atmospheric Transparency", "High Direct-Normal Beam (High-Altitude Bonus)"]
        ]

        t_geo = Table(geo_table_data, colWidths=[110, 150, 120, 150])
        t_geo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8f9fa")),
            ('TEXTCOLOR', (0, 0), (-1, -1), dark_neutral),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_geo)
        elements.append(Spacer(1, 10))

        # Thermal Simulation & Passive Design Results
        elements.append(Paragraph("2. 24-Hour Passive Thermal Simulation Analysis", section_heading))
        therm_data = [
            ["Thermal Comfort Score", f"{data.get('thermal_score', 91.2)} / 100 (GeoTherm Index)", "Minimum Indoor Temp", f"{data.get('min_indoor_temp_c', 16.4)}°C"],
            ["Peak Indoor Temp", f"{data.get('peak_indoor_temp_c', 23.8)}°C", "Average 24h Indoor Temp", f"{data.get('avg_indoor_temp_c', 19.8)}°C"],
            ["High Heat Loss Critical Window", data.get("high_heat_loss_period", "02:00–05:00"), "Daily Thermal Stability Index", f"{data.get('thermal_stability_index', 86.5)}%"],
            ["Active Heating Requirement", f"{data.get('heating_energy_required_kwh_day', 6.2)} kWh/day", "Primary Wall Envelope", data.get("wall_material", "Insulated Polyurethane Sandwich Panel")]
        ]
        t_therm = Table(therm_data, colWidths=[130, 130, 130, 140])
        t_therm.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0f7f8")),
            ('TEXTCOLOR', (0, 0), (-1, -1), dark_neutral),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#c2e0e3")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_therm)
        elements.append(Spacer(1, 10))

        # Solar PV & Optimized Generation
        elements.append(Paragraph("3. Solar Capacity & Energy Offset Configuration", section_heading))
        solar_data = [
            ["Installed Solar Capacity", f"{data.get('solar_capacity_kw', 10.0)} kWp", "Recommended Tilt Angle", f"{data.get('optimal_tilt_deg', 35.0)}° (Facing True South)"],
            ["Estimated Annual PV Generation", f"{data.get('annual_solar_generation_kwh', 15500):,.0f} kWh", "Capacity Utilization Factor (CUF)", "17.8% (Cold Climate Amplified)"],
            ["Annual Carbon (CO2) Offset", f"{data.get('co2_tonnes_annual', 11.0)} Tonnes", "Roof Placement Footprint", f"{data.get('roof_area_m2', 48.0)} m² Zone A Roof"]
        ]
        t_solar = Table(solar_data, colWidths=[130, 130, 130, 140])
        t_solar.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fefbf3")),
            ('TEXTCOLOR', (0, 0), (-1, -1), dark_neutral),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#fae1b8")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_solar)
        elements.append(Spacer(1, 10))

        # Financial Investment & Government Subsidy
        elements.append(Paragraph("4. Project Financials & Government Support Assessment", section_heading))
        fin_data = [
            ["Estimated Total Project Cost", f"₹{data.get('total_project_cost_inr', 1250000):,.0f}", "Applicable Government Scheme", "MNRE Ladakh Special / PM Surya Ghar"],
            ["Potential Government Support", f"₹{data.get('estimated_subsidy_inr', 350000):,.0f}", "Estimated Net Capital Outlay", f"₹{data.get('net_cost_inr', 900000):,.0f}"],
            ["Annual Monetary Benefit", f"₹{data.get('annual_benefit_inr', 185000):,.0f}", "Simple Payback Period", f"{data.get('payback_years', 4.8)} Years"],
            ["Diesel Fuel Offset", f"{data.get('diesel_offset_liters', 4300):,.0f} Liters/yr (DG genset replacement)", "10-Year Net Economic Return", f"₹{data.get('ten_year_net_inr', 1650000):,.0f}"]
        ]
        t_fin = Table(fin_data, colWidths=[130, 130, 130, 140])
        t_fin.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f4f9f4")),
            ('TEXTCOLOR', (0, 0), (-1, -1), dark_neutral),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cde8cd")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_fin)
        elements.append(Spacer(1, 12))

        # Recommendations & Engineering Notes
        elements.append(Paragraph("5. Recommended Architecture Summary", section_heading))
        summary_text = (
            f"<b>Configuration:</b> Direct South Orientation (180° Azimuth) with high-efficiency polyurethane sandwich envelope "
            f"(15 cm wall, 12 cm insulation) and 35° pitched roof. Maximizes passive solar capture through southern apertures, "
            f"yielding an indoor comfort stability of <b>{data.get('thermal_score', 91.2)}/100</b> under extreme sub-zero exterior temperatures. "
            f"Coupled with <b>{data.get('solar_capacity_kw', 10.0)} kWp</b> rooftop solar array, the installation satisfies off-grid electrical "
            f"demands while displacing high-cost kerosene/diesel generator logistics."
        )
        elements.append(Paragraph(summary_text, body_style))

        # Disclaimer
        disclaimer_text = (
            "<b>Engineering Disclaimer:</b> This report is generated by GeoTherm Shield (SIH26051 Decision Support System) as a "
            "preliminary software-derived estimate utilizing numerical physics models, empirical transposition radiation algorithms, "
            "and configurable subsidy data. It is not an engineering certification. All structural, electrical, and subsidy parameters "
            "must be verified on-site by accredited civil/solar engineers and relevant statutory authorities prior to construction."
        )
        elements.append(Paragraph(disclaimer_text, disclaimer_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

report_generator = ReportGenerator()
