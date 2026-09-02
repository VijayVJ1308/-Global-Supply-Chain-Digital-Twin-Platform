# Architecture Specification: Global Supply Chain Digital Twin Platform

## 1. Executive Summary

The **Global Supply Chain Digital Twin Platform** is an enterprise-grade data engineering, intelligence, and simulation system. It models a multinational enterprise's complete physical supply chain ecosystem—from raw material suppliers and manufacturing plants to regional distribution hubs, multimodal transport networks, ports, and end-customer fulfillment centers.

---

## 2. System Architecture & Data Flow

```mermaid
flowchart TD
    subgraph Data Sources & Generators
        G1[Synthetic Data Engine]
        G2[IoT Sensors & Telematics]
        G3[Weather & Disruption Generators]
    end

    subgraph Streaming Ingestion (Kafka)
        K1[Topic: orders]
        K2[Topic: inventory]
        K3[Topic: shipments]
        K4[Topic: shipment_events]
        K5[Topic: weather_events]
        K6[Topic: disruptions]
        G1 & G2 & G3 --> K1 & K2 & K3 & K4 & K5 & K6
    end

    subgraph Real-Time Processing (Spark & Streaming DB)
        S1[PySpark Structured Streaming]
        K4 & K5 & K6 --> S1
        S1 --> DB1[(PostgreSQL DB)]
        S1 --> S3[(MinIO Object Store)]
    end

    subgraph Batch Orchestration & Transformations (Airflow + dbt)
        A1[Airflow DAGs]
        D1[dbt Medallion Models]
        A1 --> D1
        D1 --> DB1
    end

    subgraph Intelligence & Simulation Engines
        M1[Demand Forecasting ML]
        M2[Shipment Delay Predictor]
        R1[Supply Chain Risk Engine]
        SIM[What-If Simulator]
        DB1 --> M1 & M2 & R1 & SIM
    end

    subgraph Presentation & APIs
        API[FastAPI Backend]
        UI[React + TS Interactive Dashboard]
        M1 & M2 & R1 & SIM & DB1 --> API
        API --> UI
    end
```

---

## 3. Core Architectural Layers

### 3.1 Medallion Data Lakehouse Design
- **Bronze Layer (`bronze`)**: Raw, immutable JSON/CSV payloads ingested from APIs, ERPs, and Kafka topics.
- **Silver Layer (`silver`)**: Cleaned, deduplicated, typed, and schema-enforced relational tables.
- **Gold Layer (`gold`)**: Business-ready Star Schema dimensional data warehouse models (`dim_supplier`, `dim_product`, `dim_warehouse`, `dim_customer`, `fact_orders`, `fact_shipments`, `fact_inventory`).

### 3.2 Digital Twin State Machine
Every supply chain entity maintains a real-time state object:
```json
{
  "entity_type": "SHIPMENT",
  "entity_id": "S10025",
  "current_location": {"latitude": 1.2902, "longitude": 103.8519, "city": "Singapore"},
  "status": "IN_TRANSIT",
  "speed_knots": 22.5,
  "eta": "2026-08-15T14:00:00Z",
  "delay_probability": 0.78,
  "risk_score": 76.5,
  "risk_level": "HIGH",
  "cold_chain_status": "NORMAL"
}
```

### 3.3 Supply Chain Risk Score Formula
The platform computes a normalized composite risk score ($0 - 100$) across 6 operational dimensions:

$$\text{Risk Score} = w_1 \cdot R_{\text{supplier}} + w_2 \cdot R_{\text{transit}} + w_3 \cdot R_{\text{weather}} + w_4 \cdot R_{\text{inventory}} + w_5 \cdot R_{\text{geo}} + w_6 \cdot R_{\text{demand}}$$

Where:
- **0–30**: LOW RISK (Green)
- **31–60**: MEDIUM RISK (Yellow)
- **61–80**: HIGH RISK (Orange)
- **81–100**: CRITICAL RISK (Red)

### 3.4 Carbon Footprint Calculation Model
CO₂ emissions ($E_{\text{CO2}}$ in kg) are calculated based on weight, distance, and transit mode emission factors:
- **Air Freight**: $0.50 \text{ kg CO}_2 / \text{tonne-km}$
- **Road Truck**: $0.105 \text{ kg CO}_2 / \text{tonne-km}$
- **Sea Freight**: $0.015 \text{ kg CO}_2 / \text{tonne-km}$
- **Rail Freight**: $0.028 \text{ kg CO}_2 / \text{tonne-km}$

---

## 4. AWS Cloud Migration Blueprint

| Local Architecture Component | Equivalent AWS Cloud Service | Migration Strategy |
| :--- | :--- | :--- |
| **MinIO Object Store** | **Amazon S3** | Replace MinIO endpoint with S3 bucket URIs (`s3://...`). |
| **Apache Kafka** | **Amazon MSK (Managed Streaming for Kafka)** | Point producers and Spark stream consumers to MSK bootstrap brokers. |
| **Apache Spark** | **Amazon EMR / AWS Glue** | Submit PySpark streaming jobs to EMR Serverless or AWS Glue. |
| **PostgreSQL / Star Schema** | **Amazon Redshift / RDS PostgreSQL** | Migrate DDLs and dbt target profiles to Amazon Redshift DWH. |
| **Apache Airflow** | **Amazon MWAA (Managed Workflows for Apache Airflow)** | Upload DAGs and plugins to MWAA S3 bucket. |
| **FastAPI Backend** | **AWS ECS (Fargate) / App Runner** | Deploy Docker containerized backend behind an Application Load Balancer. |
| **React Frontend** | **AWS CloudFront + S3** | Host static Vite React build on S3 with CloudFront CDN distribution. |
| **Prometheus & Grafana** | **Amazon Managed Prometheus & Managed Grafana** | Stream metrics to AWS Managed Prometheus workspace. |
