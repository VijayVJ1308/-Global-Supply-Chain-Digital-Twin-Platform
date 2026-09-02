# Global Supply Chain Digital Twin Platform

[![Architecture: Medallion Lakehouse](https://img.shields.io/badge/Architecture-Medallion%20Lakehouse-0284c7.svg)](#architecture)
[![Engine: Python | PySpark | Airflow | dbt](https://img.shields.io/badge/Engine-Python%20%7C%20PySpark%20%7C%20Airflow%20%7C%20dbt-10b981.svg)](#technologies)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-38bdf8.svg)](#expected-outcome)

An enterprise-grade, end-to-end Data Engineering solution creating a **Digital Twin of a Global Supply Chain**. The platform ingests, processes, transforms, validates, and analyzes batch and streaming data across suppliers, warehouses, inventory systems, shipments, ERPs, and IoT sensors (GPS, Temperature, Humidity).

---

## 🏛️ Architecture & Medallion Lakehouse

```
+-----------------------------------------------------------------------------------+
|                                  DATA SOURCES                                     |
|  [ERP System]    [WMS Warehouses]    [Shipment APIs]    [IoT Sensor Streams]     |
+-------+-----------------+-------------------+---------------------+---------------+
        |                 |                   |                     |
        | Batch (Airflow) | Batch (Airflow)   | API Extraction      | Streaming (Kafka)
        v                 v                   v                     v
+-----------------------------------------------------------------------------------+
|                                BRONZE LAYER (RAW)                                 |
|  • PostgreSQL Schema: `bronze` (raw_orders, raw_suppliers, raw_iot_sensors...)    |
|  • MinIO Object Lake: `global-supply-chain-lake/bronze/` (Raw JSON / CSV)        |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          | PySpark / Python Medallion ETL
                                          v
+-----------------------------------------------------------------------------------+
|                               SILVER LAYER (CLEANED)                              |
|  • Timezone Normalization (UTC) & Currency Standardize (USD)                       |
|  • Deduplication, Null Handling, Schema & Referential Validation                  |
|  • PostgreSQL Schema: `silver` | MinIO Lake: `global-supply-chain-lake/silver/`  |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          | dbt / SQL Dimensional Transformations
                                          v
+-----------------------------------------------------------------------------------+
|                              GOLD LAYER (STAR SCHEMA)                             |
|  Facts: fact_orders, fact_shipments, fact_inventory, fact_deliveries              |
|  Dims:  dim_supplier, dim_product, dim_warehouse, dim_customer, dim_region, dim_date |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          +-------------------------+
                                          |                         |
                                          v                         v
                       +--------------------+     +--------------------+
                       | Prometheus/Grafana |     | Digital Twin UI    |
                       | Monitoring         |     | Control Tower      |
                       +--------------------+     +--------------------+
```

---

## 📂 Project Structure

```
global-supply-chain-digital-twin/
├── airflow/                    # Airflow DAGs for batch orchestration
│   └── dags/
│       ├── supply_chain_batch_dag.py
│       └── data_quality_dag.py
├── kafka/                      # Streaming event producers & topic setup
│   ├── producers/
│   │   ├── iot_sensor_producer.py
│   │   └── shipment_event_producer.py
│   └── consumers/
│       └── kafka_lakehouse_consumer.py
├── spark/                      # PySpark Batch & Structured Streaming jobs
│   ├── streaming/
│   │   └── streaming_iot_enrichment.py
│   └── batch/
│       └── batch_medallion_etl.py
├── dbt/                        # dbt Data Warehouse Models (Staging & Gold Marts)
│   ├── dbt_project.yml
│   └── models/
│       ├── staging/
│       └── marts/
├── python/                     # Core Python engine & Data Quality framework
│   ├── db/                     # Postgres & MinIO Lakehouse clients
│   ├── data_generator/         # Synthetic enterprise supply chain generator
│   └── quality/                # Data Validator & Report Generator
├── sql/                        # Schema DDLs (Bronze, Silver, Gold Star Schema)
│   ├── init_db.sql
│   ├── ddl_bronze.sql
│   ├── ddl_silver.sql
│   └── ddl_gold_star_schema.sql
├── docker/                     # Container configuration files
├── monitoring/                 # Prometheus metrics & Grafana provisioning
│   ├── prometheus/
│   └── grafana/
├── dashboard/                  # Interactive Control Tower Web Dashboard
│   ├── app.py
│   ├── templates/
│   └── static/
├── tests/                      # Pytest Unit & Integration test suite
├── docs/                       # Architecture, Setup, and Data Dictionary docs
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Run Data Ingestion & Medallion Pipeline Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Generate synthetic dataset into Bronze storage
python3 python/data_generator/generate_mock_data.py

# Run Medallion ETL Pipeline (Bronze -> Silver -> Gold Star Schema)
python3 spark/batch/batch_medallion_etl.py

# Run Data Quality Audit Suite
python3 python/quality/data_validator.py

# Launch Digital Twin Control Tower Web App
python3 dashboard/app.py
```
Open **`http://localhost:8050`** to view the interactive Digital Twin Control Tower dashboard.

### 2. Run Containerized Stack with Docker Compose
```bash
docker compose up -d
```
- **Control Tower Web UI**: `http://localhost:8050`
- **Airflow DAG Manager**: `http://localhost:8081` (admin / admin)
- **Grafana Dashboards**: `http://localhost:3000` (admin / admin)
- **Prometheus Metrics**: `http://localhost:9090`
- **MinIO S3 Console**: `http://localhost:9001` (minioadmin / minioadmin)

---

## 🧪 Verification & Testing

Run the test suite:
```bash
python3 -m pytest tests/ -v
```

---

## 📊 Features & Functional Highlights

- **Medallion Architecture**: Fully separated Bronze (raw JSON/CSV), Silver (cleaned/standardized Parquet), and Gold (Star Schema DWH) layers.
- **Star Schema Data Warehouse**: Dimensions (`dim_supplier`, `dim_product`, `dim_warehouse`, `dim_customer`, `dim_region`, `dim_date`) and Facts (`fact_orders`, `fact_shipments`, `fact_inventory`, `fact_deliveries`).
- **Real-Time IoT Telemetry Streaming**: Cold chain temperature breach alerts (>8.0°C), vessel/truck GPS tracking, and Kafka producers.
- **Automated Data Quality Framework**: Validates primary keys, null rates, duplicate records, range bounds, and referential integrity, generating interactive HTML quality reports.
- **Monitoring & Observability**: Prometheus scraping and Grafana dashboard JSON configuration.
- **Control Tower Web UI**: Interactive global geographic map, live telemetry feeds, warehouse stock heatmaps, and batch pipeline execution triggers.
