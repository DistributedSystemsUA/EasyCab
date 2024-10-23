#Espera a que su taxi se conecte
#Una vez que taxi valide con Central y central devuelva el mapa y ira haciendo las comprobocaciones necesarias cada segundo.
#Añadir botones para estropear las conexiones de manera intencionada.
import socket
import time

def sensor_cliente(ip_taxi, puerto_taxi, sensor_id):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((ip_taxi, puerto_taxi))
    
    while True:
        mensaje = f"Sensor {sensor_id} reportando estado: OK {sensor_id}"
        cliente.send(mensaje.encode('utf-8'))
        
        respuesta = cliente.recv(1024).decode('utf-8')
        print(f"Taxi respondió: {respuesta}")
        
        time.sleep(5)

if __name__ == "__main__":
    ip_taxi = input("Ingrese la IP del taxi: ")
    puerto_taxi = int(input("Ingrese el puerto del taxi: "))
    sensor_id = input("Ingrese el ID del sensor: ")
    
    sensor_cliente(ip_taxi, puerto_taxi, sensor_id)
