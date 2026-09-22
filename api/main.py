from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.schemas.traffic import TrafficRequest, TrafficResponse
from api.services.traffic_services import predict_traffic
from api.schemas.air_quality import AirQualityRequest, AirQualityResponse
from api.services.air_quality_services import predict_air_quality
from api.schemas.waste import WasteRequest, WasteResponse
from api.services.waste_services import predict_waste
from api.schemas.transport import TransportRequest, TransportResponse
from api.services.transport_services import predict_transport

app = FastAPI(
    title="AI City Intelligence Platform",
    description="AI-powered city intelligence and traffic prediction API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "AI City Intelligence Platform API is running",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "City Intelligence",
        "modules": ["traffic", "air_quality", "waste", "transport"],
    }


@app.post("/predict", response_model=TrafficResponse)
def predict(data: TrafficRequest):

    result = predict_traffic(data)

    return result


@app.post("/air-quality/predict", response_model=AirQualityResponse)
def predict_aqi(data: AirQualityRequest):
    try:
        return predict_air_quality(data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@app.post("/waste/predict", response_model=WasteResponse)
def predict_waste_management(data: WasteRequest):
    try:
        return predict_waste(data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

@app.post("/transport/predict", response_model=TransportResponse)
def predict_transport_demand(data: TransportRequest):
    try:
        return predict_transport(data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
