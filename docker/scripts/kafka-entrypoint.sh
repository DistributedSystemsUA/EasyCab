#!/bin/sh

# Get the IP address of the host
HOST_IP=$(hostname -I | awk '{print $1}')

# Set the advertised listeners dynamically
export KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092,PLAINTEXT_HOST://$HOST_IP:29092

# Start Kafka
exec /etc/confluent/docker/run

