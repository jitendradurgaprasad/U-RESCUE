from core.location_extractor import LocationExtractor
from core.predictor import Predictor
from typing import Any, Dict

from backend.config import STANDARDIZED, MODELS
from backend.services.risk_engine import FloodRiskEngine


class PredictionService:

    def __init__(self):

        self.extractor = LocationExtractor(
            STANDARDIZED
        )

        self.predictor = Predictor(
            MODELS
        )

    def predict(self, latitude, longitude):

        features = self.extractor.extract(
            latitude,
            longitude
        )

        prediction, confidence = self.predictor.predict(
            features
        )

        return {

            "prediction": int(prediction),

            "confidence": float(confidence),

            "features": features.to_dict(
                orient="records"
            )[0]
        }


class PredictorService:
    def __init__(self) -> None:
        self.engine = FloodRiskEngine()

    def predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.engine.evaluate(payload)