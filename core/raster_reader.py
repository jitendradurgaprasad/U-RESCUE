"""
raster_reader.py

Reusable raster loading module for U Rescue.

Author: Medisetti Jitendra Durga Prasad

Purpose:
--------
Loads every standardized raster into memory and verifies that all rasters
share the same spatial properties.

This module becomes the foundation for:

- Feature Extraction
- Flood Prediction
- Safe Zone Engine
- Safe Route Engine
- Backend API
"""

from pathlib import Path

import rasterio
import numpy as np


class RasterReader:
    """
    Reads and validates all standardized raster datasets.
    """

    def __init__(self, raster_directory):

        self.raster_directory = Path(raster_directory)

        self.datasets = {}
        self.metadata = {}

        self.height = None
        self.width = None
        self.transform = None
        self.crs = None

    def load_rasters(self):
        """
        Load every .tif raster inside the directory.
        """

        tif_files = sorted(self.raster_directory.glob("*.tif"))

        if len(tif_files) == 0:
            raise FileNotFoundError(
                f"No GeoTIFF files found in:\n{self.raster_directory}"
            )

        print(f"\nFound {len(tif_files)} raster files.\n")

        for raster_path in tif_files:

            with rasterio.open(raster_path) as src:

                data = src.read(1)

                self.datasets[raster_path.stem] = data

                self.metadata[raster_path.stem] = {
                    "crs": src.crs,
                    "transform": src.transform,
                    "width": src.width,
                    "height": src.height,
                    "nodata": src.nodata,
                    "dtype": src.dtypes[0],
                }

                if self.width is None:

                    self.width = src.width
                    self.height = src.height
                    self.transform = src.transform
                    self.crs = src.crs

                else:

                    self._validate(src, raster_path.name)

        print("All rasters loaded successfully.")

    def _validate(self, src, filename):
        """
        Verify spatial consistency.
        """

        if src.width != self.width:
            raise ValueError(f"{filename} width mismatch.")

        if src.height != self.height:
            raise ValueError(f"{filename} height mismatch.")

        if src.crs != self.crs:
            raise ValueError(f"{filename} CRS mismatch.")

        if src.transform != self.transform:
            raise ValueError(f"{filename} transform mismatch.")

    def get_layer(self, layer_name):
        """
        Return raster array by layer name.
        """

        return self.datasets[layer_name]

    def list_layers(self):
        """
        Print loaded layers.
        """

        print("\nLoaded Layers\n")

        for layer in self.datasets.keys():
            print(layer)

    def summary(self):
        """
        Print raster summary.
        """

        print("\nRaster Summary")
        print("----------------------------")

        print(f"CRS       : {self.crs}")
        print(f"Width     : {self.width}")
        print(f"Height    : {self.height}")
        print(f"Layers    : {len(self.datasets)}")

    @property
    def shape(self):

        return self.height, self.width