"""
feature_extractor.py

Extract aligned raster values into a machine learning dataset.
"""

import numpy as np
import pandas as pd


class FeatureExtractor:

    def __init__(self, raster_reader):

        self.reader = raster_reader

    def extract(self):

        print("\nCreating feature table...\n")

        features = {}

        # Store every raster as a flattened column
        for layer_name, raster in self.reader.datasets.items():

            features[layer_name] = raster.flatten()

        df = pd.DataFrame(features)

        print(f"Initial rows : {len(df):,}")

        # Remove pixels containing NoData values
        mask = np.ones(len(df), dtype=bool)

        for layer_name in self.reader.datasets.keys():

            nodata = self.reader.metadata[layer_name]["nodata"]

            if nodata is not None:
                mask &= df[layer_name] != nodata

        df = df[mask].reset_index(drop=True)

        print(f"Rows after removing NoData : {len(df):,}")

        return df