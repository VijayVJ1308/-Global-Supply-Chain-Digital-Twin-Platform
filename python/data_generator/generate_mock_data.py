import json
import random
import uuid
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from python.db.postgres_client import PostgresClient
from python.db.minio_client import MinioClient
from python.config import BASE_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("DataGenerator")

WAREHOUSE_NODES = [
    {"id": "WH-US-001", "code": "LAX-HUB", "name": "Los Angeles Logistics Hub", "city": "Los Angeles", "country": "USA", "lat": 34.0522, "lon": -118.2437, "capacity": 550000, "temp_zone": "Cold Storage"},
    {"id": "WH-US-002", "code": "ORD-HUB", "name": "Chicago Central Distribution", "city": "Chicago", "country": "USA", "lat": 41.8781, "lon": -87.6298, "capacity": 450000, "temp_zone": "Ambient"},
    {"id": "WH-EU-001", "code": "HAM-HUB", "name": "Hamburg Port Terminal", "city": "Hamburg", "country": "Germany", "lat": 53.5511, "lon": 9.9937, "capacity": 600000, "temp_zone": "Cold Storage"},
    {"id": "WH-EU-002", "code": "ROT-HUB", "name": "Rotterdam Gateway Terminal", "city": "Rotterdam", "country": "Netherlands", "lat": 51.9244, "lon": 4.4777, "capacity": 700000, "temp_zone": "Frozen"},
    {"id": "WH-AP-001", "code": "TYO-HUB", "name": "Tokyo Kanto Logistics Center", "city": "Tokyo", "country": "Japan", "lat": 35.6762, "lon": 139.6503, "capacity": 500000, "temp_zone": "Ambient"},
    {"id": "WH-AP-002", "code": "SHA-HUB", "name": "Shanghai Pudong Fulfillment Center", "city": "Shanghai", "country": "China", "lat": 31.2304, "lon": 121.4737, "capacity": 850000, "temp_zone": "Cold Storage"},
    {"id": "WH-AP-003", "code": "SIN-HUB", "name": "Singapore Tuas Mega Hub", "city": "Singapore", "country": "Singapore", "lat": 1.3521, "lon": 103.8198, "capacity": 650000, "temp_zone": "Ambient"},
    {"id": "WH-ME-001", "code": "DXB-HUB", "name": "Dubai Logistics City Hub", "city": "Dubai", "country": "UAE", "lat": 25.2048, "lon": 55.2708, "capacity": 400000, "temp_zone": "Cold Storage"},
    {"id": "WH-SA-001", "code": "SAN-HUB", "name": "Santos Port Cargo Node", "city": "Santos", "country": "Brazil", "lat": -23.9608, "lon": -46.3336, "capacity": 380000, "temp_zone": "Ambient"},
    {"id": "WH-AU-001", "code": "SYD-HUB", "name": "Sydney Western Fulfillment", "city": "Sydney", "country": "Australia", "lat": -33.8688, "lon": 151.2093, "capacity": 300000, "temp_zone": "Ambient"},
]

SUPPLIER_NAMES = [
    ("Nvidia Precision Tech", "Taiwan", "Asia", "Tier 1", 4.9),
    ("Bosch Global Systems", "Germany", "Europe", "Tier 1", 4.8),
    ("Samsung Components", "South Korea", "Asia", "Tier 1", 4.85),
    ("TSMC Microelectronics", "Taiwan", "Asia", "Tier 1", 4.95),
    ("Foxconn Logistics", "China", "Asia", "Tier 1", 4.6),
    ("Siemens Automation", "Germany", "Europe", "Tier 1", 4.75),
    ("Pfizer Cold Pharma", "USA", "North America", "Tier 1", 4.9),
    ("Moderna BioSupply", "USA", "North America", "Tier 1", 4.88),
    ("BASF Chemical Works", "Germany", "Europe", "Tier 2", 4.5),
    ("SK Hynix Memory", "South Korea", "Asia", "Tier 1", 4.7),
    ("Flex Semiconductor", "Singapore", "Asia", "Tier 2", 4.4),
    ("Murata Manufacturing", "Japan", "Asia", "Tier 2", 4.65),
    ("Valero Energy Energy", "USA", "North America", "Tier 2", 4.3),
    ("Vale Mining SA", "Brazil", "South America", "Tier 2", 4.2),
    ("Tata Industrial Freight", "India", "Asia", "Tier 2", 4.45),
]

PRODUCT_CATALOG = [
    ("ELEC-1001", "AI Accelerator GPU Module", "Electronics", 1250.00, 1.2),
    ("ELEC-1002", "5G Telemetry Transceiver", "Electronics", 350.00, 0.4),
    ("ELEC-1003", "Microcontroller Board v4", "Electronics", 45.00, 0.1),
    ("AUTO-2001", "EV Battery Pack 75kWh", "Automotive", 4800.00, 320.0),
    ("AUTO-2002", "Electric Drive Motor 150kW", "Automotive", 2100.00, 85.0),
    ("PHAR-3001", "mRNA Vaccine Vials (Box 100)", "Pharmaceuticals", 1800.00, 5.0),
    ("PHAR-3002", "Biologics Injectable Reagents", "Pharmaceuticals", 3200.00, 2.5),
    ("IND-4001", "Hydraulic Servo Valve", "Industrial", 890.00, 12.0),
    ("IND-4002", "High-Torque Robot Arm Joint", "Industrial", 3400.00, 45.0),
    ("RET-5001", "Smart Logistics Tracker Device", "IoT Hardware", 120.00, 0.3),
]

CARRIERS = ["Maersk Ocean", "FedEx Express Air", "DHL Supply Chain", "Kuehne + Nagel", "DB Schenker", "Cosco Shipping", "UPS Supply Chain"]
TRANSIT_MODES = ["Air Freight", "Sea Freight", "Road Truckload", "Rail Express"]
SHIPMENT_STATUSES = ["IN_TRANSIT", "DELIVERED", "DELAYED", "CUSTOMS_HOLD"]

def generate_dataset(num_orders: int = 500, num_iot_events: int = 2000):
    logger.info("Generating realistic Global Supply Chain synthetic dataset...")
    
    # 1. Suppliers
    suppliers = []
    for i, (name, country, region, tier, rating) in enumerate(SUPPLIER_NAMES, 1):
        sup_id = f"SUP-{i:03d}"
        suppliers.append({
            "supplier_id": sup_id,
            "name": name,
            "contact_email": f"contact@{name.lower().replace(' ', '')}.com",
            "country": country,
            "region": region,
            "tier": tier,
            "rating": rating,
            "raw_payload": json.dumps({"supplier_id": sup_id, "name": name, "rating": rating})
        })
    df_suppliers = pd.DataFrame(suppliers)

    # 2. Warehouses
    warehouses = []
    for wh in WAREHOUSE_NODES:
        warehouses.append({
            "warehouse_id": wh["id"],
            "code": wh["code"],
            "name": wh["name"],
            "city": wh["city"],
            "country": wh["country"],
            "latitude": wh["lat"],
            "longitude": wh["lon"],
            "capacity_sqft": wh["capacity"],
            "temp_zone_type": wh["temp_zone"],
            "raw_payload": json.dumps(wh)
        })
    df_warehouses = pd.DataFrame(warehouses)

    # 3. Products
    products = []
    for i, (sku, name, cat, cost, weight) in enumerate(PRODUCT_CATALOG, 1):
        prod_id = f"PROD-{i:03d}"
        sup_id = random.choice(suppliers)["supplier_id"]
        products.append({
            "product_id": prod_id,
            "sku": sku,
            "name": name,
            "category": cat,
            "unit_cost": f"${cost:.2f}",
            "currency": "USD",
            "weight_kg": weight,
            "supplier_id": sup_id,
            "raw_payload": json.dumps({"product_id": prod_id, "sku": sku, "cost": cost})
        })
    df_products = pd.DataFrame(products)

    # 4. Customers
    customers = []
    customer_companies = [
        ("Apple Inc.", "Technology", "USA", "North America", "Enterprise"),
        ("Tesla Motors", "Automotive", "USA", "North America", "Enterprise"),
        ("Siemens Healthineers", "Healthcare", "Germany", "Europe", "Enterprise"),
        ("Toyota Motor Corp", "Automotive", "Japan", "Asia", "Enterprise"),
        ("Novartis Pharma", "Pharmaceuticals", "Switzerland", "Europe", "Enterprise"),
        ("General Electric", "Industrial", "USA", "North America", "Mid-Market"),
        ("Sony Electronics", "Technology", "Japan", "Asia", "Enterprise"),
        ("AstraZeneca", "Healthcare", "UK", "Europe", "Enterprise"),
        ("Foxconn Enterprise", "Manufacturing", "Taiwan", "Asia", "Enterprise"),
        ("BHP Group", "Resources", "Australia", "Oceania", "Mid-Market"),
    ]
    for i, (comp, ind, country, region, tier) in enumerate(customer_companies, 1):
        cust_id = f"CUST-{i:03d}"
        customers.append({
            "customer_id": cust_id,
            "company_name": comp,
            "industry": ind,
            "country": country,
            "region": region,
            "tier": tier,
            "raw_payload": json.dumps({"customer_id": cust_id, "company": comp})
        })
    df_customers = pd.DataFrame(customers)

    # 5. Orders & Shipments & Inventory
    orders = []
    shipments = []
    inventory_items = []

    now = datetime.utcnow()

    # Inventory baseline per product per warehouse
    inv_id_counter = 1
    for wh in warehouses:
        for prod in products:
            q_on_hand = random.randint(50, 1500)
            reorder = random.randint(100, 300)
            safety = random.randint(50, 150)
            inventory_items.append({
                "inventory_id": f"INV-{inv_id_counter:05d}",
                "warehouse_id": wh["warehouse_id"],
                "product_id": prod["product_id"],
                "quantity_on_hand": str(q_on_hand),
                "reorder_level": str(reorder),
                "safety_stock": str(safety),
                "last_counted_at": (now - timedelta(days=random.randint(1, 10))).isoformat(),
                "raw_payload": json.dumps({"inventory_id": f"INV-{inv_id_counter:05d}", "qty": q_on_hand})
            })
            inv_id_counter += 1

    for i in range(1, num_orders + 1):
        order_id = f"ORD-{i:06d}"
        cust = random.choice(customers)
        prod = random.choice(products)
        qty = random.randint(5, 200)
        unit_price = float(prod["unit_cost"].replace("$", ""))
        order_dt = now - timedelta(days=random.randint(1, 45), hours=random.randint(0, 23))
        req_dt = order_dt + timedelta(days=random.randint(5, 15))
        
        status_weights = ["DELIVERED"] * 60 + ["IN_TRANSIT"] * 25 + ["DELAYED"] * 10 + ["CUSTOMS_HOLD"] * 5
        status = random.choice(status_weights)

        orders.append({
            "order_id": order_id,
            "customer_id": cust["customer_id"],
            "product_id": prod["product_id"],
            "supplier_id": prod["supplier_id"],
            "quantity": str(qty),
            "unit_price": f"${unit_price:.2f}",
            "currency": "USD",
            "order_date": order_dt.isoformat(),
            "required_date": req_dt.isoformat(),
            "status": status,
            "raw_payload": json.dumps({"order_id": order_id, "amount": qty * unit_price})
        })

        # Create corresponding shipment
        shipment_id = f"SHP-{i:06d}"
        wh = random.choice(warehouses)
        carrier = random.choice(CARRIERS)
        mode = random.choice(TRANSIT_MODES)
        shipped_dt = order_dt + timedelta(days=random.randint(1, 3))
        est_deliv_dt = shipped_dt + timedelta(days=random.randint(3, 10))

        if status == "DELIVERED":
            delay = random.choice([0, 0, 0, 0, 12, 24, 48])
            act_deliv_dt = est_deliv_dt + timedelta(hours=delay)
        else:
            act_deliv_dt = None

        shipments.append({
            "shipment_id": shipment_id,
            "order_id": order_id,
            "origin_warehouse_id": wh["warehouse_id"],
            "destination_city": cust["country"],
            "destination_country": cust["country"],
            "carrier": carrier,
            "mode": mode,
            "status": status,
            "shipped_at": shipped_dt.isoformat(),
            "estimated_delivery_at": est_deliv_dt.isoformat(),
            "actual_delivery_at": act_deliv_dt.isoformat() if act_deliv_dt else None,
            "raw_payload": json.dumps({"shipment_id": shipment_id, "carrier": carrier, "status": status})
        })

    df_orders = pd.DataFrame(orders)
    df_shipments = pd.DataFrame(shipments)
    df_inventory = pd.DataFrame(inventory_items)

    # 6. IoT Telemetry Events
    iot_events = []
    active_shipments = df_shipments[df_shipments["status"].isin(["IN_TRANSIT", "DELAYED", "DELIVERED"])]["shipment_id"].tolist()
    
    for i in range(1, num_iot_events + 1):
        event_id = f"IOT-{i:07d}"
        sh_id = random.choice(active_shipments)
        device_id = f"DEV-{random.randint(100, 999)}"
        
        # Base location near randomly picked warehouse lat/lon
        wh = random.choice(warehouses)
        lat = wh["latitude"] + random.uniform(-2.5, 2.5)
        lon = wh["longitude"] + random.uniform(-2.5, 2.5)
        
        # Cold chain temperature simulation: mostly 2C - 6C, occasionally anomaly > 8C or frozen < -15C
        if random.random() < 0.08:
            temp = random.uniform(8.5, 18.0) # Breach anomaly!
        else:
            temp = random.uniform(2.0, 6.5)

        humidity = random.uniform(40.0, 75.0)
        battery = random.randint(15, 100)
        rec_dt = now - timedelta(hours=random.randint(0, 120), minutes=random.randint(0, 59))

        iot_events.append({
            "event_id": event_id,
            "shipment_id": sh_id,
            "device_id": device_id,
            "latitude": f"{lat:.6f}",
            "longitude": f"{lon:.6f}",
            "temperature_c": f"{temp:.2f}",
            "humidity_pct": f"{humidity:.2f}",
            "battery_level": str(battery),
            "recorded_at": rec_dt.isoformat(),
            "raw_payload": json.dumps({"event_id": event_id, "temp": temp, "lat": lat, "lon": lon})
        })

    df_iot = pd.DataFrame(iot_events)

    return {
        "suppliers": df_suppliers,
        "warehouses": df_warehouses,
        "products": df_products,
        "customers": df_customers,
        "orders": df_orders,
        "shipments": df_shipments,
        "inventory": df_inventory,
        "iot_sensors": df_iot
    }

def main():
    pg = PostgresClient()
    minio = MinioClient()

    # 1. Initialize DB DDLs
    logger.info("Initializing Postgres DB schemas...")
    for script_file in ["init_db.sql", "ddl_bronze.sql", "ddl_silver.sql", "ddl_gold_star_schema.sql"]:
        with open(BASE_DIR / "sql" / script_file, "r") as f:
            sql = f.read()
            pg.execute_script(sql)

    # 2. Generate synthetic datasets
    data = generate_dataset(num_orders=600, num_iot_events=2500)

    # 3. Write to Bronze layer in Database and MinIO Object Store
    for name, df in data.items():
        pg.write_df(df, f"raw_{name}", schema="bronze", if_exists="replace")
        
        # Save raw JSON payloads to MinIO S3 Lake
        records = df.to_dict(orient="records")
        minio.upload_json(f"bronze/{name}/{datetime.utcnow().strftime('%Y%m%d')}_{name}.json", records)

    logger.info("Successfully populated Bronze Layer with synthetic supply chain data!")

if __name__ == "__main__":
    main()
