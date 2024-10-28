import socket
from kafka import KafkaConsumer,KafkaProducer
import engine
import entities
import threading
import time
import argparse
import sqlite3
from random import randint

global ip

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
        #Añade los taxis a la BD
        conn = sqlite3.connect('EasyCab.db')
        cursor = conn.cursor()
        
        # Insertar un nuevo taxi en la tabla Taxis
        cursor.execute('''
        INSERT INTO Taxis (ID,estado)
        VALUES (?, ?)
        ''', (int(data),0))
        
        # Guardar los cambios
        conn.commit()
        
        # Cerrar la conexión
        conn.close()

        producer = KafkaProducer(bootstrap_servers= ip)
        producer.send('imprimirT', (f"{data}").encode('utf-8'))
        producer.flush()
        producer.close()


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



def imprimirPosiciones(posiciones):
    pass
    

def escucha_clientes():
    #ip = input("Dame la ip que va a usar kafka: ")
    #ip += ":9092"

    conn = sqlite3.connect('EasyCab.db')
    cursor = conn.cursor()
    
    print(ip)

    consumer = KafkaConsumer(
        'clientes',
        bootstrap_servers= ip,
        auto_offset_reset='latest',
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
            cursor.execute("SELECT ID FROM Taxis WHERE estado = ?", (1,))
            tx = cursor.fetchall()
            if ids[0] == datos[1] and len(tx) >= 1:
                producer.send(f'clientes{datos[0]}', ("OK").encode('utf-8'))
                producer.send('imprimirC',(f"{datos[1]}").encode('utf-8'))
            else:
                producer.send(f'clientes{datos[0]}', ("KO").encode('utf-8'))
    
    producer.close()

def escucha_Taxi():
    pass

#------------------------------------------------------------------------------------------------------------
def servidor_central(puerto_central):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(("localhost", puerto_central))  # Se asocia a todas las interfaces disponibles en la máquina
    servidor.listen(5)
    print(f"EC_Central escuchando en el puerto {puerto_central}...")

    while True:
        conexion, direccion = servidor.accept()  # Acepta la conexión entrante
        print(f"Conexión establecida con {direccion}")

        id_taxi = conexion.recv(1024).decode('utf-8')  # Recibe el ID del taxi
        print(f"Recibido ID de taxi: {id_taxi}")

        #Añade los taxis a la BD
        conn = sqlite3.connect('EasyCab.db')
        cursor = conn.cursor()
        
        # Insertar un nuevo taxi en la tabla Taxis
        cursor.execute('''
        INSERT INTO Taxis (ID,estado)
        VALUES (?, ?)
        ''', (int(id_taxi),0))
        
        # Guardar los cambios
        conn.commit()
        conn.close()
        
        conexion.send("OK".encode('utf-8'))

        conexion.close()

        engine.gameMap.addEntities(entities.Taxi(int(id_taxi),entities.Position(1,1)))
#-----------------------------------------------------------------------------------------------------------------
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
                engine.gameMap.addLocations(entities.Location(ID=ord(data[0]), pos=entities.Position(int(data[1]), int(data[2]))))
            else:
                print(f"ID {data[0]} ya existe. No se inserta.")
    fichero.close()
    # Guardar los cambios y cerrar la conexión
    conn.commit()
    conn.close()
#-----------------------------------------------------------------------------------------------------------------
def cargarClientes(ip):
    conn = sqlite3.connect('EasyCab.db')
    cursor = conn.cursor()

    consumer = KafkaConsumer(
        'clientes',
        bootstrap_servers= ip,
        auto_offset_reset='latest',
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
            cursor.execute("SELECT ID FROM Taxis WHERE estado = ?", (0,))
            tx = cursor.fetchall()
            if ids[0] == datos[1] and len(tx) >= 1:
                producer.send(f'clientes{datos[0]}', ("OK").encode('utf-8'))
                cursor.execute("SELECT x,y FROM Posicion WHERE ID = ?", (datos[1],))
                data = cursor.fetchone()
                engine.gameMap.addEntities(entities.Client(entities.Position(randint(1,21), randint(1,21)), entities.Position(int(data[0]), int(data[1]))))
            else:
                producer.send(f'clientes{datos[0]}', ("KO").encode('utf-8'))
    
    producer.close()

#-----------------------------------------------------------------------------------------------------------------
# Función para actualizar el estado del taxi en la base de datos
def actualizar_estado_taxi(taxi_id, estado):
    conexion = sqlite3.connect('EasyCab.db')
    cursor = conexion.cursor()
    cursor.execute("UPDATE taxis SET estado = ? WHERE id = ?", (estado, taxi_id))
    conexion.commit()
    conexion.close()

def moverTaxis():
    while engine.isRunning:
        taxis = [e for e in engine.gameMap.entities.values() if isinstance(e, entities.Taxi)]
        clientes_sin_taxi = [cliente for cliente in engine.gameMap.entities.values() if isinstance(cliente, entities.Client) and cliente.currentTaxi is None]
        
        for e in taxis:
            if e.currentClient is None and len(clientes_sin_taxi) > 0:
                cliente = clientes_sin_taxi.pop(0)
                e.assignClient(cliente)
                print(f"Taxi {e.id} ha tomado al cliente {cliente.id}")
                
                actualizar_estado_taxi(e.id, 1)
        
        l = [e for _, e in engine.gameMap.entities.items()]
        for e in l:
            if isinstance(e, entities.Taxi):
                e.move()
            time.sleep(1)
        

#-----------------------------------------------------------------------------------------------------------------
def main():
    cargarPosiciones()
    hilo_servidor = threading.Thread(target=servidor_central, args=(puerto,))
    hilo_servidor.start()
    hilo_cliente = threading.Thread(target=cargarClientes, args=(args.kafka,))
    hilo_cliente.start()
    moverTaxis()
    
if __name__ == "__main__":
    connInit = sqlite3.connect('EasyCab.db')
    cursorInit = connInit.cursor()
    cursorInit.execute("DELETE FROM Taxis")
    cursorInit.execute("DELETE FROM Posicion")
    connInit.commit()
    connInit.close()
     # Argumentos del programa
    parser = argparse.ArgumentParser()
    parser.add_argument('kafka', type=str)
    parser.add_argument('ip_central', type=str)
    parser.add_argument('puerto_central', type=int)
    #parser.add_argument('bd', type=str)

    args = parser.parse_args()

    engine.start(main)  # Pasar la función 'main' sin ejecutarla directamente

    
