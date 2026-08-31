from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.database import (
    ALERT_STATUS_NEW,
    ALERT_STATUS_NONE,
    ALERT_STATUS_RESOLVED,
    ALERT_STATUS_UNDER_REVIEW,
    VALID_ALERT_STATUSES,
    get_transaction,
    get_transactions,
    initialize_database,
    save_transaction,
    update_alert_status,
)

from app.risk_engine import calculate_risk


# ============================================================
# Project paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_FILE = (
    BASE_DIR
    / "ml"
    / "models"
    / "fraud_risk_model.joblib"
)

PREPROCESSOR_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "preprocessor.joblib"
)


# ============================================================
# Load ML components
# ============================================================

model = None
preprocessor = None


def load_ml_components() -> None:
    """
    Load the trained ML model and preprocessing pipeline.

    The application can still start if these files are missing.
    Health status will indicate that the ML components are
    unavailable.
    """

    global model
    global preprocessor

    if MODEL_FILE.exists():
        model = joblib.load(
            MODEL_FILE
        )

    if PREPROCESSOR_FILE.exists():
        preprocessor = joblib.load(
            PREPROCESSOR_FILE
        )


# Load components when the API starts.
load_ml_components()


# ============================================================
# Initialize database
# ============================================================

initialize_database()


# ============================================================
# FastAPI application
# ============================================================

app = FastAPI(
    title="Sentinal AI",
    description=(
        "AI-Powered Payment Risk Intelligence "
        "& Investigation Platform"
    ),
    version="0.1.0",
)


# ============================================================
# CORS configuration
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Request models
# ============================================================

class TransactionRequest(BaseModel):
    """
    Transaction information accepted by the risk API.

    These fields correspond to the features used by the
    trained ML model and the risk engine.
    """

    transaction_id: str = Field(
        default="TXN-API-TEST",
        description="Unique transaction identifier.",
    )

    customer_id: str = Field(
        default="CUST-API-TEST",
        description="Customer identifier.",
    )

    timestamp: str = Field(
        default="2025-06-15 14:30:00",
        description="Transaction timestamp.",
    )

    amount: float = Field(
        default=1000.0,
        ge=0,
        description="Transaction amount.",
    )

    payment_method: str = Field(
        default="upi",
        description="Payment method.",
    )

    merchant_category: str = Field(
        default="grocery",
        description="Merchant category.",
    )

    account_age_days: int = Field(
        default=365,
        ge=0,
        description="Age of the customer account in days.",
    )

    customer_transaction_count: int = Field(
        default=100,
        ge=0,
        description="Historical transaction count.",
    )

    average_transaction_amount: float = Field(
        default=1000.0,
        ge=0,
        description="Customer's average transaction amount.",
    )

    amount_deviation_ratio: float = Field(
        default=1.0,
        ge=0,
        description="Transaction amount deviation ratio.",
    )

    unusual_amount: int = Field(
        default=0,
        ge=0,
        le=1,
        description="Whether the amount is considered unusual.",
    )

    device_age_days: int = Field(
        default=180,
        ge=0,
        description="Age of the device in days.",
    )

    is_new_device: int = Field(
        default=0,
        ge=0,
        le=1,
        description="Whether the device is new.",
    )

    device_changes_30d: int = Field(
        default=0,
        ge=0,
        description="Number of device changes in 30 days.",
    )

    location: str = Field(
        default="Mumbai",
        description="Transaction location.",
    )

    location_changes_24h: int = Field(
        default=0,
        ge=0,
        description="Location changes during the last 24 hours.",
    )

    transactions_last_10min: int = Field(
        default=1,
        ge=0,
        description="Transactions during the last 10 minutes.",
    )

    transactions_last_hour: int = Field(
        default=2,
        ge=0,
        description="Transactions during the last hour.",
    )

    transactions_last_24h: int = Field(
        default=5,
        ge=0,
        description="Transactions during the last 24 hours.",
    )

    failed_attempts_24h: int = Field(
        default=0,
        ge=0,
        description="Failed authentication attempts.",
    )

    otp_failures: int = Field(
        default=0,
        ge=0,
        description="OTP verification failures.",
    )

    transaction_hour: int = Field(
        default=14,
        ge=0,
        le=23,
        description="Transaction hour.",
    )

    is_night_transaction: int = Field(
        default=0,
        ge=0,
        le=1,
        description="Whether the transaction occurred at night.",
    )

    is_weekend: int = Field(
        default=0,
        ge=0,
        le=1,
        description="Whether the transaction occurred on a weekend.",
    )

    ip_risk_score: float = Field(
        default=10.0,
        ge=0,
        le=100,
        description="IP risk score.",
    )

    proxy_or_vpn: int = Field(
        default=0,
        ge=0,
        le=1,
        description="Whether a proxy or VPN was detected.",
    )

    card_age_days: int = Field(
        default=500,
        ge=0,
        description="Age of the payment card.",
    )

    chargeback_history: int = Field(
        default=0,
        ge=0,
        le=1,
        description="Whether the customer has chargeback history.",
    )


class AlertStatusRequest(BaseModel):
    """
    Request body used to update the workflow status of
    an alert.
    """

    alert_status: str = Field(
        ...,
        description=(
            "Alert workflow status. "
            "Allowed values: NONE, NEW, UNDER_REVIEW, RESOLVED."
        ),
    )


# ============================================================
# Response models
# ============================================================

class RiskAnalysisResponse(BaseModel):
    """
    Response returned after transaction analysis.
    """

    transaction_id: str

    fraud_probability: float

    fraud_probability_percentage: float

    risk_score: int

    risk_level: str

    decision: str

    reasons: list[str]

    signals: list[dict[str, Any]]

    analyzed_at: str


# ============================================================
# Root endpoint
# ============================================================

@app.get("/")
def root():
    """
    Basic API information.
    """

    return {
        "name": "Sentinal AI",
        "message": (
            "AI-Powered Payment Risk Intelligence "
            "Platform"
        ),
        "status": "online",
        "version": "0.1.0",
    }


# ============================================================
# Health endpoint
# ============================================================

@app.get("/api/health")
def health_check():
    """
    Return backend and ML component health.
    """

    ml_status = (
        model is not None
        and preprocessor is not None
    )

    return {
        "status": "healthy",
        "service": "sentinal-ai-backend",
        "ml_model_loaded": model is not None,
        "preprocessor_loaded": preprocessor is not None,
        "risk_engine_available": True,
        "ml_pipeline_ready": ml_status,
    }


# ============================================================
# Risk analysis endpoint
# ============================================================

@app.post(
    "/api/v1/risk/analyze",
    response_model=RiskAnalysisResponse,
)
def analyze_transaction(
    transaction: TransactionRequest,
):
    """
    Analyze a payment transaction using the trained ML model
    and the Sentinal AI risk engine.

    Successful analyses are persisted to the SQLite database.
    """

    # --------------------------------------------------------
    # Verify ML components
    # --------------------------------------------------------

    if model is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "ML model is not available. "
                "Verify that ml/models/"
                "fraud_risk_model.joblib exists."
            ),
        )

    if preprocessor is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "ML preprocessor is not available. "
                "Verify that data/processed/"
                "preprocessor.joblib exists."
            ),
        )

    # --------------------------------------------------------
    # Convert request to dictionary
    # --------------------------------------------------------

    transaction_data = transaction.model_dump()

    # --------------------------------------------------------
    # Create DataFrame
    #
    # The preprocessing pipeline expects the same raw feature
    # names that were present during training.
    # --------------------------------------------------------

    transaction_dataframe = pd.DataFrame(
        [transaction_data]
    )

    # --------------------------------------------------------
    # Remove fields that were intentionally excluded during
    # model training.
    #
    # These include identifiers and timestamp information.
    # --------------------------------------------------------

    model_input = transaction_dataframe.drop(
        columns=[
            "transaction_id",
            "customer_id",
            "timestamp",
        ],
        errors="ignore",
    )

    # --------------------------------------------------------
    # Transform transaction using the SAME preprocessor that
    # was fitted during training.
    # --------------------------------------------------------

    try:
        processed_transaction = (
            preprocessor.transform(
                model_input
            )
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to preprocess transaction: "
                f"{error}"
            ),
        ) from error

    # --------------------------------------------------------
    # Generate ML prediction
    # --------------------------------------------------------

    try:
        fraud_probability = float(
            model.predict_proba(
                processed_transaction
            )[0][1]
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to generate ML prediction: "
                f"{error}"
            ),
        ) from error

    # --------------------------------------------------------
    # Run the hybrid risk engine
    # --------------------------------------------------------

    risk_result = calculate_risk(
        transaction=transaction_data,
        fraud_probability=fraud_probability,
    )

    # --------------------------------------------------------
    # Create analysis timestamp
    # --------------------------------------------------------

    from datetime import datetime, timezone

    analyzed_at = datetime.now(
        timezone.utc
    ).isoformat()

    # --------------------------------------------------------
    # Prepare database record
    # --------------------------------------------------------

    analysis_data = {
        "fraud_probability": (
            risk_result.fraud_probability
        ),
        "fraud_probability_percentage": round(
            risk_result.fraud_probability * 100,
            2,
        ),
        "risk_score": risk_result.risk_score,
        "risk_level": risk_result.risk_level,
        "decision": risk_result.decision,
        "reasons": risk_result.reasons,
        "signals": risk_result.signals,
        "analyzed_at": analyzed_at,
    }

    # --------------------------------------------------------
    # Persist completed analysis
    # --------------------------------------------------------

    try:
        save_transaction(
            transaction=transaction_data,
            analysis=analysis_data,
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Risk analysis completed, but the transaction "
                "could not be saved to the database: "
                f"{error}"
            ),
        ) from error

    # --------------------------------------------------------
    # Return final analysis
    # --------------------------------------------------------

    return RiskAnalysisResponse(
        transaction_id=transaction.transaction_id,
        fraud_probability=(
            risk_result.fraud_probability
        ),
        fraud_probability_percentage=round(
            risk_result.fraud_probability * 100,
            2,
        ),
        risk_score=risk_result.risk_score,
        risk_level=risk_result.risk_level,
        decision=risk_result.decision,
        reasons=risk_result.reasons,
        signals=risk_result.signals,
        analyzed_at=analyzed_at,
    )


# ============================================================
# Transaction history endpoint
# ============================================================

@app.get(
    "/api/v1/transactions",
)
def transaction_history(
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
        description="Maximum number of transactions to return.",
    ),
):
    """
    Return recently analyzed transactions.

    Transactions are returned newest first.
    """

    try:
        transactions = get_transactions(
            limit=limit
        )

        return {
            "count": len(transactions),
            "transactions": transactions,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to retrieve transaction history: "
                f"{error}"
            ),
        ) from error


# ============================================================
# Single transaction endpoint
# ============================================================

@app.get(
    "/api/v1/transactions/{transaction_id}",
)
def transaction_details(
    transaction_id: str,
):
    """
    Return a single analyzed transaction.
    """

    try:
        transaction = get_transaction(
            transaction_id
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to retrieve transaction: "
                f"{error}"
            ),
        ) from error

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Transaction '{transaction_id}' "
                "was not found."
            ),
        )

    return transaction


# ============================================================
# Alert status endpoint
# ============================================================

@app.patch(
    "/api/v1/transactions/{transaction_id}/alert-status",
)
def change_alert_status(
    transaction_id: str,
    request: AlertStatusRequest,
):
    """
    Update the workflow status of a transaction alert.

    Supported statuses:

        NONE
        NEW
        UNDER_REVIEW
        RESOLVED
    """

    # --------------------------------------------------------
    # Normalize the requested status.
    # --------------------------------------------------------

    requested_status = (
        request.alert_status
        .upper()
        .strip()
    )

    # --------------------------------------------------------
    # Validate status.
    # --------------------------------------------------------

    if requested_status not in VALID_ALERT_STATUSES:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid alert status.",
                "allowed_statuses": sorted(
                    VALID_ALERT_STATUSES
                ),
            },
        )

    # --------------------------------------------------------
    # Retrieve the transaction first.
    #
    # This gives the API a clear 404 response rather than
    # silently updating zero rows.
    # --------------------------------------------------------

    try:
        existing_transaction = get_transaction(
            transaction_id
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to retrieve transaction: "
                f"{error}"
            ),
        ) from error

    if existing_transaction is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Transaction '{transaction_id}' "
                "was not found."
            ),
        )

    # --------------------------------------------------------
    # Only HIGH and CRITICAL transactions should normally
    # participate in alert workflow management.
    #
    # NONE is allowed so an alert can be cleared if required.
    # --------------------------------------------------------

    risk_level = str(
        existing_transaction.get(
            "risk_level",
            "LOW",
        )
    ).upper()

    if (
        requested_status
        in {
            ALERT_STATUS_NEW,
            ALERT_STATUS_UNDER_REVIEW,
            ALERT_STATUS_RESOLVED,
        }
        and risk_level
        not in {
            "HIGH",
            "CRITICAL",
        }
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Only HIGH or CRITICAL transactions "
                "can have an active alert status."
            ),
        )

    # --------------------------------------------------------
    # Update status.
    # --------------------------------------------------------

    try:
        updated_transaction = update_alert_status(
            transaction_id=transaction_id,
            alert_status=requested_status,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to update alert status: "
                f"{error}"
            ),
        ) from error

    if updated_transaction is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Transaction '{transaction_id}' "
                "was not found."
            ),
        )

    # --------------------------------------------------------
    # Return updated transaction.
    # --------------------------------------------------------

    return {
        "message": "Alert status updated successfully.",
        "transaction_id": transaction_id,
        "alert_status": updated_transaction[
            "alert_status"
        ],
        "transaction": updated_transaction,
    }