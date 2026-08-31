from app.risk_engine import calculate_risk


def main():
    transaction = {
        "amount": 125000,
        "account_age_days": 4,
        "amount_deviation_ratio": 8.2,
        "is_new_device": 1,
        "device_changes_30d": 5,
        "location_changes_24h": 4,
        "transactions_last_10min": 6,
        "transactions_last_hour": 14,
        "transactions_last_24h": 42,
        "failed_attempts_24h": 7,
        "otp_failures": 3,
        "is_night_transaction": 1,
        "ip_risk_score": 87,
        "proxy_or_vpn": 1,
        "chargeback_history": 1,
    }

    fraud_probability = 0.91

    result = calculate_risk(
        transaction=transaction,
        fraud_probability=fraud_probability,
    )

    print("=" * 70)
    print("SENTINAL AI - RISK ENGINE TEST")
    print("=" * 70)

    print()
    print(
        f"Fraud Probability : "
        f"{result.fraud_probability * 100:.2f}%"
    )

    print(
        f"Risk Score        : "
        f"{result.risk_score}/100"
    )

    print(
        f"Risk Level        : "
        f"{result.risk_level}"
    )

    print(
        f"Decision           : "
        f"{result.decision}"
    )

    print()
    print("Risk Reasons")
    print("-" * 70)

    for index, reason in enumerate(
        result.reasons,
        start=1,
    ):
        print(
            f"{index}. {reason}"
        )

    print()
    print("Detailed Signals")
    print("-" * 70)

    for signal in result.signals:
        print(
            f"[{signal['severity']}] "
            f"{signal['code']}: "
            f"{signal['message']}"
        )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()