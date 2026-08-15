import json
import re
from datetime import datetime
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
)
from sklearn.pipeline import Pipeline

# CONFIG
DATASET_PATH = Path(
    r"C:\Users\M jitendra\OneDrive\Desktop\projects\U RESCUE\Datasets\training_dataset_v2.csv"
)

TRAIN_ROWS = 100_000
HOLDOUT_ROWS = 1_000

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

MODEL_DIR = Path(__file__).resolve().parent / "feature_models"
REPORT_DIR = Path(__file__).resolve().parent / "feature_reports"
SUMMARY_PATH = Path(__file__).resolve().parent / f"feature_training_summary_{RUN_ID}.csv"
LATEST_SUMMARY_PATH = Path(__file__).resolve().parent / "feature_training_summary_latest.csv"

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


def sanitize_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_")


def normalize_target(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        values = series.astype(float)
        if values.nunique() <= 2:
            return values.astype(int)
        return values
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
    }
    mapped = text.map(mapping)
    return mapped.fillna(1).astype(int)


def load_data() -> pd.DataFrame:
    total_rows = TRAIN_ROWS + HOLDOUT_ROWS
    df = pd.read_csv(DATASET_PATH, nrows=total_rows)
    if df.empty:
        raise ValueError("Dataset is empty or could not be loaded.")
    return df


def find_target_column(df: pd.DataFrame) -> str | None:
    for col in TARGET_CANDIDATES:
        if col in df.columns:
            return col
    return None


def build_model():
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)),
        ]
    )


def compute_metrics(y_true, y_pred):
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "classification_report": classification_report(y_true, y_pred, zero_division=0),
    }


def train_feature_models():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_data()
    target_col = find_target_column(df)
    if target_col is None:
        raise ValueError("No valid target column found in the dataset.")

    print(f"Dataset: {DATASET_PATH}")
    print(f"Rows loaded: {len(df)}")
    print(f"Target column: {target_col}")
    print(f"Run ID: {RUN_ID}")

    train_df = df.iloc[:TRAIN_ROWS].copy()
    test_df = df.iloc[TRAIN_ROWS:TRAIN_ROWS + HOLDOUT_ROWS].copy()

    if len(test_df) < 10:
        raise ValueError("Not enough holdout rows for evaluation.")

    y_train = normalize_target(train_df[target_col])
    y_test = normalize_target(test_df[target_col])

    feature_candidates = []
    for col in df.columns:
        if col == target_col:
            continue
        if col in {"id", "name", "location", "geometry"}:
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            feature_candidates.append(col)

    print(f"Features to train: {feature_candidates}")

    results = []

    for feature in feature_candidates:
        X_train = train_df[[feature]].copy()
        X_test = test_df[[feature]].copy()

        train_mask = X_train.notna().all(axis=1)
        test_mask = X_test.notna().all(axis=1)

        if train_mask.sum() < 50 or test_mask.sum() < 100:
            print(f"Skipping {feature}: insufficient data after dropna (train {train_mask.sum()}, test {test_mask.sum()})")
            continue

        X_train = X_train[train_mask]
        y_train_filtered = y_train[train_mask]

        X_test = X_test[test_mask]
        y_test_filtered = y_test[test_mask]

        model = build_model()
        model.fit(X_train, y_train_filtered)

        preds = model.predict(X_test)
        metrics = compute_metrics(y_test_filtered, preds)

        model_path = MODEL_DIR / f"{sanitize_name(feature)}_{RUN_ID}.joblib"
        joblib.dump(model, model_path)

        report = {
            "feature": feature,
            "model_file": str(model_path),
            "train_rows": int(len(X_train)),
            "test_rows": int(len(X_test)),
            "metrics": metrics,
            "predictions": [
                {"actual": int(a), "predicted": int(p)} for a, p in zip(y_test_filtered.tolist(), preds.tolist())
            ],
        }

        report_path = REPORT_DIR / f"{sanitize_name(feature)}_{RUN_ID}.json"
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

        results.append({
            "feature": feature,
            "accuracy": metrics["accuracy"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "train_rows": len(X_train),
            "test_rows": len(X_test),
            "model_file": str(model_path),
            "report_file": str(report_path),
        })

        print(
            f"Trained {feature} -> "
            f"accuracy={metrics['accuracy']:.4f}, "
            f"precision={metrics['precision']:.4f}, "
            f"recall={metrics['recall']:.4f}, "
            f"f1={metrics['f1']:.4f}"
        )

    if not results:
        print()
        print("No feature models were trained.")
    else:
        summary_df = pd.DataFrame(results)
        if "f1" in summary_df.columns:
            summary_df = summary_df.sort_values(by="f1", ascending=False)
        summary_df.to_csv(SUMMARY_PATH, index=False)
        summary_df.to_csv(LATEST_SUMMARY_PATH, index=False)

        print()
        print("Summary saved to:")
        print(SUMMARY_PATH)
        print("Latest summary saved to:")
        print(LATEST_SUMMARY_PATH)
        print("Per-feature model files saved to:")
        print(MODEL_DIR)
        print("Per-feature reports saved to:")
        print(REPORT_DIR)


if __name__ == "__main__":
    train_feature_models()