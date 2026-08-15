import os
from pathlib import Path

import rasterio
from rasterio.warp import reproject, Resampling
from tqdm import tqdm

# ==========================================================
# PATHS
# ==========================================================

DATASET_FOLDER = Path(r"C:\Users\M jitendra\OneDrive\Desktop\U RESCUE\Datasets")

REFERENCE_RASTER = DATASET_FOLDER / "Derived" / "dem.tif"

OUTPUT_FOLDER = DATASET_FOLDER / "Standardized"

OUTPUT_FOLDER.mkdir(exist_ok=True)

# ==========================================================
# READ REFERENCE RASTER (DEM)
# ==========================================================

with rasterio.open(REFERENCE_RASTER) as ref:

    ref_crs = ref.crs
    ref_transform = ref.transform
    ref_width = ref.width
    ref_height = ref.height
    ref_profile = ref.profile

print("=" * 50)
print("REFERENCE RASTER")
print("=" * 50)

print("CRS:", ref_crs)
print("Size:", ref_width, "x", ref_height)
print("Resolution:", ref.res)

# ==========================================================
# FIND ALL TIFF FILES
# ==========================================================

raster_files = []

for root, dirs, files in os.walk(DATASET_FOLDER):

    # Skip folders we don't want
    if "Standardized" in root:
        continue

    if "Archive" in root:
        continue

    if "v1" in root:
        continue

    for file in files:

        if file.lower().endswith(".tif"):

            raster_files.append(os.path.join(root, file))

print("\nFound Raster Files")
print("=" * 50)

for raster in raster_files:
    print(os.path.basename(raster))

print(f"\nTotal Raster Files: {len(raster_files)}")

# ==========================================================
# RESAMPLING METHOD
# ==========================================================

def get_resampling_method(filename):

    filename = filename.lower()

    categorical = [

        "lulc",

        "soil"

    ]

    for item in categorical:

        if item in filename:

            return Resampling.nearest

    return Resampling.bilinear


# ==========================================================
# STANDARDIZE ONE RASTER
# ==========================================================

def standardize_raster(input_path):

    filename = os.path.basename(input_path)

    output_path = OUTPUT_FOLDER / filename

    method = get_resampling_method(filename)

    print(f"\nProcessing -> {filename}")

    with rasterio.open(input_path) as src:

        profile = src.profile.copy()

        profile.update(

            crs=ref_crs,

            transform=ref_transform,

            width=ref_width,

            height=ref_height

        )

        with rasterio.open(output_path, "w", **profile) as dst:

            reproject(

                source=rasterio.band(src, 1),

                destination=rasterio.band(dst, 1),

                src_transform=src.transform,

                src_crs=src.crs,

                dst_transform=ref_transform,

                dst_crs=ref_crs,

                resampling=method

            )

    print("✓ Completed")


# ==========================================================
# MAIN PROGRAM
# ==========================================================

print("\n")
print("=" * 50)
print("STANDARDIZING DATASETS")
print("=" * 50)

for raster in tqdm(raster_files):

    standardize_raster(raster)

print("\n")
print("=" * 50)
print("ALL DATASETS STANDARDIZED SUCCESSFULLY")
print("=" * 50)