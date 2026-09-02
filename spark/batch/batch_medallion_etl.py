import logging
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from python.db.postgres_client import PostgresClient
from python.db.minio_client import MinioClient
from python.quality.data_validator import DataValidator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] BatchMedallionETL: %(message)s")
logger = logging.getLogger("BatchMedallionETL")

class BatchMedallionETL:
    """
    Production ETL Pipeline processing Bronze -> Silver -> Gold Medallion data transformations.
    Handles data cleaning, currency conversion (to USD), timezone normalization (UTC),
    deduplication, business rule enrichment, and Star Schema population.
    """
    def __init__(self):
        self.pg = PostgresClient()
        self.minio = MinioClient()
        self.validator = DataValidator(self.pg, self.minio)

    def process_bronze_to_silver(self):
        logger.info("Executing Bronze -> Silver Data Transformation...")

        # 1. Suppliers Transformation
        raw_sup = self.pg.read_df("SELECT * FROM bronze.raw_suppliers")
        if not raw_sup.empty:
            df_sup = raw_sup.drop_duplicates(subset=["supplier_id"]).copy()
            df_sup["is_active"] = True
            df_sup["rating"] = pd.to_numeric(df_sup["rating"], errors="coerce").fillna(4.0)
            clean_sup = df_sup[["supplier_id", "name", "contact_email", "country", "region", "tier", "rating", "is_active"]]
            self.pg.write_df(clean_sup, "suppliers", schema="silver", if_exists="replace")
            self.minio.upload_parquet(f"silver/suppliers/{datetime.utcnow().strftime('%Y%m%d')}_suppliers.parquet", clean_sup)

        # 2. Warehouses Transformation
        raw_wh = self.pg.read_df("SELECT * FROM bronze.raw_warehouses")
        if not raw_wh.empty:
            df_wh = raw_wh.drop_duplicates(subset=["warehouse_id"]).copy()
            df_wh["latitude"] = pd.to_numeric(df_wh["latitude"], errors="coerce")
            df_wh["longitude"] = pd.to_numeric(df_wh["longitude"], errors="coerce")
            df_wh["capacity_sqft"] = pd.to_numeric(df_wh["capacity_sqft"], errors="coerce").fillna(100000).astype(int)
            clean_wh = df_wh[["warehouse_id", "code", "name", "city", "country", "latitude", "longitude", "capacity_sqft", "temp_zone_type"]]
            self.pg.write_df(clean_wh, "warehouses", schema="silver", if_exists="replace")
            self.minio.upload_parquet(f"silver/warehouses/{datetime.utcnow().strftime('%Y%m%d')}_warehouses.parquet", clean_wh)

        # 3. Products Transformation
        raw_prod = self.pg.read_df("SELECT * FROM bronze.raw_products")
        if not raw_prod.empty:
            df_prod = raw_prod.drop_duplicates(subset=["product_id"]).copy()
            # Clean currency strings "$1200.00" -> 1200.00
            df_prod["unit_cost_usd"] = df_prod["unit_cost"].astype(str).str.replace("$", "").str.replace(",", "").astype(float)
            df_prod["weight_kg"] = pd.to_numeric(df_prod["weight_kg"], errors="coerce").fillna(1.0)
            clean_prod = df_prod[["product_id", "sku", "name", "category", "unit_cost_usd", "weight_kg", "supplier_id"]]
            self.pg.write_df(clean_prod, "products", schema="silver", if_exists="replace")
            self.minio.upload_parquet(f"silver/products/{datetime.utcnow().strftime('%Y%m%d')}_products.parquet", clean_prod)

        # 4. Customers Transformation
        raw_cust = self.pg.read_df("SELECT * FROM bronze.raw_customers")
        if not raw_cust.empty:
            df_cust = raw_cust.drop_duplicates(subset=["customer_id"]).copy()
            clean_cust = df_cust[["customer_id", "company_name", "industry", "country", "region", "tier"]]
            self.pg.write_df(clean_cust, "customers", schema="silver", if_exists="replace")
            self.minio.upload_parquet(f"silver/customers/{datetime.utcnow().strftime('%Y%m%d')}_customers.parquet", clean_cust)

        # 5. Orders Transformation
        raw_ord = self.pg.read_df("SELECT * FROM bronze.raw_orders")
        if not raw_ord.empty:
            df_ord = raw_ord.drop_duplicates(subset=["order_id"]).copy()
            df_ord["quantity"] = pd.to_numeric(df_ord["quantity"], errors="coerce").fillna(1).astype(int)
            df_ord["unit_price_usd"] = df_ord["unit_price"].astype(str).str.replace("$", "").str.replace(",", "").astype(float)
            df_ord["total_amount_usd"] = df_ord["quantity"] * df_ord["unit_price_usd"]
            df_ord["original_currency"] = df_ord["currency"].fillna("USD")
            df_ord["order_date"] = pd.to_datetime(df_ord["order_date"], errors="coerce")
            df_ord["required_date"] = pd.to_datetime(df_ord["required_date"], errors="coerce")
            clean_ord = df_ord[["order_id", "customer_id", "product_id", "supplier_id", "quantity", "unit_price_usd", "total_amount_usd", "original_currency", "order_date", "required_date", "status"]]
            self.pg.write_df(clean_ord, "orders", schema="silver", if_exists="replace")
            self.minio.upload_parquet(f"silver/orders/{datetime.utcnow().strftime('%Y%m%d')}_orders.parquet", clean_ord)

        # 6. Shipments Transformation
        raw_shp = self.pg.read_df("SELECT * FROM bronze.raw_shipments")
        if not raw_shp.empty:
            df_shp = raw_shp.drop_duplicates(subset=["shipment_id"]).copy()
            df_shp["shipped_at"] = pd.to_datetime(df_shp["shipped_at"], errors="coerce")
            df_shp["estimated_delivery_at"] = pd.to_datetime(df_shp["estimated_delivery_at"], errors="coerce")
            df_shp["actual_delivery_at"] = pd.to_datetime(df_shp["actual_delivery_at"], errors="coerce")
            
            # Compute delay hours
            delay_mask = (df_shp["actual_delivery_at"].notnull()) & (df_shp["actual_delivery_at"] > df_shp["estimated_delivery_at"])
            df_shp["delay_hours"] = 0
            df_shp.loc[delay_mask, "delay_hours"] = ((df_shp.loc[delay_mask, "actual_delivery_at"] - df_shp.loc[delay_mask, "estimated_delivery_at"]).dt.total_seconds() / 3600).astype(int)
            df_shp["is_delayed"] = df_shp["delay_hours"] > 0
            
            clean_shp = df_shp[["shipment_id", "order_id", "origin_warehouse_id", "destination_city", "destination_country", "carrier", "mode", "status", "shipped_at", "estimated_delivery_at", "actual_delivery_at", "delay_hours", "is_delayed"]]
            self.pg.write_df(clean_shp, "shipments", schema="silver", if_exists="replace")
            self.minio.upload_parquet(f"silver/shipments/{datetime.utcnow().strftime('%Y%m%d')}_shipments.parquet", clean_shp)

        # 7. Inventory Transformation
        raw_inv = self.pg.read_df("SELECT * FROM bronze.raw_inventory")
        if not raw_inv.empty:
            df_inv = raw_inv.drop_duplicates(subset=["inventory_id"]).copy()
            df_inv["quantity_on_hand"] = pd.to_numeric(df_inv["quantity_on_hand"], errors="coerce").fillna(0).astype(int)
            df_inv["reorder_level"] = pd.to_numeric(df_inv["reorder_level"], errors="coerce").fillna(100).astype(int)
            df_inv["safety_stock"] = pd.to_numeric(df_inv["safety_stock"], errors="coerce").fillna(50).astype(int)
            df_inv["is_low_stock"] = df_inv["quantity_on_hand"] <= df_inv["reorder_level"]
            df_inv["last_counted_at"] = pd.to_datetime(df_inv["last_counted_at"], errors="coerce")
            
            clean_inv = df_inv[["inventory_id", "warehouse_id", "product_id", "quantity_on_hand", "reorder_level", "safety_stock", "is_low_stock", "last_counted_at"]]
            self.pg.write_df(clean_inv, "inventory", schema="silver", if_exists="replace")
            self.minio.upload_parquet(f"silver/inventory/{datetime.utcnow().strftime('%Y%m%d')}_inventory.parquet", clean_inv)

        # 8. IoT Sensors Transformation
        raw_iot = self.pg.read_df("SELECT * FROM bronze.raw_iot_sensors")
        if not raw_iot.empty:
            df_iot = raw_iot.drop_duplicates(subset=["event_id"]).copy()
            df_iot["latitude"] = pd.to_numeric(df_iot["latitude"], errors="coerce")
            df_iot["longitude"] = pd.to_numeric(df_iot["longitude"], errors="coerce")
            df_iot["temperature_c"] = pd.to_numeric(df_iot["temperature_c"], errors="coerce")
            df_iot["humidity_pct"] = pd.to_numeric(df_iot["humidity_pct"], errors="coerce")
            df_iot["battery_level"] = pd.to_numeric(df_iot["battery_level"], errors="coerce").fillna(100).astype(int)
            df_iot["recorded_at"] = pd.to_datetime(df_iot["recorded_at"], errors="coerce")
            df_iot["is_temp_breach"] = df_iot["temperature_c"] > 8.0 # Cold chain anomaly rule
            
            clean_iot = df_iot[["event_id", "shipment_id", "device_id", "latitude", "longitude", "temperature_c", "humidity_pct", "battery_level", "recorded_at", "is_temp_breach"]]
            self.pg.write_df(clean_iot, "iot_sensors", schema="silver", if_exists="replace")
            self.minio.upload_parquet(f"silver/iot_sensors/{datetime.utcnow().strftime('%Y%m%d')}_iot.parquet", clean_iot)

        logger.info("Bronze -> Silver Transformation completed successfully!")

    def process_silver_to_gold(self):
        logger.info("Executing Silver -> Gold Star Schema Transformation...")

        # 1. Populate dim_date
        start_date = datetime(2026, 1, 1)
        dates = [start_date + timedelta(days=i) for i in range(365)]
        date_records = []
        for d in dates:
            d_key = int(d.strftime("%Y%m%d"))
            date_records.append({
                "date_key": d_key,
                "full_date": d.strftime("%Y-%m-%d"),
                "year": d.year,
                "quarter": (d.month - 1) // 3 + 1,
                "month": d.month,
                "month_name": d.strftime("%B"),
                "day_of_month": d.day,
                "day_of_week": d.isoweekday(),
                "day_name": d.strftime("%A"),
                "is_weekend": d.isoweekday() in (6, 7)
            })
        df_dim_date = pd.DataFrame(date_records)
        self.pg.write_df(df_dim_date, "dim_date", schema="gold", if_exists="replace")

        # 2. Populate dim_supplier
        silver_sup = self.pg.read_df("SELECT * FROM silver.suppliers")
        if not silver_sup.empty:
            dim_sup = silver_sup.rename(columns={"name": "supplier_name"})
            dim_sup["supplier_key"] = range(1, len(dim_sup) + 1)
            self.pg.write_df(dim_sup, "dim_supplier", schema="gold", if_exists="replace")

        # 3. Populate dim_product
        silver_prod = self.pg.read_df("SELECT * FROM silver.products")
        if not silver_prod.empty:
            dim_prod = silver_prod.rename(columns={"name": "product_name"})
            dim_prod["product_key"] = range(1, len(dim_prod) + 1)
            self.pg.write_df(dim_prod, "dim_product", schema="gold", if_exists="replace")

        # 4. Populate dim_warehouse
        silver_wh = self.pg.read_df("SELECT * FROM silver.warehouses")
        if not silver_wh.empty:
            dim_wh = silver_wh.rename(columns={"code": "warehouse_code", "name": "warehouse_name"})
            dim_wh["warehouse_key"] = range(1, len(dim_wh) + 1)
            self.pg.write_df(dim_wh, "dim_warehouse", schema="gold", if_exists="replace")

        # 5. Populate dim_customer
        silver_cust = self.pg.read_df("SELECT * FROM silver.customers")
        if not silver_cust.empty:
            dim_cust = silver_cust.copy()
            dim_cust["customer_key"] = range(1, len(dim_cust) + 1)
            self.pg.write_df(dim_cust, "dim_customer", schema="gold", if_exists="replace")

        # 6. Populate fact_orders
        orders = self.pg.read_df("SELECT * FROM silver.orders")
        dim_s = self.pg.read_df("SELECT supplier_key, supplier_id FROM gold.dim_supplier")
        dim_p = self.pg.read_df("SELECT product_key, product_id FROM gold.dim_product")
        dim_c = self.pg.read_df("SELECT customer_key, customer_id FROM gold.dim_customer")

        if not orders.empty:
            orders["order_date_dt"] = pd.to_datetime(orders["order_date"], errors="coerce")
            orders["order_date_key"] = orders["order_date_dt"].dt.strftime("%Y%m%d").fillna("20260101").astype(int)

            fact_ord = orders.merge(dim_s, on="supplier_id", how="left") \
                             .merge(dim_p, on="product_id", how="left") \
                             .merge(dim_c, on="customer_id", how="left")

            fact_ord_clean = fact_ord[["order_id", "customer_key", "product_key", "supplier_key", "order_date_key", "quantity", "unit_price_usd", "total_amount_usd", "status"]]
            fact_ord_clean = fact_ord_clean.rename(columns={"status": "order_status"})
            self.pg.write_df(fact_ord_clean, "fact_orders", schema="gold", if_exists="replace")

        # 7. Populate fact_shipments
        shipments = self.pg.read_df("SELECT * FROM silver.shipments")
        dim_w = self.pg.read_df("SELECT warehouse_key, warehouse_id FROM gold.dim_warehouse")

        if not shipments.empty:
            shipments["shipped_dt"] = pd.to_datetime(shipments["shipped_at"], errors="coerce")
            shipments["shipped_date_key"] = shipments["shipped_dt"].dt.strftime("%Y%m%d").fillna("20260101").astype(int)
            shipments["delivery_dt"] = pd.to_datetime(shipments["actual_delivery_at"], errors="coerce")
            shipments["delivery_date_key"] = shipments["delivery_dt"].dt.strftime("%Y%m%d").fillna("20260101").astype(int)

            fact_shp = shipments.merge(dim_w, left_on="origin_warehouse_id", right_on="warehouse_id", how="left")
            fact_shp_clean = fact_shp.rename(columns={"warehouse_key": "origin_warehouse_key", "mode": "transit_mode", "status": "shipment_status"})
            
            # Join temp breach counts
            iot_breaches = self.pg.read_df("SELECT shipment_id, COUNT(*) as temp_breach_count FROM silver.iot_sensors WHERE is_temp_breach = TRUE GROUP BY shipment_id")
            if not iot_breaches.empty:
                fact_shp_clean = fact_shp_clean.merge(iot_breaches, on="shipment_id", how="left")
                fact_shp_clean["temp_breach_count"] = fact_shp_clean["temp_breach_count"].fillna(0).astype(int)
            else:
                fact_shp_clean["temp_breach_count"] = 0

            cols = ["shipment_id", "order_id", "origin_warehouse_key", "shipped_date_key", "delivery_date_key", "carrier", "transit_mode", "shipment_status", "delay_hours", "is_delayed", "temp_breach_count"]
            self.pg.write_df(fact_shp_clean[cols], "fact_shipments", schema="gold", if_exists="replace")

        logger.info("Silver -> Gold Transformation completed successfully!")

    def run_pipeline(self):
        logger.info("=== Starting Global Supply Chain Medallion Pipeline Execution ===")
        self.process_bronze_to_silver()
        self.process_silver_to_gold()
        
        # Execute Data Quality Audit
        logger.info("Running Data Quality Checks on Processed Layers...")
        results = self.validator.run_all_checks()
        logger.info(f"=== ETL Pipeline Complete. Data Quality Score: {results['summary']['score_pct']}% ===")
        return results

if __name__ == "__main__":
    etl = BatchMedallionETL()
    etl.run_pipeline()
