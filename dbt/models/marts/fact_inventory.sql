WITH stg_inv AS (
    SELECT * FROM {{ ref('stg_inventory') }}
),
dim_wh AS (
    SELECT * FROM {{ ref('dim_warehouse') }}
),
dim_prod AS (
    SELECT * FROM {{ ref('dim_product') }}
)
SELECT
    i.inventory_id,
    w.warehouse_key,
    p.product_key,
    i.quantity_on_hand,
    i.reorder_level,
    i.safety_stock,
    i.is_low_stock,
    (i.quantity_on_hand * p.unit_cost_usd) AS inventory_value_usd,
    i.last_counted_at
FROM stg_inv i
LEFT JOIN dim_wh w ON i.warehouse_id = w.warehouse_id
LEFT JOIN dim_prod p ON i.product_id = p.product_id;
