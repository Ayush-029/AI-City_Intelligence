from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

model = joblib.load(BASE_DIR / "models" / "aqi_xgboost_model.joblib")
city_encoder = joblib.load(BASE_DIR / "models" / "aqi_city_encoder.joblib")
features = joblib.load(BASE_DIR / "models" / "aqi_features.joblib")


def get_aqi_category(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    return "Severe"


def predict_air_quality(data):
    if data.city not in city_encoder.classes_:
        raise ValueError(f"Unsupported city: {data.city}")

    timestamp = data.datetime

    input_data = pd.DataFrame([{
        "City": city_encoder.transform([data.city])[0],
        "PM2.5": data.pm25,
        "PM10": data.pm10,
        "NO": data.no,
        "NO2": data.no2,
        "NOx": data.nox,
        "NH3": data.nh3,
        "CO": data.co,
        "SO2": data.so2,
        "O3": data.o3,
        "Year": timestamp.year,
        "Month": timestamp.month,
        "Day": timestamp.day,
        "Hour": timestamp.hour,
        "Day_of_Week": timestamp.weekday()
    }])

    input_data = input_data.reindex(columns=features)

    predicted_aqi = float(model.predict(input_data)[0])
    predicted_aqi = max(0, round(predicted_aqi))

    return {
        "predicted_aqi": predicted_aqi,
        "aqi_category": get_aqi_category(predicted_aqi),
        "risk_score": min(100, round((predicted_aqi / 500) * 100))
    }