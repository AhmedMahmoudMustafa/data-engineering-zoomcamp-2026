{{ config(materialized='table') }}

SELECT
    risk_level,
    COUNT(*)                                            AS transaction_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2)  AS percentage,
    ROUND(SUM(amount), 2)                               AS total_amount,
    COUNTIF(is_fraud = TRUE)                            AS confirmed_fraud_count
FROM {{ ref('int_transactions_enriched') }}
GROUP BY risk_level
ORDER BY transaction_count DESC
