WITH source AS (
    SELECT * FROM bronze.raw_customers
)
SELECT
    customer_id,
    TRIM(company_name) AS company_name,
    industry,
    country,
    region,
    tier,
    ingested_at
FROM source
WHERE customer_id IS NOT NULL;
