"""
Kafka Event Producer for Global Supply Chain Streaming Events.
Continuously streams real-time events across 8 core Kafka topics:
- orders, inventory, shipments, shipment_events, supplier_events, warehouse_events, weather_events, disruptions
"""

import json
import time
import random
import logging
from datetime import datetime
from typing import Dict, Any, List
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from python.utils.logger import get_logger

logger = get_logger("KafkaEventProducer")

KAFKA_TOPICS = [
    "orders", "inventory", "shipments", "shipment_events",
    "supplier_events", "warehouse_events", "weather_events", "disruptions"
]

class SupplyChainKafkaProducer:
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        try:
            from kafka import KafkaProducer
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: str(k).encode("utf-8") if k else None,
                retries=3
            )
            logger.info(f"Kafka Producer connected successfully to {bootstrap_servers}")
        except Exception as e:
            logger.warning(f"Kafka broker not available at {bootstrap_servers}: {e}. Operating in Standalone Event Emulation Mode.")

    def produce_event(self, topic: str, key: str, payload: Dict[str, Any]):
        if self.producer:
            try:
                self.producer.send(topic, key=key, value=payload)
                logger.info(f"[KAFKA PUBLISH] Topic '{topic}' | Key '{key}'")
            except Exception as e:
                logger.error(f"Failed to send message to Kafka topic {topic}: {e}")
        else:
            logger.info(f"[EVENT STREAM EMULATOR] Topic: {topic} | Key: {key} | Payload: {payload}")

    def generate_live_shipment_event(self) -> Dict[str, Any]:
        shipment_id = f"SHIP_{random.randint(10000, 99999)}"
        return {
            "event_id": f"EVT_{random.randint(100000, 999999)}",
            "shipment_id": shipment_id,
            "timestamp": datetime.now().isoformat(),
            "latitude": round(random.uniform(1.2, 53.5), 4),
            "longitude": round(random.uniform(-118.0, 121.5), 4),
            "temperature": round(random.uniform(2.0, 9.5), 1),
            "speed": random.randint(15, 60),
            "status": random.choice(["IN_TRANSIT", "PORT_CHECKIN", "DELIVERED", "DELAYED"])
        }

    def generate_weather_event(self) -> Dict[str, Any]:
        return {
            "timestamp": datetime.now().isoformat(),
            "location": random.choice(["Singapore", "Shanghai", "Rotterdam", "Hamburg", "Los Angeles"]),
            "temperature": round(random.uniform(12.0, 36.0), 1),
            "wind_speed": round(random.uniform(10.0, 80.0), 1),
            "storm_probability": round(random.uniform(0.1, 0.9), 2),
            "condition": random.choice(["Clear", "Rain", "Typhoon", "Dense Fog"])
        }

    def start_streaming_loop(self, iterations: int = 10, delay_seconds: float = 1.0):
        logger.info(f"Starting Kafka Streaming Loop for {iterations} cycles...")
        for i in range(iterations):
            # Publish shipment tracking telemetry
            ship_event = self.generate_live_shipment_event()
            self.produce_event("shipment_events", ship_event["shipment_id"], ship_event)
            
            # Publish weather telemetry
            wx_event = self.generate_weather_event()
            self.produce_event("weather_events", wx_event["location"], wx_event)
            
            time.sleep(delay_seconds)
        logger.info("Kafka Streaming Loop completed successfully.")

if __name__ == "__main__":
    producer = SupplyChainKafkaProducer()
    producer.start_streaming_loop(iterations=5, delay_seconds=0.5)
