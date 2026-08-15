import pandas as pd

df = pd.read_csv(
    r"C:\Users\M jitendra\OneDrive\Desktop\u rescue\Datasets\Derived\training_dataset.csv"
)

sample = df.sample(
    n=100000,
    random_state=42
)

sample.to_csv(
    r"C:\Users\M jitendra\OneDrive\Desktop\u rescue\Datasets\Derived\training_dataset_sample.csv",
    index=False
)

print(sample.shape)