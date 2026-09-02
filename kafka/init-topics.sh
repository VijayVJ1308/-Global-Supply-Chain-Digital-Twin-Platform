#!/bin/bash
# Kafka topic initialization script
KAFKA_BROKER=${KAFKA_BOOTSTRAP_SERVERS:-"localhost:9092"}

echo "Initializing Kafka topics on broker: $KAFKA_BROKER"

kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_BROKER --partitions 3 --replication-factor 1 --topic supply-chain-iot-telemetry
kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_BROKER --partitions 3 --replication-factor 1 --topic supply-chain-shipment-events
kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_BROKER --partitions 3 --replication-factor 1 --topic supply-chain-order-events
kafka-topics --create --if-not-exists --bootstrap-server $KAFKA_BROKER --partitions 3 --replication-factor 1 --topic supply-chain-inventory-changes

echo "Kafka topics created successfully:"
kafka-topics --list --bootstrap-server $KAFKA_BROKER
