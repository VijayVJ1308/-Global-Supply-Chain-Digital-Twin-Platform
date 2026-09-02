import json
import logging
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from python.config import KAFKA_BOOTSTRAP_SERVERS, TOPIC_IOT_TELEMETRY
from python.db.postgres_client import PostgresClient
from python.db.minio_client import MinioClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] LakehouseConsumer: %(message)s")
logger = logging.getLogger("LakehouseConsumer")

def start_consumer():
    pg = PostgresClient()
    minio = MinioClient()
    
    try:
        from kafka import KafkaConsumer
        consumer = KafkaConsumer(
            TOPIC_IOT_TELEMETRY,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset='earliest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            consumer_timeout_ms=5000
        )
        logger.info(f"Subscribed to Kafka topic: {TOPIC_IOT_TELEMETRY}")
        events = []
        for msg in consumer:
            evt = msg.value
            events.append(evt)
            logger.info(f"Consumed Kafka event: {evt.get('event_id')} | Temp: {evt.get('temperature_c')}C")
            
        if events:
            df = pd.DataFrame(events)
            pg.write_df(df, "raw_iot_sensors", schema="bronze", if_exists="append")
            minio.upload_json(f"bronze/iot_stream/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_stream.json", events)
            logger.info(f"Successfully committed {len(events)} streaming events to Lakehouse!")
    except Exception as e:
        logger.warning(f"Kafka Consumer error / broker offline ({e}). Consumer ready for active stream.")

if __name__ == "__main__":
    start_consumer()
