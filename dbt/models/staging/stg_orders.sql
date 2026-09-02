WITH source AS (
    SELECT * FROM bronze.raw_orders
)
SELECT
    order_id,
    customer_id,
    product_id,
    supplier_id,
    CAST(quantity AS INT) AS quantity,
    CAST(REPLACE(REPLACE(unit_price, '$', ''), ',', '') AS NUMERIC(12,2)) AS unit_price_usd,
    CAST(quantity AS INT) * CAST(REPLACE(REPLACE(unit_price, '$', ''), ',', '') AS NUMERIC(12,2)) AS total_amount_usd,
    CAST(order_date AS TIMESTAMP) AS order_date,
    CAST(required_date AS TIMESTAMP) AS required_date,
    status AS order_status
FROM source
WHERE order_id IS NOT NULL
