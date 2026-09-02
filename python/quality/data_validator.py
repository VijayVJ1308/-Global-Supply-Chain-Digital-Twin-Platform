import logging
import json
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from python.db.postgres_client import PostgresClient
from python.db.minio_client import MinioClient

logger = logging.getLogger("DataValidator")

class DataValidator:
    """
    Automated Data Quality & Validation Engine for Supply Chain Medallion Pipeline.
    Performs null checks, primary key uniqueness, referential integrity, range bounds, and business rules.
    """
    def __init__(self, pg_client: PostgresClient = None, minio_client: MinioClient = None):
        self.pg = pg_client or PostgresClient()
        self.minio = minio_client or MinioClient()

    def run_all_checks(self) -> Dict[str, Any]:
        """Runs validation across Bronze, Silver, and Gold layers."""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {"total_tests": 0, "passed": 0, "failed": 0, "score_pct": 100.0},
            "layer_results": {}
        }
        
        # Test rules definition
        tests = [
            # Bronze checks
            {"layer": "bronze", "name": "bronze_suppliers_not_empty", "query": "SELECT COUNT(*) as cnt FROM bronze.raw_suppliers", "condition": lambda df: df["cnt"].iloc[0] > 0, "desc": "Bronze suppliers raw table must contain rows"},
            {"layer": "bronze", "name": "bronze_orders_not_empty", "query": "SELECT COUNT(*) as cnt FROM bronze.raw_orders", "condition": lambda df: df["cnt"].iloc[0] > 0, "desc": "Bronze orders raw table must contain rows"},
            
            # Silver checks
            {"layer": "silver", "name": "silver_suppliers_no_null_id", "query": "SELECT COUNT(*) as cnt FROM silver.suppliers WHERE supplier_id IS NULL", "condition": lambda df: df["cnt"].iloc[0] == 0, "desc": "Silver suppliers supplier_id must not be null"},
            {"layer": "silver", "name": "silver_products_unique_sku", "query": "SELECT COUNT(sku) - COUNT(DISTINCT sku) as dup_cnt FROM silver.products", "condition": lambda df: df["dup_cnt"].iloc[0] == 0, "desc": "Silver product SKUs must be unique"},
            {"layer": "silver", "name": "silver_orders_positive_quantity", "query": "SELECT COUNT(*) as cnt FROM silver.orders WHERE quantity <= 0", "condition": lambda df: df["cnt"].iloc[0] == 0, "desc": "Silver order quantity must be greater than zero"},
            {"layer": "silver", "name": "silver_orders_referential_customer", "query": "SELECT COUNT(*) as cnt FROM silver.orders o LEFT JOIN silver.customers c ON o.customer_id = c.customer_id WHERE c.customer_id IS NULL", "condition": lambda df: df["cnt"].iloc[0] == 0, "desc": "All Silver orders must link to a valid customer"},
            {"layer": "silver", "name": "silver_shipments_referential_order", "query": "SELECT COUNT(*) as cnt FROM silver.shipments s LEFT JOIN silver.orders o ON s.order_id = o.order_id WHERE o.order_id IS NULL", "condition": lambda df: df["cnt"].iloc[0] == 0, "desc": "All Silver shipments must link to a valid order"},
            {"layer": "silver", "name": "silver_inventory_non_negative", "query": "SELECT COUNT(*) as cnt FROM silver.inventory WHERE quantity_on_hand < 0", "condition": lambda df: df["cnt"].iloc[0] == 0, "desc": "Silver inventory quantity on hand must be non-negative"},

            # Gold checks
            {"layer": "gold", "name": "gold_fact_orders_valid_keys", "query": "SELECT COUNT(*) as cnt FROM gold.fact_orders WHERE customer_key IS NULL OR product_key IS NULL OR supplier_key IS NULL", "condition": lambda df: df["cnt"].iloc[0] == 0, "desc": "Gold fact_orders dimension keys must not be null"},
            {"layer": "gold", "name": "gold_dim_date_populated", "query": "SELECT COUNT(*) as cnt FROM gold.dim_date", "condition": lambda df: df["cnt"].iloc[0] >= 365, "desc": "Gold dim_date dimension must contain at least 1 year of dates"},
        ]

        passed = 0
        failed = 0
        test_details = []

        for test in tests:
            try:
                df = self.pg.read_df(test["query"])
                is_passed = bool(test["condition"](df))
                if is_passed:
                    passed += 1
                else:
                    failed += 1

                test_details.append({
                    "layer": test["layer"],
                    "test_name": test["name"],
                    "description": test["desc"],
                    "status": "PASSED" if is_passed else "FAILED",
                    "executed_at": datetime.utcnow().isoformat()
                })
            except Exception as e:
                failed += 1
                test_details.append({
                    "layer": test["layer"],
                    "test_name": test["name"],
                    "description": test["desc"],
                    "status": "ERROR",
                    "error": str(e),
                    "executed_at": datetime.utcnow().isoformat()
                })

        total = passed + failed
        score = round((passed / total * 100.0), 2) if total > 0 else 0.0

        results["summary"] = {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "score_pct": score
        }
        results["test_details"] = test_details

        # Upload quality audit payload to MinIO object store
        audit_path = f"quality_reports/data_quality_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        self.minio.upload_json(audit_path, results)

        logger.info(f"Data Quality Validation Finished. Score: {score}% ({passed}/{total} Passed)")
        return results

if __name__ == "__main__":
    validator = DataValidator()
    report = validator.run_all_checks()
    print(json.dumps(report["summary"], indent=2))
