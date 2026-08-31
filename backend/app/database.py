from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


# ============================================================
# Database configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE_DIR = BASE_DIR / "data"

DATABASE_FILE = DATABASE_DIR / "sentinal_ai.db"


# ============================================================
# Alert status constants
# ============================================================

ALERT_STATUS_NONE = "NONE"
ALERT_STATUS_NEW = "NEW"
ALERT_STATUS_UNDER_REVIEW = "UNDER_REVIEW"
ALERT_STATUS_RESOLVED = "RESOLVED"


VALID_ALERT_STATUSES = {
    ALERT_STATUS_NONE,
    ALERT_STATUS_NEW,
    ALERT_STATUS_UNDER_REVIEW,
    ALERT_STATUS_RESOLVED,
}


# ============================================================
# Database connection
# ============================================================

def get_connection() -> sqlite3.Connection:
    """
    Create and return a connection to the Sentinal AI SQLite
    database.

    The database directory is created automatically if it does
    not already exist.
    """

    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_FILE,
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# Determine initial alert status
# ============================================================

def determine_alert_status(
    risk_level: str,
) -> str:
    """
    Determine the initial alert status for a transaction.

    Only HIGH and CRITICAL transactions become alerts.

    LOW and MEDIUM transactions do not require alert
    management and therefore receive NONE.
    """

    normalized_risk_level = str(
        risk_level
    ).upper()

    if normalized_risk_level in {
        "HIGH",
        "CRITICAL",
    }:
        return ALERT_STATUS_NEW

    return ALERT_STATUS_NONE


# ============================================================
# Database initialization
# ============================================================

def initialize_database() -> None:
    """
    Create the transactions table if it does not already exist.

    If an older version of the database already exists without
    the alert_status column, migrate it safely.
    """

    connection = get_connection()

    try:
        # ----------------------------------------------------
        # Create the base table.
        # ----------------------------------------------------

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                transaction_id TEXT NOT NULL UNIQUE,
                customer_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,

                amount REAL NOT NULL,
                payment_method TEXT NOT NULL,
                merchant_category TEXT NOT NULL,
                location TEXT NOT NULL,

                account_age_days INTEGER NOT NULL,
                customer_transaction_count INTEGER NOT NULL,
                average_transaction_amount REAL NOT NULL,
                amount_deviation_ratio REAL NOT NULL,
                unusual_amount INTEGER NOT NULL,

                device_age_days INTEGER NOT NULL,
                is_new_device INTEGER NOT NULL,
                device_changes_30d INTEGER NOT NULL,

                location_changes_24h INTEGER NOT NULL,

                transactions_last_10min INTEGER NOT NULL,
                transactions_last_hour INTEGER NOT NULL,
                transactions_last_24h INTEGER NOT NULL,

                failed_attempts_24h INTEGER NOT NULL,
                otp_failures INTEGER NOT NULL,

                transaction_hour INTEGER NOT NULL,
                is_night_transaction INTEGER NOT NULL,
                is_weekend INTEGER NOT NULL,

                ip_risk_score REAL NOT NULL,
                proxy_or_vpn INTEGER NOT NULL,

                card_age_days INTEGER NOT NULL,
                chargeback_history INTEGER NOT NULL,

                fraud_probability REAL NOT NULL,
                fraud_probability_percentage REAL NOT NULL,

                risk_score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                decision TEXT NOT NULL,

                reasons TEXT NOT NULL,
                signals TEXT NOT NULL,

                analyzed_at TEXT NOT NULL,

                alert_status TEXT NOT NULL DEFAULT 'NONE'
            )
            """
        )

        # ----------------------------------------------------
        # Check whether alert_status already exists.
        # ----------------------------------------------------

        columns = connection.execute(
            """
            PRAGMA table_info(transactions)
            """
        ).fetchall()

        column_names = {
            column["name"]
            for column in columns
        }

        # ----------------------------------------------------
        # Migrate an existing database.
        #
        # SQLite does not modify an existing table when
        # CREATE TABLE IF NOT EXISTS is executed.
        #
        # Therefore we explicitly add the missing column.
        # ----------------------------------------------------

        if "alert_status" not in column_names:
            connection.execute(
                """
                ALTER TABLE transactions
                ADD COLUMN alert_status TEXT
                NOT NULL
                DEFAULT 'NONE'
                """
            )

        # ----------------------------------------------------
        # Populate alert status for existing transactions.
        #
        # Existing HIGH / CRITICAL transactions become NEW.
        # Existing LOW / MEDIUM transactions remain NONE.
        #
        # This migration intentionally does not overwrite
        # existing non-NONE statuses.
        # ----------------------------------------------------

        connection.execute(
            """
            UPDATE transactions
            SET alert_status = 'NEW'
            WHERE risk_level IN ('HIGH', 'CRITICAL')
              AND (
                  alert_status IS NULL
                  OR alert_status = 'NONE'
              )
            """
        )

        connection.execute(
            """
            UPDATE transactions
            SET alert_status = 'NONE'
            WHERE risk_level NOT IN ('HIGH', 'CRITICAL')
              AND (
                  alert_status IS NULL
                  OR alert_status = ''
              )
            """
        )

        connection.commit()

    finally:
        connection.close()


# ============================================================
# Save transaction
# ============================================================

def save_transaction(
    transaction: dict[str, Any],
    analysis: dict[str, Any],
) -> None:
    """
    Save a completed transaction analysis.

    If the transaction ID already exists, the existing record is
    updated with the latest transaction and analysis data.

    IMPORTANT:
    alert_status is intentionally NOT overwritten when an
    existing transaction is updated.

    This preserves analyst actions such as:

        NEW
        UNDER_REVIEW
        RESOLVED

    when the same transaction is analyzed again.
    """

    connection = get_connection()

    try:
        alert_status = determine_alert_status(
            analysis["risk_level"]
        )

        connection.execute(
            """
            INSERT INTO transactions (
                transaction_id,
                customer_id,
                timestamp,

                amount,
                payment_method,
                merchant_category,
                location,

                account_age_days,
                customer_transaction_count,
                average_transaction_amount,
                amount_deviation_ratio,
                unusual_amount,

                device_age_days,
                is_new_device,
                device_changes_30d,

                location_changes_24h,

                transactions_last_10min,
                transactions_last_hour,
                transactions_last_24h,

                failed_attempts_24h,
                otp_failures,

                transaction_hour,
                is_night_transaction,
                is_weekend,

                ip_risk_score,
                proxy_or_vpn,

                card_age_days,
                chargeback_history,

                fraud_probability,
                fraud_probability_percentage,

                risk_score,
                risk_level,
                decision,

                reasons,
                signals,

                analyzed_at,

                alert_status
            )
            VALUES (
                :transaction_id,
                :customer_id,
                :timestamp,

                :amount,
                :payment_method,
                :merchant_category,
                :location,

                :account_age_days,
                :customer_transaction_count,
                :average_transaction_amount,
                :amount_deviation_ratio,
                :unusual_amount,

                :device_age_days,
                :is_new_device,
                :device_changes_30d,

                :location_changes_24h,

                :transactions_last_10min,
                :transactions_last_hour,
                :transactions_last_24h,

                :failed_attempts_24h,
                :otp_failures,

                :transaction_hour,
                :is_night_transaction,
                :is_weekend,

                :ip_risk_score,
                :proxy_or_vpn,

                :card_age_days,
                :chargeback_history,

                :fraud_probability,
                :fraud_probability_percentage,

                :risk_score,
                :risk_level,
                :decision,

                :reasons,
                :signals,

                :analyzed_at,

                :alert_status
            )

            ON CONFLICT(transaction_id)
            DO UPDATE SET

                customer_id = excluded.customer_id,
                timestamp = excluded.timestamp,

                amount = excluded.amount,
                payment_method = excluded.payment_method,
                merchant_category = excluded.merchant_category,
                location = excluded.location,

                account_age_days =
                    excluded.account_age_days,

                customer_transaction_count =
                    excluded.customer_transaction_count,

                average_transaction_amount =
                    excluded.average_transaction_amount,

                amount_deviation_ratio =
                    excluded.amount_deviation_ratio,

                unusual_amount =
                    excluded.unusual_amount,

                device_age_days =
                    excluded.device_age_days,

                is_new_device =
                    excluded.is_new_device,

                device_changes_30d =
                    excluded.device_changes_30d,

                location_changes_24h =
                    excluded.location_changes_24h,

                transactions_last_10min =
                    excluded.transactions_last_10min,

                transactions_last_hour =
                    excluded.transactions_last_hour,

                transactions_last_24h =
                    excluded.transactions_last_24h,

                failed_attempts_24h =
                    excluded.failed_attempts_24h,

                otp_failures =
                    excluded.otp_failures,

                transaction_hour =
                    excluded.transaction_hour,

                is_night_transaction =
                    excluded.is_night_transaction,

                is_weekend =
                    excluded.is_weekend,

                ip_risk_score =
                    excluded.ip_risk_score,

                proxy_or_vpn =
                    excluded.proxy_or_vpn,

                card_age_days =
                    excluded.card_age_days,

                chargeback_history =
                    excluded.chargeback_history,

                fraud_probability =
                    excluded.fraud_probability,

                fraud_probability_percentage =
                    excluded.fraud_probability_percentage,

                risk_score =
                    excluded.risk_score,

                risk_level =
                    excluded.risk_level,

                decision =
                    excluded.decision,

                reasons =
                    excluded.reasons,

                signals =
                    excluded.signals,

                analyzed_at =
                    excluded.analyzed_at
            """,
            {
                "transaction_id": transaction["transaction_id"],
                "customer_id": transaction["customer_id"],
                "timestamp": transaction["timestamp"],

                "amount": transaction["amount"],
                "payment_method": transaction["payment_method"],
                "merchant_category": transaction["merchant_category"],
                "location": transaction["location"],

                "account_age_days":
                    transaction["account_age_days"],

                "customer_transaction_count":
                    transaction["customer_transaction_count"],

                "average_transaction_amount":
                    transaction["average_transaction_amount"],

                "amount_deviation_ratio":
                    transaction["amount_deviation_ratio"],

                "unusual_amount":
                    transaction["unusual_amount"],

                "device_age_days":
                    transaction["device_age_days"],

                "is_new_device":
                    transaction["is_new_device"],

                "device_changes_30d":
                    transaction["device_changes_30d"],

                "location_changes_24h":
                    transaction["location_changes_24h"],

                "transactions_last_10min":
                    transaction["transactions_last_10min"],

                "transactions_last_hour":
                    transaction["transactions_last_hour"],

                "transactions_last_24h":
                    transaction["transactions_last_24h"],

                "failed_attempts_24h":
                    transaction["failed_attempts_24h"],

                "otp_failures":
                    transaction["otp_failures"],

                "transaction_hour":
                    transaction["transaction_hour"],

                "is_night_transaction":
                    transaction["is_night_transaction"],

                "is_weekend":
                    transaction["is_weekend"],

                "ip_risk_score":
                    transaction["ip_risk_score"],

                "proxy_or_vpn":
                    transaction["proxy_or_vpn"],

                "card_age_days":
                    transaction["card_age_days"],

                "chargeback_history":
                    transaction["chargeback_history"],

                "fraud_probability":
                    analysis["fraud_probability"],

                "fraud_probability_percentage":
                    analysis[
                        "fraud_probability_percentage"
                    ],

                "risk_score":
                    analysis["risk_score"],

                "risk_level":
                    analysis["risk_level"],

                "decision":
                    analysis["decision"],

                "reasons":
                    json.dumps(
                        analysis["reasons"]
                    ),

                "signals":
                    json.dumps(
                        analysis["signals"]
                    ),

                "analyzed_at":
                    analysis["analyzed_at"],

                "alert_status":
                    alert_status,
            },
        )

        connection.commit()

    finally:
        connection.close()


# ============================================================
# Update alert status
# ============================================================

def update_alert_status(
    transaction_id: str,
    alert_status: str,
) -> dict[str, Any] | None:
    """
    Update the alert status of a transaction.

    Returns the updated transaction.

    Returns None if the transaction does not exist.
    """

    normalized_status = str(
        alert_status
    ).upper().strip()

    if normalized_status not in VALID_ALERT_STATUSES:
        raise ValueError(
            f"Invalid alert status: {alert_status}"
        )

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE transactions
            SET alert_status = ?
            WHERE transaction_id = ?
            """,
            (
                normalized_status,
                transaction_id,
            ),
        )

        if cursor.rowcount == 0:
            connection.commit()
            return None

        connection.commit()

        row = connection.execute(
            """
            SELECT *
            FROM transactions
            WHERE transaction_id = ?
            """,
            (transaction_id,),
        ).fetchone()

        if row is None:
            return None

        return row_to_transaction(row)

    finally:
        connection.close()


# ============================================================
# Convert database row to API-friendly dictionary
# ============================================================

def row_to_transaction(
    row: sqlite3.Row,
) -> dict[str, Any]:
    """
    Convert a SQLite row into a normal Python dictionary.
    """

    data = dict(row)

    data["reasons"] = json.loads(
        data["reasons"]
    )

    data["signals"] = json.loads(
        data["signals"]
    )

    # --------------------------------------------------------
    # Backward compatibility.
    #
    # This protects against unexpected NULL values from an
    # older database.
    # --------------------------------------------------------

    if not data.get("alert_status"):
        data["alert_status"] = determine_alert_status(
            data.get(
                "risk_level",
                "LOW",
            )
        )

    return data


# ============================================================
# Get transaction history
# ============================================================

def get_transactions(
    limit: int = 100,
) -> list[dict[str, Any]]:
    """
    Return the most recently analyzed transactions.
    """

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT *
            FROM transactions
            ORDER BY analyzed_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [
            row_to_transaction(row)
            for row in rows
        ]

    finally:
        connection.close()


# ============================================================
# Get a single transaction
# ============================================================

def get_transaction(
    transaction_id: str,
) -> dict[str, Any] | None:
    """
    Return one transaction by transaction ID.

    Returns None when the transaction does not exist.
    """

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT *
            FROM transactions
            WHERE transaction_id = ?
            """,
            (transaction_id,),
        ).fetchone()

        if row is None:
            return None

        return row_to_transaction(row)

    finally:
        connection.close()