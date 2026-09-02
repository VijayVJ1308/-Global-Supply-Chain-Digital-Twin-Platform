-- ====================================================================
-- GLOBAL SUPPLY CHAIN DIGITAL TWIN PLATFORM
-- Complete Master SQL Pipeline: Schemas, DDLs, Star Schema & Analytics
-- Engine: PostgreSQL 15+ / Medallion Lakehouse Architecture
-- ====================================================================

-- ====================================================================
-- STEP 1: SCHEMA INITIALIZATION
-- ====================================================================
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

COMMENT ON SCHEMA bronze IS 'Raw ingested data payloads from ERP, WMS, CRM, and IoT streaming Kafka';
COMMENT ON SCHEMA silver IS 'Cleaned, deduplicated, standardized, and typed relational datasets';
COMMENT ON SCHEMA gold IS 'Curated dimensional star schema and operational analytics reporting views';

-- ====================================================================
-- STEP 2: BRONZE LAYER (RAW INGESTION TABLES)
-- ====================================================================
DROP TABLE IF EXISTS bronze.raw_suppliers CASCADE;
CREATE TABLE bronze.raw_suppliers (
    supplier_id VARCHAR(50),
    name VARCHAR(255),
    contact_email VARCHAR(255),
    country VARCHAR(100),
    region VARCHAR(100),
    tier VARCHAR(50),
    rating NUMERIC(3,2),
    raw_payload JSONB,
    source_system VARCHAR(50) DEFAULT 'ERP_SUPPLIER_API',
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS bronze.raw_products CASCADE;
CREATE TABLE bronze.raw_products (
    product_id VARCHAR(50),
    sku VARCHAR(100),
    name VARCHAR(255),
    category VARCHAR(100),
    unit_cost VARCHAR(50),
    currency VARCHAR(10),
    weight_kg VARCHAR(50),
    supplier_id VARCHAR(50),
    raw_payload JSONB,
    source_system VARCHAR(50) DEFAULT 'ERP_CATALOG',
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS bronze.raw_warehouses CASCADE;
CREATE TABLE bronze.raw_warehouses (
    warehouse_id VARCHAR(50),
    code VARCHAR(50),
    name VARCHAR(255),
    city VARCHAR(100),
    country VARCHAR(100),
    latitude VARCHAR(50),
    longitude VARCHAR(50),
    capacity_sqft VARCHAR(50),
    temp_zone_type VARCHAR(50),
    raw_payload JSONB,
    source_system VARCHAR(50) DEFAULT 'WMS_FACILITY_DB',
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS bronze.raw_customers CASCADE;
CREATE TABLE bronze.raw_customers (
    customer_id VARCHAR(50),
    company_name VARCHAR(255),
    industry VARCHAR(100),
    country VARCHAR(100),
    region VARCHAR(100),
    tier VARCHAR(50),
    raw_payload JSONB,
    source_system VARCHAR(50) DEFAULT 'CRM_SYSTEM',
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS bronze.raw_orders CASCADE;
CREATE TABLE bronze.raw_orders (
    order_id VARCHAR(50),
    customer_id VARCHAR(50),
    product_id VARCHAR(50),
    supplier_id VARCHAR(50),
    quantity VARCHAR(50),
    unit_price VARCHAR(50),
    currency VARCHAR(10),
    order_date VARCHAR(50),
    required_date VARCHAR(50),
    status VARCHAR(50),
    raw_payload JSONB,
    source_system VARCHAR(50) DEFAULT 'ERP_ORDERS',
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS bronze.raw_shipments CASCADE;
CREATE TABLE bronze.raw_shipments (
    shipment_id VARCHAR(50),
    order_id VARCHAR(50),
    origin_warehouse_id VARCHAR(50),
    destination_city VARCHAR(100),
    destination_country VARCHAR(100),
    carrier VARCHAR(100),
    mode VARCHAR(50),
    status VARCHAR(50),
    shipped_at VARCHAR(50),
    estimated_delivery_at VARCHAR(50),
    actual_delivery_at VARCHAR(50),
    raw_payload JSONB,
    source_system VARCHAR(50) DEFAULT 'TMS_TRACKING_API',
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS bronze.raw_inventory CASCADE;
CREATE TABLE bronze.raw_inventory (
    inventory_id VARCHAR(50),
    warehouse_id VARCHAR(50),
    product_id VARCHAR(50),
    quantity_on_hand VARCHAR(50),
    reorder_level VARCHAR(50),
    safety_stock VARCHAR(50),
    last_counted_at VARCHAR(50),
    raw_payload JSONB,
    source_system VARCHAR(50) DEFAULT 'WMS_INVENTORY',
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS bronze.raw_iot_sensors CASCADE;
CREATE TABLE bronze.raw_iot_sensors (
    event_id VARCHAR(50),
    shipment_id VARCHAR(50),
    device_id VARCHAR(50),
    latitude VARCHAR(50),
    longitude VARCHAR(50),
    temperature_c VARCHAR(50),
    humidity_pct VARCHAR(50),
    battery_level VARCHAR(50),
    recorded_at VARCHAR(50),
    raw_payload JSONB,
    source_system VARCHAR(50) DEFAULT 'IOT_SENSOR_KAFKA',
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ====================================================================
-- STEP 3: SILVER LAYER (CLEANED & STANDARDIZED TABLES)
-- ====================================================================
DROP TABLE IF EXISTS silver.suppliers CASCADE;
CREATE TABLE silver.suppliers (
    supplier_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    country VARCHAR(100),
    region VARCHAR(100),
    tier VARCHAR(50),
    rating NUMERIC(3,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS silver.products CASCADE;
CREATE TABLE silver.products (
    product_id VARCHAR(50) PRIMARY KEY,
    sku VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    unit_cost_usd NUMERIC(12,2) NOT NULL,
    weight_kg NUMERIC(10,2),
    supplier_id VARCHAR(50) REFERENCES silver.suppliers(supplier_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS silver.warehouses CASCADE;
CREATE TABLE silver.warehouses (
    warehouse_id VARCHAR(50) PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100),
    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6),
    capacity_sqft INTEGER,
    temp_zone_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS silver.customers CASCADE;
CREATE TABLE silver.customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    country VARCHAR(100),
    region VARCHAR(100),
    tier VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS silver.orders CASCADE;
CREATE TABLE silver.orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES silver.customers(customer_id),
    product_id VARCHAR(50) REFERENCES silver.products(product_id),
    supplier_id VARCHAR(50) REFERENCES silver.suppliers(supplier_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_usd NUMERIC(12,2) NOT NULL,
    total_amount_usd NUMERIC(14,2) NOT NULL,
    original_currency VARCHAR(10),
    order_date TIMESTAMP WITH TIME ZONE NOT NULL,
    required_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS silver.shipments CASCADE;
CREATE TABLE silver.shipments (
    shipment_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES silver.orders(order_id),
    origin_warehouse_id VARCHAR(50) REFERENCES silver.warehouses(warehouse_id),
    destination_city VARCHAR(100),
    destination_country VARCHAR(100),
    carrier VARCHAR(100),
    mode VARCHAR(50),
    status VARCHAR(50) NOT NULL,
    shipped_at TIMESTAMP WITH TIME ZONE,
    estimated_delivery_at TIMESTAMP WITH TIME ZONE,
    actual_delivery_at TIMESTAMP WITH TIME ZONE,
    delay_hours INTEGER DEFAULT 0,
    is_delayed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS silver.inventory CASCADE;
CREATE TABLE silver.inventory (
    inventory_id VARCHAR(50) PRIMARY KEY,
    warehouse_id VARCHAR(50) REFERENCES silver.warehouses(warehouse_id),
    product_id VARCHAR(50) REFERENCES silver.products(product_id),
    quantity_on_hand INTEGER NOT NULL CHECK (quantity_on_hand >= 0),
    reorder_level INTEGER NOT NULL,
    safety_stock INTEGER NOT NULL,
    is_low_stock BOOLEAN DEFAULT FALSE,
    last_counted_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS silver.iot_sensors CASCADE;
CREATE TABLE silver.iot_sensors (
    event_id VARCHAR(50) PRIMARY KEY,
    shipment_id VARCHAR(50) REFERENCES silver.shipments(shipment_id),
    device_id VARCHAR(50) NOT NULL,
    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6),
    temperature_c NUMERIC(5,2),
    humidity_pct NUMERIC(5,2),
    battery_level INTEGER,
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_temp_breach BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ====================================================================
-- STEP 4: GOLD LAYER (STAR SCHEMA WAREHOUSE MODELS)
-- ====================================================================
DROP TABLE IF EXISTS gold.dim_supplier CASCADE;
CREATE TABLE gold.dim_supplier (
    supplier_key SERIAL PRIMARY KEY,
    supplier_id VARCHAR(50) UNIQUE NOT NULL,
    supplier_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    country VARCHAR(100),
    region VARCHAR(100),
    tier VARCHAR(50),
    rating NUMERIC(3,2),
    is_active BOOLEAN DEFAULT TRUE
);

DROP TABLE IF EXISTS gold.dim_product CASCADE;
CREATE TABLE gold.dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(50) UNIQUE NOT NULL,
    sku VARCHAR(100) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    unit_cost_usd NUMERIC(12,2),
    weight_kg NUMERIC(10,2),
    supplier_id VARCHAR(50)
);

DROP TABLE IF EXISTS gold.dim_warehouse CASCADE;
CREATE TABLE gold.dim_warehouse (
    warehouse_key SERIAL PRIMARY KEY,
    warehouse_id VARCHAR(50) UNIQUE NOT NULL,
    warehouse_code VARCHAR(50) NOT NULL,
    warehouse_name VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100),
    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6),
    capacity_sqft INTEGER,
    temp_zone_type VARCHAR(50)
);

DROP TABLE IF EXISTS gold.dim_customer CASCADE;
CREATE TABLE gold.dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    country VARCHAR(100),
    region VARCHAR(100),
    tier VARCHAR(50)
);

DROP TABLE IF EXISTS gold.dim_date CASCADE;
CREATE TABLE gold.dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day_of_month INT NOT NULL,
    day_of_week INT NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

DROP TABLE IF EXISTS gold.fact_orders CASCADE;
CREATE TABLE gold.fact_orders (
    order_fact_key SERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    customer_key INT REFERENCES gold.dim_customer(customer_key),
    product_key INT REFERENCES gold.dim_product(product_key),
    supplier_key INT REFERENCES gold.dim_supplier(supplier_key),
    order_date_key INT REFERENCES gold.dim_date(date_key),
    quantity INT NOT NULL,
    unit_price_usd NUMERIC(12,2) NOT NULL,
    total_amount_usd NUMERIC(14,2) NOT NULL,
    order_status VARCHAR(50) NOT NULL
);

DROP TABLE IF EXISTS gold.fact_shipments CASCADE;
CREATE TABLE gold.fact_shipments (
    shipment_fact_key SERIAL PRIMARY KEY,
    shipment_id VARCHAR(50) NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    origin_warehouse_key INT REFERENCES gold.dim_warehouse(warehouse_key),
    shipped_date_key INT REFERENCES gold.dim_date(date_key),
    delivery_date_key INT REFERENCES gold.dim_date(date_key),
    carrier VARCHAR(100),
    transit_mode VARCHAR(50),
    shipment_status VARCHAR(50),
    delay_hours INT DEFAULT 0,
    is_delayed BOOLEAN DEFAULT FALSE,
    temp_breach_count INT DEFAULT 0
);

DROP TABLE IF EXISTS gold.fact_inventory CASCADE;
CREATE TABLE gold.fact_inventory (
    inventory_fact_key SERIAL PRIMARY KEY,
    inventory_id VARCHAR(50) NOT NULL,
    warehouse_key INT REFERENCES gold.dim_warehouse(warehouse_key),
    product_key INT REFERENCES gold.dim_product(product_key),
    snapshot_date_key INT REFERENCES gold.dim_date(date_key),
    quantity_on_hand INT NOT NULL,
    reorder_level INT NOT NULL,
    safety_stock INT NOT NULL,
    is_low_stock BOOLEAN DEFAULT FALSE,
    inventory_value_usd NUMERIC(14,2)
);

-- ====================================================================
-- STEP 5: GOLD REPORTING & OPERATIONAL ANALYTICS VIEWS
-- ====================================================================

-- 1. C-Suite Executive Summary KPI View
CREATE OR REPLACE VIEW gold.vw_executive_kpi_summary AS
WITH order_stats AS (
    SELECT 
        COUNT(DISTINCT order_id) AS total_orders,
        COALESCE(SUM(total_amount_usd), 0) AS total_revenue_usd,
        COUNT(CASE WHEN order_status = 'DELIVERED' THEN 1 END) AS delivered_orders
    FROM gold.fact_orders
),
shipment_stats AS (
    SELECT 
        COUNT(DISTINCT shipment_id) AS total_shipments,
        COUNT(CASE WHEN is_delayed = TRUE OR shipment_status = 'DELAYED' THEN 1 END) AS delayed_shipments,
        COUNT(CASE WHEN shipment_status = 'DELIVERED' AND is_delayed = FALSE THEN 1 END) AS on_time_shipments,
        COALESCE(AVG(delay_hours), 0) AS avg_delay_hours,
        COALESCE(SUM(temp_breach_count), 0) AS total_temp_breaches
    FROM gold.fact_shipments
),
inventory_stats AS (
    SELECT 
        COUNT(DISTINCT inventory_id) AS total_monitored_skus,
        COUNT(CASE WHEN is_low_stock = TRUE THEN 1 END) AS stockout_risk_items,
        COALESCE(SUM(inventory_value_usd), 0) AS total_inventory_value_usd
    FROM gold.fact_inventory
)
SELECT 
    o.total_orders,
    o.total_revenue_usd,
    ROUND((o.delivered_orders::NUMERIC / NULLIF(o.total_orders, 0)) * 100.0, 2) AS order_fulfillment_rate_pct,
    s.total_shipments,
    s.delayed_shipments,
    ROUND((s.delayed_shipments::NUMERIC / NULLIF(s.total_shipments, 0)) * 100.0, 2) AS shipment_delay_rate_pct,
    ROUND((s.on_time_shipments::NUMERIC / NULLIF(s.total_shipments, 0)) * 100.0, 2) AS on_time_delivery_rate_pct,
    ROUND(s.avg_delay_hours, 1) AS avg_shipment_delay_hours,
    s.total_temp_breaches,
    i.total_monitored_skus,
    i.stockout_risk_items,
    i.total_inventory_value_usd,
    CURRENT_TIMESTAMP AS last_refreshed_at
FROM order_stats o
CROSS JOIN shipment_stats s
CROSS JOIN inventory_stats i;

-- 2. Supplier Reliability Scorecard View
CREATE OR REPLACE VIEW gold.vw_supplier_scorecard AS
SELECT 
    sup.supplier_id,
    sup.supplier_name,
    sup.country AS supplier_country,
    sup.tier AS supplier_tier,
    sup.rating AS supplier_base_rating,
    COUNT(DISTINCT fo.order_id) AS total_orders_fulfilled,
    COALESCE(SUM(fo.total_amount_usd), 0) AS total_procurement_spend_usd,
    COUNT(CASE WHEN fo.order_status = 'DELIVERED' THEN 1 END) AS delivered_orders,
    ROUND(
        (COUNT(CASE WHEN fo.order_status = 'DELIVERED' THEN 1 END)::NUMERIC / 
        NULLIF(COUNT(DISTINCT fo.order_id), 0)) * 100.0, 2
    ) AS supplier_otif_pct,
    CASE 
        WHEN sup.rating >= 4.5 THEN 'Tier 1 Preferred'
        WHEN sup.rating >= 3.8 THEN 'Standard Vendor'
        ELSE 'Under Watch / Risk'
    END AS vendor_risk_category
FROM gold.dim_supplier sup
LEFT JOIN gold.fact_orders fo ON sup.supplier_key = fo.supplier_key
GROUP BY sup.supplier_id, sup.supplier_name, sup.country, sup.tier, sup.rating;

-- 3. Carrier & Transit Mode Logistics Analytics View
CREATE OR REPLACE VIEW gold.vw_carrier_performance AS
SELECT 
    fs.carrier,
    fs.transit_mode,
    COUNT(fs.shipment_fact_key) AS total_shipments_handled,
    COUNT(CASE WHEN fs.is_delayed = TRUE THEN 1 END) AS total_delayed_shipments,
    ROUND(COALESCE(AVG(fs.delay_hours), 0), 1) AS avg_delay_hours,
    ROUND(
        ((COUNT(fs.shipment_fact_key) - COUNT(CASE WHEN fs.is_delayed = TRUE THEN 1 END))::NUMERIC / 
        NULLIF(COUNT(fs.shipment_fact_key), 0)) * 100.0, 2
    ) AS carrier_on_time_pct,
    COALESCE(SUM(fs.temp_breach_count), 0) AS total_cold_chain_breaches
FROM gold.fact_shipments fs
GROUP BY fs.carrier, fs.transit_mode;

-- 4. Warehouse Stockout Risk & Reorder Alerts View
CREATE OR REPLACE VIEW gold.vw_inventory_stockout_risk AS
SELECT 
    dw.warehouse_code,
    dw.warehouse_name,
    dw.city AS warehouse_city,
    dp.sku,
    dp.product_name,
    dp.category AS product_category,
    fi.quantity_on_hand,
    fi.safety_stock,
    fi.reorder_level,
    fi.inventory_value_usd,
    CASE 
        WHEN fi.quantity_on_hand <= (fi.safety_stock * 0.5) THEN 'CRITICAL STOCKOUT'
        WHEN fi.quantity_on_hand <= fi.safety_stock THEN 'HIGH RISK'
        WHEN fi.quantity_on_hand <= fi.reorder_level THEN 'REORDER REQUIRED'
        ELSE 'HEALTHY'
    END AS stock_status
FROM gold.fact_inventory fi
JOIN gold.dim_warehouse dw ON fi.warehouse_key = dw.warehouse_key
JOIN gold.dim_product dp ON fi.product_key = dp.product_key
WHERE fi.is_low_stock = TRUE OR fi.quantity_on_hand <= fi.reorder_level;

-- ====================================================================
-- END OF MASTER PIPELINE SCRIPT
-- ====================================================================
