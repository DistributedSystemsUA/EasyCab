from path_load import *

import socket
from kafka import KafkaConsumer,KafkaProducer
import engine
import entities
import threading
import time
import argparse
import sqlite3
from random import randint

from confluent_kafka.admin import AdminClient

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
    global idClientes

    conn = sqlite3.connect('EasyCab.db')
    cursor = conn.cursor()

    consumer = KafkaConsumer(
        'clientes',
        bootstrap_servers= ip,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='cargar_Cliente'
    )

    producer = KafkaProducer(bootstrap_servers= ip)

    for message in consumer:
        peticion= f"{message.value.decode('utf-8')}"

        datos = peticion.strip().split()
        print(datos[1])
        if datos[1] == "Todas_las_peticiones_completadas":
            for i in idClientes:
                if i[0] == datos[0]:
                    taxi = engine.gameMap.entities.get(i[1])
                    engine.gameMap.removeEntity(taxi)
                    idClientes.remove(i)

        if peticion != "" and datos[1] != "Todas_las_peticiones_completadas":
            cursor.execute("SELECT ID FROM Posicion WHERE ID = ?", (datos[1],))
            ids = cursor.fetchone()
            cursor.execute("SELECT ID FROM Taxis WHERE estado = ?", (0,))
            tx = cursor.fetchall()
            if ids[0] == datos[1] and len(tx) >= 1:
                time.sleep(2)
                producer.send(f'clientes{datos[0]}', ("OK").encode('utf-8'))
                cursor.execute("SELECT x,y FROM Posicion WHERE ID = ?", (datos[1],))
                data = cursor.fetchone()
                if len(idClientes) == 0 or not(any(tupla[0] == datos[0] for tupla in idClientes)):
                    engine.gameMap.addEntities(entities.Client(entities.Position(randint(1,21), randint(1,21)), entities.Position(int(data[0]), int(data[1]))))
                    time.sleep(3)
                    todoslosCliente = [entity for entity in engine.gameMap.entities.values() if isinstance(entity, entities.Client)]
                    #print(len(todoslosCliente))
                    idClientes.append((datos[0],todoslosCliente[-1].id))
                else:
                    for cliente in idClientes:
                        if cliente[0] == datos[0]:
                            engine.gameMap.entities.get(cliente[1]).dst = entities.Position(int(data[0]), int(data[1]))
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

# Funcion saber cuando frenar los taxis
def paraTaxi(ip):
    global pararT

    insertar = True

    consumer = KafkaConsumer(
        'pararTaxi',
        bootstrap_servers= ip,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='cargar_Cliente'
    )
    for message in consumer:
        peticion= f"{message.value.decode('utf-8')}"
        datos = peticion.strip().split()
        for t in pararT:
            if t[1] == datos[1]:
                insertar = False

        if insertar == True:
            pararT.append([datos[0],datos[1]])

def moverTaxis(ip):
    global pararT
    global idClientes
    producer = KafkaProducer(bootstrap_servers= ip)

    asociacionClienteTaxi = []

    while engine.isRunning:
        taxis = [e for e in engine.gameMap.entities.values() if isinstance(e, entities.Taxi)]
        clientes_sin_taxi = [cliente for cliente in engine.gameMap.entities.values() if isinstance(cliente, entities.Client) and cliente.currentTaxi is None]
        
        for e in taxis:
            if e.currentClient is None and len(clientes_sin_taxi) > 0:
                cliente = clientes_sin_taxi.pop(0)
                e.assignClient(cliente)
                if e.currentClient is not None:
                    print(f"Taxi {e.id} ha tomado al cliente {chr(cliente.id)}")
                    asociacionClienteTaxi.append((e.id, e.currentClient.id))
                actualizar_estado_taxi(e.id, e.logType)
        
        l = [e for _, e in engine.gameMap.entities.items()]
        for e in l:
            if isinstance(e, entities.Taxi):
                for t in pararT:
                    if t[0] == 0:
                        pararT.remove(t)

                if any(t[1] == e.id for t in pararT):
                    e.stop()
                    for t in pararT:
                        if t[1] == e.id:
                            t[0] -= 1
                else:
                    e.move()

                actualizar_estado_taxi(e.id, e.logType)
                if e.logType == 0:
                    for CT in asociacionClienteTaxi:
                        if CT[0] == e.id:
                            print("entro servicio completo")
                            cli = [c for c in idClientes if c[1] == CT[1]]
                            producer.send(f'clientes{cli[0][0]}', ("Servicio Completado").encode('utf-8'))
                            asociacionClienteTaxi.remove(CT)
            time.sleep(1)
        

#-----------------------------------------------------------------------------------------------------------------
def main():
    # Configurar el cliente administrador de Kafka
    admin_client = AdminClient({
        "bootstrap.servers": args.kafka
    })

    nombres_taxis = [f"taxi{i}" for i in range(1, 100)]
    nombres_clientes = [f"clientes{i}" for i in range(1, 100)]

    # Combinar todos los topics (taxis y clientes)
    topics_to_delete = ["clientes","pararTaxi"] + nombres_taxis + nombres_clientes

    # Intentar eliminar los topics
    futures = admin_client.delete_topics(topics_to_delete)

    # Manejar posibles errores al borrar los topics
    for topic, future in futures.items():
        try:
            future.result()  # Esto lanza una excepción si hay un error
            print(f"Topic {topic} eliminado correctamente.")
        except Exception as e:
            pass
            #if "UNKNOWN_TOPIC_OR_PART" in str(e):
            #    print(f"El topic {topic} no existe. Continuando con el siguiente.")
            #else:
            #    print(f"Error inesperado al intentar eliminar el topic {topic}: {e}")

    cargarPosiciones()
    hilo_servidor = threading.Thread(target=servidor_central, args=(args.puerto_central,))
    hilo_servidor.start()
    hilo_cliente = threading.Thread(target=cargarClientes, args=(args.kafka,))
    hilo_cliente.start()
    hilo_pararT= threading.Thread(target=paraTaxi, args=(args.kafka,))
    hilo_pararT.start()
    moverTaxis(args.kafka)
    
if __name__ == "__main__":
    idClientes = []
    pararT = []

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

    
