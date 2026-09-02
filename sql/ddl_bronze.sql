-- Bronze Layer DDLs: Raw Ingested Data (Payloads, ingested_at, source_system, raw JSON/text)

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
    unit_cost VARCHAR(50), -- May contain raw currency strings like "$120.50" or "EUR 100"
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
    order_date VARCHAR(50), -- String timestamp from source system
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
    mode VARCHAR(50), -- Air, Sea, Road, Rail
    status VARCHAR(50), -- In Transit, Delivered, Delayed, Customs Hold
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
