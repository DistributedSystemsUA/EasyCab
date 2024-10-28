import socket
import argparse
from kafka import KafkaProducer

HOST = 'localhost'
PORT = 9991

BEL = 0x07

def sensor(kafka):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))

    server_socket.listen(1)
    print(f"Servidor escuchando en {HOST}:{PORT}")

    conn, addr = server_socket.accept()
    print(f"Conexión establecida con {addr}")

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            if data[0] == BEL:
                producer = KafkaProducer(bootstrap_servers= kafka)
                producer.send('pararTaxi', (f"{data[1]}").encode('utf-8'))
                producer.flush()
                producer.close()

    except KeyboardInterrupt:
        print("Cerrando servidor")
    finally:
        conn.close()


def validarTaxi(ip_central, puerto_central, id_taxi):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((ip_central, puerto_central))
    cliente.send(str(id_taxi).encode('utf-8'))
    
    respuesta = cliente.recv(1024).decode('utf-8')
    if respuesta == "OK":
        print(f"Taxi {id_taxi} autenticado correctamente con EC_Central")
    else:
        print(f"Autenticación fallida para Taxi {id_taxi}")
    cliente.close()


if __name__ == "__main__":
     # Argumentos del programa
    parser = argparse.ArgumentParser()
    parser.add_argument('ip_central', type=str)
    parser.add_argument('puerto_central', type=int)
    parser.add_argument('id_taxi', type=int)
    parser.add_argument('kafka', type=str)

    args = parser.parse_args()

    args = parser.parse_args()
    validarTaxi(args.ip_central,args.puerto_central,args.id_taxi)
    sensor(args.kafka)
