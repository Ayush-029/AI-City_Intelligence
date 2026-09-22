from pydantic import BaseModel, Field


class TransportRequest(BaseModel):
    city: str
    year_start: int = Field(ge=2015, le=2018)
    daily_trips: float = Field(gt=0)
    daily_trip_length_km: float = Field(gt=0)
    total_buses: int = Field(gt=0)
    bus_terminals: int = Field(ge=0)
    bus_stands: int = Field(ge=0)
    bus_stops: int = Field(ge=0)


class TransportResponse(BaseModel):
    predicted_daily_passengers: int
    crowd_level: str
    recommendation: str
