"""
preprocessor.py

Reusable preprocessing pipeline for U Rescue.

Handles:
- Feature/Target separation
- Numerical & categorical feature detection
- Missing value handling
- Optional scaling
- Optional encoding

Author: Medisetti Jitendra Durga Prasad
"""

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder


class DataPreprocessor:

    def __init__(self):

        self.numerical_features = []
        self.categorical_features = []

        self.preprocessor = None

    def detect_features(self, dataframe, target_column):

        X = dataframe.drop(columns=[target_column])

        self.numerical_features = list(
            X.select_dtypes(include=["int64", "float64"]).columns
        )

        self.categorical_features = list(
            X.select_dtypes(include=["object", "category"]).columns
        )

        print("\n========== FEATURE SUMMARY ==========\n")

        print("Numerical Features")

        for feature in self.numerical_features:
            print("  •", feature)

        print("\nCategorical Features")

        if len(self.categorical_features) == 0:
            print("  None")
        else:
            for feature in self.categorical_features:
                print("  •", feature)

        return self.numerical_features, self.categorical_features

    def build_pipeline(self):

        numeric_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler())
            ]
        )

        categorical_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                (
                    "encoder",
                    OneHotEncoder(
                        handle_unknown="ignore"
                    )
                )
            ]
        )

        self.preprocessor = ColumnTransformer(
            transformers=[
                (
                    "numeric",
                    numeric_pipeline,
                    self.numerical_features
                ),
                (
                    "categorical",
                    categorical_pipeline,
                    self.categorical_features
                )
            ],
            remainder="drop"
        )

        print("\nPreprocessing pipeline created.")

        return self.preprocessor

    def fit_transform(self, X):

        print("\nApplying preprocessing...\n")

        X_processed = self.preprocessor.fit_transform(X)

        print("Preprocessing completed.")

        print("Processed Shape :", X_processed.shape)

        return X_processed

    def transform(self, X):

        return self.preprocessor.transform(X)