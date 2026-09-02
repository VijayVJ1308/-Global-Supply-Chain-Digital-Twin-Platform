import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Database Configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB = os.getenv("POSTGRES_DB", "supply_chain_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

# MinIO S3-Compatible Object Store
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "global-supply-chain-lake")

# Apache Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_IOT_TELEMETRY = "supply-chain-iot-telemetry"
TOPIC_SHIPMENT_EVENTS = "supply-chain-shipment-events"
TOPIC_ORDER_EVENTS = "supply-chain-order-events"
TOPIC_INVENTORY_CHANGES = "supply-chain-inventory-changes"

# Prometheus Metrics
PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", 8000))

# Operational UI Settings
WEB_PORT = int(os.getenv("WEB_PORT", 8050))
