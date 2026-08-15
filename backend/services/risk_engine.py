import json
from pathlib import Path
from typing import Dict

import joblib

from backend.models import FloodRiskInput
from backend.train_model import train_and_save_model


class FloodRiskEngine:
    def __init__(self) -> None:
        self.model = None
        self.feature_names = None
        self._load_or_train()

    def _model_paths(self):
        base_dir = Path(__file__).resolve().parents[1]
        return [
            base_dir / "models" / "flood_model.joblib",
            base_dir / "models" / "flood_model.pkl",
        ]

    def _load_or_train(self) -> None:
        if self._load_model():
            return

        trained = train_and_save_model()
        if trained:
            self._load_model()

    def _load_model(self):
        for path in self._model_paths():
            if path.exists():
                self.model = joblib.load(path)

                metadata_path = path.with_suffix(".json")
                if metadata_path.exists():
                    with metadata_path.open("r", encoding="utf-8") as fh:
                        data = json.load(fh)
                        self.feature_names = data.get("feature_names", None)

                return True

        return False

    def _build_feature_vector(self, payload: Dict) -> list:
        if self.feature_names:
            return [payload.get(name, 0.0) for name in self.feature_names]

        latitude = payload.get("latitude", 0.0)
        longitude = payload.get("longitude", 0.0)

        return [
            latitude,
            longitude,
            abs(latitude),
            abs(longitude),
            latitude * latitude,
            longitude * longitude,
            latitude / 90.0,
            longitude / 180.0,
        ]

    def _predict_from_model(self, payload: Dict):
        if self.model is None:
            return None

        try:
            features = self._build_feature_vector(payload)
            prediction = self.model.predict([features])[0]
        except Exception:
            return None

        if isinstance(prediction, (int, float)):
            value = float(prediction)

            if 0 <= value <= 1:
                return round(value * 100, 1)

            if value > 100:
                return round(min(value, 100), 1)

            return round(value, 1)

        return None

    def evaluate(self, payload: Dict) -> Dict:
        data = FloodRiskInput(**payload)

        latitude = data.latitude
        longitude = data.longitude

        payload = dict(payload)
        payload["latitude"] = latitude
        payload["longitude"] = longitude

        model_score = self._predict_from_model(payload)

        if model_score is not None:
            score = round(float(model_score), 1)

            if score >= 70:
                level = "High"
                summary = "The trained model predicts high flood risk for this location."
                recommendations = [
                    "Issue early warnings for this area.",
                    "Prepare emergency shelters and evacuation routes.",
                    "Monitor drainage and local water levels closely.",
                ]
            elif score >= 35:
                level = "Moderate"
                summary = "The trained model predicts moderate flood risk for this location."
                recommendations = [
                    "Keep monitoring rainfall and water levels.",
                    "Prepare emergency kits and response plans.",
                    "Review access routes for responders.",
                ]
            else:
                level = "Low"
                summary = "The trained model predicts low flood risk for this location."
                recommendations = [
                    "Continue routine monitoring.",
                    "Stay updated on weather conditions.",
                    "Maintain drainage and water management systems.",
                ]

            return {
                "risk_score": score,
                "risk_level": level,
                "summary": summary,
                "recommendations": recommendations,
                "location": {
                    "latitude": round(latitude, 5),
                    "longitude": round(longitude, 5),
                },
            }

        # fallback
        abs_lat = abs(latitude)
        abs_lon = abs(longitude)

        score = 15.0

        if 5 <= abs_lat <= 25:
            score += 22.0
        elif abs_lat <= 40:
            score += 10.0
        else:
            score += 3.0

        if abs_lon <= 20 or abs_lon >= 155:
            score += 16.0
        elif 65 <= abs_lon <= 95:
            score += 20.0
        elif 100 <= abs_lon <= 140:
            score += 10.0
        else:
            score += 5.0

        score = round(min(score, 100.0), 1)

        if score >= 70:
            level = "High"
        elif score >= 35:
            level = "Moderate"
        else:
            level = "Low"

        return {
            "risk_score": score,
            "risk_level": level,
            "summary": "Fallback heuristic used because no trained model was loaded.",
            "recommendations": [
                "Continue monitoring.",
                "Prepare emergency resources.",
            ],
            "location": {
                "latitude": round(latitude, 5),
                "longitude": round(longitude, 5),
            },
        }

    def save_model(self, path: Path) -> None:
        joblib.dump(self.model, path)