{{ config(materialized='table') }}

SELECT * FROM {{ ref('int_transactions_enriched') }}