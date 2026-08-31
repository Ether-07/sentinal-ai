from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


# ============================================================
# Configuration
# ============================================================

RANDOM_SEED = 42

BASE_DIR = Path(__file__).resolve().parents[2]

PROCESSED_DATA_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)

MODEL_DIR = (
    BASE_DIR
    / "ml"
    / "models"
)

MODEL_FILE = (
    MODEL_DIR
    / "fraud_risk_model.joblib"
)

X_TRAIN_FILE = (
    PROCESSED_DATA_DIR
    / "X_train.csv"
)

X_TEST_FILE = (
    PROCESSED_DATA_DIR
    / "X_test.csv"
)

Y_TRAIN_FILE = (
    PROCESSED_DATA_DIR
    / "y_train.csv"
)

Y_TEST_FILE = (
    PROCESSED_DATA_DIR
    / "y_test.csv"
)


# ============================================================
# Model configuration
# ============================================================

MODEL_PARAMETERS = {
    "n_estimators": 250,
    "max_depth": 16,
    "min_samples_split": 8,
    "min_samples_leaf": 3,
    "class_weight": "balanced",
    "random_state": RANDOM_SEED,
    "n_jobs": -1,
}


# ============================================================
# Load processed data
# ============================================================

def load_data():
    required_files = [
        X_TRAIN_FILE,
        X_TEST_FILE,
        Y_TRAIN_FILE,
        Y_TEST_FILE,
    ]

    for file in required_files:
        if not file.exists():
            raise FileNotFoundError(
                f"Required processed file was not found:\n{file}\n\n"
                "Run prepare_data.py first."
            )

    print("Loading processed training data...")

    X_train = pd.read_csv(
        X_TRAIN_FILE
    )

    X_test = pd.read_csv(
        X_TEST_FILE
    )

    y_train = pd.read_csv(
        Y_TRAIN_FILE
    ).squeeze("columns")

    y_test = pd.read_csv(
        Y_TEST_FILE
    ).squeeze("columns")

    return (
        X_train,
        X_test,
        y_train,
        y_test,
    )


# ============================================================
# Train model
# ============================================================

def train_model(X_train, y_train):
    print()
    print("Creating Random Forest model...")

    model = RandomForestClassifier(
        **MODEL_PARAMETERS
    )

    print()
    print("Training model...")
    print(
        f"Training samples: {len(X_train):,}"
    )

    model.fit(
        X_train,
        y_train,
    )

    print("Training completed.")

    return model


# ============================================================
# Evaluate model
# ============================================================

def evaluate_model(
    model,
    X_test,
    y_test,
):
    print()
    print("=" * 70)
    print("MODEL EVALUATION")
    print("=" * 70)

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0,
    )

    roc_auc = roc_auc_score(
        y_test,
        probabilities,
    )

    # --------------------------------------------------------
    # Print metrics
    # --------------------------------------------------------

    print()
    print("Classification Metrics")
    print("-" * 70)

    print(
        f"Accuracy : {accuracy:.4f}"
    )

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall   : {recall:.4f}"
    )

    print(
        f"F1 Score : {f1:.4f}"
    )

    print(
        f"ROC-AUC  : {roc_auc:.4f}"
    )

    # --------------------------------------------------------
    # Classification report
    # --------------------------------------------------------

    print()
    print("Classification Report")
    print("-" * 70)

    print(
        classification_report(
            y_test,
            predictions,
            target_names=[
                "Legitimate",
                "Fraud",
            ],
            zero_division=0,
        )
    )

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    matrix = confusion_matrix(
        y_test,
        predictions,
    )

    print()
    print("Confusion Matrix")
    print("-" * 70)

    print(
        "                 Predicted"
    )

    print(
        "                 Legitimate   Fraud"
    )

    print(
        f"Actual Legitimate  {matrix[0, 0]:>8}   {matrix[0, 1]:>7}"
    )

    print(
        f"Actual Fraud       {matrix[1, 0]:>8}   {matrix[1, 1]:>7}"
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "roc_auc": roc_auc,
        "confusion_matrix": matrix,
    }


# ============================================================
# Feature importance
# ============================================================

def show_feature_importance(
    model,
    feature_names,
):
    print()
    print("=" * 70)
    print("TOP MODEL FEATURES")
    print("=" * 70)

    importance = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": model.feature_importances_,
        }
    )

    importance = importance.sort_values(
        by="importance",
        ascending=False,
    )

    top_features = importance.head(
        15
    )

    for index, row in top_features.iterrows():
        print(
            f"{row['feature']:<55} "
            f"{row['importance']:.5f}"
        )


# ============================================================
# Save model
# ============================================================

def save_model(model):
    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_FILE,
    )

    print()
    print("=" * 70)
    print("MODEL SAVED")
    print("=" * 70)

    print(
        f"Model file: {MODEL_FILE}"
    )


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 70)
    print("SENTINAL AI - FRAUD RISK MODEL TRAINING")
    print("=" * 70)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    (
        X_train,
        X_test,
        y_train,
        y_test,
    ) = load_data()

    print()
    print("Dataset information")
    print("-" * 70)

    print(
        f"Training features : {X_train.shape}"
    )

    print(
        f"Testing features  : {X_test.shape}"
    )

    print(
        f"Training labels   : {y_train.shape}"
    )

    print(
        f"Testing labels    : {y_test.shape}"
    )

    # --------------------------------------------------------
    # Train
    # --------------------------------------------------------

    model = train_model(
        X_train,
        y_train,
    )

    # --------------------------------------------------------
    # Evaluate
    # --------------------------------------------------------

    metrics = evaluate_model(
        model,
        X_test,
        y_test,
    )

    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    show_feature_importance(
        model,
        X_train.columns,
    )

    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    save_model(
        model
    )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("TRAINING PIPELINE COMPLETED")
    print("=" * 70)

    print()
    print(
        f"ROC-AUC : {metrics['roc_auc']:.4f}"
    )

    print(
        f"F1      : {metrics['f1_score']:.4f}"
    )

    print(
        f"Recall  : {metrics['recall']:.4f}"
    )

    print()
    print(
        "The trained model is ready for backend integration."
    )

    print("=" * 70)


if __name__ == "__main__":
    main()