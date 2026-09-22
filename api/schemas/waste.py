from pydantic import BaseModel, Field


class WasteRequest(BaseModel):
    city: str
    waste_type: str
    recycling_rate: float = Field(ge=0, le=100)
    population_density: float = Field(ge=0)
    municipal_efficiency_score: float = Field(ge=1, le=10)
    disposal_method: str
    awareness_campaigns_count: int = Field(ge=0)
    landfill_capacity_tons: float = Field(ge=0)
    waste_reduction_initiatives: float = Field(ge=0)
    industrial_symbiosis_index: float = Field(ge=0)
    community_participation_score: float = Field(ge=0)
    green_technology_adoption: float = Field(ge=0)
    recycling_infrastructure_rating: float = Field(ge=0)


class WasteResponse(BaseModel):
    predicted_waste_tons_per_day: int
    collection_priority: str
    recommendation: str
    model_note: str
