"""
location_extractor.py

Extract raster values from latitude/longitude.
Automatically converts WGS84 (EPSG:4326)
to the raster CRS.
"""

from pathlib import Path

import pandas as pd
import rasterio
from pyproj import Transformer


class LocationExtractor:

    def __init__(self, raster_folder):

        self.raster_folder = Path(raster_folder)

        self.layers = {}

        self.transformer = None

        self._load()

    def _load(self):

        tif_files = sorted(self.raster_folder.glob("*.tif"))

        for file in tif_files:

            raster = rasterio.open(file)

            self.layers[file.stem] = raster

        first = next(iter(self.layers.values()))

        self.transformer = Transformer.from_crs(
            "EPSG:4326",
            first.crs,
            always_xy=True
        )

        print(f"{len(self.layers)} raster layers loaded.")

    def extract(self, latitude, longitude):

        x, y = self.transformer.transform(
            longitude,
            latitude
        )

        features = {}

        for name, raster in self.layers.items():

            row, col = raster.index(x, y)

            if (
                row < 0
                or col < 0
                or row >= raster.height
                or col >= raster.width
            ):
                raise ValueError(
                    f"Location is outside raster extent for {name}."
                )

            value = raster.read(1)[row, col]

            features[name] = float(value)

        return pd.DataFrame([features])