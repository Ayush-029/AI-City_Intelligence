from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

bundle = joblib.load(
    BASE_DIR / "models" / "waste_xgboost_model.joblib"
)

model = bundle["model"]
preprocessor = bundle["preprocessor"]
features = bundle["features"]


def _request_data(data):
    return data.model_dump() if hasattr(data, "model_dump") else data.dict()


def _valid_categories():
    categories = preprocessor.named_transformers_["categorical"].categories_
    return {
        "city": set(categories[0]),
        "waste_type": set(categories[1]),
        "disposal_method": set(categories[2]),
    }


def get_collection_priority(predicted_waste):
    if predicted_waste < 3000:
        return "LOW"
    elif predicted_waste < 6000:
        return "MEDIUM"
    return "HIGH"


def get_recommendation(priority):
    if priority == "LOW":
        return "Routine waste collection is sufficient."
    elif priority == "MEDIUM":
        return "Schedule additional collection capacity for this area."
    return (
        "High waste generation expected. "
        "Deploy additional collection vehicles and prioritize recycling."
    )


def predict_waste(data):
    valid_categories = _valid_categories()
    for field, value in {
        "city": data.city,
        "waste_type": data.waste_type,
        "disposal_method": data.disposal_method,
    }.items():
        if value not in valid_categories[field]:
            raise ValueError(f"Unsupported {field.replace('_', ' ')}: {value}")

    input_data = pd.DataFrame([_request_data(data)])

    # Guarantees the same raw-feature order used during training.
    input_data = input_data.reindex(columns=features)

    prepared_data = preprocessor.transform(input_data)

    prediction = float(model.predict(prepared_data)[0])
    prediction = max(0, round(prediction))

    priority = get_collection_priority(prediction)

    return {
        "predicted_waste_tons_per_day": prediction,
        "collection_priority": priority,
        "recommendation": get_recommendation(priority),
        "model_note": bundle.get(
            "model_note",
            "Scenario estimate. Validate it with local collection records before planning operations."
        )
    }
