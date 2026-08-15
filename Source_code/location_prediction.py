from pathlib import Path

from core.location_extractor import LocationExtractor
from core.predictor import Predictor


PROJECT_ROOT = Path(__file__).resolve().parent.parent

STANDARDIZED = PROJECT_ROOT / "Datasets" / "Standardized"

MODELS = PROJECT_ROOT / "Models"


extractor = LocationExtractor(STANDARDIZED)

predictor = Predictor(MODELS)


# Change these coordinates later
LATITUDE = 17.4065
LONGITUDE = 78.4772


features = extractor.extract(
    LATITUDE,
    LONGITUDE
)

prediction, confidence = predictor.predict(features)


print()

print(features)

print()

print("Prediction :", prediction)

print(f"Confidence : {confidence*100:.2f}%")