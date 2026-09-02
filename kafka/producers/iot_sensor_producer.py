import json
import time
import random
import logging
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from python.config import KAFKA_BOOTSTRAP_SERVERS, TOPIC_IOT_TELEMETRY

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] KafkaIoTProducer: %(message)s")
logger = logging.getLogger("KafkaIoTProducer")

def generate_iot_telemetry():
    shipment_ids = [f"SHP-{i:06d}" for i in range(1, 100)]
    sh_id = random.choice(shipment_ids)
    device_id = f"DEV-{random.randint(100, 999)}"
    
    # Temperature simulation (cold chain breach > 8.0 C)
    is_breach = random.random() < 0.1
    temp = random.uniform(8.5, 16.0) if is_breach else random.uniform(2.0, 6.0)

    event = {
        "event_id": f"EVT-{int(time.time() * 1000)}",
        "shipment_id": sh_id,
        "device_id": device_id,
        "latitude": round(random.uniform(-40.0, 60.0), 6),
        "longitude": round(random.uniform(-120.0, 140.0), 6),
        "temperature_c": round(temp, 2),
        "humidity_pct": round(random.uniform(45.0, 80.0), 2),
        "battery_level": random.randint(20, 100),
        "is_temp_breach": is_breach,
        "recorded_at": datetime.utcnow().isoformat()
    }
    return event

def run_producer(max_events: int = 50, interval_sec: float = 0.5):
    try:
        from kafka import KafkaProducer
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            request_timeout_ms=3000
        )
        logger.info(f"Kafka Producer connected to {KAFKA_BOOTSTRAP_SERVERS}")
        for _ in range(max_events):
            event = generate_iot_telemetry()
            producer.send(TOPIC_IOT_TELEMETRY, value=event)
            logger.info(f"Published Kafka event {event['event_id']} for shipment {event['shipment_id']} (Temp: {event['temperature_c']}C)")
            time.sleep(interval_sec)
        producer.flush()
    except Exception as e:
        logger.warning(f"Kafka broker offline or unreachable ({e}). Running local simulated producer stream.")
        for _ in range(max_events):
            event = generate_iot_telemetry()
            logger.info(f"[SIMULATED STREAM] Event {event['event_id']} -> Temp: {event['temperature_c']}C, Breach: {event['is_temp_breach']}")
            time.sleep(0.1)

if __name__ == "__main__":
    run_producer(max_events=20)
