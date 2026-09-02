-- Database initialization script for Global Supply Chain Digital Twin Platform

CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

COMMENT ON SCHEMA bronze IS 'Raw data ingested directly from source systems (ERP, IoT, CSV, REST APIs)';
COMMENT ON SCHEMA silver IS 'Cleaned, standardized, deduplicated, and validated data';
COMMENT ON SCHEMA gold IS 'Curated business-ready Star Schema data warehouse models for operational analytics';
