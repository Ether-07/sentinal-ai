import {
    useEffect,
    useState,
} from "react";


import {
    Activity,
    AlertTriangle,
    ArrowRight,
    CheckCircle2,
    Clock3,
    ShieldAlert,
    ShieldCheck,
    TrendingUp,
} from "lucide-react";


import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";


import {
    analyzeTransaction,
    getTransactions,
    updateAlertStatus,
} from "./services/api";


import "./App.css";


const initialTransaction = {
    transaction_id: "TXN-WEB-001",
    customer_id: "CUST-WEB-001",
    timestamp: "2025-06-15 14:30:00",
    amount: 1000,
    payment_method: "upi",
    merchant_category: "grocery",
    account_age_days: 365,
    customer_transaction_count: 100,
    average_transaction_amount: 1000,
    amount_deviation_ratio: 1,
    unusual_amount: 0,
    device_age_days: 180,
    is_new_device: 0,
    device_changes_30d: 0,
    location: "Mumbai",
    location_changes_24h: 0,
    transactions_last_10min: 1,
    transactions_last_hour: 2,
    transactions_last_24h: 5,
    failed_attempts_24h: 0,
    otp_failures: 0,
    transaction_hour: 14,
    is_night_transaction: 0,
    is_weekend: 0,
    ip_risk_score: 10,
    proxy_or_vpn: 0,
    card_age_days: 500,
    chargeback_history: 0,
};


const emptyDashboardStats = {
    total: 0,
    highRisk: 0,
    blocked: 0,
    averageRisk: 0,
};


function App() {
    const [
        activePage,
        setActivePage,
    ] = useState(
        "analyze"
    );


    const [
        transaction,
        setTransaction,
    ] = useState(
        initialTransaction
    );


    const [
        result,
        setResult,
    ] = useState(null);


    const [
        transactions,
        setTransactions,
    ] = useState([]);


    const [
        loading,
        setLoading,
    ] = useState(false);


    const [
        historyLoading,
        setHistoryLoading,
    ] = useState(true);


    const [
        error,
        setError,
    ] = useState("");


    // ========================================================
    // Load persistent transaction history
    // ========================================================

    async function loadTransactionHistory() {
        try {
            setHistoryLoading(true);

            const data =
                await getTransactions();

            setTransactions(
                data.transactions || []
            );
        } catch (historyError) {
            console.error(
                "Failed to load transaction history:",
                historyError
            );

            setError(
                "Unable to load transaction history from the backend."
            );
        } finally {
            setHistoryLoading(false);
        }
    }


    // ========================================================
    // Initial application load
    // ========================================================

    useEffect(() => {
        loadTransactionHistory();
    }, []);


    // ========================================================
    // Form field changes
    // ========================================================

    function handleChange(
        event
    ) {
        const {
            name,
            value,
        } = event.target;


        const numericFields = [
            "amount",
            "account_age_days",
            "customer_transaction_count",
            "average_transaction_amount",
            "amount_deviation_ratio",
            "unusual_amount",
            "device_age_days",
            "is_new_device",
            "device_changes_30d",
            "location_changes_24h",
            "transactions_last_10min",
            "transactions_last_hour",
            "transactions_last_24h",
            "failed_attempts_24h",
            "otp_failures",
            "transaction_hour",
            "is_night_transaction",
            "is_weekend",
            "ip_risk_score",
            "proxy_or_vpn",
            "card_age_days",
            "chargeback_history",
        ];


        const parsedValue =
            numericFields.includes(
                name
            )
                ? Number(value)
                : value;


        setTransaction(
            (current) => ({
                ...current,
                [name]: parsedValue,
            })
        );
    }


    // ========================================================
    // Checkbox / toggle changes
    // ========================================================

    function setToggle(
        field,
        checked
    ) {
        setTransaction(
            (current) => ({
                ...current,
                [field]: checked
                    ? 1
                    : 0,
            })
        );
    }


    // ========================================================
    // Analyze transaction
    // ========================================================

    async function handleSubmit(
        event
    ) {
        event.preventDefault();


        setLoading(true);
        setError("");
        setResult(null);


        try {
            const data =
                await analyzeTransaction(
                    transaction
                );


            setResult(data);


            await loadTransactionHistory();

        } catch (requestError) {
            console.error(
                requestError
            );


            if (
                requestError.response
                    ?.data
                    ?.detail
            ) {
                setError(
                    requestError
                        .response
                        .data
                        .detail
                );
            } else {
                setError(
                    "Unable to connect to the Sentinal AI backend."
                );
            }
        } finally {
            setLoading(false);
        }
    }


    // ========================================================
    // Alert status update
    // ========================================================

    async function handleAlertStatusChange(
        transactionId,
        alertStatus
    ) {
        try {
            setError("");


            await updateAlertStatus(
                transactionId,
                alertStatus
            );


            await loadTransactionHistory();

        } catch (statusError) {
            console.error(
                "Failed to update alert status:",
                statusError
            );


            if (
                statusError.response
                    ?.data
                    ?.detail
            ) {
                setError(
                    statusError
                        .response
                        .data
                        .detail
                );
            } else {
                setError(
                    "Unable to update the alert status."
                );
            }
        }
    }


    // ========================================================
    // Dashboard statistics
    // ========================================================

    const dashboardStats =
        transactions.reduce(
            (
                stats,
                item
            ) => {
                stats.total += 1;


                if (
                    item.risk_level ===
                        "HIGH" ||
                    item.risk_level ===
                        "CRITICAL"
                ) {
                    stats.highRisk += 1;
                }


                if (
                    item.decision ===
                    "BLOCK"
                ) {
                    stats.blocked += 1;
                }


                stats.averageRisk +=
                    Number(
                        item.risk_score || 0
                    );


                return stats;
            },
            {
                ...emptyDashboardStats,
            }
        );


    if (
        dashboardStats.total >
        0
    ) {
        dashboardStats.averageRisk =
            Math.round(
                dashboardStats.averageRisk /
                    dashboardStats.total
            );
    }


    // ========================================================
    // Page renderer
    // ========================================================

    function renderPage() {
        if (
            activePage ===
            "dashboard"
        ) {
            return (
                <DashboardPage
                    stats={
                        dashboardStats
                    }
                    transactions={
                        transactions
                    }
                    loading={
                        historyLoading
                    }
                />
            );
        }


        if (
            activePage ===
            "transactions"
        ) {
            return (
                <TransactionsPage
                    transactions={
                        transactions
                    }
                    loading={
                        historyLoading
                    }
                    onAnalyze={() =>
                        setActivePage(
                            "analyze"
                        )
                    }
                />
            );
        }


        if (
            activePage ===
            "alerts"
        ) {
            return (
                <AlertsPage
                    transactions={
                        transactions
                    }
                    loading={
                        historyLoading
                    }
                    onAnalyze={() =>
                        setActivePage(
                            "analyze"
                        )
                    }
                    onAlertStatusChange={
                        handleAlertStatusChange
                    }
                />
            );
        }


        if (
            activePage ===
            "settings"
        ) {
            return (
                <SettingsPage />
            );
        }


        return (
            <AnalyzePage
                transaction={
                    transaction
                }
                result={
                    result
                }
                loading={
                    loading
                }
                error={
                    error
                }
                onChange={
                    handleChange
                }
                onToggle={
                    setToggle
                }
                onSubmit={
                    handleSubmit
                }
            />
        );
    }


    return (
        <div className="application-shell">

            <Sidebar
                activePage={
                    activePage
                }
                onPageChange={
                    setActivePage
                }
            />


            <div className="application-main">

                <Topbar />


                <main className="page-content">
                    {renderPage()}
                </main>

            </div>

        </div>
    );
}


/* ============================================================
   Analyze Page
   ============================================================ */

function AnalyzePage({
    transaction,
    result,
    loading,
    error,
    onChange,
    onToggle,
    onSubmit,
}) {
    return (
        <div className="page-container">

            <div className="page-heading">

                <div>

                    <div className="page-eyebrow">
                        TRANSACTION ANALYSIS
                    </div>

                    <h1>
                        Analyze a payment
                    </h1>

                    <p>
                        Submit transaction attributes to
                        generate an AI-assisted risk assessment.
                    </p>

                </div>


                <div className="heading-status">

                    <span className="live-indicator"></span>

                    RISK ENGINE READY

                </div>

            </div>


            <div className="analysis-layout">

                <section className="content-card">

                    <div className="card-heading">

                        <div>

                            <span className="card-kicker">
                                INPUT
                            </span>

                            <h2>
                                Transaction details
                            </h2>

                        </div>

                        <Activity
                            size={18}
                        />

                    </div>


                    <form
                        onSubmit={
                            onSubmit
                        }
                    >

                        <div className="form-section">

                            <div className="form-section-title">
                                TRANSACTION
                            </div>


                            <div className="form-grid">

                                <Field
                                    label="Transaction ID"
                                    name="transaction_id"
                                    value={
                                        transaction.transaction_id
                                    }
                                    onChange={
                                        onChange
                                    }
                                />


                                <Field
                                    label="Amount"
                                    name="amount"
                                    type="number"
                                    min="0"
                                    value={
                                        transaction.amount
                                    }
                                    onChange={
                                        onChange
                                    }
                                />


                                <SelectField
                                    label="Payment method"
                                    name="payment_method"
                                    value={
                                        transaction.payment_method
                                    }
                                    onChange={
                                        onChange
                                    }
                                    options={[
                                        [
                                            "upi",
                                            "UPI",
                                        ],
                                        [
                                            "credit_card",
                                            "Credit Card",
                                        ],
                                        [
                                            "debit_card",
                                            "Debit Card",
                                        ],
                                        [
                                            "wallet",
                                            "Wallet",
                                        ],
                                        [
                                            "netbanking",
                                            "Net Banking",
                                        ],
                                    ]}
                                />


                                <SelectField
                                    label="Merchant category"
                                    name="merchant_category"
                                    value={
                                        transaction.merchant_category
                                    }
                                    onChange={
                                        onChange
                                    }
                                    options={[
                                        [
                                            "grocery",
                                            "Grocery",
                                        ],
                                        [
                                            "electronics",
                                            "Electronics",
                                        ],
                                        [
                                            "travel",
                                            "Travel",
                                        ],
                                        [
                                            "gaming",
                                            "Gaming",
                                        ],
                                        [
                                            "food",
                                            "Food",
                                        ],
                                        [
                                            "retail",
                                            "Retail",
                                        ],
                                    ]}
                                />


                                <Field
                                    label="Location"
                                    name="location"
                                    value={
                                        transaction.location
                                    }
                                    onChange={
                                        onChange
                                    }
                                />


                                <Field
                                    label="IP risk score"
                                    name="ip_risk_score"
                                    type="number"
                                    min="0"
                                    max="100"
                                    value={
                                        transaction.ip_risk_score
                                    }
                                    onChange={
                                        onChange
                                    }
                                />

                            </div>

                        </div>


                        <div className="form-section">

                            <div className="form-section-title">
                                BEHAVIOUR & DEVICE
                            </div>


                            <div className="form-grid">

                                <Field
                                    label="Account age (days)"
                                    name="account_age_days"
                                    type="number"
                                    min="0"
                                    value={
                                        transaction.account_age_days
                                    }
                                    onChange={
                                        onChange
                                    }
                                />


                                <Field
                                    label="Device age (days)"
                                    name="device_age_days"
                                    type="number"
                                    min="0"
                                    value={
                                        transaction.device_age_days
                                    }
                                    onChange={
                                        onChange
                                    }
                                />


                                <Field
                                    label="Amount deviation ratio"
                                    name="amount_deviation_ratio"
                                    type="number"
                                    min="0"
                                    step="0.01"
                                    value={
                                        transaction.amount_deviation_ratio
                                    }
                                    onChange={
                                        onChange
                                    }
                                />


                                <Field
                                    label="Transactions / hour"
                                    name="transactions_last_hour"
                                    type="number"
                                    min="0"
                                    value={
                                        transaction.transactions_last_hour
                                    }
                                    onChange={
                                        onChange
                                    }
                                />


                                <Field
                                    label="Transactions / 10 min"
                                    name="transactions_last_10min"
                                    type="number"
                                    min="0"
                                    value={
                                        transaction.transactions_last_10min
                                    }
                                    onChange={
                                        onChange
                                    }
                                />


                                <Field
                                    label="Failed attempts / 24h"
                                    name="failed_attempts_24h"
                                    type="number"
                                    min="0"
                                    value={
                                        transaction.failed_attempts_24h
                                    }
                                    onChange={
                                        onChange
                                    }
                                />

                            </div>


                            <div className="toggle-grid">

                                <Toggle
                                    label="New device"
                                    checked={
                                        transaction.is_new_device ===
                                        1
                                    }
                                    onChange={
                                        (checked) =>
                                            onToggle(
                                                "is_new_device",
                                                checked
                                            )
                                    }
                                />


                                <Toggle
                                    label="Proxy / VPN"
                                    checked={
                                        transaction.proxy_or_vpn ===
                                        1
                                    }
                                    onChange={
                                        (checked) =>
                                            onToggle(
                                                "proxy_or_vpn",
                                                checked
                                            )
                                    }
                                />


                                <Toggle
                                    label="Chargeback history"
                                    checked={
                                        transaction.chargeback_history ===
                                        1
                                    }
                                    onChange={
                                        (checked) =>
                                            onToggle(
                                                "chargeback_history",
                                                checked
                                            )
                                    }
                                />

                            </div>

                        </div>


                        {error && (
                            <div className="error-banner">

                                <AlertTriangle
                                    size={17}
                                />

                                <span>
                                    {error}
                                </span>

                            </div>
                        )}


                        <button
                            className="primary-action"
                            type="submit"
                            disabled={
                                loading
                            }
                        >

                            {loading
                                ? "ANALYZING TRANSACTION..."
                                : "ANALYZE TRANSACTION"
                            }

                            <ArrowRight
                                size={17}
                            />

                        </button>

                    </form>

                </section>


                <RiskResult
                    result={
                        result
                    }
                    loading={
                        loading
                    }
                />

            </div>

        </div>
    );
}


/* ============================================================
   Risk Result
   ============================================================ */

function RiskResult({
    result,
    loading,
}) {
    if (
        loading
    ) {
        return (
            <section className="content-card result-card">

                <div className="card-heading">

                    <div>

                        <span className="card-kicker">
                            SENTINAL AI
                        </span>

                        <h2>
                            Risk assessment
                        </h2>

                    </div>

                </div>


                <div className="result-empty">

                    <div className="result-loader"></div>

                    <h3>
                        Analyzing transaction
                    </h3>

                    <p>
                        Running the trained model and
                        hybrid risk engine.
                    </p>

                </div>

            </section>
        );
    }


    if (
        !result
    ) {
        return (
            <section className="content-card result-card">

                <div className="card-heading">

                    <div>

                        <span className="card-kicker">
                            SENTINAL AI
                        </span>

                        <h2>
                            Risk assessment
                        </h2>

                    </div>

                </div>


                <div className="result-empty">

                    <ShieldCheck
                        size={42}
                        strokeWidth={1.3}
                    />

                    <h3>
                        Awaiting analysis
                    </h3>

                    <p>
                        Submit a transaction to generate
                        an AI-powered risk assessment.
                    </p>

                </div>

            </section>
        );
    }


    return (
        <section className="content-card result-card">

            <div className="card-heading">

                <div>

                    <span className="card-kicker">
                        ANALYSIS RESULT
                    </span>

                    <h2>
                        Risk assessment
                    </h2>

                </div>

                <ShieldAlert
                    size={18}
                />

            </div>


            <div className="risk-result">

                <div className="risk-main">

                    <div>

                        <span className="risk-label">
                            RISK SCORE
                        </span>

                        <div className="risk-number">

                            {result.risk_score}

                            <span>
                                /100
                            </span>

                        </div>

                    </div>


                    <RiskBadge
                        level={
                            result.risk_level
                        }
                    />

                </div>


                <div className="result-metrics">

                    <Metric
                        label="Fraud probability"
                        value={`${result.fraud_probability_percentage}%`}
                    />


                    <Metric
                        label="Decision"
                        value={
                            result.decision
                        }
                    />

                </div>


                <div className="reasons-block">

                    <div className="result-section-title">
                        RISK DRIVERS
                    </div>


                    {result.reasons.map(
                        (
                            reason,
                            index
                        ) => (
                            <div
                                className="risk-reason"
                                key={
                                    `${reason}-${index}`
                                }
                            >

                                <span>
                                    {index + 1}
                                </span>

                                <p>
                                    {reason}
                                </p>

                            </div>
                        )
                    )}

                </div>


                <div className="result-footer">

                    <div>

                        <Clock3
                            size={14}
                        />

                        Analysis completed

                    </div>


                    <span>
                        {result.transaction_id}
                    </span>

                </div>

            </div>

        </section>
    );
}


/* ============================================================
   Dashboard Page
   ============================================================ */

function DashboardPage({
    stats,
    transactions,
    loading,
}) {
    return (
        <div className="page-container">

            <div className="page-heading">

                <div>

                    <div className="page-eyebrow">
                        OVERVIEW
                    </div>

                    <h1>
                        Risk dashboard
                    </h1>

                    <p>
                        Live statistics from your analyzed
                        transaction history.
                    </p>

                </div>

            </div>


            <div className="stat-grid">

                <StatCard
                    label="Analyzed"
                    value={
                        stats.total
                    }
                    icon={
                        Activity
                    }
                />


                <StatCard
                    label="High / Critical"
                    value={
                        stats.highRisk
                    }
                    icon={
                        ShieldAlert
                    }
                />


                <StatCard
                    label="Blocked"
                    value={
                        stats.blocked
                    }
                    icon={
                        AlertTriangle
                    }
                />


                <StatCard
                    label="Average risk"
                    value={
                        stats.total
                            ? `${stats.averageRisk}/100`
                            : "—"
                    }
                    icon={
                        TrendingUp
                    }
                />

            </div>


            <section className="content-card dashboard-table-card">

                <div className="card-heading">

                    <div>

                        <span className="card-kicker">
                            ACTIVITY
                        </span>

                        <h2>
                            Recent analyses
                        </h2>

                    </div>

                </div>


                {loading ? (
                    <EmptyTableState
                        message="Loading transaction history..."
                    />
                ) : transactions.length === 0 ? (
                    <EmptyTableState />
                ) : (
                    <TransactionTable
                        transactions={
                            transactions
                        }
                    />
                )}

            </section>

        </div>
    );
}


/* ============================================================
   Transactions Page
   ============================================================ */

function TransactionsPage({
    transactions,
    loading,
    onAnalyze,
}) {
    return (
        <div className="page-container">

            <div className="page-heading">

                <div>

                    <div className="page-eyebrow">
                        TRANSACTION MONITORING
                    </div>

                    <h1>
                        Transactions
                    </h1>

                    <p>
                        Review transactions stored in the
                        Sentinel AI database.
                    </p>

                </div>


                <button
                    className="secondary-action"
                    onClick={
                        onAnalyze
                    }
                >

                    Analyze new

                    <ArrowRight
                        size={15}
                    />

                </button>

            </div>


            <section className="content-card dashboard-table-card">

                <div className="card-heading">

                    <div>

                        <span className="card-kicker">
                            PERSISTENT HISTORY
                        </span>

                        <h2>
                            Transaction history
                        </h2>

                    </div>

                </div>


                {loading ? (
                    <EmptyTableState
                        message="Loading transaction history..."
                    />
                ) : transactions.length === 0 ? (
                    <EmptyTableState
                        message="No transactions have been analyzed yet."
                    />
                ) : (
                    <TransactionTable
                        transactions={
                            transactions
                        }
                    />
                )}

            </section>

        </div>
    );
}


/* ============================================================
   Alerts Page
   ============================================================ */

function AlertsPage({
    transactions,
    loading,
    onAnalyze,
    onAlertStatusChange,
}) {
    const alerts =
        transactions.filter(
            (transaction) =>
                transaction.risk_level ===
                    "HIGH" ||
                transaction.risk_level ===
                    "CRITICAL"
        );


    const alertSummary =
        alerts.reduce(
            (summary, transaction) => {
                const status =
                    transaction.alert_status ||
                    "NEW";

                summary.total += 1;

                if (status === "NEW") {
                    summary.newAlerts += 1;
                }

                if (status === "UNDER_REVIEW") {
                    summary.underReview += 1;
                }

                if (status === "RESOLVED") {
                    summary.resolved += 1;
                }

                if (
                    transaction.risk_level ===
                    "CRITICAL"
                ) {
                    summary.critical += 1;
                }

                return summary;
            },
            {
                total: 0,
                newAlerts: 0,
                underReview: 0,
                resolved: 0,
                critical: 0,
            }
        );


    return (
        <div className="page-container">

            <div className="page-heading">

                <div>

                    <div className="page-eyebrow">
                        RISK OPERATIONS
                    </div>

                    <h1>
                        Alerts
                    </h1>

                    <p>
                        High-risk transactions requiring
                        attention.
                    </p>

                </div>

            </div>


            <div className="alert-summary-grid">

                <AlertSummaryCard
                    label="Total alerts"
                    value={alertSummary.total}
                />

                <AlertSummaryCard
                    label="New"
                    value={alertSummary.newAlerts}
                />

                <AlertSummaryCard
                    label="Under review"
                    value={alertSummary.underReview}
                />

                <AlertSummaryCard
                    label="Resolved"
                    value={alertSummary.resolved}
                />

                <AlertSummaryCard
                    label="Critical"
                    value={alertSummary.critical}
                />

            </div>


            <section className="content-card dashboard-table-card">

                <div className="card-heading">

                    <div>

                        <span className="card-kicker">
                            PRIORITY QUEUE
                        </span>

                        <h2>
                            Risk alerts
                        </h2>

                    </div>


                    <ShieldAlert
                        size={18}
                    />

                </div>


                {loading ? (
                    <EmptyTableState
                        message="Loading risk alerts..."
                    />
                ) : alerts.length === 0 ? (
                    <div className="alert-empty">

                        <CheckCircle2
                            size={38}
                        />

                        <h3>
                            No high-risk alerts
                        </h3>

                        <p>
                            High and critical transactions
                            will appear here after analysis.
                        </p>


                        <button
                            className="secondary-action"
                            onClick={
                                onAnalyze
                            }
                        >

                            Analyze transaction

                            <ArrowRight
                                size={15}
                            />

                        </button>

                    </div>
                ) : (
                    <AlertTable
                        transactions={
                            alerts
                        }
                        onAlertStatusChange={
                            onAlertStatusChange
                        }
                    />
                )}

            </section>

        </div>
    );
}


/* ============================================================
   Alert Summary Card
   ============================================================ */

function AlertSummaryCard({
    label,
    value,
}) {
    return (
        <div className="alert-summary-card">

            <span>
                {label}
            </span>

            <strong>
                {value}
            </strong>

        </div>
    );
}


/* ============================================================
   Alert Table
   ============================================================ */

function AlertTable({
    transactions,
    onAlertStatusChange,
}) {
    return (
        <div className="table-wrapper">

            <table>

                <thead>

                    <tr>

                        <th>
                            Transaction
                        </th>

                        <th>
                            Amount
                        </th>

                        <th>
                            Risk
                        </th>

                        <th>
                            Probability
                        </th>

                        <th>
                            Status
                        </th>

                        <th>
                            Action
                        </th>

                    </tr>

                </thead>


                <tbody>

                    {transactions.map(
                        (
                            transaction,
                            index
                        ) => {

                            const alertStatus =
                                transaction.alert_status ||
                                "NEW";


                            return (
                                <tr
                                    key={
                                        `${transaction.transaction_id}-${index}`
                                    }
                                >

                                    <td>

                                        <strong>
                                            {
                                                transaction.transaction_id
                                            }
                                        </strong>

                                    </td>


                                    <td>

                                        ₹
                                        {Number(
                                            transaction.amount
                                        ).toLocaleString(
                                            "en-IN"
                                        )}

                                    </td>


                                    <td>

                                        <RiskBadge
                                            level={
                                                transaction.risk_level
                                            }
                                        />

                                    </td>


                                    <td>

                                        {
                                            transaction.fraud_probability_percentage
                                        }%

                                    </td>


                                    <td>

                                        <AlertStatusBadge
                                            status={
                                                alertStatus
                                            }
                                        />

                                    </td>


                                    <td>

                                        <AlertAction
                                            status={
                                                alertStatus
                                            }
                                            onAction={
                                                () =>
                                                    onAlertStatusChange(
                                                        transaction.transaction_id,
                                                        alertStatus ===
                                                            "NEW"
                                                            ? "UNDER_REVIEW"
                                                            : "RESOLVED"
                                                    )
                                            }
                                        />

                                    </td>

                                </tr>
                            );
                        }
                    )}

                </tbody>

            </table>

        </div>
    );
}


/* ============================================================
   Alert Status Badge
   ============================================================ */

function AlertStatusBadge({
    status,
}) {
    const normalizedStatus =
        status ||
        "NEW";


    return (
        <span
            className={
                `alert-status alert-status-${normalizedStatus.toLowerCase().replace("_", "-")}`
            }
        >
            {normalizedStatus.replace(
                "_",
                " "
            )}
        </span>
    );
}


/* ============================================================
   Alert Action
   ============================================================ */

function AlertAction({
    status,
    onAction,
}) {
    if (
        status ===
        "RESOLVED"
    ) {
        return (
            <span className="alert-resolved-label">
                Resolved
            </span>
        );
    }


    return (
        <button
            className="secondary-action alert-action"
            onClick={
                onAction
            }
        >

            {status ===
            "NEW"
                ? "Review"
                : "Resolve"
            }

            <ArrowRight
                size={14}
            />

        </button>
    );
}


/* ============================================================
   Settings Page
   ============================================================ */

function SettingsPage() {
    return (
        <div className="page-container">

            <div className="page-heading">

                <div>

                    <div className="page-eyebrow">
                        CONFIGURATION
                    </div>

                    <h1>
                        Settings
                    </h1>

                    <p>
                        Application configuration and
                        risk-engine information.
                    </p>

                </div>

            </div>


            <section className="content-card settings-card">

                <div className="setting-row">

                    <div>

                        <strong>
                            Risk engine
                        </strong>

                        <span>
                            Hybrid ML + rule-based scoring
                        </span>

                    </div>


                    <span className="setting-status">
                        ACTIVE
                    </span>

                </div>


                <div className="setting-row">

                    <div>

                        <strong>
                            Machine learning model
                        </strong>

                        <span>
                            Random Forest classifier
                        </span>

                    </div>


                    <span className="setting-status">
                        LOADED
                    </span>

                </div>


                <div className="setting-row">

                    <div>

                        <strong>
                            Analysis mode
                        </strong>

                        <span>
                            Transaction-level risk assessment
                        </span>

                    </div>


                    <span className="setting-status">
                        READY
                    </span>

                </div>


                <div className="setting-row">

                    <div>

                        <strong>
                            Transaction storage
                        </strong>

                        <span>
                            Persistent SQLite database
                        </span>

                    </div>


                    <span className="setting-status">
                        ACTIVE
                    </span>

                </div>

            </section>

        </div>
    );
}


/* ============================================================
   Reusable UI components
   ============================================================ */

function Field({
    label,
    name,
    value,
    onChange,
    type = "text",
    min,
    max,
    step,
}) {
    return (
        <div className="field">

            <label>
                {label}
            </label>


            <input
                name={name}
                type={type}
                value={value}
                min={min}
                max={max}
                step={step}
                onChange={onChange}
            />

        </div>
    );
}


function SelectField({
    label,
    name,
    value,
    onChange,
    options,
}) {
    return (
        <div className="field">

            <label>
                {label}
            </label>


            <select
                name={name}
                value={value}
                onChange={onChange}
            >

                {options.map(
                    (option) => (
                        <option
                            key={
                                option[0]
                            }
                            value={
                                option[0]
                            }
                        >
                            {option[1]}
                        </option>
                    )
                )}

            </select>

        </div>
    );
}


function Toggle({
    label,
    checked,
    onChange,
}) {
    return (
        <label className="toggle-field">

            <input
                type="checkbox"
                checked={checked}
                onChange={
                    (event) =>
                        onChange(
                            event.target.checked
                        )
                }
            />


            <span>
                {label}
            </span>

        </label>
    );
}


function RiskBadge({
    level,
}) {
    return (
        <span
            className={
                `risk-badge risk-${level.toLowerCase()}`
            }
        >
            {level}
        </span>
    );
}


function Metric({
    label,
    value,
}) {
    return (
        <div className="result-metric">

            <span>
                {label}
            </span>


            <strong>
                {value}
            </strong>

        </div>
    );
}


function StatCard({
    label,
    value,
    icon: Icon,
}) {
    return (
        <div className="stat-card">

            <div className="stat-card-icon">

                <Icon
                    size={18}
                />

            </div>


            <div>

                <span>
                    {label}
                </span>


                <strong>
                    {value}
                </strong>

            </div>

        </div>
    );
}


function TransactionTable({
    transactions,
}) {
    return (
        <div className="table-wrapper">

            <table>

                <thead>

                    <tr>

                        <th>
                            Transaction
                        </th>

                        <th>
                            Amount
                        </th>

                        <th>
                            Risk
                        </th>

                        <th>
                            Probability
                        </th>

                        <th>
                            Decision
                        </th>

                    </tr>

                </thead>


                <tbody>

                    {transactions.map(
                        (
                            transaction,
                            index
                        ) => (
                            <tr
                                key={
                                    `${transaction.transaction_id}-${index}`
                                }
                            >

                                <td>

                                    <strong>
                                        {
                                            transaction.transaction_id
                                        }
                                    </strong>

                                </td>


                                <td>

                                    ₹
                                    {Number(
                                        transaction.amount
                                    ).toLocaleString(
                                        "en-IN"
                                    )}

                                </td>


                                <td>

                                    <RiskBadge
                                        level={
                                            transaction.risk_level
                                        }
                                    />

                                </td>


                                <td>

                                    {
                                        transaction.fraud_probability_percentage
                                    }%

                                </td>


                                <td>

                                    <span
                                        className={
                                            `decision decision-${transaction.decision.toLowerCase()}`
                                        }
                                    >
                                        {
                                            transaction.decision
                                        }
                                    </span>

                                </td>

                            </tr>
                        )
                    )}

                </tbody>

            </table>

        </div>
    );
}


function EmptyTableState({
    message = "Analyze a transaction to populate this view.",
}) {
    return (
        <div className="table-empty">

            <Activity
                size={32}
            />

            <p>
                {message}
            </p>

        </div>
    );
}


export default App;