"""
Data Quality Rules & Constraint Definitions for Global Supply Chain Digital Twin Platform.
"""

from typing import Dict, List, Any

BRONZE_RULES = [
    {"rule_id": "BR-01", "entity": "raw_suppliers", "type": "not_null", "columns": ["supplier_id", "name"]},
    {"rule_id": "BR-02", "entity": "raw_warehouses", "type": "not_null", "columns": ["warehouse_id", "code"]},
    {"rule_id": "BR-03", "entity": "raw_orders", "type": "not_null", "columns": ["order_id", "customer_id", "product_id"]},
    {"rule_id": "BR-04", "entity": "raw_iot_sensors", "type": "range", "column": "temperature_c", "min": -50, "max": 100},
]

SILVER_RULES = [
    {"rule_id": "SR-01", "entity": "suppliers", "type": "unique", "column": "supplier_id"},
    {"rule_id": "SR-02", "entity": "products", "type": "unique", "column": "sku"},
    {"rule_id": "SR-03", "entity": "orders", "type": "positive", "column": "quantity"},
    {"rule_id": "SR-04", "entity": "orders", "type": "foreign_key", "column": "customer_id", "ref_table": "customers", "ref_column": "customer_id"},
    {"rule_id": "SR-05", "entity": "shipments", "type": "foreign_key", "column": "order_id", "ref_table": "orders", "ref_column": "order_id"},
    {"rule_id": "SR-06", "entity": "inventory", "type": "non_negative", "column": "quantity_on_hand"},
]

GOLD_RULES = [
    {"rule_id": "GR-01", "entity": "fact_orders", "type": "not_null", "columns": ["order_key", "customer_key", "product_key", "supplier_key", "date_key"]},
    {"rule_id": "GR-02", "entity": "fact_shipments", "type": "not_null", "columns": ["shipment_key", "order_key", "warehouse_key", "date_key"]},
    {"rule_id": "GR-03", "entity": "dim_date", "type": "min_count", "min_rows": 365},
]
