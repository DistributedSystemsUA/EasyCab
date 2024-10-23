import socket
import threading

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

# Empaqueta el mensaje en el formato adecuado
def empaquetar_mensaje(data):
    mensaje = f"{STX}{data}{ETX}"
    lrc = calcular_lrc(mensaje)
    return mensaje + lrc

# Desempaqueta el mensaje y verifica el LRC
def desempaquetar_mensaje(mensaje):
    if mensaje[0] == STX and mensaje[-2] == ETX:
        data = mensaje[1:-2]  # Extraemos el DATA
        lrc_recibido = mensaje[-1]
        mensaje_completo = mensaje[:-1]  # Sin el LRC
        lrc_calculado = calcular_lrc(mensaje_completo)
        if lrc_recibido == lrc_calculado:
            return data, True
        else:
            return data, False
    return None, False

# Función para manejar la conexión del sensor
def manejar_sensor(conexion_sensor, direccion_sensor, taxi_id):
    print(f"Taxi {taxi_id} conectado con su sensor en {direccion_sensor}")
    
    while True:
        try:
            # Recibe el mensaje del sensor
            mensaje = conexion_sensor.recv(1024).decode('utf-8')
            if not mensaje:
                break
            
            data, valido = desempaquetar_mensaje(mensaje)
            if valido:
                print(f"Taxi {taxi_id} recibió del sensor: {data}")
                conexion_sensor.send(ACK.encode('utf-8'))  # Enviar ACK si el mensaje es válido
            else:
                print("Mensaje del sensor no válido. Enviando NACK.")
                conexion_sensor.send(NACK.encode('utf-8'))  # Enviar NACK si el mensaje es inválido
        except:
            print(f"Error en la conexión con el sensor de Taxi {taxi_id}.")
            break
    
    print(f"Conexión cerrada con el sensor del Taxi {taxi_id}.")
    conexion_sensor.close()

# Servidor para el taxi que escucha conexiones de su sensor
def taxi_servidor(ip_central, puerto_central, puerto_taxi, taxi_id):
    # Autenticarse con EC_Central
    autenticar_con_central(ip_central, puerto_central, taxi_id)
    
    # Crear el servidor que escuchará al sensor
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('0.0.0.0', puerto_taxi))
    servidor.listen(1)
    
    print(f"Taxi {taxi_id} esperando a su sensor en el puerto {puerto_taxi}...")
    conexion_sensor, direccion_sensor = servidor.accept()
    
    # Manejar la conexión del sensor en un bucle continuo
    manejar_sensor(conexion_sensor, direccion_sensor, taxi_id)

    # Función de autenticación con el EC_Central
def autenticar_con_central(ip_central, puerto_central, id_taxi):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((ip_central, puerto_central))
    
    # Empaquetar mensaje de autenticación
    mensaje = empaquetar_mensaje(f"REQUEST#{id_taxi}")
    cliente.send(mensaje.encode('utf-8'))
    
    respuesta = cliente.recv(1024).decode('utf-8')
    if respuesta == ACK:
        print(f"Taxi {id_taxi} autenticado correctamente con EC_Central")
    else:
        print(f"Autenticación fallida para Taxi {id_taxi}")
    cliente.close()

if __name__ == "__main__":
    ip_central = input("Ingrese la IP de EC_Central: ")
    puerto_central = int(input("Ingrese el puerto de EC_Central: "))
    puerto_taxi = int(input("Ingrese el puerto para este taxi: "))
    taxi_id = input("Ingrese el ID del taxi: ")
    
    taxi_servidor(ip_central, puerto_central, puerto_taxi, taxi_id)