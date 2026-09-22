from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AirQualityRequest(BaseModel):
    city: Literal["Bangalore", "Chennai", "Delhi", "Kolkata", "Mumbai"]
    datetime: datetime
    pm25: float = Field(alias="PM2.5", ge=0)
    pm10: float = Field(alias="PM10", ge=0)
    no: float = Field(alias="NO", ge=0)
    no2: float = Field(alias="NO2", ge=0)
    nox: float = Field(alias="NOx", ge=0)
    nh3: float = Field(alias="NH3", ge=0)
    co: float = Field(alias="CO", ge=0)
    so2: float = Field(alias="SO2", ge=0)
    o3: float = Field(alias="O3", ge=0)


class AirQualityResponse(BaseModel):
    predicted_aqi: int
    aqi_category: str
    risk_score: int