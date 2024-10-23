from kafka import KafkaProducer

ip = input("Dame la ip que va a usar kafka: ")
ip += ":9092"

print(ip)

# Cambia la dirección IP por la dirección de tu host
producer = KafkaProducer(bootstrap_servers= ip)

# Enviar un mensaje
texto = ""
while texto != "q":
    texto = input()
    producer.send('test', texto.encode('utf-8'))
producer.flush()

producer.close()
