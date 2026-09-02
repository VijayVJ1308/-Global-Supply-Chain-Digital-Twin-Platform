WITH source AS (
    SELECT * FROM bronze.raw_inventory
)
SELECT
    inventory_id,
    warehouse_id,
    product_id,
    CAST(quantity_on_hand AS INT) AS quantity_on_hand,
    CAST(reorder_level AS INT) AS reorder_level,
    CAST(safety_stock AS INT) AS safety_stock,
    CASE WHEN CAST(quantity_on_hand AS INT) <= CAST(safety_stock AS INT) THEN TRUE ELSE FALSE END AS is_low_stock,
    CAST(last_counted_at AS TIMESTAMP) AS last_counted_at,
    ingested_at
FROM source
WHERE inventory_id IS NOT NULL;
