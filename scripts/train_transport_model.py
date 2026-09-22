"""Train the transport-demand model from infrastructure and operations data."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
MODEL_PATH = ROOT_DIR / "models" / "transport_demand_model.joblib"

INFRASTRUCTURE_PATH = RAW_DATA_DIR / "eb1fa0a4-e095-476b-af46-382094ddda53.csv"
OPERATIONS_PATH = RAW_DATA_DIR / "e333a07c-9d92-4b9a-a856-9eb29055f772.csv"


def city_key(value: str) -> str:
    return str(value).strip().casefold()


def load_transport_data() -> pd.DataFrame:
    infrastructure = pd.read_csv(INFRASTRUCTURE_PATH)
    operations = pd.read_csv(OPERATIONS_PATH)

    infrastructure.columns = [
        "city", "bus_type", "bus_count", "bus_terminals", "bus_stands", "bus_stops"
    ]
    operations.columns = [
        "city", "year", "daily_trips", "daily_passengers", "daily_trip_length_km",
        "daily_cost_rupees", "revenue_per_km"
    ]

    infrastructure["city_key"] = infrastructure["city"].map(city_key)
    operations["city_key"] = operations["city"].map(city_key)

    infrastructure_numeric = ["bus_count", "bus_terminals", "bus_stands", "bus_stops"]
    operations_numeric = [
        "daily_trips", "daily_passengers", "daily_trip_length_km",
        "daily_cost_rupees", "revenue_per_km"
    ]
    infrastructure[infrastructure_numeric] = infrastructure[infrastructure_numeric].apply(
        pd.to_numeric, errors="coerce"
    )
    operations[operations_numeric] = operations[operations_numeric].apply(
        pd.to_numeric, errors="coerce"
    )

    city_infrastructure = infrastructure.groupby("city_key", as_index=False).agg(
        total_buses=("bus_count", "sum"),
        bus_terminals=("bus_terminals", "max"),
        bus_stands=("bus_stands", "max"),
        bus_stops=("bus_stops", "max"),
    )

    transport = operations.merge(city_infrastructure, on="city_key", how="inner")
    transport["year_start"] = transport["year"].str.extract(r"(\d{4})").astype(int)

    required_columns = [
        "city", "year_start", "daily_trips", "daily_passengers",
        "daily_trip_length_km", "total_buses", "bus_terminals", "bus_stands", "bus_stops"
    ]
    return transport.dropna(subset=required_columns).copy()


def main() -> None:
    transport = load_transport_data()
    features = [
        "city", "year_start", "daily_trips", "daily_trip_length_km",
        "total_buses", "bus_terminals", "bus_stands", "bus_stops"
    ]
    target = "daily_passengers"

    train = transport[transport["year_start"] < 2018].copy()
    test = transport[transport["year_start"] >= 2018].copy()
    if train.empty or test.empty:
        raise ValueError("A chronological split requires data before and during/after 2018.")

    preprocessor = ColumnTransformer([
        ("city_encoder", OneHotEncoder(handle_unknown="ignore"), ["city"]),
        ("numeric", "passthrough", features[1:]),
    ])
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", RandomForestRegressor(
            n_estimators=300, max_depth=8, random_state=42, n_jobs=-1
        )),
    ])

    pipeline.fit(train[features], train[target])
    predictions = pipeline.predict(test[features])
    metrics = {
        "mae": float(mean_absolute_error(test[target], predictions)),
        "rmse": float(mean_squared_error(test[target], predictions) ** 0.5),
        "r2": float(r2_score(test[target], predictions)),
    }

    joblib.dump({
        "model": pipeline,
        "features": features,
        "metrics": metrics,
        "train_years": sorted(train["year_start"].unique().tolist()),
        "test_years": sorted(test["year_start"].unique().tolist()),
    }, MODEL_PATH)
    print(f"Saved {MODEL_PATH}")
    print(metrics)


if __name__ == "__main__":
    main()
