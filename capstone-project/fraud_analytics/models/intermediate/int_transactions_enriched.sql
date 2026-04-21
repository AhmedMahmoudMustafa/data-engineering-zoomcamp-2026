{{ config(materialized='view') }}

SELECT
    *,
    -- Risk scoring
    CASE
        WHEN is_fraud = TRUE                        THEN 'CONFIRMED_FRAUD'
        WHEN has_balance_mismatch = TRUE
         AND is_large_transaction = TRUE            THEN 'HIGH_RISK'
        WHEN has_balance_mismatch = TRUE            THEN 'MEDIUM_RISK'
        ELSE                                             'LOW_RISK'
    END AS risk_level,

    -- Balance difference (how much origin lost)
    ROUND(old_balance_origin - new_balance_origin, 2) AS origin_balance_change,

    -- Transaction size bucket
    CASE
        WHEN amount < 10000     THEN 'SMALL'
        WHEN amount < 100000    THEN 'MEDIUM'
        WHEN amount < 500000    THEN 'LARGE'
        ELSE                         'VERY_LARGE'
    END AS transaction_size

FROM {{ ref('stg_transactions') }}