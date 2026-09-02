"""
Synthetic Data Generation Engine for Global Supply Chain Digital Twin Platform.
Generates realistic, correlated data for all 12 core supply chain entities.
"""

import random
import uuid
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Any

# Predefined Global Hub Locations with GPS coordinates
GLOBAL_HUBS = [
    {"city": "Singapore", "country": "Singapore", "region": "APAC", "lat": 1.2902, "lon": 103.8519},
    {"city": "Shanghai", "country": "China", "region": "APAC", "lat": 31.2304, "lon": 121.4737},
    {"city": "Rotterdam", "country": "Netherlands", "region": "EMEA", "lat": 51.9244, "lon": 4.4777},
    {"city": "Hamburg", "country": "Germany", "region": "EMEA", "lat": 53.5511, "lon": 9.9937},
    {"city": "Los Angeles", "country": "United States", "region": "AMER", "lat": 34.0522, "lon": -118.2437},
    {"city": "Dubai", "country": "UAE", "region": "MEA", "lat": 25.2048, "lon": 55.2708},
    {"city": "Tokyo", "country": "Japan", "region": "APAC", "lat": 35.6762, "lon": 139.6503},
    {"city": "Frankfurt", "country": "Germany", "region": "EMEA", "lat": 50.1109, "lon": 8.6821},
    {"city": "Long Beach", "country": "United States", "region": "AMER", "lat": 33.7701, "lon": -118.1937},
    {"city": "Busan", "country": "South Korea", "region": "APAC", "lat": 35.1796, "lon": 129.0756}
]

CARRIERS = ["Maersk Line", "MSC Logistics", "DHL Express", "FedEx Supply Chain", "COSCO Shipping", "Kuehne+Nagel"]
PRODUCT_CATEGORIES = ["Electronics", "Semiconductors", "Automotive Parts", "Pharmaceuticals", "Consumer Goods", "Industrial Machinery"]
SUPPLIER_TYPES = ["Tier 1 Primary", "Component Manufacturer", "Raw Material Vendor", "OEM Distributor"]
CUSTOMER_SEGMENTS = ["Enterprise High-Volume", "Regional Wholesaler", "Direct OEM", "Retail Partner"]
DISRUPTION_TYPES = ["Storm", "Port Congestion", "Factory Failure", "Supplier Delay", "Labor Strike", "Road Closure", "Geopolitical Disruption"]
WEATHER_CONDITIONS = ["Clear", "Heavy Rain", "Typhoon", "Dense Fog", "Severe Storm", "Extreme Heat"]

class SupplyChainDataGenerator:
    def __init__(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)

    def generate_suppliers(self, count: int = 20) -> pd.DataFrame:
        suppliers = []
        for i in range(1, count + 1):
            hub = random.choice(GLOBAL_HUBS)
            suppliers.append({
                "supplier_id": f"SUP_{i:04d}",
                "supplier_name": f"Global Vendor {i} ({hub['country']})",
                "country": hub["country"],
                "region": hub["region"],
                "supplier_type": random.choice(SUPPLIER_TYPES),
                "rating": round(random.uniform(3.2, 4.95), 2),
                "lead_time_days": random.randint(3, 21),
                "capacity": random.randint(5000, 50000),
                "reliability_score": round(random.uniform(70.0, 99.5), 1),
                "risk_score": round(random.uniform(10.0, 85.0), 1)
            })
        return pd.DataFrame(suppliers)

    def generate_products(self, count: int = 30) -> pd.DataFrame:
        products = []
        for i in range(1, count + 1):
            unit_cost = round(random.uniform(15.0, 1200.0), 2)
            products.append({
                "product_id": f"PROD_{i:04d}",
                "product_name": f"Enterprise Product Component {i}",
                "category": random.choice(PRODUCT_CATEGORIES),
                "unit_cost": unit_cost,
                "selling_price": round(unit_cost * random.uniform(1.3, 2.2), 2),
                "weight": round(random.uniform(0.5, 45.0), 2),
                "volume": round(random.uniform(0.01, 1.5), 3)
            })
        return pd.DataFrame(products)

    def generate_factories(self, count: int = 10) -> pd.DataFrame:
        factories = []
        for i in range(1, count + 1):
            hub = GLOBAL_HUBS[i % len(GLOBAL_HUBS)]
            factories.append({
                "factory_id": f"FAC_{i:04d}",
                "factory_name": f"Digital Twin Manufacturing Plant {i}",
                "country": hub["country"],
                "latitude": hub["lat"] + round(random.uniform(-0.1, 0.1), 4),
                "longitude": hub["lon"] + round(random.uniform(-0.1, 0.1), 4),
                "production_capacity": random.randint(10000, 100000),
                "utilization": round(random.uniform(65.0, 98.0), 1)
            })
        return pd.DataFrame(factories)

    def generate_warehouses(self, count: int = 10) -> pd.DataFrame:
        warehouses = []
        for i in range(1, count + 1):
            hub = GLOBAL_HUBS[i % len(GLOBAL_HUBS)]
            capacity = random.randint(50000, 250000)
            warehouses.append({
                "warehouse_id": f"WH_{i:04d}",
                "warehouse_name": f"Hub Warehouse {hub['city']}",
                "country": hub["country"],
                "city": hub["city"],
                "latitude": hub["lat"],
                "longitude": hub["lon"],
                "capacity": capacity,
                "current_utilization": round(random.uniform(50.0, 92.0), 1)
            })
        return pd.DataFrame(warehouses)

    def generate_customers(self, count: int = 25) -> pd.DataFrame:
        customers = []
        for i in range(1, count + 1):
            hub = random.choice(GLOBAL_HUBS)
            customers.append({
                "customer_id": f"CUST_{i:04d}",
                "country": hub["country"],
                "region": hub["region"],
                "customer_segment": random.choice(CUSTOMER_SEGMENTS)
            })
        return pd.DataFrame(customers)

    def generate_orders(self, count: int = 100, customers_df: pd.DataFrame = None, products_df: pd.DataFrame = None) -> pd.DataFrame:
        orders = []
        cust_ids = customers_df["customer_id"].tolist() if customers_df is not None else [f"CUST_{i:04d}" for i in range(1, 20)]
        prod_ids = products_df["product_id"].tolist() if products_df is not None else [f"PROD_{i:04d}" for i in range(1, 20)]
        start_date = datetime.now() - timedelta(days=30)
        
        for i in range(1, count + 1):
            order_dt = start_date + timedelta(days=random.randint(0, 25), hours=random.randint(0, 23))
            promised_dt = order_dt + timedelta(days=random.randint(3, 7))
            status = random.choice(["PENDING", "SHIPPED", "DELIVERED", "CANCELLED"])
            delivery_dt = promised_dt + timedelta(days=random.randint(-1, 3)) if status == "DELIVERED" else None
            
            orders.append({
                "order_id": f"ORD_{i:05d}",
                "customer_id": random.choice(cust_ids),
                "product_id": random.choice(prod_ids),
                "quantity": random.randint(10, 500),
                "order_date": order_dt.isoformat(),
                "promised_date": promised_dt.isoformat(),
                "delivery_date": delivery_dt.isoformat() if delivery_dt else None,
                "order_status": status
            })
        return pd.DataFrame(orders)

    def generate_inventory(self, warehouses_df: pd.DataFrame = None, products_df: pd.DataFrame = None) -> pd.DataFrame:
        inventory = []
        wh_ids = warehouses_df["warehouse_id"].tolist() if warehouses_df is not None else [f"WH_{i:04d}" for i in range(1, 5)]
        prod_ids = products_df["product_id"].tolist() if products_df is not None else [f"PROD_{i:04d}" for i in range(1, 10)]
        
        idx = 1
        for wh in wh_ids:
            for prod in prod_ids:
                qty = random.randint(50, 5000)
                safety = random.randint(100, 800)
                inventory.append({
                    "inventory_id": f"INV_{idx:05d}",
                    "warehouse_id": wh,
                    "product_id": prod,
                    "quantity": qty,
                    "reserved_quantity": random.randint(0, int(qty * 0.3)),
                    "reorder_point": safety + random.randint(50, 200),
                    "safety_stock": safety,
                    "inventory_date": datetime.now().isoformat()
                })
                idx += 1
        return pd.DataFrame(inventory)

    def generate_shipments(self, orders_df: pd.DataFrame = None) -> pd.DataFrame:
        shipments = []
        order_ids = orders_df["order_id"].tolist() if orders_df is not None else [f"ORD_{i:05d}" for i in range(1, 30)]
        
        for i, ord_id in enumerate(order_ids, start=1):
            origin = random.choice(GLOBAL_HUBS)
            dest = random.choice([h for h in GLOBAL_HUBS if h != origin])
            mode = random.choice(["Air", "Sea", "Road", "Rail"])
            dept_time = datetime.now() - timedelta(days=random.randint(1, 10))
            est_arrival = dept_time + timedelta(days=random.randint(2, 14))
            status = random.choice(["IN_TRANSIT", "DELIVERED", "DELAYED", "CUSTOMS_HOLD"])
            actual_arrival = est_arrival + timedelta(days=random.randint(0, 4)) if status == "DELIVERED" else None
            
            shipments.append({
                "shipment_id": f"SHIP_{i:05d}",
                "order_id": ord_id,
                "origin": f"{origin['city']}, {origin['country']}",
                "destination": f"{dest['city']}, {dest['country']}",
                "carrier": random.choice(CARRIERS),
                "transport_mode": mode,
                "departure_time": dept_time.isoformat(),
                "estimated_arrival": est_arrival.isoformat(),
                "actual_arrival": actual_arrival.isoformat() if actual_arrival else None,
                "shipment_status": status
            })
        return pd.DataFrame(shipments)

    def generate_shipment_events(self, shipments_df: pd.DataFrame = None) -> pd.DataFrame:
        events = []
        shipments = shipments_df.to_dict("records") if shipments_df is not None else []
        idx = 1
        
        for ship in shipments[:15]:
            for step in range(3):
                events.append({
                    "event_id": f"EVT_{idx:06d}",
                    "shipment_id": ship["shipment_id"],
                    "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
                    "latitude": round(random.uniform(1.0, 55.0), 4),
                    "longitude": round(random.uniform(-118.0, 139.0), 4),
                    "temperature": round(random.uniform(2.0, 9.5), 1),
                    "speed": random.randint(15, 65),
                    "event_type": random.choice(["GPS_PING", "PORT_CHECKIN", "TEMP_READING", "CUSTOMS_SCAN"])
                })
                idx += 1
        return pd.DataFrame(events)

    def generate_purchase_orders(self, count: int = 40, suppliers_df: pd.DataFrame = None, products_df: pd.DataFrame = None) -> pd.DataFrame:
        pos = []
        sup_ids = suppliers_df["supplier_id"].tolist() if suppliers_df is not None else [f"SUP_{i:04d}" for i in range(1, 5)]
        prod_ids = products_df["product_id"].tolist() if products_df is not None else [f"PROD_{i:04d}" for i in range(1, 5)]
        
        for i in range(1, count + 1):
            order_dt = datetime.now() - timedelta(days=random.randint(5, 30))
            expected_dt = order_dt + timedelta(days=random.randint(7, 21))
            status = random.choice(["ISSUED", "IN_PRODUCTION", "SHIPPED", "RECEIVED"])
            actual_dt = expected_dt + timedelta(days=random.randint(-1, 4)) if status == "RECEIVED" else None
            
            pos.append({
                "po_id": f"PO_{i:05d}",
                "supplier_id": random.choice(sup_ids),
                "product_id": random.choice(prod_ids),
                "quantity": random.randint(100, 5000),
                "order_date": order_dt.isoformat(),
                "expected_delivery": expected_dt.isoformat(),
                "actual_delivery": actual_dt.isoformat() if actual_dt else None,
                "status": status
            })
        return pd.DataFrame(pos)

    def generate_weather(self) -> pd.DataFrame:
        records = []
        for hub in GLOBAL_HUBS:
            records.append({
                "timestamp": datetime.now().isoformat(),
                "location": f"{hub['city']}, {hub['country']}",
                "temperature": round(random.uniform(10.0, 38.0), 1),
                "rainfall": round(random.uniform(0.0, 45.0), 1),
                "wind_speed": round(random.uniform(5.0, 85.0), 1),
                "storm_probability": round(random.uniform(0.05, 0.90), 2),
                "weather_condition": random.choice(WEATHER_CONDITIONS)
            })
        return pd.DataFrame(records)

    def generate_disruptions(self, count: int = 8) -> pd.DataFrame:
        disruptions = []
        for i in range(1, count + 1):
            hub = random.choice(GLOBAL_HUBS)
            start_dt = datetime.now() - timedelta(hours=random.randint(2, 72))
            disruptions.append({
                "disruption_id": f"DIS_{i:04d}",
                "disruption_type": random.choice(DISRUPTION_TYPES),
                "location": f"{hub['city']}, {hub['country']}",
                "severity": random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
                "start_time": start_dt.isoformat(),
                "end_time": (start_dt + timedelta(hours=random.randint(12, 120))).isoformat(),
                "affected_routes": f"Trade Lane {hub['region']} -> Global"
            })
        return pd.DataFrame(disruptions)

    def generate_all(self) -> Dict[str, pd.DataFrame]:
        suppliers = self.generate_suppliers(20)
        products = self.generate_products(30)
        factories = self.generate_factories(10)
        warehouses = self.generate_warehouses(10)
        customers = self.generate_customers(25)
        orders = self.generate_orders(100, customers, products)
        inventory = self.generate_inventory(warehouses, products)
        shipments = self.generate_shipments(orders)
        events = self.generate_shipment_events(shipments)
        pos = self.generate_purchase_orders(40, suppliers, products)
        weather = self.generate_weather()
        disruptions = self.generate_disruptions(8)
        
        return {
            "suppliers": suppliers,
            "products": products,
            "factories": factories,
            "warehouses": warehouses,
            "customers": customers,
            "orders": orders,
            "inventory": inventory,
            "shipments": shipments,
            "shipment_events": events,
            "purchase_orders": pos,
            "weather": weather,
            "disruptions": disruptions
        }

if __name__ == "__main__":
    gen = SupplyChainDataGenerator()
    data = gen.generate_all()
    print("Successfully generated all 12 core supply chain datasets:")
    for key, df in data.items():
        print(f" - {key}: {len(df)} records")
