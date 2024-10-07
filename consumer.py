from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'test',
    bootstrap_servers='192.168.18.54:29092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group'
)

for message in consumer:
    print(f"Received message: {message.value.decode('utf-8')}")
