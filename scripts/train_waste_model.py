"""Train the best validated waste-generation estimator from the available dataset."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT_DIR / "data" / "raw" / "Waste_Management_with_Extra_Features.csv"
MODEL_PATH = ROOT_DIR / "models" / "waste_xgboost_model.joblib"


def main() -> None:
    data = pd.read_csv(DATA_PATH)
    data.columns = [
        "city", "waste_type", "waste_generated_tons_per_day", "recycling_rate",
        "population_density", "municipal_efficiency_score", "disposal_method",
        "cost_per_ton", "awareness_campaigns_count", "landfill_name",
        "landfill_location", "landfill_capacity_tons", "year",
        "waste_reduction_initiatives", "industrial_symbiosis_index",
        "community_participation_score", "green_technology_adoption",
        "recycling_infrastructure_rating",
    ]
    features = [
        "city", "waste_type", "recycling_rate", "population_density",
        "municipal_efficiency_score", "disposal_method", "awareness_campaigns_count",
        "landfill_capacity_tons", "waste_reduction_initiatives",
        "industrial_symbiosis_index", "community_participation_score",
        "green_technology_adoption", "recycling_infrastructure_rating",
    ]
    target = "waste_generated_tons_per_day"
    X_train, X_test, y_train, y_test = train_test_split(
        data[features], data[target], test_size=0.2, random_state=42,
        stratify=data["waste_type"]
    )
    categorical = ["city", "waste_type", "disposal_method"]
    numeric = [column for column in features if column not in categorical]
    preprocessor = ColumnTransformer([
        ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical),
        ("numeric", "passthrough", numeric),
    ])
    X_train_prepared = preprocessor.fit_transform(X_train)
    X_test_prepared = preprocessor.transform(X_test)

    candidates = {
        "linear_regression": LinearRegression(),
        "mean_baseline": DummyRegressor(strategy="mean"),
    }
    evaluated = {}
    for name, candidate in candidates.items():
        candidate.fit(X_train_prepared, y_train)
        predictions = candidate.predict(X_test_prepared)
        evaluated[name] = {
            "model": candidate,
            "mae": float(mean_absolute_error(y_test, predictions)),
            "rmse": float(mean_squared_error(y_test, predictions) ** 0.5),
            "r2": float(r2_score(y_test, predictions)),
        }

    best_name = min(evaluated, key=lambda name: evaluated[name]["mae"])
    best = evaluated[best_name]
    model_note = (
        "Scenario estimate only. The available waste dataset has limited predictive signal; "
        "validate this result with local collection records before operational use."
    )
    joblib.dump({
        "model": best["model"], "preprocessor": preprocessor, "features": features,
        "metrics": {key: best[key] for key in ("mae", "rmse", "r2")},
        "model_name": best_name, "model_note": model_note,
    }, MODEL_PATH)
    print(f"Saved {MODEL_PATH}")
    print({name: {key: value for key, value in result.items() if key != "model"}
           for name, result in evaluated.items()})


if __name__ == "__main__":
    main()
