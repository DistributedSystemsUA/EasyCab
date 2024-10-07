from kafka import KafkaConsumer

# Replace 'your.kafka.server.ip' with the IP address of the machine running Kafka broker
KAFKA_BROKER = '0.0.0.0:9092'

consumer = KafkaConsumer(
    'test_topic',
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group')

def consume_messages():
    for message in consumer:
        print(f"Received: {message.value.decode('utf-8')}")

if __name__ == "__main__":
    consume_messages()
