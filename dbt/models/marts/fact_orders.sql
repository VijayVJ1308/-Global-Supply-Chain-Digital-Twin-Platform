WITH stg_ord AS (
    SELECT * FROM {{ ref('stg_orders') }}
),
dim_sup AS (
    SELECT * FROM {{ ref('stg_suppliers') }}
)
SELECT
    o.order_id,
    o.customer_id,
    o.product_id,
    s.supplier_id,
    o.quantity,
    o.unit_price_usd,
    o.total_amount_usd,
    o.order_date,
    o.order_status
FROM stg_ord o
LEFT JOIN dim_sup s ON o.supplier_id = s.supplier_id
