from pydantic import BaseModel, ConfigDict, Field


class FloodRiskInput(BaseModel):
    model_config = ConfigDict(extra="allow")

    latitude: float = Field(..., ge=-90, le=90, description="Selected latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Selected longitude")


class FloodRiskResponse(BaseModel):
    risk_score: float
    risk_level: str
    summary: str
    recommendations: list[str]
    location: dict