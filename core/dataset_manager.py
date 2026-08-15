"""
dataset_manager.py

Reusable dataset manager for U Rescue.
"""

from pathlib import Path
import pandas as pd


class DatasetManager:

    def __init__(self, dataset_path):

        self.dataset_path = Path(dataset_path)

        self.df = None
        self.X = None
        self.y = None

    def load(self):

        print("\nLoading Dataset...\n")

        self.df = pd.read_csv(self.dataset_path)

        print(f"Rows : {len(self.df):,}")
        print(f"Columns : {len(self.df.columns)}")

        return self.df

    def info(self):

        print("\n========== DATASET SUMMARY ==========\n")

        print(self.df.describe())

        print("\nMissing Values\n")

        print(self.df.isnull().sum())

        print("\nDuplicate Rows :", self.df.duplicated().sum())

    def sample(self, n=300000):

        if n >= len(self.df):

            print("Requested sample larger than dataset.")
            return self.df

        print(f"\nCreating random sample ({n:,} rows)...")

        self.df = self.df.sample(

            n=n,

            random_state=42,

            replace=False
        ).reset_index(drop=True)

        print("Done.")

        return self.df

    def class_distribution(self, target):

        print("\nTarget Distribution\n")

        print(self.df[target].value_counts())

        print("\nPercentages\n")

        print(

            self.df[target]

            .value_counts(normalize=True)

            * 100
        )

    def split(self, target):

        self.X = self.df.drop(columns=[target])

        self.y = self.df[target]

        print("\nFeatures :", self.X.shape)

        print("Labels :", self.y.shape)

        return self.X, self.y