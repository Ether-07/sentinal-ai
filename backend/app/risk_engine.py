from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# ============================================================
# Risk thresholds
# ============================================================

LOW_RISK_MAX = 29
MEDIUM_RISK_MAX = 59
HIGH_RISK_MAX = 79


# ============================================================
# Risk result
# ============================================================

@dataclass
class RiskResult:
    risk_score: int
    risk_level: str
    decision: str
    fraud_probability: float
    reasons: list[str]
    signals: list[dict[str, Any]]


# ============================================================
# Helper functions
# ============================================================

def clamp_score(score: float) -> int:
    """
    Keep the final risk score between 0 and 100.
    """

    return int(
        max(
            0,
            min(
                100,
                round(score),
            ),
        )
    )


def classify_risk(
    risk_score: int,
) -> tuple[str, str]:
    """
    Convert a numeric risk score into a risk level
    and recommended action.
    """

    if risk_score <= LOW_RISK_MAX:
        return "LOW", "ALLOW"

    if risk_score <= MEDIUM_RISK_MAX:
        return "MEDIUM", "MONITOR"

    if risk_score <= HIGH_RISK_MAX:
        return "HIGH", "REVIEW"

    return "CRITICAL", "BLOCK"


# ============================================================
# Rule-based signal detection
# ============================================================

def detect_risk_signals(
    transaction: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Detect interpretable risk signals from transaction
    attributes.

    These rules provide human-readable security indicators
    that complement the machine-learning prediction.
    """

    signals: list[dict[str, Any]] = []

    amount = float(
        transaction.get(
            "amount",
            0,
        )
    )

    account_age_days = int(
        transaction.get(
            "account_age_days",
            0,
        )
    )

    amount_deviation_ratio = float(
        transaction.get(
            "amount_deviation_ratio",
            1,
        )
    )

    is_new_device = int(
        transaction.get(
            "is_new_device",
            0,
        )
    )

    device_changes_30d = int(
        transaction.get(
            "device_changes_30d",
            0,
        )
    )

    location_changes_24h = int(
        transaction.get(
            "location_changes_24h",
            0,
        )
    )

    transactions_last_10min = int(
        transaction.get(
            "transactions_last_10min",
            0,
        )
    )

    transactions_last_hour = int(
        transaction.get(
            "transactions_last_hour",
            0,
        )
    )

    transactions_last_24h = int(
        transaction.get(
            "transactions_last_24h",
            0,
        )
    )

    failed_attempts_24h = int(
        transaction.get(
            "failed_attempts_24h",
            0,
        )
    )

    otp_failures = int(
        transaction.get(
            "otp_failures",
            0,
        )
    )

    is_night_transaction = int(
        transaction.get(
            "is_night_transaction",
            0,
        )
    )

    ip_risk_score = float(
        transaction.get(
            "ip_risk_score",
            0,
        )
    )

    proxy_or_vpn = int(
        transaction.get(
            "proxy_or_vpn",
            0,
        )
    )

    chargeback_history = int(
        transaction.get(
            "chargeback_history",
            0,
        )
    )

    # --------------------------------------------------------
    # Transaction amount
    # --------------------------------------------------------

    if amount >= 100000:
        signals.append(
            {
                "code": "VERY_HIGH_AMOUNT",
                "severity": "HIGH",
                "message": (
                    "Transaction amount is exceptionally high."
                ),
                "value": amount,
            }
        )

    elif amount >= 50000:
        signals.append(
            {
                "code": "HIGH_AMOUNT",
                "severity": "MEDIUM",
                "message": (
                    "Transaction amount is significantly high."
                ),
                "value": amount,
            }
        )

    # --------------------------------------------------------
    # Behavioural deviation
    # --------------------------------------------------------

    if amount_deviation_ratio >= 6:
        signals.append(
            {
                "code": "EXTREME_AMOUNT_DEVIATION",
                "severity": "HIGH",
                "message": (
                    "Transaction amount is more than "
                    "six times the customer's typical amount."
                ),
                "value": amount_deviation_ratio,
            }
        )

    elif amount_deviation_ratio >= 3:
        signals.append(
            {
                "code": "UNUSUAL_AMOUNT",
                "severity": "MEDIUM",
                "message": (
                    "Transaction amount is substantially "
                    "above the customer's typical behaviour."
                ),
                "value": amount_deviation_ratio,
            }
        )

    # --------------------------------------------------------
    # Account age
    # --------------------------------------------------------

    if account_age_days <= 7:
        signals.append(
            {
                "code": "VERY_NEW_ACCOUNT",
                "severity": "HIGH",
                "message": (
                    "Transaction originates from an account "
                    "less than seven days old."
                ),
                "value": account_age_days,
            }
        )

    elif account_age_days <= 30:
        signals.append(
            {
                "code": "NEW_ACCOUNT",
                "severity": "MEDIUM",
                "message": (
                    "Transaction originates from a recently "
                    "created account."
                ),
                "value": account_age_days,
            }
        )

    # --------------------------------------------------------
    # Device behaviour
    # --------------------------------------------------------

    if is_new_device == 1:
        signals.append(
            {
                "code": "NEW_DEVICE",
                "severity": "HIGH",
                "message": (
                    "Transaction was initiated from a new device."
                ),
                "value": True,
            }
        )

    if device_changes_30d >= 4:
        signals.append(
            {
                "code": "FREQUENT_DEVICE_CHANGES",
                "severity": "MEDIUM",
                "message": (
                    "Multiple device changes were detected "
                    "during the last 30 days."
                ),
                "value": device_changes_30d,
            }
        )

    # --------------------------------------------------------
    # Location behaviour
    # --------------------------------------------------------

    if location_changes_24h >= 4:
        signals.append(
            {
                "code": "LOCATION_ANOMALY",
                "severity": "HIGH",
                "message": (
                    "Multiple location changes were detected "
                    "within 24 hours."
                ),
                "value": location_changes_24h,
            }
        )

    elif location_changes_24h >= 2:
        signals.append(
            {
                "code": "LOCATION_CHANGE",
                "severity": "MEDIUM",
                "message": (
                    "Unusual location movement was detected."
                ),
                "value": location_changes_24h,
            }
        )

    # --------------------------------------------------------
    # Transaction velocity
    # --------------------------------------------------------

    if transactions_last_10min >= 4:
        signals.append(
            {
                "code": "HIGH_VELOCITY_10MIN",
                "severity": "HIGH",
                "message": (
                    "Unusually high transaction velocity "
                    "was detected over the last 10 minutes."
                ),
                "value": transactions_last_10min,
            }
        )

    if transactions_last_hour >= 10:
        signals.append(
            {
                "code": "HIGH_VELOCITY_1H",
                "severity": "HIGH",
                "message": (
                    "Unusually high transaction velocity "
                    "was detected over the last hour."
                ),
                "value": transactions_last_hour,
            }
        )

    if transactions_last_24h >= 30:
        signals.append(
            {
                "code": "HIGH_DAILY_VELOCITY",
                "severity": "MEDIUM",
                "message": (
                    "Transaction activity is unusually high "
                    "over the last 24 hours."
                ),
                "value": transactions_last_24h,
            }
        )

    # --------------------------------------------------------
    # Authentication failures
    # --------------------------------------------------------

    if failed_attempts_24h >= 6:
        signals.append(
            {
                "code": "EXCESSIVE_FAILED_ATTEMPTS",
                "severity": "HIGH",
                "message": (
                    "A large number of failed authentication "
                    "attempts were detected."
                ),
                "value": failed_attempts_24h,
            }
        )

    elif failed_attempts_24h >= 3:
        signals.append(
            {
                "code": "MULTIPLE_FAILED_ATTEMPTS",
                "severity": "MEDIUM",
                "message": (
                    "Multiple failed authentication attempts "
                    "were detected."
                ),
                "value": failed_attempts_24h,
            }
        )

    if otp_failures >= 2:
        signals.append(
            {
                "code": "OTP_FAILURES",
                "severity": "MEDIUM",
                "message": (
                    "Multiple OTP verification failures "
                    "were detected."
                ),
                "value": otp_failures,
            }
        )

    # --------------------------------------------------------
    # Night activity
    # --------------------------------------------------------

    if is_night_transaction == 1:
        signals.append(
            {
                "code": "NIGHT_TRANSACTION",
                "severity": "LOW",
                "message": (
                    "Transaction occurred during a "
                    "high-risk overnight period."
                ),
                "value": True,
            }
        )

    # --------------------------------------------------------
    # IP risk
    # --------------------------------------------------------

    if ip_risk_score >= 80:
        signals.append(
            {
                "code": "HIGH_IP_RISK",
                "severity": "HIGH",
                "message": (
                    "Source IP has a very high risk score."
                ),
                "value": ip_risk_score,
            }
        )

    elif ip_risk_score >= 70:
        signals.append(
            {
                "code": "ELEVATED_IP_RISK",
                "severity": "MEDIUM",
                "message": (
                    "Source IP has an elevated risk score."
                ),
                "value": ip_risk_score,
            }
        )

    if proxy_or_vpn == 1:
        signals.append(
            {
                "code": "PROXY_OR_VPN",
                "severity": "MEDIUM",
                "message": (
                    "Transaction is associated with a "
                    "proxy or VPN connection."
                ),
                "value": True,
            }
        )

    # --------------------------------------------------------
    # Chargeback history
    # --------------------------------------------------------

    if chargeback_history == 1:
        signals.append(
            {
                "code": "CHARGEBACK_HISTORY",
                "severity": "HIGH",
                "message": (
                    "Customer has a previous chargeback history."
                ),
                "value": True,
            }
        )

    return signals


# ============================================================
# Calculate rule-based risk contribution
# ============================================================

def calculate_rule_score(
    signals: list[dict[str, Any]],
) -> float:
    """
    Convert detected risk signals into an interpretable
    rule-based risk contribution.

    The contribution is capped at 70 so that rule-based
    security controls can meaningfully influence the final
    classification while the ML probability remains important.
    """

    severity_weights = {
        "LOW": 3,
        "MEDIUM": 8,
        "HIGH": 14,
    }

    total = 0.0

    for signal in signals:
        severity = signal.get(
            "severity",
            "LOW",
        )

        total += severity_weights.get(
            severity,
            0,
        )

    return min(
        total,
        70,
    )


# ============================================================
# Main risk calculation
# ============================================================

def calculate_risk(
    transaction: dict[str, Any],
    fraud_probability: float,
) -> RiskResult:
    """
    Combine ML fraud probability with interpretable
    transaction risk signals.

    The final score uses a balanced hybrid approach:

        ML contribution    = 60%
        Rule contribution  = 40%

    This prevents a very low ML probability from completely
    suppressing strong deterministic security indicators.
    """

    # --------------------------------------------------------
    # Normalize probability
    # --------------------------------------------------------

    fraud_probability = max(
        0.0,
        min(
            1.0,
            float(fraud_probability),
        ),
    )

    # --------------------------------------------------------
    # ML contribution
    # --------------------------------------------------------

    ml_score = (
        fraud_probability
        * 100
    )

    # --------------------------------------------------------
    # Rule contribution
    # --------------------------------------------------------

    signals = detect_risk_signals(
        transaction
    )

    rule_score = calculate_rule_score(
        signals
    )

    # --------------------------------------------------------
    # Combined hybrid score
    # --------------------------------------------------------

    risk_score = (
        ml_score * 0.60
        + rule_score * 0.40
    )

    risk_score = clamp_score(
        risk_score
    )

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    risk_level, decision = classify_risk(
        risk_score
    )

    # --------------------------------------------------------
    # Generate human-readable reasons
    # --------------------------------------------------------

    reasons = [
        signal["message"]
        for signal in signals
    ]

    if not reasons:
        reasons.append(
            "No significant rule-based risk indicators were detected."
        )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return RiskResult(
        risk_score=risk_score,
        risk_level=risk_level,
        decision=decision,
        fraud_probability=round(
            fraud_probability,
            4,
        ),
        reasons=reasons,
        signals=signals,
    )