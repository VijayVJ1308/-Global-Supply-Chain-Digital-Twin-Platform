WITH source AS (
    SELECT * FROM bronze.raw_suppliers
)
SELECT
    supplier_id,
    TRIM(name) AS supplier_name,
    LOWER(contact_email) AS contact_email,
    country,
    region,
    tier,
    CAST(rating AS NUMERIC(3,2)) AS rating,
    ingested_at
FROM source
WHERE supplier_id IS NOT NULL
