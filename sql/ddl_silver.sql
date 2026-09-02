-- Silver Layer DDLs: Cleaned, Deduplicated, Standardized, and Validated Data

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
    temp_zone_type VARCHAR(50), -- Cold Storage, Ambient, Frozen
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
    status VARCHAR(50) NOT NULL, -- PENDING, SHIPPED, DELIVERED, CANCELLED
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
    status VARCHAR(50) NOT NULL, -- IN_TRANSIT, DELIVERED, DELAYED, CUSTOMS_HOLD
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
    is_temp_breach BOOLEAN DEFAULT FALSE, -- Cold chain violation alert
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
