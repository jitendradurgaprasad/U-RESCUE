from pathlib import Path

from core.dataset_manager import DatasetManager
from core.preprocessor import DataPreprocessor
from core.model_trainer import ModelTrainer
from core.evaluator import Evaluator


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET = PROJECT_ROOT / "Datasets" / "training_dataset_v2.csv"

MODELS = PROJECT_ROOT / "Models"


# -------------------------------
# Load Dataset
# -------------------------------

manager = DatasetManager(DATASET)

manager.load()

manager.info()

manager.class_distribution("flood_risk_final")

manager.sample(300000)

X, y = manager.split("flood_risk_final")


# -------------------------------
# Preprocessing
# -------------------------------

preprocessor = DataPreprocessor()

preprocessor.detect_features(
    manager.df,
    "flood_risk_final"
)

# preprocessor.build_pipeline()

# X = preprocessor.fit_transform(X)


# -------------------------------
# Model Training
# -------------------------------

trainer = ModelTrainer(X, y)

trainer.split_data()

trainer.train()

trainer.save(MODELS)


# -------------------------------
# Evaluation
# -------------------------------

evaluator = Evaluator(trainer)

evaluator.evaluate()

evaluator.save(MODELS)


print("\n====================================")
print("U RESCUE MODEL TRAINING COMPLETED")
print("====================================")