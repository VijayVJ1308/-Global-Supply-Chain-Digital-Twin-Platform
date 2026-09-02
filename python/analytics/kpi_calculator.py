"""
Operational KPI Calculator for Global Supply Chain Digital Twin Platform.
Computes core supply chain metrics:
- Warehouse Capacity Utilization
- Supplier On-Time In-Full (OTIF) Delivery & Quality Ratings
- Shipment Lead Time & Delay Percentages
- Inventory Stockout Risk & Reorder Urgency
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from python.db.postgres_client import PostgresClient
from python.utils.logger import get_logger

logger = get_logger("KPICalculator")

class KPICalculator:
    def __init__(self, pg_client: PostgresClient = None):
        self.pg = pg_client or PostgresClient()

    def get_summary_kpis(self) -> Dict[str, Any]:
        """Calculates executive dashboard metrics."""
        try:
            # 1. Total Orders & Revenue
            df_orders = self.pg.read_df("SELECT * FROM silver.orders")
            if df_orders.empty:
                df_orders = self.pg.read_df("SELECT * FROM bronze_raw_orders")

            total_orders = len(df_orders)
            delivered_orders = len(df_orders[df_orders["status"] == "DELIVERED"]) if "status" in df_orders.columns else 0
            fulfillment_rate = round((delivered_orders / total_orders * 100.0), 1) if total_orders > 0 else 0.0

            # 2. Shipment Delays
            df_shipments = self.pg.read_df("SELECT * FROM silver.shipments")
            if df_shipments.empty:
                df_shipments = self.pg.read_df("SELECT * FROM bronze_raw_shipments")

            total_shipments = len(df_shipments)
            delayed_shipments = len(df_shipments[df_shipments["status"] == "DELAYED"]) if "status" in df_shipments.columns else 0
            on_time_shipments = len(df_shipments[df_shipments["status"] == "DELIVERED"]) if "status" in df_shipments.columns else 0
            delay_pct = round((delayed_shipments / total_shipments * 100.0), 1) if total_shipments > 0 else 0.0

            # 3. Warehouse Utilization
            df_inventory = self.pg.read_df("SELECT * FROM silver.inventory")
            if df_inventory.empty:
                df_inventory = self.pg.read_df("SELECT * FROM bronze_raw_inventory")

            stockout_risk_items = 0
            if not df_inventory.empty and "quantity_on_hand" in df_inventory.columns and "safety_stock" in df_inventory.columns:
                df_inventory["qty"] = pd.to_numeric(df_inventory["quantity_on_hand"], errors="coerce").fillna(0)
                df_inventory["safety"] = pd.to_numeric(df_inventory["safety_stock"], errors="coerce").fillna(0)
                stockout_risk_items = len(df_inventory[df_inventory["qty"] <= df_inventory["safety"]])

            # 4. Supplier Performance
            df_suppliers = self.pg.read_df("SELECT * FROM silver.suppliers")
            if df_suppliers.empty:
                df_suppliers = self.pg.read_df("SELECT * FROM bronze_raw_suppliers")

            avg_supplier_rating = 0.0
            if not df_suppliers.empty and "rating" in df_suppliers.columns:
                avg_supplier_rating = round(float(pd.to_numeric(df_suppliers["rating"], errors="coerce").mean()), 2)

            return {
                "total_orders": total_orders,
                "fulfillment_rate_pct": fulfillment_rate,
                "total_shipments": total_shipments,
                "delayed_shipments": delayed_shipments,
                "on_time_shipments": on_time_shipments,
                "delay_pct": delay_pct,
                "stockout_risk_items": stockout_risk_items,
                "active_suppliers": len(df_suppliers),
                "avg_supplier_rating": avg_supplier_rating
            }
        except Exception as e:
            logger.error(f"Error calculating KPIs: {e}")
            return {
                "total_orders": 0, "fulfillment_rate_pct": 0.0, "total_shipments": 0,
                "delayed_shipments": 0, "on_time_shipments": 0, "delay_pct": 0.0,
                "stockout_risk_items": 0, "active_suppliers": 0, "avg_supplier_rating": 0.0
            }

if __name__ == "__main__":
    calc = KPICalculator()
    print(calc.get_summary_kpis())
