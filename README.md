# AI City Intelligence Platform

A local, full-stack city-intelligence dashboard with four machine-learning modules. Each form sends validated input to FastAPI and returns a prediction, status level, and recommendation.

## Modules

| Module | Predicts | Status |
| --- | --- | --- |
| Traffic Intelligence | Hourly traffic volume and congestion | Validated XGBoost model |
| Air Quality Intelligence | AQI, category, and risk score | Validated XGBoost estimator |
| Waste Management | Daily waste generation and collection priority | Scenario estimate; validate locally before operations |
| Transport Intelligence | Daily passenger demand and crowd level | Retrain with the corrected script before relying on results |

## Project structure

```text
api/          FastAPI schemas, services, and endpoints
dashboard/    HTML, CSS, and JavaScript interface
data/raw/     Source CSV datasets
models/       Saved model artifacts
notebooks/    Exploration and experimentation
scripts/      Reproducible model-training scripts
tests/        API tests
```

## Run locally

Create or select a working Python interpreter in VS Code, then run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn api.main:app --reload
```

Open the API documentation at `http://127.0.0.1:8000/docs`. Open `dashboard/index.html` using VS Code Live Server.

## Run the Streamlit app locally

The Streamlit app uses the saved models directly, so FastAPI does not need to run for this interface.

```powershell
streamlit run streamlit_app.py
```

## Deploy on Streamlit Community Cloud

1. Run the corrected training scripts first, so the four model files in `models/` are current.
2. Commit and push `streamlit_app.py`, `.streamlit/config.toml`, `requirements.txt`, the `api/` package, and all required `.joblib` model files to GitHub.
3. Open [Streamlit Community Cloud](https://share.streamlit.io/), connect GitHub, and select **Create app**.
4. Choose your repository, branch, and `streamlit_app.py` as the entrypoint.
5. In Advanced settings, select Python 3.12, then deploy.

Streamlit Community Cloud installs dependencies from `requirements.txt`, and every model artifact used by the app must be available in the repository. Streamlit supports Git LFS if model files become too large.

## Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/health` | Reports API status and active modules |
| POST | `/predict` | Traffic-volume prediction |
| POST | `/air-quality/predict` | AQI estimation |
| POST | `/waste/predict` | Waste scenario estimate |
| POST | `/transport/predict` | Transport-demand prediction |

## Model notes

- Traffic uses a chronological split: data before 2018 for training and 2018 for testing. Recorded MAE is about 268.5 vehicles/hour and R² is 0.938.
- AQI uses measured pollutant concentrations to estimate AQI. It is an estimator, not a future air-quality forecast. Recorded MAE is about 6.26 AQI points and R² is 0.977.
- Waste data has limited predictive signal. The API explicitly labels results as scenario estimates.
- Transport combines bus infrastructure with annual operations data. The original notebook treated bus counts as text; retrain before using the current artifact.

## Retrain corrected models

With a working virtual environment:

```powershell
python scripts/train_transport_model.py
python scripts/train_waste_model.py
```

Restart FastAPI after retraining.

## Tests

```powershell
pytest -q
```
