from fastapi.testclient import TestClient

from app.main import app
from app.risk_engine import calculate_risk


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["ml_model_loaded"] is True
    assert data["preprocessor_loaded"] is True
    assert data["risk_engine_available"] is True
    assert data["ml_pipeline_ready"] is True


def test_risk_engine_low_case():
    transaction = {
        "amount": 1000,
        "account_age_days": 365,
        "amount_deviation_ratio": 1,
        "is_new_device": 0,
        "device_changes_30d": 0,
        "location_changes_24h": 0,
        "transactions_last_10min": 1,
        "transactions_last_hour": 2,
        "transactions_last_24h": 5,
        "failed_attempts_24h": 0,
        "otp_failures": 0,
        "is_night_transaction": 0,
        "ip_risk_score": 10,
        "proxy_or_vpn": 0,
        "chargeback_history": 0,
    }

    result = calculate_risk(
        transaction,
        0.02,
    )

    assert result.risk_level == "LOW"
    assert result.decision == "ALLOW"


def test_risk_engine_medium_case():
    transaction = {
        "amount": 50000,
        "account_age_days": 30,
        "amount_deviation_ratio": 3,
        "is_new_device": 0,
        "device_changes_30d": 0,
        "location_changes_24h": 2,
        "transactions_last_10min": 1,
        "transactions_last_hour": 2,
        "transactions_last_24h": 5,
        "failed_attempts_24h": 3,
        "otp_failures": 0,
        "is_night_transaction": 1,
        "ip_risk_score": 70,
        "proxy_or_vpn": 0,
        "chargeback_history": 0,
    }

    result = calculate_risk(
        transaction,
        0.20,
    )

    assert result.risk_level == "MEDIUM"
    assert result.decision == "MONITOR"


def test_risk_engine_high_case():
    transaction = {
        "amount": 100000,
        "account_age_days": 5,
        "amount_deviation_ratio": 6,
        "is_new_device": 1,
        "device_changes_30d": 4,
        "location_changes_24h": 4,
        "transactions_last_10min": 4,
        "transactions_last_hour": 10,
        "transactions_last_24h": 30,
        "failed_attempts_24h": 6,
        "otp_failures": 2,
        "is_night_transaction": 1,
        "ip_risk_score": 80,
        "proxy_or_vpn": 1,
        "chargeback_history": 1,
    }

    result = calculate_risk(
        transaction,
        0.65,
    )

    assert result.risk_level == "HIGH"
    assert result.decision == "REVIEW"


def test_risk_engine_critical_case():
    transaction = {
        "amount": 200000,
        "account_age_days": 2,
        "amount_deviation_ratio": 10,
        "is_new_device": 1,
        "device_changes_30d": 6,
        "location_changes_24h": 6,
        "transactions_last_10min": 8,
        "transactions_last_hour": 15,
        "transactions_last_24h": 40,
        "failed_attempts_24h": 10,
        "otp_failures": 4,
        "is_night_transaction": 1,
        "ip_risk_score": 95,
        "proxy_or_vpn": 1,
        "chargeback_history": 1,
    }

    result = calculate_risk(
        transaction,
        0.95,
    )

    assert result.risk_level == "CRITICAL"
    assert result.decision == "BLOCK"


def test_risk_analysis_endpoint():
    payload = {
        "transaction_id": "TXN-15-6-TEST",
        "customer_id": "CUST-15-6",
        "timestamp": "2026-09-01 01:00:00",
        "amount": 1000,
        "payment_method": "upi",
        "merchant_category": "grocery",
        "account_age_days": 365,
        "customer_transaction_count": 100,
        "average_transaction_amount": 1000,
        "amount_deviation_ratio": 1,
        "unusual_amount": 0,
        "device_age_days": 180,
        "is_new_device": 0,
        "device_changes_30d": 0,
        "location": "Mumbai",
        "location_changes_24h": 0,
        "transactions_last_10min": 1,
        "transactions_last_hour": 2,
        "transactions_last_24h": 5,
        "failed_attempts_24h": 0,
        "otp_failures": 0,
        "transaction_hour": 1,
        "is_night_transaction": 0,
        "is_weekend": 0,
        "ip_risk_score": 10,
        "proxy_or_vpn": 0,
        "card_age_days": 500,
        "chargeback_history": 0,
    }

    response = client.post(
        "/api/v1/risk/analyze",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["transaction_id"] == "TXN-15-6-TEST"
    assert "fraud_probability" in data
    assert "fraud_probability_percentage" in data
    assert "risk_score" in data
    assert "risk_level" in data
    assert "decision" in data
    assert "reasons" in data
    assert "signals" in data
    assert "analyzed_at" in data
