import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"

def test_climate_leh():
    res = client.get("/climate?latitude=34.1526&longitude=77.5771")
    assert res.status_code == 200
    data = res.json()
    assert "Ladakh" in data["location_name"] or "34.15" in data["location_name"]
    assert len(data["hourly_temperatures"]) == 24

def test_solar_potential():
    payload = {"latitude": 34.1526, "longitude": 77.5771, "slope_deg": 0.0}
    res = client.post("/solar/potential", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["solar_potential_score"] > 80.0

def test_thermal_simulation():
    payload = {
        "location_name": "Leh, Ladakh",
        "latitude": 34.1526,
        "longitude": 77.5771
    }
    res = client.post("/thermal/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["indoor_temperature_c"]) == 24
    assert data["thermal_comfort_score"] > 0

def test_optimizer():
    payload = {
        "location_name": "Leh, Ladakh",
        "latitude": 34.1526,
        "longitude": 77.5771,
        "floor_area_m2": 48.0
    }
    res = client.post("/optimizer/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["top_designs"]) == 3

def test_finance():
    payload = {
        "system_capacity_kw": 10.0,
        "shelter_floor_area_m2": 48.0,
        "state_or_ut": "Ladakh"
    }
    res = client.post("/financial/calculate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_project_cost_inr"] > 0
    assert len(data["applicable_schemes"]) > 0

def test_report_pdf():
    payload = {
        "location_name": "Leh, Ladakh",
        "latitude": 34.1526,
        "longitude": 77.5771,
        "solar_capacity_kw": 10.0
    }
    res = client.post("/reports/generate", json=payload)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert len(res.content) > 1000
