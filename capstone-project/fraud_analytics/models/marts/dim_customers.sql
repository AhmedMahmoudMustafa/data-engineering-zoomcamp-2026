{{ config(materialized='table') }}

SELECT
    customer_id,
    COUNT(*)                            AS total_transactions,
    COUNTIF(is_fraud = TRUE)            AS fraud_count,
    ROUND(SUM(amount), 2)               AS total_amount_sent,
    ROUND(MAX(amount), 2)               AS max_transaction,
    ROUND(AVG(amount), 2)               AS avg_transaction,
    COUNTIF(has_balance_mismatch = TRUE) AS mismatch_count,
    CASE
        WHEN COUNTIF(is_fraud = TRUE) > 0   THEN 'FRAUDSTER'
        WHEN COUNTIF(has_balance_mismatch
             = TRUE) > 2                    THEN 'SUSPICIOUS'
        ELSE                                     'CLEAN'
    END AS customer_risk_label
FROM {{ ref('int_transactions_enriched') }}
GROUP BY customer_id