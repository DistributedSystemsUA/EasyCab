from kafka import KafkaConsumer

ip = input("Dame la ip que va a usar kafka: ")
ip += ":9092"

print(ip)

consumer = KafkaConsumer(
    'test',
    bootstrap_servers= ip,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group'
)

for message in consumer:
    print(f"Received message: {message.value.decode('utf-8')}")
