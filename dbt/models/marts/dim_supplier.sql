WITH stg AS (
    SELECT * FROM {{ ref('stg_suppliers') }}
)
SELECT
    ROW_NUMBER() OVER (ORDER BY supplier_id) AS supplier_key,
    supplier_id,
    supplier_name,
    contact_email,
    country,
    region,
    tier,
    rating,
    TRUE AS is_active
FROM stg;
