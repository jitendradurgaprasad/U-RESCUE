from pathlib import Path

from core.raster_reader import RasterReader

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STANDARDIZED = PROJECT_ROOT / "Datasets" / "Standardized"

reader = RasterReader(STANDARDIZED)

reader.load_rasters()
reader.summary()
reader.list_layers()