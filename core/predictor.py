"""
predictor.py

Prediction module for U Rescue
"""

from pathlib import Path
import json
import joblib
import pandas as pd


class Predictor:

    def __init__(self, model_folder):

        model_folder = Path(model_folder)

        self.model = joblib.load(
            model_folder / "flood_rf_model.pkl"
        )

        with open(
            model_folder / "feature_names.json",
            "r"
        ) as f:

            self.feature_names = json.load(f)

    def predict(self, feature_vector):

        if isinstance(feature_vector, dict):

            feature_vector = pd.DataFrame(
                [feature_vector]
            )

        feature_vector = feature_vector[
            self.feature_names
        ]

        prediction = self.model.predict(
            feature_vector
        )[0]

        probability = self.model.predict_proba(
            feature_vector
        )[0]

        confidence = max(probability)

        return prediction, confidence