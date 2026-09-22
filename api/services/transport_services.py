from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

bundle = joblib.load(
    BASE_DIR / "models" / "transport_demand_model.joblib"
)

transport_model = bundle["model"]
features = bundle["features"]


def _request_data(data):
    return data.model_dump() if hasattr(data, "model_dump") else data.dict()


def _valid_cities():
    preprocessor = transport_model.named_steps["preprocessor"]
    encoder = preprocessor.named_transformers_["city_encoder"]
    return set(encoder.categories_[0])


def get_crowd_level(passengers):
    if passengers < 5000:
        return "LOW"
    elif passengers < 20000:
        return "MEDIUM"
    return "HIGH"


def get_recommendation(crowd_level):
    if crowd_level == "LOW":
        return "Normal service frequency is sufficient."
    elif crowd_level == "MEDIUM":
        return (
            "Moderate passenger demand expected. "
            "Monitor peak-hour routes and consider additional trips."
        )
    return (
        "High passenger demand expected. "
        "Add buses and increase service frequency."
    )


def predict_transport(data):
    if data.city not in _valid_cities():
        raise ValueError(f"Unsupported city: {data.city}")

    input_data = pd.DataFrame([_request_data(data)])

    # Maintain the same input columns and feature order used in training.
    input_data = input_data.reindex(columns=features)

    prediction = float(transport_model.predict(input_data)[0])
    prediction = max(0, round(prediction))

    crowd_level = get_crowd_level(prediction)

    return {
        "predicted_daily_passengers": prediction,
        "crowd_level": crowd_level,
        "recommendation": get_recommendation(crowd_level)
    }
