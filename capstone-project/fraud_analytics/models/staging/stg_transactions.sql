{{ config(materialized='view') }}

SELECT
    step                                    AS time_step,
    type                                    AS transaction_type,
    ROUND(amount, 2)                        AS amount,
    customer_id,
    recipient_id,
    
    ROUND(old_balance_origin, 2)            AS old_balance_origin,
    ROUND(new_balance_origin, 2)            AS new_balance_origin,
    ROUND(old_balance_dest, 2)              AS old_balance_dest,
    ROUND(new_balance_dest, 2)              AS new_balance_dest,

    CAST(isFraud AS BOOLEAN)                AS is_fraud,
    CAST(isFlaggedFraud AS BOOLEAN)         AS is_flagged_fraud,
    CAST(is_large_transaction AS BOOLEAN)   AS is_large_transaction,
    CAST(balance_mismatch AS BOOLEAN)       AS has_balance_mismatch

FROM {{ source('raw', 'transactions_raw') }}