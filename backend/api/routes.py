from fastapi import APIRouter

from backend.models import FloodRiskInput, FloodRiskResponse
from backend.predictor_service import PredictorService

router = APIRouter()
service = PredictorService()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/predict", response_model=FloodRiskResponse)
def predict(payload: FloodRiskInput) -> FloodRiskResponse:
    data = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    result = service.predict(data)
    return FloodRiskResponse(**result)