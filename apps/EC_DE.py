from path_load import *

import threading
import json

import engine
import entities

import time
import socket
import argparse
from kafka import KafkaProducer,KafkaConsumer

HOST = 'localhost'
#PORT = 9991

BEL = 0x07

def sensor(kafka,id_taxi):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, args.puerto))

    server_socket.listen(1)
    print(f"Servidor escuchando en {HOST}:{args.puerto}")

    conn, addr = server_socket.accept()
    print(f"Conexión establecida con {addr}")

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            if data[0] == BEL:
                producer = KafkaProducer(bootstrap_servers= kafka)
                producer.send('pararTaxi', (f"{data[1]} {id_taxi}").encode('utf-8'))
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

#----------------------------------------------------------------------------------------------------------
def carga_mapa():
    consumer = KafkaConsumer(
        'escucha_mapa',
        bootstrap_servers=args.kafka,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=f'clientes_recibir{args.id_taxi}Taxi',
    )

    for message in consumer:
        #time.sleep(4)
        mens = message.value.decode('utf-8')
        datos = mens.strip().split()

        print(datos[0],datos[1])

        if datos[0] == "Crear_Taxi":
            if int(datos[1]) not in engine.gameMap.entities:
                engine.gameMap.addEntities(entities.Taxi(int(datos[1]),entities.Position(1,1)))

        elif datos[0] == "Borrar_Cliente":
            cliente = engine.gameMap.entities.get(int(datos[1]))
            engine.gameMap.removeEntity(cliente)

        elif datos[0] == "Crear_Cliente":
            if int(datos[5]) not in engine.gameMap.entities:
                engine.gameMap.addEntities(entities.Client(entities.Position(int(datos[1]), int(datos[2])), entities.Position(int(datos[3]), int(datos[4]))))

        elif datos[0] == "Cambiar_Cliente":
            engine.gameMap.entities.get(int(datos[1])).dst = entities.Position(int(datos[2]), int(datos[3]))

        elif datos[0] == "Parar_taxi":
            e = engine.gameMap.entities[int(datos[1])]
            e.stop()

        elif datos[0] == "Mover_taxi":
            e = engine.gameMap.entities[int(datos[1])]
            e.move()
        
        elif datos[0] == "TaxiCogeCliente":
            e = engine.gameMap.entities[int(datos[1])]
            c = engine.gameMap.entities[int(datos[2])]
            e.assignClient(c)

def escucha_mapa():
    ubicaciones = []
    taxis = []
    clientes = []

    consumer = KafkaConsumer(
        'enviar_mapa',
        bootstrap_servers=args.kafka,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id=f'clientes_recibir{args.id_taxi}Taxi2',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    for message in consumer:
        print("Entro")
        orden = message.value  # Este es el diccionario deserializado
        ubicaciones = orden["ubicaciones"]  # Extraer la lista de diccionarios
        clientes = orden["clientes"]
        taxis = orden["taxis"]


        for u in ubicaciones:
            engine.gameMap.addLocations(entities.Location(ID=u["id"], pos=entities.Position(int(u["x"]), int(u["y"]))))

        for u in taxis:
            id_entidad = int(u["id"])
            # Verificar si la entidad ya existe
            if id_entidad not in engine.gameMap.entities:
                engine.gameMap.addEntities(entities.Taxi(int(u["id"]),entities.Position(int(u["x"]),int(u["y"]))))

        for c in clientes:
            id_entidad = c["id"]
            # Verificar si la entidad ya existe
            if id_entidad not in engine.gameMap.entities:
                engine.gameMap.addEntities(entities.Client(entities.Position(c["x_p"], c["y_p"]), entities.Position(int(c["x_d"]), int(c["y_d"]))))
        exit()
#----------------------------------------------------------------------------------------------------------

def main():
    validarTaxi(args.ip_central,args.puerto_central,args.id_taxi)
    engine.gameMap.addEntities(entities.Taxi(args.id_taxi,entities.Position(1,1)))
    engine.pointedEntity = engine.gameMap.entities[args.id_taxi]
    Hilo_M = threading.Thread(target=escucha_mapa)
    Hilo_M.start()
    Hilo_M.join()  # Espera a que Hilo_M termine
    Hilo_M2 = threading.Thread(target=carga_mapa)
    Hilo_M2.start()
    sensor(args.kafka,args.id_taxi)


if __name__ == "__main__":
     # Argumentos del programa
    parser = argparse.ArgumentParser()
    parser.add_argument('ip_central', type=str)
    parser.add_argument('puerto_central', type=int)
    parser.add_argument('id_taxi', type=int)
    parser.add_argument('kafka', type=str)
    parser.add_argument('puerto', type=int)

    args = parser.parse_args()

    args = parser.parse_args()
    
    engine.start_passive(main)
    #engine.start(main)
    

    
