WITH source AS (
    SELECT * FROM bronze.raw_warehouses
)
SELECT
    warehouse_id,
    UPPER(TRIM(code)) AS warehouse_code,
    TRIM(name) AS warehouse_name,
    city,
    country,
    CAST(latitude AS NUMERIC(9,6)) AS latitude,
    CAST(longitude AS NUMERIC(9,6)) AS longitude,
    CAST(capacity_sqft AS INT) AS capacity_sqft,
    temp_zone_type,
    ingested_at
FROM source
WHERE warehouse_id IS NOT NULL;
