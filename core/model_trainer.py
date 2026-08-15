"""
model_trainer.py

Production Model Trainer for U Rescue
"""

from pathlib import Path
import json
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


class ModelTrainer:

    def __init__(self, X, y):

        self.X = X
        self.y = y

        self.model = None

        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None

    def split_data(self):

        (
            self.X_train,
            self.X_test,
            self.y_train,
            self.y_test

        ) = train_test_split(

            self.X,
            self.y,

            test_size=0.2,

            random_state=42,

            stratify=self.y

        )

        print("\nTrain Shape :", self.X_train.shape)
        print("Test Shape  :", self.X_test.shape)

    def train(self):

        print("\nTraining Random Forest...\n")

        self.model = RandomForestClassifier(

            n_estimators=200,

            max_depth=20,

            random_state=42,

            n_jobs=-1

        )

        self.model.fit(

            self.X_train,

            self.y_train

        )

        print("Training Complete.")

    def save(self, output_folder):

        output_folder = Path(output_folder)

        output_folder.mkdir(exist_ok=True)

        joblib.dump(

            self.model,

            output_folder / "flood_rf_model.pkl"

        )

        with open(

            output_folder / "feature_names.json",

            "w"

        ) as f:

            if hasattr(self.X, "columns"):
                feature_names = list(self.X.columns)
            else:
                feature_names = [f"feature_{i}" for i in range(self.X.shape[1])]

            json.dump(
                feature_names,
                f,
                indent = 4
            )

        print("\nModel Saved Successfully.")