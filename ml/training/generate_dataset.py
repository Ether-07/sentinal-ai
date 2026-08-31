from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# Configuration
# ============================================================

RANDOM_SEED = 42
NUMBER_OF_TRANSACTIONS = 30000

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

OUTPUT_FILE = RAW_DATA_DIR / "transactions.csv"


# ============================================================
# Random generator
# ============================================================

rng = np.random.default_rng(RANDOM_SEED)


# ============================================================
# Helper functions
# ============================================================

def generate_transaction_ids(count: int) -> list[str]:
    numbers = rng.choice(
        np.arange(10000000, 99999999),
        size=count,
        replace=False,
    )

    return [f"TXN-{number}" for number in numbers]


def generate_customer_ids(count: int) -> list[str]:
    customer_numbers = rng.integers(
        100000,
        999999,
        size=count,
    )

    return [f"CUST-{number}" for number in customer_numbers]


def sigmoid(value: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-value))


# ============================================================
# Dataset generation
# ============================================================

def generate_dataset() -> pd.DataFrame:
    count = NUMBER_OF_TRANSACTIONS

    transaction_ids = generate_transaction_ids(count)
    customer_ids = generate_customer_ids(count)

    timestamps = pd.date_range(
        start="2025-01-01",
        end="2025-12-31 23:59:59",
        periods=count,
    )

    # --------------------------------------------------------
    # Basic transaction information
    # --------------------------------------------------------

    amount = np.round(
        np.random.default_rng(RANDOM_SEED).lognormal(
            mean=7.0,
            sigma=1.05,
            size=count,
        ),
        2,
    )

    amount = np.clip(amount, 20, 250000)

    payment_methods = np.array(
        [
            "upi",
            "credit_card",
            "debit_card",
            "netbanking",
            "wallet",
        ]
    )

    payment_method = rng.choice(
        payment_methods,
        size=count,
        p=[0.48, 0.22, 0.16, 0.09, 0.05],
    )

    merchant_categories = np.array(
        [
            "grocery",
            "electronics",
            "fashion",
            "travel",
            "gaming",
            "food",
            "healthcare",
            "utilities",
            "digital_services",
            "luxury",
        ]
    )

    merchant_category = rng.choice(
        merchant_categories,
        size=count,
        p=[
            0.16,
            0.10,
            0.13,
            0.08,
            0.08,
            0.15,
            0.08,
            0.10,
            0.08,
            0.04,
        ],
    )

    # --------------------------------------------------------
    # Customer information
    # --------------------------------------------------------

    account_age_days = rng.integers(
        1,
        3650,
        size=count,
    )

    customer_transaction_count = rng.integers(
        1,
        1500,
        size=count,
    )

    average_transaction_amount = np.round(
        np.clip(
            rng.lognormal(
                mean=6.4,
                sigma=0.75,
                size=count,
            ),
            50,
            100000,
        ),
        2,
    )

    # --------------------------------------------------------
    # Device information
    # --------------------------------------------------------

    device_age_days = rng.integers(
        1,
        1500,
        size=count,
    )

    is_new_device = (
        rng.random(count) < 0.10
    ).astype(int)

    device_changes_30d = rng.poisson(
        lam=0.7,
        size=count,
    )

    device_changes_30d = np.clip(
        device_changes_30d,
        0,
        12,
    )

    # --------------------------------------------------------
    # Location information
    # --------------------------------------------------------

    normal_locations = np.array(
        [
            "Mumbai",
            "Delhi",
            "Bangalore",
            "Hyderabad",
            "Chennai",
            "Pune",
            "Ahmedabad",
            "Kolkata",
            "Jaipur",
            "Surat",
        ]
    )

    location = rng.choice(
        normal_locations,
        size=count,
    )

    location_changes_24h = rng.poisson(
        lam=0.25,
        size=count,
    )

    location_changes_24h = np.clip(
        location_changes_24h,
        0,
        8,
    )

    # --------------------------------------------------------
    # Transaction velocity
    # --------------------------------------------------------

    transactions_last_10min = rng.poisson(
        lam=0.7,
        size=count,
    )

    transactions_last_hour = (
        transactions_last_10min
        + rng.poisson(
            lam=2.0,
            size=count,
        )
    )

    transactions_last_24h = (
        transactions_last_hour
        + rng.poisson(
            lam=8.0,
            size=count,
        )
    )

    # --------------------------------------------------------
    # Authentication / failure behaviour
    # --------------------------------------------------------

    failed_attempts_24h = rng.poisson(
        lam=0.35,
        size=count,
    )

    failed_attempts_24h = np.clip(
        failed_attempts_24h,
        0,
        12,
    )

    otp_failures = rng.poisson(
        lam=0.12,
        size=count,
    )

    otp_failures = np.clip(
        otp_failures,
        0,
        8,
    )

    # --------------------------------------------------------
    # Time-based information
    # --------------------------------------------------------

    transaction_hour = timestamps.hour

    is_night_transaction = (
        (transaction_hour >= 0)
        & (transaction_hour < 5)
    ).astype(int)

    is_weekend = (
        timestamps.dayofweek >= 5
    ).astype(int)

    # --------------------------------------------------------
    # Behavioural deviation
    # --------------------------------------------------------

    amount_deviation_ratio = np.round(
        amount
        / np.maximum(
            average_transaction_amount,
            1,
        ),
        3,
    )

    unusual_amount = (
        amount_deviation_ratio >= 3.0
    ).astype(int)

    # --------------------------------------------------------
    # Network / IP information
    # --------------------------------------------------------

    ip_risk_score = np.round(
        rng.beta(
            a=2.0,
            b=7.0,
            size=count,
        )
        * 100,
        2,
    )

    proxy_or_vpn = (
        rng.random(count) < 0.07
    ).astype(int)

    # --------------------------------------------------------
    # Card / payment behaviour
    # --------------------------------------------------------

    card_age_days = rng.integers(
        1,
        2500,
        size=count,
    )

    chargeback_history = (
        rng.random(count) < 0.035
    ).astype(int)

    # --------------------------------------------------------
    # Build fraud risk signal
    #
    # This is NOT the ML model.
    #
    # We use hidden rules to create realistic labels that
    # the future ML model will attempt to learn.
    # --------------------------------------------------------

    risk_signal = np.full(
        count,
        -4.8,
        dtype=float,
    )

    # High transaction amount
    risk_signal += np.where(
        amount > 50000,
        1.1,
        0,
    )

    risk_signal += np.where(
        amount > 100000,
        1.0,
        0,
    )

    # Amount very different from customer's normal behaviour
    risk_signal += np.where(
        amount_deviation_ratio > 3,
        1.3,
        0,
    )

    risk_signal += np.where(
        amount_deviation_ratio > 6,
        1.1,
        0,
    )

    # Account age
    risk_signal += np.where(
        account_age_days < 30,
        1.5,
        0,
    )

    risk_signal += np.where(
        account_age_days < 7,
        1.1,
        0,
    )

    # New device
    risk_signal += is_new_device * 1.3

    risk_signal += np.where(
        device_changes_30d >= 3,
        0.8,
        0,
    )

    # Location anomalies
    risk_signal += np.where(
        location_changes_24h >= 2,
        1.0,
        0,
    )

    risk_signal += np.where(
        location_changes_24h >= 4,
        1.0,
        0,
    )

    # Transaction velocity
    risk_signal += np.where(
        transactions_last_10min >= 4,
        1.3,
        0,
    )

    risk_signal += np.where(
        transactions_last_hour >= 10,
        1.4,
        0,
    )

    risk_signal += np.where(
        transactions_last_24h >= 30,
        1.1,
        0,
    )

    # Authentication failures
    risk_signal += np.where(
        failed_attempts_24h >= 3,
        1.2,
        0,
    )

    risk_signal += np.where(
        failed_attempts_24h >= 6,
        1.2,
        0,
    )

    risk_signal += np.where(
        otp_failures >= 2,
        0.9,
        0,
    )

    # Night-time activity
    risk_signal += is_night_transaction * 0.6

    # IP / proxy risk
    risk_signal += np.where(
        ip_risk_score >= 70,
        1.0,
        0,
    )

    risk_signal += proxy_or_vpn * 0.8

    # Chargeback history
    risk_signal += chargeback_history * 1.3

    # Payment-method-specific behaviour
    risk_signal += np.where(
        payment_method == "wallet",
        0.15,
        0,
    )

    # Gaming / luxury / digital services can have slightly
    # higher risk in this synthetic environment.
    risk_signal += np.where(
        np.isin(
            merchant_category,
            [
                "gaming",
                "luxury",
                "digital_services",
            ],
        ),
        0.25,
        0,
    )

    # Random noise prevents the dataset from becoming a
    # simple deterministic rule engine.
    risk_signal += rng.normal(
        loc=0,
        scale=0.75,
        size=count,
    )

    fraud_probability = sigmoid(
        risk_signal
    )

    fraud_label = (
        rng.random(count)
        < fraud_probability
    ).astype(int)

    # --------------------------------------------------------
    # Final dataset
    # --------------------------------------------------------

    dataframe = pd.DataFrame(
        {
            "transaction_id": transaction_ids,
            "customer_id": customer_ids,
            "timestamp": timestamps,
            "amount": amount,
            "payment_method": payment_method,
            "merchant_category": merchant_category,
            "account_age_days": account_age_days,
            "customer_transaction_count": customer_transaction_count,
            "average_transaction_amount": average_transaction_amount,
            "amount_deviation_ratio": amount_deviation_ratio,
            "unusual_amount": unusual_amount,
            "device_age_days": device_age_days,
            "is_new_device": is_new_device,
            "device_changes_30d": device_changes_30d,
            "location": location,
            "location_changes_24h": location_changes_24h,
            "transactions_last_10min": transactions_last_10min,
            "transactions_last_hour": transactions_last_hour,
            "transactions_last_24h": transactions_last_24h,
            "failed_attempts_24h": failed_attempts_24h,
            "otp_failures": otp_failures,
            "transaction_hour": transaction_hour,
            "is_night_transaction": is_night_transaction,
            "is_weekend": is_weekend,
            "ip_risk_score": ip_risk_score,
            "proxy_or_vpn": proxy_or_vpn,
            "card_age_days": card_age_days,
            "chargeback_history": chargeback_history,
            "fraud_probability_hidden": np.round(
                fraud_probability,
                4,
            ),
            "fraud_label": fraud_label,
        }
    )

    return dataframe


# ============================================================
# Main
# ============================================================

def main() -> None:
    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("Generating synthetic transaction dataset...")
    print(f"Number of transactions: {NUMBER_OF_TRANSACTIONS}")
    print(f"Random seed: {RANDOM_SEED}")

    dataframe = generate_dataset()

    dataframe.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    fraud_count = int(
        dataframe["fraud_label"].sum()
    )

    legitimate_count = (
        len(dataframe) - fraud_count
    )

    fraud_percentage = (
        fraud_count / len(dataframe)
    ) * 100

    print()
    print("=" * 60)
    print("DATASET GENERATED SUCCESSFULLY")
    print("=" * 60)
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Total transactions: {len(dataframe):,}")
    print(f"Legitimate transactions: {legitimate_count:,}")
    print(f"Fraudulent transactions: {fraud_count:,}")
    print(f"Fraud percentage: {fraud_percentage:.2f}%")
    print(f"Number of features: {len(dataframe.columns)}")
    print("=" * 60)


if __name__ == "__main__":
    main()