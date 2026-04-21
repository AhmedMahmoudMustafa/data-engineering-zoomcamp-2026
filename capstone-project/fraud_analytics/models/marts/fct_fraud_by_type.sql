{{ config(materialized='table') }}

SELECT
    transaction_type,
    risk_level,
    COUNT(*)                                        AS total_transactions,
    COUNTIF(is_fraud = TRUE)                        AS fraud_count,
    ROUND(AVG(amount), 2)                           AS avg_amount,
    ROUND(SUM(amount), 2)                           AS total_amount,
    ROUND(COUNTIF(is_fraud = TRUE) / COUNT(*) * 100, 4) AS fraud_rate_pct
FROM {{ ref('int_transactions_enriched') }}
GROUP BY transaction_type, risk_level
ORDER BY fraud_count DESC   