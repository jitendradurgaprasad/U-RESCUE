import json
import time
from pathlib import Path
from statistics import mean, pstdev

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.pipeline import Pipeline


# ==========================================================
# CONFIGURATION
# ==========================================================

MODEL_DIR = Path(__file__).resolve().parent / "models"
MODEL_PATH = MODEL_DIR / "flood_model.joblib"
METADATA_PATH = MODEL_DIR / "flood_model.json"

# Train only on the first 200,000 rows
MAX_TRAIN_ROWS = 200_000

# Number of validation scenarios
N_VALIDATION_SPLITS = 10

# Model settings
N_ESTIMATORS = 200
MAX_DEPTH = 20
RANDOM_STATE = 42
N_JOBS = -1


# ==========================================================
# DATASET SEARCH
# ==========================================================

def find_dataset_file() -> Path | None:
    explicit_path = Path(
        r"C:\Users\M jitendra\OneDrive\Desktop\projects\U RESCUE\Datasets\training_dataset_v2.csv"
    )

    if explicit_path.exists():
        return explicit_path

    base_dir = Path(__file__).resolve().parent.parent

    exact_names = [
        "trainign_dataset_v2.csv",
        "training_dataset_v2.csv",
        "flood_training.csv",
        "training_data.csv",
    ]

    for name in exact_names:
        path = base_dir / name
        if path.exists():
            return path

    for path in base_dir.rglob("*.csv"):
        name = path.name.lower()

        if "train" in name and "dataset" in name and "v2" in name:
            return path

    for path in base_dir.rglob("*.csv"):
        name = path.name.lower()

        if "flood" in name and "train" in name:
            return path

    return None


# ==========================================================
# LOAD DATASET
# ==========================================================

def load_dataframe(path: Path, nrows=None) -> pd.DataFrame:
    return pd.read_csv(path, nrows=nrows)


# ==========================================================
# NORMALIZE TARGET
# ==========================================================

def normalize_target(series: pd.Series):
    if pd.api.types.is_numeric_dtype(series):
        values = series.astype(float)

        if values.nunique() <= 2:
            return values.astype(int)

        return values

    text = series.astype(str).str.strip().str.lower()

    mapping = {
        "low": 20.0,
        "moderate": 50.0,
        "high": 80.0,
        "critical": 90.0,
        "none": 10.0,
        "0": 0.0,
        "1": 1.0,
    }

    mapped = []
    for value in text:
        mapped.append(mapping.get(value, 50.0))

    return pd.Series(mapped, dtype=float)


# ==========================================================
# FEATURE PREPARATION
# ==========================================================

def prepare_features(df: pd.DataFrame, target_col: str):
    feature_cols = []

    for col in df.columns:
        if col == target_col:
            continue

        if col in {"id", "name", "location", "geometry"}:
            continue

        if pd.api.types.is_numeric_dtype(df[col]):
            feature_cols.append(col)

    if "latitude" in df.columns and "longitude" in df.columns:
        feature_cols = [c for c in feature_cols if c not in {"latitude", "longitude"}]
        feature_cols = ["latitude", "longitude"] + feature_cols

    X = df[feature_cols].copy()

    if "latitude" in X.columns:
        X["lat_abs"] = X["latitude"].abs()

    if "longitude" in X.columns:
        X["lon_abs"] = X["longitude"].abs()

    if "latitude" in X.columns:
        X["lat_sq"] = X["latitude"] ** 2

    if "longitude" in X.columns:
        X["lon_sq"] = X["longitude"] ** 2

    if "latitude" in X.columns:
        X["lat_norm"] = X["latitude"] / 90.0

    if "longitude" in X.columns:
        X["lon_norm"] = X["longitude"] / 180.0

    final_cols = []

    for col in feature_cols:
        if col in X.columns:
            final_cols.append(col)

    for extra in [
        "lat_abs",
        "lon_abs",
        "lat_sq",
        "lon_sq",
        "lat_norm",
        "lon_norm",
    ]:
        if extra in X.columns:
            final_cols.append(extra)

    return X[final_cols], final_cols


def build_model(target_series):
    if pd.Series(target_series).nunique() <= 2:
        return Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("model", RandomForestClassifier(
                    n_estimators=N_ESTIMATORS,
                    max_depth=MAX_DEPTH,
                    random_state=RANDOM_STATE,
                    n_jobs=N_JOBS,
                    verbose=0,
                )),
            ]
        )

    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestRegressor(
                n_estimators=N_ESTIMATORS,
                max_depth=MAX_DEPTH,
                random_state=RANDOM_STATE,
                n_jobs=N_JOBS,
                verbose=0,
            )),
        ]
    )


# ==========================================================
# TRAIN MODEL
# ==========================================================

def train_and_save_model():
    dataset_path = find_dataset_file()

    if dataset_path is None:
        print("❌ No dataset file found.")
        return None

    print("=" * 60)
    print("Loading Dataset...")
    print("=" * 60)

    df = load_dataframe(dataset_path, nrows=MAX_TRAIN_ROWS)

    print(f"Dataset : {dataset_path}")
    print(f"Rows used for training : {len(df):,}")
    print(f"Columns : {len(df.columns)}")
    print()

    target_candidates = [
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

    target_col = None

    for col in target_candidates:
        if col in df.columns:
            target_col = col
            break

    if target_col is None:
        print("❌ Target column not found.")
        return None

    print(f"Target Column : {target_col}")

    y = normalize_target(df[target_col])
    X, feature_names = prepare_features(df, target_col)

    mask = X.notna().all(axis=1) & y.notna()
    X = X[mask]
    y = y[mask]

    print(f"Valid Samples : {len(X):,}")
    print(f"Features      : {len(feature_names)}")
    print()

    if len(X) < 10:
        print("Not enough samples.")
        return None

    print("=" * 60)
    print(f"Running {N_VALIDATION_SPLITS} validation scenarios...")
    print("=" * 60)

    if pd.Series(y).nunique() <= 2:
        cv = StratifiedKFold(
            n_splits=N_VALIDATION_SPLITS,
            shuffle=True,
            random_state=RANDOM_STATE,
        )

        fold_accuracies = []
        fold_precisions = []
        fold_recalls = []
        fold_f1s = []

        all_y_true = []
        all_y_pred = []

        for fold_idx, (train_idx, val_idx) in enumerate(cv.split(X, y), start=1):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

            fold_model = build_model(y_train)
            fold_model.fit(X_train, y_train)

            pred = fold_model.predict(X_val)

            accuracy = accuracy_score(y_val, pred)
            precision = precision_score(y_val, pred, average="weighted", zero_division=0)
            recall = recall_score(y_val, pred, average="weighted", zero_division=0)
            f1 = f1_score(y_val, pred, average="weighted", zero_division=0)

            fold_accuracies.append(accuracy)
            fold_precisions.append(precision)
            fold_recalls.append(recall)
            fold_f1s.append(f1)

            all_y_true.extend(y_val.tolist())
            all_y_pred.extend(pred.tolist())

            print(
                f"Fold {fold_idx}/{N_VALIDATION_SPLITS}: "
                f"accuracy={accuracy:.4f}, "
                f"precision={precision:.4f}, "
                f"recall={recall:.4f}, "
                f"f1={f1:.4f}"
            )

        validation_metrics = {
            "type": "classification",
            "n_scenarios": N_VALIDATION_SPLITS,
            "accuracy_mean": float(mean(fold_accuracies)),
            "accuracy_std": float(pstdev(fold_accuracies)),
            "precision_mean": float(mean(fold_precisions)),
            "recall_mean": float(mean(fold_recalls)),
            "f1_mean": float(mean(fold_f1s)),
            "classification_report": classification_report(all_y_true, all_y_pred, zero_division=0),
            "confusion_matrix": confusion_matrix(all_y_true, all_y_pred).tolist(),
        }

    else:
        cv = KFold(
            n_splits=N_VALIDATION_SPLITS,
            shuffle=True,
            random_state=RANDOM_STATE,
        )

        fold_maes = []
        fold_rmses = []
        fold_r2s = []

        for fold_idx, (train_idx, val_idx) in enumerate(cv.split(X), start=1):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

            fold_model = build_model(y_train)
            fold_model.fit(X_train, y_train)

            pred = fold_model.predict(X_val)

            mae = mean_absolute_error(y_val, pred)
            rmse = mean_squared_error(y_val, pred) ** 0.5
            r2 = r2_score(y_val, pred)

            fold_maes.append(mae)
            fold_rmses.append(rmse)
            fold_r2s.append(r2)

            print(
                f"Fold {fold_idx}/{N_VALIDATION_SPLITS}: "
                f"mae={mae:.4f}, "
                f"rmse={rmse:.4f}, "
                f"r2={r2:.4f}"
            )

        validation_metrics = {
            "type": "regression",
            "n_scenarios": N_VALIDATION_SPLITS,
            "mae_mean": float(mean(fold_maes)),
            "mae_std": float(pstdev(fold_maes)),
            "rmse_mean": float(mean(fold_rmses)),
            "rmse_std": float(pstdev(fold_rmses)),
            "r2_mean": float(mean(fold_r2s)),
            "r2_std": float(pstdev(fold_r2s)),
        }

    print()
    print("Cross-validation summary")
    print("------------------------")
    if validation_metrics["type"] == "classification":
        print(f"Accuracy mean ± std : {validation_metrics['accuracy_mean']:.4f} ± {validation_metrics['accuracy_std']:.4f}")
        print(f"Precision mean      : {validation_metrics['precision_mean']:.4f}")
        print(f"Recall mean         : {validation_metrics['recall_mean']:.4f}")
        print(f"F1 mean             : {validation_metrics['f1_mean']:.4f}")
        print()
        print(validation_metrics["classification_report"])
    else:
        print(f"MAE mean ± std : {validation_metrics['mae_mean']:.4f} ± {validation_metrics['mae_std']:.4f}")
        print(f"RMSE mean      : {validation_metrics['rmse_mean']:.4f}")
        print(f"R2 mean        : {validation_metrics['r2_mean']:.4f}")

    print()
    print("=" * 60)
    print("Training final model on full dataset...")
    print("=" * 60)

    final_model = build_model(y)
    final_model.fit(X, y)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_model, MODEL_PATH)

    metadata = {
        "feature_names": feature_names,
        "source_file": str(dataset_path),
        "target_column": target_col,
        "rows_used": int(len(X)),
        "trees": N_ESTIMATORS,
        "max_depth": MAX_DEPTH,
        "validation_metrics": validation_metrics,
    }

    METADATA_PATH.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    print("Model Saved Successfully.")
    print(MODEL_PATH)
    print()

    print("Metadata Saved Successfully.")
    print(METADATA_PATH)
    print()

    return final_model


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":
    print()
    print("=" * 60)
    print("U RESCUE MODEL TRAINER")
    print("=" * 60)
    print()

    try:
        train_and_save_model()
        print()
        print("=" * 60)
        print("Everything completed successfully.")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print("Training Failed")
        print("=" * 60)
        print(e)