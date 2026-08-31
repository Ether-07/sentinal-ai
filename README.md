# Sentinal AI

AI-Powered Payment Risk Intelligence & Investigation Platform.

## Overview

Sentinal AI is a web-based payment risk management platform that analyzes payment transactions using a hybrid machine-learning and rule-based risk engine.

The platform is designed to help security and payment-risk analysts:

- Analyze individual transactions
- Calculate fraud probability
- Generate a normalized risk score
- Classify transactions by risk level
- Produce explainable risk reasons and signals
- Make risk-based decisions
- Persist transaction analyses
- Review transaction history
- Monitor high-risk transactions through alerts
- Investigate transaction-level risk information

## Current Capabilities

### Transaction Analysis

The analysis workflow accepts transaction, customer, device, location, behavioral, authentication, network, and payment-history attributes.

The backend processes the transaction through:

1. A trained machine-learning preprocessing pipeline
2. A trained fraud classification model
3. The hybrid Sentinal AI risk engine
4. Risk scoring and decision logic
5. Persistent SQLite storage

### Risk Assessment

Each analyzed transaction receives:

- Fraud probability
- Fraud probability percentage
- Risk score from 0–100
- Risk level
- Risk decision
- Explainable risk reasons
- Detailed risk signals
- Analysis timestamp

### Risk Levels

The current risk engine supports:

- LOW
- MEDIUM
- HIGH
- CRITICAL

Decisions include:

- ALLOW
- MONITOR
- REVIEW
- BLOCK

### Transaction Monitoring

The application maintains persistent transaction history using SQLite.

The frontend provides:

- Dashboard statistics
- Recent transaction history
- Transaction monitoring
- High-risk alert queue
- Transaction analysis interface
- Application settings

## Technology Stack

### Frontend

- React
- Vite
- Axios
- Lucide React

### Backend

- Python
- FastAPI
- Pydantic
- Uvicorn

### Machine Learning

- scikit-learn
- pandas
- NumPy
- joblib
- SHAP
- SciPy
- numba

### Database

- SQLite

### Testing

- pytest
- FastAPI TestClient

## Project Structure

```text
Sentinal AI
├── backend
│   ├── app
│   │   ├── database.py
│   │   ├── main.py
│   │   └── risk_engine.py
│   ├── test_risk_engine.py
│   └── tests
│       └── test_backend.py
│
├── frontend
│   ├── public
│   ├── src
│   │   ├── api
│   │   ├── assets
│   │   ├── components
│   │   ├── services
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── ml
│   ├── models
│   └── training
│
├── data
│   ├── raw
│   ├── processed
│   └── sentinal_ai.db
│
├── docs
├── requirements.txt
├── README.md
└── .gitignore