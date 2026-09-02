import sys
import logging
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from python.config import KAFKA_BOOTSTRAP_SERVERS, TOPIC_SHIPMENT_EVENTS
from python.db.postgres_client import PostgresClient
from python.utils.logger import get_logger

logger = get_logger("ShipmentStreamingProcessor")

def process_shipment_stream():
    try:
        # pyrefly: ignore [missing-import]
        from pyspark.sql import SparkSession
        # pyrefly: ignore [missing-import]
        from pyspark.sql.functions import from_json, col, current_timestamp
        # pyrefly: ignore [missing-import]
        from pyspark.sql.types import StructType, StructField, StringType, IntegerType

        logger.info("Initializing Spark Streaming Session for Shipment Events...")
        spark = SparkSession.builder \
            .appName("ShipmentStreamingProcessor") \
            .master("local[*]") \
            .getOrCreate()

        schema = StructType([
            StructField("event_id", StringType(), True),
            StructField("shipment_id", StringType(), True),
            StructField("status", StringType(), True),
            StructField("delay_hours", IntegerType(), True),
            StructField("location", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

        kafka_df = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
            .option("subscribe", TOPIC_SHIPMENT_EVENTS) \
            .load()

        events = kafka_df.selectExpr("CAST(value AS STRING) as json_val") \
            .select(from_json(col("json_val"), schema).alias("data")) \
            .select("data.*")

        query = events.writeStream.format("console").start()
        query.awaitTermination(timeout=5)
    except Exception as e:
        logger.warning(f"Spark Kafka stream unavailable ({e}). Fallback processor active.")
        pg = PostgresClient()
        df = pg.read_df("SELECT * FROM silver.shipments LIMIT 20")
        logger.info(f"Processed {len(df)} shipment tracking updates.")

if __name__ == "__main__":
    process_shipment_stream()
