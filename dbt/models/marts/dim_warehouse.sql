WITH stg AS (
    SELECT * FROM {{ ref('stg_warehouses') }}
)
SELECT
    ROW_NUMBER() OVER (ORDER BY warehouse_id) AS warehouse_key,
    warehouse_id,
    warehouse_code,
    warehouse_name,
    city,
    country,
    latitude,
    longitude,
    capacity_sqft,
    temp_zone_type
FROM stg;
