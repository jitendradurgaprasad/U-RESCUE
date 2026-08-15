import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import matplotlib.pyplot as plt

# Load sample dataset
df = pd.read_csv(
    r"C:\Users\M jitendra\OneDrive\Desktop\U RESCUE\Datasets\Derived\training_dataset_sample.csv"
)

print("Dataset Shape:", df.shape)

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

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

# Model
rf = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

print("Training model...")

rf.fit(X_train, y_train)

print("Model trained.")

# Prediction
y_pred = rf.predict(X_test)

# Metrics
accuracy = accuracy_score(y_test, y_pred)

print("\nAccuracy:", accuracy)

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save model
joblib.dump(
    rf,
    r"C:\Users\M jitendra\OneDrive\Desktop\U RESCUE\Models\flood_rf_model.pkl"
)

print("\nFeature Importance")

for feature, importance in zip(X.columns, rf.feature_importances_):
    print(f"{feature}: {importance:.4f}")


importance = rf.feature_importances_
features = X.columns

plt.figure(figsize=(8,5))
plt.bar(features, importance)
plt.title("Feature Importance")
plt.tight_layout()

plt.savefig(
    r"C:\Users\M jitendra\OneDrive\Desktop\U RESCUE\Results\feature_importance.png"
)

plt.show()

print("\nModel saved successfully.")
