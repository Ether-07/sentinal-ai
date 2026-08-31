import axios from "axios";


const API_BASE_URL = "http://127.0.0.1:8000";


const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});


export async function analyzeTransaction(
    transaction
) {
    const response = await api.post(
        "/api/v1/risk/analyze",
        transaction
    );

    return response.data;
}


export async function getTransactions(
    limit = 100
) {
    const response = await api.get(
        "/api/v1/transactions",
        {
            params: {
                limit,
            },
        }
    );

    return response.data;
}


export async function getTransaction(
    transactionId
) {
    const response = await api.get(
        `/api/v1/transactions/${encodeURIComponent(
            transactionId
        )}`
    );

    return response.data;
}


export async function updateAlertStatus(
    transactionId,
    alertStatus
) {
    const response = await api.patch(
        `/api/v1/transactions/${encodeURIComponent(
            transactionId
        )}/alert-status`,
        {
            alert_status: alertStatus,
        }
    );

    return response.data;
}


export async function getHealthStatus() {
    const response = await api.get(
        "/api/health"
    );

    return response.data;
}