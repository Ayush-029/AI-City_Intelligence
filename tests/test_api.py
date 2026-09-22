from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_health_reports_all_modules():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["modules"] == ["traffic", "air_quality", "waste", "transport"]


def test_traffic_prediction():
    response = client.post("/predict", json={
        "temp": 288, "rain_1h": 0, "snow_1h": 0, "clouds_all": 40,
        "hour": 8, "day_of_week": 0, "month": 6, "is_weekend": 0,
    })
    assert response.status_code == 200
    assert response.json()["predicted_traffic_volume"] >= 0


def test_air_quality_prediction():
    response = client.post("/air-quality/predict", json={
        "city": "Bangalore", "datetime": "2020-01-01T10:00:00",
        "PM2.5": 50, "PM10": 80, "NO": 10, "NO2": 25, "NOx": 30,
        "NH3": 15, "CO": 0.8, "SO2": 12, "O3": 35,
    })
    assert response.status_code == 200
    assert "predicted_aqi" in response.json()


def test_waste_rejects_unknown_city():
    response = client.post("/waste/predict", json={
        "city": "Unknown City", "waste_type": "Plastic", "recycling_rate": 50,
        "population_density": 1000, "municipal_efficiency_score": 5,
        "disposal_method": "Recycling", "awareness_campaigns_count": 2,
        "landfill_capacity_tons": 10000, "waste_reduction_initiatives": 5,
        "industrial_symbiosis_index": 5, "community_participation_score": 5,
        "green_technology_adoption": 5, "recycling_infrastructure_rating": 50,
    })
    assert response.status_code == 400


def test_transport_rejects_unknown_city():
    response = client.post("/transport/predict", json={
        "city": "Unknown City", "year_start": 2018, "daily_trips": 100,
        "daily_trip_length_km": 500, "total_buses": 20, "bus_terminals": 1,
        "bus_stands": 2, "bus_stops": 15,
    })
    assert response.status_code == 400
