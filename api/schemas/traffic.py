from pydantic import BaseModel, Field


class TrafficRequest(BaseModel):
    temp: float
    rain_1h: float = Field(ge=0)
    snow_1h: float = Field(ge=0)
    clouds_all: float = Field(ge=0, le=100)
    hour: int = Field(ge=0, le=23)
    day_of_week: int = Field(ge=0, le=6)
    month: int = Field(ge=1, le=12)
    is_weekend: int = Field(ge=0, le=1)


class TrafficResponse(BaseModel):
    predicted_traffic_volume: int
    congestion_level: str
    risk_score: int
    time_period: str
    recommendation: str