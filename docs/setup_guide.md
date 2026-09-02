# Global Supply Chain Digital Twin - Setup & Operations Guide

## Prerequisites
- Python 3.10+
- Docker & Docker Compose (Optional for full containerization)

---

## 🚀 Quick Start (Local Direct Mode - No Docker Required)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Synthetic Supply Chain Data
Populates Bronze tables and initializes the SQLite/PostgreSQL database and MinIO lake storage:
```bash
python3 python/data_generator/generate_mock_data.py
```

### 3. Run Batch Medallion ETL Pipeline
Transforms Bronze raw data -> Silver cleaned tables -> Gold Star Schema data warehouse models:
```bash
python3 spark/batch/batch_medallion_etl.py
```

### 4. Run Automated Data Quality Audit
Executes automated test assertions across Bronze, Silver, and Gold schemas:
```bash
python3 python/quality/data_validator.py
```

### 5. Launch Digital Twin Control Tower Web App
Start the web server:
```bash
python3 dashboard/app.py
```
Open your browser at: **`http://localhost:8050`**

---

## 🐳 Docker Deployment (Full Containerized Stack)

To run the complete platform with PostgreSQL, MinIO, Kafka, Spark, Airflow, Prometheus, Grafana, and Dashboard:

```bash
docker compose up -d
```

### Service Access URLs:
- **Digital Twin Control Tower**: `http://localhost:8050`
- **Apache Airflow DAG Manager**: `http://localhost:8081` (admin / admin)
- **Grafana Monitoring Dashboards**: `http://localhost:3000` (admin / admin)
- **Prometheus Metrics**: `http://localhost:9090`
- **MinIO S3 Console**: `http://localhost:9001` (minioadmin / minioadmin)
- **Spark Cluster Manager**: `http://localhost:8080`

---

## 🧪 Running Unit & Integration Tests

```bash
python3 -m pytest tests/ -v
```
