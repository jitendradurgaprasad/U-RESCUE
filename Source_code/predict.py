from pathlib import Path

import pandas as pd

from core.predictor import Predictor


PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODELS = PROJECT_ROOT / "Models"

DATASET = PROJECT_ROOT / "Datasets" / "training_dataset_v2.csv"


df = pd.read_csv(DATASET)

sample = df.drop(columns=["flood_risk_final"]).iloc[0]

actual = df["flood_risk_final"].iloc[0]


predictor = Predictor(MODELS)

prediction, confidence = predictor.predict(sample.to_dict())


print("\n==============================")
print("Prediction Test")
print("==============================")

print("Actual Label     :", actual)
print("Predicted Label  :", prediction)
print(f"Confidence       : {confidence*100:.2f}%")