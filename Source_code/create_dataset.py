from pathlib import Path

from core.raster_reader import RasterReader
from core.feature_extractor import FeatureExtractor

PROJECT_ROOT = Path(__file__).resolve().parent.parent

STANDARDIZED = PROJECT_ROOT / "Datasets" / "Standardized"

OUTPUT = PROJECT_ROOT / "Datasets" / "training_dataset_v2.csv"

reader = RasterReader(STANDARDIZED)

reader.load_rasters()

extractor = FeatureExtractor(reader)

dataset = extractor.extract()

print("\nSaving CSV...\n")

dataset.to_csv(OUTPUT, index=False)

print("\nDataset created successfully.")

print(f"\nSaved to:\n{OUTPUT}")