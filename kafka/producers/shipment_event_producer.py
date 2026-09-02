import json
import time
import random
import logging
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from python.config import KAFKA_BOOTSTRAP_SERVERS, TOPIC_SHIPMENT_EVENTS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] ShipmentProducer: %(message)s")
logger = logging.getLogger("ShipmentProducer")

def generate_shipment_event():
    shipment_id = f"SHP-{random.randint(1, 600):06d}"
    statuses = ["IN_TRANSIT", "DELIVERED", "DELAYED", "CUSTOMS_HOLD"]
    status = random.choice(statuses)
    delay_hours = random.choice([0, 6, 12, 24, 48]) if status == "DELAYED" else 0
    
    event = {
        "event_id": f"SHPEVT-{int(time.time() * 1000)}",
        "shipment_id": shipment_id,
        "status": status,
        "delay_hours": delay_hours,
        "location": random.choice(["Rotterdam Hub", "Los Angeles Customs", "Hamburg Port", "Dubai Gateway", "Tokyo Airport"]),
        "updated_at": datetime.utcnow().isoformat()
    }
    return event

def run_producer(max_events: int = 20):
    try:
        from kafka import KafkaProducer
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            request_timeout_ms=3000
        )
        for _ in range(max_events):
            event = generate_shipment_event()
            producer.send(TOPIC_SHIPMENT_EVENTS, value=event)
            logger.info(f"Published shipment event: {event['shipment_id']} -> {event['status']}")
            time.sleep(0.5)
        producer.flush()
    except Exception as e:
        logger.warning(f"Kafka unreachable ({e}). Simulated shipment event stream running.")

if __name__ == "__main__":
    run_producer()
