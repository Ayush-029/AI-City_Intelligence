from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "models" / "traffic_xgboost_model.joblib"

model = joblib.load(MODEL_PATH)


def get_time_period(hour: int) -> str:

    if 5 <= hour < 12:
        return "Morning"

    elif 12 <= hour < 17:
        return "Afternoon"

    elif 17 <= hour < 21:
        return "Evening"

    else:
        return "Night"


def predict_traffic(data):
    time_period = get_time_period(data.hour)

    time_period_mapping = {
        "Afternoon": 0,
        "Evening": 1,
        "Morning": 2,
        "Night": 3
    }

    input_data = pd.DataFrame([{
        "temp": data.temp,
        "rain_1h": data.rain_1h,
        "snow_1h": data.snow_1h,
        "clouds_all": data.clouds_all,
        "hour": data.hour,
        "day_of_week": data.day_of_week,
        "month": data.month,
        "is_weekend": data.is_weekend,
        "is_rush_hour": int(data.hour in [7, 8, 9, 16, 17, 18]),
        "time_period": time_period_mapping[time_period]
    }])

    # Force exact feature order used during model training
    expected_features = model.get_booster().feature_names
    input_data = input_data.reindex(columns=expected_features)

    prediction = model.predict(input_data)[0]

    if prediction < 2000:
        congestion_level = "LOW"
    elif prediction < 4000:
        congestion_level = "MEDIUM"
    else:
        congestion_level = "HIGH"

    risk_score = min(100, round((prediction / 6000) * 100))

    if congestion_level == "LOW":
        recommendation = "Traffic is normal. No immediate action required."
    elif congestion_level == "MEDIUM":
        recommendation = "Moderate traffic. Consider an alternate route."
    else:
        recommendation = "High congestion. Consider alternate routes and avoid peak traffic."

    return {
        "predicted_traffic_volume": round(float(prediction)),
        "congestion_level": congestion_level,
        "risk_score": risk_score,
        "time_period": time_period,
        "recommendation": recommendation
    }