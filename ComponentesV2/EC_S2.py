import socket
import time

# Constantes para el protocolo
STX = '\x02'
ETX = '\x03'
ACK = '\x06'
NACK = '\x15'

def calcular_lrc(mensaje):
    lrc = 0
    for char in mensaje:
        lrc ^= ord(char)
    return chr(lrc)

# Empaqueta el mensaje en el formato <STX><DATA><ETX><LRC>
def empaquetar_mensaje(data):
    mensaje = f"{STX}{data}{ETX}"
    lrc = calcular_lrc(mensaje)
    return mensaje + lrc

def sensor_cliente(ip_taxi, puerto_taxi, sensor_id):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((ip_taxi, puerto_taxi))
    
    while True:
        mensaje = empaquetar_mensaje(f"Sensor#{sensor_id}#Estado:OK")
        cliente.send(mensaje.encode('utf-8'))
        
        respuesta = cliente.recv(1024).decode('utf-8')
        if respuesta == ACK:
            print(f"Respuesta del taxi: Mensaje recibido correctamente.")
        else:
            print(f"Respuesta del taxi: Error en el mensaje.")
        
        time.sleep(5)

if __name__ == "__main__":
    ip_taxi = input("Ingrese la IP del taxi: ")
    puerto_taxi = int(input("Ingrese el puerto del taxi: "))
    sensor_id = input("Ingrese el ID del sensor: ")
    
    sensor_cliente(ip_taxi, puerto_taxi, sensor_id)
