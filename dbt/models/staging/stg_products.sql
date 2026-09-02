WITH source AS (
    SELECT * FROM bronze.raw_products
)
SELECT
    product_id,
    UPPER(TRIM(sku)) AS sku,
    TRIM(name) AS product_name,
    category,
    CAST(REPLACE(REPLACE(unit_cost, '$', ''), ',', '') AS NUMERIC(12,2)) AS unit_cost_usd,
    CAST(weight_kg AS NUMERIC(10,2)) AS weight_kg,
    supplier_id,
    ingested_at
FROM source
WHERE product_id IS NOT NULL;
