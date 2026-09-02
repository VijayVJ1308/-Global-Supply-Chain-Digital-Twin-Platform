-- Gold Layer DDLs: Star Schema Dimensional Warehouse Models

-- Dimensions
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
    is_active BOOLEAN
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

DROP TABLE IF EXISTS gold.dim_region CASCADE;
CREATE TABLE gold.dim_region (
    region_key SERIAL PRIMARY KEY,
    region_name VARCHAR(100) UNIQUE NOT NULL,
    subregion VARCHAR(100),
    continent VARCHAR(100),
    primary_hub VARCHAR(100)
);

DROP TABLE IF EXISTS gold.dim_date CASCADE;
CREATE TABLE gold.dim_date (
    date_key INT PRIMARY KEY, -- e.g., 20260805
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

-- Fact Tables
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
    delay_hours INT,
    is_delayed BOOLEAN,
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
    is_low_stock BOOLEAN,
    inventory_value_usd NUMERIC(14,2)
);

DROP TABLE IF EXISTS gold.fact_deliveries CASCADE;
CREATE TABLE gold.fact_deliveries (
    delivery_fact_key SERIAL PRIMARY KEY,
    shipment_id VARCHAR(50) NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    customer_key INT REFERENCES gold.dim_customer(customer_key),
    supplier_key INT REFERENCES gold.dim_supplier(supplier_key),
    warehouse_key INT REFERENCES gold.dim_warehouse(warehouse_key),
    delivery_date_key INT REFERENCES gold.dim_date(date_key),
    promised_days INT,
    actual_days INT,
    on_time_delivery_flag BOOLEAN,
    customer_satisfaction_score NUMERIC(3,2)
);
