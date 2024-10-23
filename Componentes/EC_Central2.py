import socket
import sqlite3

# Constantes para el protocolo
STX = '\x02'
ETX = '\x03'
ACK = '\x06'
NACK = '\x15'

# Calcula LRC (XOR de todos los bytes del mensaje)
def calcular_lrc(mensaje):
    lrc = 0
    for char in mensaje:
        lrc ^= ord(char)
    return chr(lrc)

# Función para desempaquetar y verificar mensajes
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

def manejar_taxi(conexion, direccion):
    print(f"Autenticando taxi desde {direccion}...")
    mensaje = conexion.recv(1024).decode('utf-8')
    
    data, valido = desempaquetar_mensaje(mensaje)
    if valido:
        print(f"Taxi autenticado correctamente con ID: {data}")
        conexion.send(ACK.encode('utf-8'))
    else:
        print("Error en el mensaje, enviando NACK.")
        conexion.send(NACK.encode('utf-8'))
    conexion.close()

def ec_central():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('0.0.0.0', 8888))  # Puerto para EC_Central
    servidor.listen(5)
    print("EC_Central esperando taxis...")
    
    while True:
        conexion, direccion = servidor.accept()
        manejar_taxi(conexion, direccion)

if __name__ == "__main__":
    ec_central()
