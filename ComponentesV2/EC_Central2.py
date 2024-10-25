import socket
from kafka import KafkaConsumer,KafkaProducer
from engine import *
import threading
import time
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

def cargarPosiciones():
    conn = sqlite3.connect('EasyCab.db')
    cursor = conn.cursor()
    fichero = open('mapaConf.txt','r')
    lineas = fichero.readlines()
    for linea in lineas:
        data = linea.strip().split()
        if (len(data) == 3):
            cursor.execute("SELECT COUNT(1) FROM Posicion WHERE ID = ?", (data[0],))
            if cursor.fetchone()[0] == 0:  # Si no existe, insertar
                cursor.execute("INSERT INTO Posicion (ID, x, y) VALUES (?, ?, ?)", (data[0], data[1], data[2]))
            else:
                print(f"ID {data[0]} ya existe. No se inserta.")
    fichero.close()
    # Guardar los cambios y cerrar la conexión
    conn.commit()
    conn.close()


def imprimirPosiciones(posiciones):
    pass
    

def escucha_clientes():
    ip = input("Dame la ip que va a usar kafka: ")
    ip += ":9092"

    conn = sqlite3.connect('EasyCab.db')
    cursor = conn.cursor()
    
    print(ip)

    consumer = KafkaConsumer(
        'clientes',
        bootstrap_servers= ip,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='my-group'
    )

    producer = KafkaProducer(bootstrap_servers= ip)

    for message in consumer:
        peticion= f"{message.value.decode('utf-8')}"
        datos = peticion.strip().split()

        if peticion != "":
            cursor.execute("SELECT ID FROM Posicion WHERE ID = ?", (datos[1],))
            ids = cursor.fetchone()
            if ids[0] == datos[1]:
                producer.send(f'clientes{datos[0]}', ("OK").encode('utf-8'))
                producer.send('imprimirC',(f"{datos[1]}").encode('utf-8'))
            else:
                producer.send(f'clientes{datos[0]}', ("KO").encode('utf-8'))
    
    producer.close()

def escucha_Taxi():
    pass


def main():
    cargarPosiciones()
        
    hilo_1 = threading.Thread(target=escucha_clientes)
    hilo_1.start()
    # Aquí podrías llamar a ec_central() si lo necesitas más adelante

if __name__ == "__main__":
    start(main())  # Pasar la función 'main' sin ejecutarla directamente

    
