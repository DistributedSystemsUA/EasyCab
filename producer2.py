from kafka import KafkaProducer
import time

# Replace 'your.kafka.server.ip' with the IP address of the machine running Kafka broker
KAFKA_BROKER = '0.0.0.0:9092'
print(KAFKA_BROKER)

producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

def produce_messages():
    for i in range(10):
        message = f"message {i}"
        producer.send('test_topic', value=message.encode('utf-8'))
        print(f"Sent: {message}")
        time.sleep(1)

if __name__ == "__main__":
    produce_messages()
    producer.close()
