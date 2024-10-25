from kafka import KafkaConsumer,KafkaProducer

id = input("Dime el id del cliente: ")
ip = input("Dame la ip que va a usar kafka: ")
ip += ":9092"

# Cambia la dirección IP por la dirección de tu host
print(ip)
producer = KafkaProducer(bootstrap_servers= ip)

f = open('Peticiones'+ id + ".txt",'r')
lineas = f.readlines()
for linea in lineas:
    # Enviar un mensaje
    texto = linea.strip()
    producer.send('clientes', f"{id} {texto}".encode('utf-8'))

producer.flush()
producer.close()

consumer = KafkaConsumer(
    f'clientes{id}',
    bootstrap_servers= ip,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group'
)

for message in consumer:
    print(f"Received message: {message.value.decode('utf-8')}")