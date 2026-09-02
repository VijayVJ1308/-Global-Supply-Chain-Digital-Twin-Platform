import os
import json
import sys
import logging
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import pandas as pd

from python.config import WEB_PORT
from python.db.postgres_client import PostgresClient
from python.data_generator.generate_mock_data import main as run_generator
from spark.batch.batch_medallion_etl import BatchMedallionETL
from python.quality.data_validator import DataValidator
from python.quality.quality_report_generator import generate_html_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] WebDashboard: %(message)s")
logger = logging.getLogger("WebDashboard")

app = FastAPI(title="Global Supply Chain Digital Twin Platform")

# Serve static files & templates
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "dashboard" / "static")), name="static")

pg = PostgresClient()
validator = DataValidator(pg)

@app.get("/", response_class=HTMLResponse)
def index():
    template_path = BASE_DIR / "dashboard" / "templates" / "index.html"
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/kpis")
def get_kpis():
    try:
        ord_df = pg.read_df("SELECT COUNT(*) as total_orders, SUM(total_amount_usd) as total_revenue FROM silver.orders")
        shp_df = pg.read_df("SELECT COUNT(*) as total_shipments, SUM(CASE WHEN status='IN_TRANSIT' THEN 1 ELSE 0 END) as active_transit, SUM(CASE WHEN is_delayed=TRUE THEN 1 ELSE 0 END) as delayed FROM silver.shipments")
        inv_df = pg.read_df("SELECT COUNT(*) as total_skus, SUM(CASE WHEN is_low_stock=TRUE THEN 1 ELSE 0 END) as low_stock_count FROM silver.inventory")
        iot_df = pg.read_df("SELECT COUNT(*) as total_readings, SUM(CASE WHEN is_temp_breach=TRUE THEN 1 ELSE 0 END) as temp_breaches FROM silver.iot_sensors")
        sup_df = pg.read_df("SELECT AVG(rating) as avg_supplier_rating FROM silver.suppliers")

        kpis = {
            "total_orders": int(ord_df["total_orders"].fillna(0).iloc[0]) if not ord_df.empty else 0,
            "total_revenue_usd": float(ord_df["total_revenue"].fillna(0).iloc[0]) if not ord_df.empty else 0.0,
            "active_transit_shipments": int(shp_df["active_transit"].fillna(0).iloc[0]) if not shp_df.empty else 0,
            "delayed_shipments": int(shp_df["delayed"].fillna(0).iloc[0]) if not shp_df.empty else 0,
            "low_stock_items": int(inv_df["low_stock_count"].fillna(0).iloc[0]) if not inv_df.empty else 0,
            "temp_breaches": int(iot_df["temp_breaches"].fillna(0).iloc[0]) if not iot_df.empty else 0,
            "avg_supplier_rating": round(float(sup_df["avg_supplier_rating"].fillna(4.5).iloc[0]), 2) if not sup_df.empty else 4.5
        }
        return kpis
    except Exception as e:
        logger.error(f"Error fetching KPIs: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/nodes")
def get_supply_chain_nodes():
    """Returns warehouses, active shipment routes, and IoT device pins for the interactive map."""
    try:
        warehouses = pg.read_df("SELECT * FROM silver.warehouses").to_dict(orient="records")
        iot_latest = pg.read_df("SELECT * FROM silver.iot_sensors ORDER BY recorded_at DESC LIMIT 100").to_dict(orient="records")
        shipments = pg.read_df("""
            SELECT s.shipment_id, s.carrier, s.mode, s.status, s.destination_city, s.destination_country,
                   w.name as origin_wh, w.latitude as origin_lat, w.longitude as origin_lon
            FROM silver.shipments s
            LEFT JOIN silver.warehouses w ON s.origin_warehouse_id = w.warehouse_id
            WHERE s.status IN ('IN_TRANSIT', 'DELAYED')
            LIMIT 40
        """).to_dict(orient="records")

        return {
            "warehouses": warehouses,
            "active_shipments": shipments,
            "iot_telemetry": iot_latest
        }
    except Exception as e:
        logger.error(f"Error fetching nodes: {e}")
        return {"warehouses": [], "active_shipments": [], "iot_telemetry": []}

@app.get("/api/inventory")
def get_inventory():
    try:
        df = pg.read_df("""
            SELECT i.inventory_id, w.name as warehouse_name, p.name as product_name, p.category,
                   i.quantity_on_hand, i.reorder_level, i.is_low_stock
            FROM silver.inventory i
            JOIN silver.warehouses w ON i.warehouse_id = w.warehouse_id
            JOIN silver.products p ON i.product_id = p.product_id
            ORDER BY i.is_low_stock DESC, i.quantity_on_hand ASC
            LIMIT 50
        """)
        return df.to_dict(orient="records")
    except Exception as e:
        return []

@app.get("/api/quality")
def get_quality_report():
    try:
        results = validator.run_all_checks()
        return results
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/quality/download", response_class=HTMLResponse)
def download_quality_report():
    results = validator.run_all_checks()
    html = generate_html_report(results)
    return HTMLResponse(content=html)

@app.post("/api/actions/run_etl")
def trigger_etl():
    """Triggers batch medallion ETL pipeline."""
    try:
        run_generator()
        etl = BatchMedallionETL()
        res = etl.run_pipeline()
        return {"status": "SUCCESS", "message": "Batch Medallion ETL executed successfully!", "quality_score": res["summary"]["score_pct"]}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "ERROR", "message": str(e)})

if __name__ == "__main__":
    # Initialize DB baseline if needed
    try:
        df_check = pg.read_df("SELECT COUNT(*) FROM silver.orders")
        if df_check.empty or df_check.iloc[0, 0] == 0:
            logger.info("Initializing synthetic dataset for first run...")
            run_generator()
            etl = BatchMedallionETL()
            etl.run_pipeline()
    except Exception:
        pass

    uvicorn.run(app, host="0.0.0.0", port=WEB_PORT)
