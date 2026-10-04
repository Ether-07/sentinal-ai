# Sentinal AI

AI-Powered Payment Risk Intelligence & Investigation Platform.



## 🎥 Project Demo

Watch the Sentinal AI project demo and pitch video:

[![Sentinal AI — Payment Risk Intelligence & Investigation Platform](docs/assets/sentinal-ai-thumbnail.jpg)](https://drive.google.com/file/d/1J5Rv3D-xX8F7uQvw1xf2TjEnNBYwlk3d/view)

**[▶️ Watch the 5-minute project demo](https://drive.google.com/file/d/1J5Rv3D-xX8F7uQvw1xf2TjEnNBYwlk3d/view)**

The video demonstrates the transaction-risk workflow, hybrid ML + rule-based scoring, explainable risk signals, risk decisions, dashboard monitoring, alerts, and investigation workflow.


## Overview

Sentinal AI is a web-based payment risk intelligence platform designed to analyze payment transactions, identify potentially fraudulent behavior, explain risk decisions, and assist security and payment-risk analysts with transaction monitoring and investigation.

The platform combines:

- Machine-learning fraud prediction
- Rule-based risk detection
- Hybrid risk scoring
- Explainable risk signals
- Transaction persistence
- Risk alerts
- Transaction monitoring
- Investigator-oriented workflows

---

## Key Capabilities

### Transaction Analysis

Sentinal AI accepts transaction, customer, device, location, behavioral, authentication, network, and payment-history attributes.

Each transaction is processed through:

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

The current risk engine supports four risk levels:

| Risk Level | Purpose |
|------------|---------|
| LOW | Transaction presents limited risk |
| MEDIUM | Transaction requires monitoring |
| HIGH | Transaction requires analyst review |
| CRITICAL | Transaction presents severe risk |

Risk decisions include:

- ALLOW
- MONITOR
- REVIEW
- BLOCK

### Transaction Monitoring

Analyzed transactions are persisted in a SQLite database.

The frontend provides:

- Risk dashboard
- Transaction analysis
- Transaction history
- High-risk alerts
- Alert status handling
- Risk statistics
- Application settings

---

## Architecture

```text
                        +---------------------+
                        |     React / Vite    |
                        |      Frontend       |
                        +----------+----------+
                                   |
                                   | HTTP / JSON
                                   v
                        +---------------------+
                        |       FastAPI       |
                        |       Backend       |
                        +----------+----------+
                                   |
                    +--------------+--------------+
                    |              |              |
                    v              v              v
             +-----------+ +------------+ +--------------+
             | ML Model  | | Risk Engine| |   SQLite DB  |
             |           | |            | |              |
             | Random    | | ML + Rules | | Transactions |
             | Forest    | | + Scoring  | | + Alerts     |
             +-----------+ +------------+ +--------------+
```

### Request Flow

```text
Transaction
     |
     v
React Frontend
     |
     v
FastAPI API
     |
     v
Preprocessing Pipeline
     |
     v
ML Fraud Probability
     |
     v
Hybrid Risk Engine
     |
     +-- Machine-learning signal
     +-- Behavioral signals
     +-- Device signals
     +-- Location signals
     +-- Authentication signals
     +-- Network signals
     +-- Payment-history signals
     |
     v
Risk Score + Risk Level + Decision
     |
     v
SQLite Persistence
     |
     v
Frontend Result / Dashboard / Alerts
```

---

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

---

## Project Structure

```text
Sentinal AI
|
+-- backend
|   +-- app
|   |   +-- database.py
|   |   +-- main.py
|   |   +-- risk_engine.py
|   |
|   +-- test_risk_engine.py
|   +-- tests
|       +-- test_backend.py
|
+-- frontend
|   +-- public
|   +-- src
|   |   +-- api
|   |   +-- assets
|   |   +-- components
|   |   +-- services
|   |   +-- App.css
|   |   +-- App.jsx
|   |   +-- index.css
|   |   +-- main.jsx
|   |
|   +-- index.html
|   +-- package.json
|   +-- package-lock.json
|   +-- vite.config.js
|
+-- ml
|   +-- models
|   +-- training
|
+-- data
|   +-- raw
|   +-- processed
|   +-- sentinal_ai.db
|
+-- docs
+-- requirements.txt
+-- start.ps1
+-- README.md
+-- .gitignore
```

---

# Getting Started

## Prerequisites

The development environment requires:

- Python 3.14+
- Node.js
- npm

Git is required if cloning the repository from GitHub.

---

## Installation

Clone the repository:

```powershell
git clone https://github.com/Ether-07/sentinal-ai
cd sentinal-ai
```

### Python environment

Create the virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

### Frontend dependencies

```powershell
cd frontend
npm install
cd ..
```

---

# Running Sentinal AI

The project includes a root startup script so the backend and frontend can be started without manually opening and configuring two terminals.

From the project root:

```powershell
.\start.ps1
```

If PowerShell execution policy prevents the script from running, use:

```powershell
powershell -ExecutionPolicy Bypass -File ".\start.ps1"
```

The launcher starts:

- FastAPI backend
- React/Vite frontend

The application is normally available at:

```text
Frontend:
http://localhost:5173

Backend:
http://127.0.0.1:8000
```

Keep both server windows running while using the application.

---

# Backend API

## Health

```text
GET /api/health
```

Returns backend and machine-learning component status.

Example response:

```json
{
  "status": "healthy",
  "service": "sentinal-ai-backend",
  "ml_model_loaded": true,
  "preprocessor_loaded": true,
  "risk_engine_available": true,
  "ml_pipeline_ready": true
}
```

## Analyze Transaction

```text
POST /api/v1/risk/analyze
```

Analyzes a transaction using the trained machine-learning model and hybrid risk engine.

A successful analysis is persisted to SQLite.

## Transaction History

```text
GET /api/v1/transactions
```

Returns recently analyzed transactions.

## Transaction Details

```text
GET /api/v1/transactions/{transaction_id}
```

Returns a specific analyzed transaction.

## Alert Status

```text
PATCH /api/v1/transactions/{transaction_id}/alert-status
```

Updates the alert status associated with a transaction.

---

# API Documentation

When the backend is running, FastAPI automatically provides interactive API documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

# Machine Learning

The machine-learning workflow is located under:

```text
ml/training/
```

The project includes scripts for:

```text
generate_dataset.py
prepare_data.py
train_model.py
```

The trained fraud model and preprocessing pipeline are used by the backend during transaction analysis.

The application expects the following artifacts:

```text
ml/models/fraud_risk_model.joblib
data/processed/preprocessor.joblib
```

These generated artifacts are intentionally excluded from Git source control through `.gitignore`.

---

# Dataset

Sentinal AI uses synthetic transaction data for development and model training.

No real customer financial information is required by the project.

The dataset includes transaction attributes such as:

- Transaction amount
- Customer information
- Payment method
- Merchant category
- Account age
- Device characteristics
- Location behavior
- Transaction velocity
- Authentication failures
- IP risk
- Proxy/VPN indicators
- Card age
- Chargeback history
- Fraud classification

The synthetic-data approach allows the project to demonstrate fraud-risk detection without exposing real financial or personally identifiable information.

---

# Risk Engine

The Sentinal AI risk engine combines machine-learning predictions with deterministic risk signals.

Conceptually:

```text
                 ML Fraud Probability
                          |
                          v
              +-----------------------+
              |   Hybrid Risk Engine  |
              |                       |
              |  ML + Rules + Signals |
              +-----------+-----------+
                          |
                          v
                    Risk Score
                      0-100
                          |
             +------------+------------+
             v            v            v
            LOW        MEDIUM       HIGH/CRITICAL
             |            |            |
           ALLOW       MONITOR     REVIEW/BLOCK
```

The deterministic signals consider transaction behavior, account characteristics, device changes, location changes, transaction velocity, authentication failures, network risk, and payment history.

---

# Explainability

The risk engine produces human-readable explanations alongside the numerical risk assessment.

Risk output includes:

- Risk reasons
- Signal codes
- Signal severity
- Signal messages
- Risk score
- Risk level
- Decision

This allows analysts to understand why a transaction received a particular risk classification rather than relying only on an opaque numerical prediction.

---

# Transaction Investigation

The platform provides transaction-level monitoring and investigation functionality.

Analysts can review:

- Transaction identifiers
- Transaction amounts
- Risk scores
- Fraud probabilities
- Risk levels
- Decisions
- Risk drivers
- Alert status
- Historical analysis records

---

# Testing

Backend tests can be executed from the backend directory:

```powershell
cd backend
python -m pytest -q
```

The project also contains a standalone risk-engine demonstration script:

```powershell
python test_risk_engine.py
```

The FastAPI test client can be used to validate API behavior.

---

# Frontend Development

Start the frontend independently when development requires it:

```powershell
cd frontend
npm run dev
```

Build the production frontend:

```powershell
cd frontend
npm run build
```

Run the frontend lint check:

```powershell
cd frontend
npm run lint
```

Preview the production build:

```powershell
cd frontend
npm run preview
```

---

# Production Build

Generate the frontend production bundle:

```powershell
cd frontend
npm run build
```

The generated files are placed in:

```text
frontend/dist/
```

Build artifacts are excluded from Git source control.

---

# Data and Generated Artifacts

Runtime and generated files are intentionally excluded from source control where appropriate.

Examples include:

- SQLite runtime database
- Raw datasets
- Processed datasets
- Trained machine-learning models
- Preprocessing artifacts
- Python cache files
- pytest cache files
- Node modules
- Frontend build output

The local runtime database is:

```text
data/sentinal_ai.db
```

It is created and maintained locally by the backend.

---

# Limitations

Sentinal AI is a buildathon and demonstration project rather than a production financial-fraud prevention system.

Important limitations include:

- The training data is synthetic.
- Model performance depends on the generated dataset and feature distributions.
- Risk decisions should not be treated as definitive proof of fraud.
- The system does not connect to real payment networks.
- The SQLite database is intended for local development and demonstration.
- ML artifacts are generated/runtime dependencies and are not committed to source control.
- No production-grade authentication or authorization system is currently included.
- Deployment infrastructure is outside the current project scope.

---

# Security Considerations

The project is designed for demonstration and development purposes.

Do not use real payment credentials, production customer data, API secrets, or other sensitive financial information with the application.

Before production deployment, additional controls would be required, including:

- Authentication
- Authorization
- Secure secret management
- HTTPS
- Database hardening
- Input validation and abuse protection
- Rate limiting
- Audit logging
- Secure model artifact distribution
- Monitoring and alerting
- Production deployment infrastructure

---

# Current Status

The core Sentinal AI transaction-risk workflow is implemented.

Current functionality includes:

- Transaction analysis
- Machine-learning fraud prediction
- Hybrid risk scoring
- Explainable risk signals
- Risk decisions
- Persistent transaction storage
- Dashboard statistics
- Transaction monitoring
- High-risk alerts
- Alert status handling
- Backend API
- Frontend interface
- Automated backend/frontend startup
- Backend tests
- Production frontend build

The project is prepared for buildathon presentation and submission.

---

# License

This project is currently intended as a buildathon and educational demonstration project.
