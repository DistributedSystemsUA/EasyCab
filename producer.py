from kafka import KafkaProducer

# Cambia la dirección IP por la dirección de tu host
producer = KafkaProducer(bootstrap_servers='192.168.18.54:29092')

# Enviar un mensaje
texto = ""
while texto != "q":
    texto = input()
    producer.send('test', texto.encode('utf-8'))
producer.flush()

producer.close()
