from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder


# ============================================================
# Configuration
# ============================================================

RANDOM_SEED = 42

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DATA_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "transactions.csv"
)

PROCESSED_DATA_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)

PREPROCESSOR_FILE = (
    PROCESSED_DATA_DIR
    / "preprocessor.joblib"
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
# Columns that must not be used as model features
# ============================================================

DROP_COLUMNS = [
    "transaction_id",
    "customer_id",
    "timestamp",
    "fraud_probability_hidden",
]


# ============================================================
# Target column
# ============================================================

TARGET_COLUMN = "fraud_label"


# ============================================================
# Main preprocessing function
# ============================================================

def prepare_data() -> None:
    print("=" * 70)
    print("SENTINAL AI - DATA PREPROCESSING")
    print("=" * 70)

    # --------------------------------------------------------
    # Check input file
    # --------------------------------------------------------

    if not RAW_DATA_FILE.exists():
        raise FileNotFoundError(
            f"Raw dataset was not found:\n{RAW_DATA_FILE}\n\n"
            "Run generate_dataset.py first."
        )

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Load raw dataset
    # --------------------------------------------------------

    print()
    print("Loading raw dataset...")
    print(f"File: {RAW_DATA_FILE}")

    dataframe = pd.read_csv(
        RAW_DATA_FILE
    )

    print(
        f"Loaded {len(dataframe):,} transactions."
    )

    # --------------------------------------------------------
    # Validate required target column
    # --------------------------------------------------------

    if TARGET_COLUMN not in dataframe.columns:
        raise ValueError(
            f"Required target column '{TARGET_COLUMN}' "
            "was not found in the dataset."
        )

    # --------------------------------------------------------
    # Check for missing values
    # --------------------------------------------------------

    print()
    print("Checking missing values...")

    missing_values = dataframe.isnull().sum()

    total_missing = int(
        missing_values.sum()
    )

    if total_missing == 0:
        print("No missing values detected.")
    else:
        print(
            f"Detected {total_missing} missing values."
        )

        print(
            missing_values[
                missing_values > 0
            ]
        )

        # Fill numerical columns with median.
        numerical_columns = (
            dataframe.select_dtypes(
                include=["number"]
            ).columns
        )

        for column in numerical_columns:
            if dataframe[column].isnull().any():
                dataframe[column] = dataframe[
                    column
                ].fillna(
                    dataframe[column].median()
                )

        # Fill categorical columns with most
        # frequent value.
        categorical_columns = (
            dataframe.select_dtypes(
                include=["object"]
            ).columns
        )

        for column in categorical_columns:
            if dataframe[column].isnull().any():
                dataframe[column] = dataframe[
                    column
                ].fillna(
                    dataframe[column].mode()[0]
                )

    # --------------------------------------------------------
    # Separate features and target
    # --------------------------------------------------------

    print()
    print("Separating features and target...")

    y = dataframe[TARGET_COLUMN].astype(int)

    X = dataframe.drop(
        columns=[
            TARGET_COLUMN,
            *DROP_COLUMNS,
        ],
        errors="ignore",
    )

    print(
        f"Raw feature count: {len(X.columns)}"
    )

    # --------------------------------------------------------
    # Display removed columns
    # --------------------------------------------------------

    print()
    print("Columns excluded from ML features:")

    for column in [
        TARGET_COLUMN,
        *DROP_COLUMNS,
    ]:
        print(f"  - {column}")

    # --------------------------------------------------------
    # Identify categorical and numerical columns
    # --------------------------------------------------------

    categorical_columns = (
        X.select_dtypes(
            include=["object"]
        ).columns.tolist()
    )

    numerical_columns = (
        X.select_dtypes(
            include=["number"]
        ).columns.tolist()
    )

    print()
    print(
        f"Numerical features: {len(numerical_columns)}"
    )

    print(
        f"Categorical features: {len(categorical_columns)}"
    )

    if categorical_columns:
        print()
        print("Categorical columns:")

        for column in categorical_columns:
            print(f"  - {column}")

    # --------------------------------------------------------
    # Create preprocessing pipeline
    # --------------------------------------------------------
    #
    # Numerical values are kept as they are.
    #
    # Categorical values such as:
    #
    #   upi
    #   credit_card
    #   debit_card
    #
    # are converted into machine-readable
    # one-hot encoded columns.
    #
    # handle_unknown="ignore" is important because
    # the production system may later receive a category
    # that was not present in the training data.
    # --------------------------------------------------------

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
                categorical_columns,
            ),
            (
                "numerical",
                "passthrough",
                numerical_columns,
            ),
        ],
        remainder="drop",
    )

    # --------------------------------------------------------
    # Split training and testing data
    # --------------------------------------------------------

    print()
    print("Splitting dataset...")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_SEED,
        stratify=y,
    )

    print(
        f"Training transactions: {len(X_train):,}"
    )

    print(
        f"Testing transactions: {len(X_test):,}"
    )

    # --------------------------------------------------------
    # Fit preprocessing ONLY on training data
    # --------------------------------------------------------
    #
    # This is important.
    #
    # We do NOT fit the preprocessor on the complete dataset.
    #
    # Otherwise information from the test set could leak
    # into the training process.
    # --------------------------------------------------------

    print()
    print("Fitting preprocessing pipeline...")

    X_train_processed = preprocessor.fit_transform(
        X_train
    )

    X_test_processed = preprocessor.transform(
        X_test
    )

    # --------------------------------------------------------
    # Get processed feature names
    # --------------------------------------------------------

    feature_names = (
        preprocessor.get_feature_names_out()
    )

    print(
        f"Processed feature count: {len(feature_names)}"
    )

    # --------------------------------------------------------
    # Convert processed arrays to DataFrames
    # --------------------------------------------------------

    X_train_processed = pd.DataFrame(
        X_train_processed,
        columns=feature_names,
        index=X_train.index,
    )

    X_test_processed = pd.DataFrame(
        X_test_processed,
        columns=feature_names,
        index=X_test.index,
    )

    y_train_processed = pd.DataFrame(
        {
            TARGET_COLUMN: y_train
        },
        index=y_train.index,
    )

    y_test_processed = pd.DataFrame(
        {
            TARGET_COLUMN: y_test
        },
        index=y_test.index,
    )

    # --------------------------------------------------------
    # Reset indexes
    # --------------------------------------------------------

    X_train_processed = (
        X_train_processed.reset_index(
            drop=True
        )
    )

    X_test_processed = (
        X_test_processed.reset_index(
            drop=True
        )
    )

    y_train_processed = (
        y_train_processed.reset_index(
            drop=True
        )
    )

    y_test_processed = (
        y_test_processed.reset_index(
            drop=True
        )
    )

    # --------------------------------------------------------
    # Save processed datasets
    # --------------------------------------------------------

    print()
    print("Saving processed datasets...")

    X_train_processed.to_csv(
        X_TRAIN_FILE,
        index=False,
    )

    X_test_processed.to_csv(
        X_TEST_FILE,
        index=False,
    )

    y_train_processed.to_csv(
        Y_TRAIN_FILE,
        index=False,
    )

    y_test_processed.to_csv(
        Y_TEST_FILE,
        index=False,
    )

    # --------------------------------------------------------
    # Save preprocessing pipeline
    # --------------------------------------------------------

    joblib.dump(
        preprocessor,
        PREPROCESSOR_FILE,
    )

    # --------------------------------------------------------
    # Print class distribution
    # --------------------------------------------------------

    train_fraud_count = int(
        y_train.sum()
    )

    train_legitimate_count = (
        len(y_train) - train_fraud_count
    )

    test_fraud_count = int(
        y_test.sum()
    )

    test_legitimate_count = (
        len(y_test) - test_fraud_count
    )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("PREPROCESSING COMPLETED SUCCESSFULLY")
    print("=" * 70)

    print()
    print("DATASET")
    print("-" * 70)

    print(
        f"Original transactions : {len(dataframe):,}"
    )

    print(
        f"Training transactions : {len(X_train_processed):,}"
    )

    print(
        f"Testing transactions  : {len(X_test_processed):,}"
    )

    print(
        f"Processed features    : {len(feature_names):,}"
    )

    print()
    print("TRAINING CLASS DISTRIBUTION")
    print("-" * 70)

    print(
        f"Legitimate : {train_legitimate_count:,}"
    )

    print(
        f"Fraudulent : {train_fraud_count:,}"
    )

    print()
    print("TEST CLASS DISTRIBUTION")
    print("-" * 70)

    print(
        f"Legitimate : {test_legitimate_count:,}"
    )

    print(
        f"Fraudulent : {test_fraud_count:,}"
    )

    print()
    print("OUTPUT FILES")
    print("-" * 70)

    print(
        f"X_train : {X_TRAIN_FILE}"
    )

    print(
        f"X_test  : {X_TEST_FILE}"
    )

    print(
        f"y_train : {Y_TRAIN_FILE}"
    )

    print(
        f"y_test  : {Y_TEST_FILE}"
    )

    print(
        f"Pipeline: {PREPROCESSOR_FILE}"
    )

    print("=" * 70)


if __name__ == "__main__":
    prepare_data()