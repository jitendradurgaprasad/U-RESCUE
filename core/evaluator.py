"""
evaluator.py

Evaluation module for U Rescue
"""

import json
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay,
)


class Evaluator:

    def __init__(self, trainer):

        self.trainer = trainer

    def evaluate(self):

        predictions = self.trainer.model.predict(
            self.trainer.X_test
        )

        self.metrics = {

            "accuracy": float(
                accuracy_score(
                    self.trainer.y_test,
                    predictions
                )
            ),

            "precision": float(
                precision_score(
                    self.trainer.y_test,
                    predictions,
                    average="weighted"
                )
            ),

            "recall": float(
                recall_score(
                    self.trainer.y_test,
                    predictions,
                    average="weighted"
                )
            ),

            "f1_score": float(
                f1_score(
                    self.trainer.y_test,
                    predictions,
                    average="weighted"
                )
            ),
        }

        self.report = classification_report(
            self.trainer.y_test,
            predictions,
            output_dict=True
        )

        self.cm = confusion_matrix(
            self.trainer.y_test,
            predictions
        )

        return predictions

    def save(self, output_folder):

        output_folder = Path(output_folder)

        with open(
            output_folder / "metrics.json",
            "w"
        ) as f:

            json.dump(
                self.metrics,
                f,
                indent=4
            )

        pd.DataFrame(self.report).transpose().to_csv(
            output_folder / "classification_report.csv"
        )

        importance = pd.DataFrame({

            "Feature": self.trainer.X.columns,

            "Importance": self.trainer.model.feature_importances_

        })

        importance.sort_values(

            by="Importance",

            ascending=False,

            inplace=True

        )

        importance.to_csv(

            output_folder / "feature_importance.csv",

            index=False

        )

        disp = ConfusionMatrixDisplay(
            confusion_matrix=self.cm
        )

        disp.plot()

        plt.tight_layout()

        plt.savefig(
            output_folder / "confusion_matrix.png",
            dpi=300
        )

        plt.close()

        print("\nEvaluation Saved Successfully.")