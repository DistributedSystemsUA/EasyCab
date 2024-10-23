#Le paso una ID que lo identifique
#Espero a que se conecte con su sensor correspondiente
#Paso autentificacion a Central
import argparse
import requests
import time
import socket
import threading


def main():
    parser = argparse.ArgumentParser(description="Taxis")
    parser.add_argument("--EC", type=int, help="IP DEL EC CENTRAL")
    parser.add_argument("--BROKER", type=int, help="IP DEL BROKER")
    parser.add_argument("--SENSOR", type=int, help="LA IP DEL SENSOR")
    parser.add_argument("--ID", type=int, help="La ID del Taxi")
    args = parser.parse_args()

    print(f"Hola, {args.EC} , {args.BROKER} , {args.SENSOR} , {args.ID}.")

    
# Cliente que se conecta a EC_Central para autenticarse
def autenticar_con_central(ip_central, puerto_central, id_taxi):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((ip_central, puerto_central))
    cliente.send(id_taxi.encode('utf-8'))
    
    respuesta = cliente.recv(1024).decode('utf-8')
    if respuesta == "OK":
        print(f"Taxi {id_taxi} autenticado correctamente con EC_Central")
    else:
        print(f"Autenticación fallida para Taxi {id_taxi}")
    cliente.close()

# Servidor para recibir mensajes del sensor
def manejar_sensor(conexion_sensor, direccion_sensor, taxi_id):
    print(f"Taxi {taxi_id} conectado con su sensor en {direccion_sensor}")
    while True:
        try:
            mensaje = conexion_sensor.recv(1024).decode('utf-8')
            if not mensaje:
                break
            print(f"Taxi {taxi_id} recibió del sensor: {mensaje}")
            conexion_sensor.send("OK".encode('utf-8'))
        except:
            break
    conexion_sensor.close()

def taxi_servidor(ip_central, puerto_central, puerto_taxi, taxi_id):
    # Autenticarse con EC_Central
    autenticar_con_central(ip_central, puerto_central, taxi_id)
    
    # Crear el servidor que escuchará al sensor
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('0.0.0.0', puerto_taxi))
    servidor.listen(1)
    
    print(f"Taxi {taxi_id} esperando a su sensor en el puerto {puerto_taxi}...")
    conexion_sensor, direccion_sensor = servidor.accept()
    manejar_sensor(conexion_sensor, direccion_sensor, taxi_id)

if __name__ == "__main__":
    ip_central = input("Ingrese la IP de EC_Central: ")
    puerto_central = int(input("Ingrese el puerto de EC_Central: "))
    puerto_taxi = int(input("Ingrese el puerto para este taxi: "))
    taxi_id = input("Ingrese el ID del taxi: ")
    
    taxi_servidor(ip_central, puerto_central, puerto_taxi, taxi_id)


# Configura tu subdominio y token de DuckDNS
#SUBDOMAIN = 'pruebasdspractica1'  # Reemplaza con tu subdominio
#TOKEN = '0df02128-4445-43d7-bf8b-3ba42c2a797d'  # Reemplaza con tu token

#def update_duckdns():
#    url = f'https://www.duckdns.org/update?domains={SUBDOMAIN}&token={TOKEN}&ip='
#    #url = f'pruebasSDP1.giize.com'
#   response = requests.get(url)
#    print(response.text)  # Para ver la respuesta de DuckDNS

# Actualiza la IP cada 5 minutos
#while True:
#    update_duckdns()
#    time.sleep(300)  # Espera 5 minutos (300 segundos)
