import sys
import logging
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from python.config import KAFKA_BOOTSTRAP_SERVERS, TOPIC_IOT_TELEMETRY
from python.db.postgres_client import PostgresClient
from python.db.minio_client import MinioClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] SparkStreamingEnrichment: %(message)s")
logger = logging.getLogger("SparkStreamingEnrichment")

def run_pyspark_streaming():
    """Runs PySpark Structured Streaming job consuming Kafka IoT events."""
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import from_json, col, when, current_timestamp
        from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, BooleanType

        logger.info("Initializing PySpark Structured Streaming session...")
        spark = SparkSession.builder \
            .appName("SupplyChainIoTStreamingEnrichment") \
            .master("local[*]") \
            .config("spark.sql.shuffle.partitions", "2") \
            .getOrCreate()

        schema = StructType([
            StructField("event_id", StringType(), True),
            StructField("shipment_id", StringType(), True),
            StructField("device_id", StringType(), True),
            StructField("latitude", DoubleType(), True),
            StructField("longitude", DoubleType(), True),
            StructField("temperature_c", DoubleType(), True),
            StructField("humidity_pct", DoubleType(), True),
            StructField("battery_level", IntegerType(), True),
            StructField("recorded_at", StringType(), True),
        ])

        kafka_df = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
            .option("subscribe", TOPIC_IOT_TELEMETRY) \
            .option("startingOffsets", "latest") \
            .load()

        parsed_df = kafka_df.selectExpr("CAST(value AS STRING) as json_payload") \
            .select(from_json(col("json_payload"), schema).alias("data")) \
            .select("data.*") \
            .withColumn("is_temp_breach", when(col("temperature_c") > 8.0, True).otherwise(False)) \
            .withColumn("ingested_at", current_timestamp())

        query = parsed_df.writeStream \
            .format("console") \
            .outputMode("append") \
            .option("truncate", "false") \
            .start()

        logger.info("Spark Structured Streaming query active. Awaiting micro-batches...")
        query.awaitTermination(timeout=10)

    except Exception as e:
        logger.warning(f"PySpark environment or Kafka stream unavailable ({e}). Running streaming simulator.")
        run_streaming_fallback()

def run_streaming_fallback():
    pg = PostgresClient()
    minio = MinioClient()
    logger.info("Streaming Processor: Ingesting active IoT telemetry events...")
    
    # Read raw bronze events and detect cold chain breaches
    df_raw = pg.read_df("SELECT * FROM bronze.raw_iot_sensors LIMIT 50")
    if not df_raw.empty:
        df_raw["temperature_c"] = df_raw["temperature_c"].astype(float)
        df_raw["is_temp_breach"] = df_raw["temperature_c"] > 8.0
        breaches = df_raw[df_raw["is_temp_breach"]]
        logger.info(f"Stream Processor Analyzed {len(df_raw)} telemetry events: Detected {len(breaches)} Temperature Breaches (>8°C)!")

if __name__ == "__main__":
    run_pyspark_streaming()
