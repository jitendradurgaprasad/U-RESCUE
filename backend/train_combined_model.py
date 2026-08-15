import json
import time
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    confusion_matrix,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline

DATASET_PATH = Path(
    r"C:\Users\M jitendra\OneDrive\Desktop\projects\U RESCUE\Datasets\training_dataset_v2.csv"
)

MODEL_DIR = Path(__file__).resolve().parent / "models"
MODEL_PATH = MODEL_DIR / "combined_model_100k_1k.joblib"
METADATA_PATH = MODEL_DIR / "combined_model_100k_1k.json"

TRAIN_ROWS = 100_000
TEST_ROWS = 1_000
TOTAL_ROWS = TRAIN_ROWS + TEST_ROWS
N_FOLDS = 5

TARGET_CANDIDATES = [
    "flood_risk_final",
    "flood_risk",
    "risk_score",
    "risk",
    "target",
    "flood_label",
    "risk_label",
    "label",
    "class",
    "flood_class",
    "severity",
]


def find_target_column(df: pd.DataFrame) -> str | None:
    for col in TARGET_CANDIDATES:
        if col in df.columns:
            return col
    return None


def normalize_target(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        values = series.astype(float)
        if values.nunique() <= 2:
            return values.astype(int)
        return values.astype(int)
    text = series.astype(str).str.strip().str.lower()
    mapping = {
        "low": 0,
        "moderate": 1,
        "high": 2,
        "critical": 3,
        "none": 0,
        "0": 0,
        "1": 1,
        "2": 2,
        "3": 3,
    }
    mapped = text.map(mapping)
    return mapped.fillna(1).astype(int)


def load_data(path: Path, nrows: int) -> pd.DataFrame:
    return pd.read_csv(path, nrows=nrows)


def build_model() -> Pipeline:
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestClassifier(
                n_estimators=200,
                max_depth=20,
                random_state=42,
                n_jobs=-1,
                verbose=0,
            )),
        ]
    )


def evaluate_cross_validation(X: pd.DataFrame, y: pd.Series):
    cv = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    accuracies = []
    precisions = []
    recalls = []
    f1s = []

    for fold_idx, (train_idx, val_idx) in enumerate(cv.split(X, y), start=1):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model = build_model()
        model.fit(X_train, y_train)
        preds = model.predict(X_val)

        accuracy = accuracy_score(y_val, preds)
        precision = precision_score(y_val, preds, average="weighted", zero_division=0)
        recall = recall_score(y_val, preds, average="weighted", zero_division=0)
        f1 = f1_score(y_val, preds, average="weighted", zero_division=0)

        accuracies.append(accuracy)
        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)

        print(
            f"Fold {fold_idx}/{N_FOLDS}: "
            f"accuracy={accuracy:.4f}, "
            f"precision={precision:.4f}, "
            f"recall={recall:.4f}, "
            f"f1={f1:.4f}"
        )

    return {
        "accuracy_mean": float(pd.Series(accuracies).mean()),
        "precision_mean": float(pd.Series(precisions).mean()),
        "recall_mean": float(pd.Series(recalls).mean()),
        "f1_mean": float(pd.Series(f1s).mean()),
    }


def main():
    df = load_data(DATASET_PATH, TOTAL_ROWS)

    target_col = find_target_column(df)
    if target_col is None:
        raise ValueError("Target column not found in dataset")

    feature_cols = [
        col for col in df.columns
        if col != target_col
        and col not in {"id", "name", "location", "geometry"}
        and pd.api.types.is_numeric_dtype(df[col])
    ]

    y = normalize_target(df[target_col])
    X = df[feature_cols].copy()

    valid_mask = y.notna()
    X = X[valid_mask]
    y = y[valid_mask]

    print(f"Target column: {target_col}")
    print(f"Features used: {feature_cols}")
    print(f"Rows loaded: {len(df)}")
    print(f"Valid rows after target filtering: {len(X)}")
    print()

    if len(X) < 1000:
        raise ValueError("Not enough valid rows for training and validation.")

    cv_metrics = evaluate_cross_validation(X, y)

    print()
    print("Cross-validation summary")
    print("------------------------")
    print(f"Accuracy mean : {cv_metrics['accuracy_mean']:.4f}")
    print(f"Precision mean: {cv_metrics['precision_mean']:.4f}")
    print(f"Recall mean   : {cv_metrics['recall_mean']:.4f}")
    print(f"F1 mean       : {cv_metrics['f1_mean']:.4f}")
    print()

    final_model = build_model()
    final_model.fit(X, y)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_model, MODEL_PATH)

    metadata = {
        "feature_columns": feature_cols,
        "target_column": target_col,
        "total_rows": len(X),
        "cv_metrics": cv_metrics,
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Final model saved to: {MODEL_PATH}")
    print(f"Metadata saved to: {METADATA_PATH}")


if __name__ == "__main__":
    main()