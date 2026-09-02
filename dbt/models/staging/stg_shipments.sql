WITH source AS (
    SELECT * FROM bronze.raw_shipments
)
SELECT
    shipment_id,
    order_id,
    origin_warehouse_id,
    destination_city,
    destination_country,
    carrier,
    mode AS transit_mode,
    status AS shipment_status,
    CAST(shipped_at AS TIMESTAMP) AS shipped_at,
    CAST(estimated_delivery_at AS TIMESTAMP) AS estimated_delivery_at,
    CAST(actual_delivery_at AS TIMESTAMP) AS actual_delivery_at,
    ingested_at
FROM source
WHERE shipment_id IS NOT NULL;
