import pandas as pd
df = pd.read_csv(r"C:\Users\M jitendra\OneDrive\Desktop\projects\U RESCUE\Datasets\training_dataset_v2.csv", nrows=5)
print(df.columns.tolist())
print(df.dtypes)