WITH stg AS (
    SELECT * FROM {{ ref('stg_products') }}
)
SELECT
    ROW_NUMBER() OVER (ORDER BY product_id) AS product_key,
    product_id,
    sku,
    product_name,
    category,
    unit_cost_usd,
    weight_kg,
    supplier_id
FROM stg;
