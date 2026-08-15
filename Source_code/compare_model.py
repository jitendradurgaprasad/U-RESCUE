import pandas as pd
import time

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier

# Load dataset
df = pd.read_csv(
    r"C:\Users\M jitendra\OneDrive\Desktop\U RESCUE\Datasets\Derived\training_dataset_sample.csv"
)

# Features
X = df[
    [
        "Elevation",
        "Slope",
        "Aspect",
        "FlowAccum",
        "FlowDir"
    ]
]

# Target
y = df["FloodRisk"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

models = {
    "Decision Tree": DecisionTreeClassifier(random_state=42),

    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    ),

    "Gradient Boosting": GradientBoostingClassifier(
        random_state=42
    )
}

results = []

for name, model in models.items():

    print(f"\nTraining {name}...")

    start = time.time()

    model.fit(X_train, y_train)

    train_time = time.time() - start

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)

    results.append(
        [
            name,
            round(accuracy, 6),
            round(train_time, 2)
        ]
    )

    print(f"Accuracy: {accuracy:.6f}")
    print(f"Training Time: {train_time:.2f} sec")

print("\n==============================")
print("MODEL COMPARISON")
print("==============================")

for row in results:
    print(row)

results_df = pd.DataFrame(
    results,
    columns=[
        "Model",
        "Accuracy",
        "Training_Time_sec"
    ]
)

results_df.to_csv(
    r"C:\Users\M jitendra\OneDrive\Desktop\U RESCUE\Results\model_comparison.csv",
    index=False
)

print("\nResults saved successfully.")