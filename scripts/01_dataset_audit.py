import os
import rasterio
import pandas as pd

# --------------------------------------------------
# CHANGE THIS PATH TO YOUR DATASETS FOLDER
# --------------------------------------------------

DATASET_FOLDER = r"C:\Users\M jitendra\OneDrive\Desktop\U RESCUE\Datasets"

# --------------------------------------------------

records = []

for folder in os.listdir(DATASET_FOLDER):

    folder_path = os.path.join(DATASET_FOLDER, folder)

    if not os.path.isdir(folder_path):
        continue

    for file in os.listdir(folder_path):

        if file.lower().endswith(".tif"):

            path = os.path.join(folder_path, file)

            with rasterio.open(path) as src:

                records.append({

                    "Folder": folder,

                    "Dataset": file,

                    "CRS": str(src.crs),

                    "Resolution": src.res,

                    "Width": src.width,

                    "Height": src.height,

                    "Bands": src.count,

                    "Data Type": src.dtypes[0],

                    "NoData": src.nodata,

                    "Bounds": src.bounds

                })

df = pd.DataFrame(records)

print(df)

df.to_csv("dataset_audit.csv", index=False)

print("\nDataset audit completed!")
print("CSV saved as dataset_audit.csv")