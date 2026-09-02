WITH stg_ship AS (
    SELECT * FROM {{ ref('stg_shipments') }}
),
dim_wh AS (
    SELECT * FROM {{ ref('dim_warehouse') }}
)
SELECT
    s.shipment_id,
    s.order_id,
    w.warehouse_key AS origin_warehouse_key,
    s.carrier,
    s.transit_mode,
    s.shipment_status,
    s.shipped_at,
    s.estimated_delivery_at,
    s.actual_delivery_at,
    CASE 
        WHEN s.actual_delivery_at > s.estimated_delivery_at THEN 
            EXTRACT(EPOCH FROM (s.actual_delivery_at - s.estimated_delivery_at)) / 3600
        ELSE 0 
    END AS delay_hours,
    CASE WHEN s.actual_delivery_at > s.estimated_delivery_at THEN TRUE ELSE FALSE END AS is_delayed
FROM stg_ship s
LEFT JOIN dim_wh w ON s.origin_warehouse_id = w.warehouse_id;
