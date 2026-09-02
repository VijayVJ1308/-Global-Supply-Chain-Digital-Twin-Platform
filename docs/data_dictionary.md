# Global Supply Chain Digital Twin - Data Dictionary

## 1. Bronze Layer Schema (`bronze`)
Stores un-cleansed raw ingested payloads directly from ERP, WMS, CRM, and IoT sources.

| Table Name | Column Name | Type | Description |
| :--- | :--- | :--- | :--- |
| `raw_suppliers` | `supplier_id` | VARCHAR | Source primary key |
| | `name` | VARCHAR | Supplier organization name |
| | `country` | VARCHAR | Country of incorporation |
| | `raw_payload` | JSONB | Raw JSON string from API |
| `raw_products` | `product_id` | VARCHAR | SKU item code |
| | `unit_cost` | VARCHAR | Unformatted cost string (e.g. "$1,250.00") |
| `raw_iot_sensors` | `event_id` | VARCHAR | Event telemetry GUID |
| | `temperature_c` | VARCHAR | Ambient container temperature string |

---

## 2. Silver Layer Schema (`silver`)
Cleaned, deduplicated, UTC-normalized, and currency-converted data.

| Table Name | Column Name | Type | Description |
| :--- | :--- | :--- | :--- |
| `suppliers` | `supplier_id` | VARCHAR (PK) | Unique supplier identifier |
| | `rating` | NUMERIC(3,2) | Quality score (1.00 - 5.00) |
| `products` | `unit_cost_usd` | NUMERIC(12,2)| Standardized unit cost in USD |
| `shipments` | `is_delayed` | BOOLEAN | Calculated delay flag (`actual > estimated`) |
| | `delay_hours` | INTEGER | Total transit lag in hours |
| `iot_sensors` | `is_temp_breach` | BOOLEAN | Cold chain breach flag (`temperature_c > 8.0°C`) |

---

## 3. Gold Layer Star Schema (`gold`)
Curated dimensional model for OLAP analytical queries and executive dashboards.

| Table Name | Type | Key Columns | Business Metrics |
| :--- | :--- | :--- | :--- |
| `fact_orders` | Fact | `order_id`, `customer_key`, `supplier_key` | `quantity`, `unit_price_usd`, `total_amount_usd` |
| `fact_shipments` | Fact | `shipment_id`, `origin_warehouse_key` | `delay_hours`, `is_delayed`, `temp_breach_count` |
| `fact_inventory` | Fact | `inventory_id`, `warehouse_key`, `product_key` | `quantity_on_hand`, `is_low_stock` |
| `fact_deliveries` | Fact | `shipment_id`, `customer_key` | `promised_days`, `actual_days`, `on_time_delivery_flag` |
| `dim_supplier` | Dimension | `supplier_key` (PK), `supplier_id` | Supplier tier, country, rating |
| `dim_product` | Dimension | `product_key` (PK), `sku` | Category, weight_kg, unit_cost_usd |
| `dim_warehouse` | Dimension | `warehouse_key` (PK), `warehouse_code` | GPS lat/lon, capacity_sqft, temp_zone_type |
| `dim_customer` | Dimension | `customer_key` (PK), `customer_id` | Company name, industry, region |
| `dim_date` | Dimension | `date_key` (PK), `full_date` | Year, quarter, month, day_of_week |
