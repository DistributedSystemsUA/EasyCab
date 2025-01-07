from path_load import *

import sys
import os
import threading
import json
import subprocess

import engine
import entities

import time
import socket
import argparse
from kafka import KafkaProducer,KafkaConsumer

from net_instructions import *

HOST = 'localhost'
BEL = 0x07
TOPIC = 'map-events'

service_enabled = True
current_entity: Taxi = None
central_communicator: KafkaProducer = None


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

def sensor2(kafka, id_taxi):
    global sensorA
    parado = False
    producer = KafkaProducer(bootstrap_servers=kafka)
    while True:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permitir reutilizar el puerto
        server_socket.bind((HOST, args.puerto))
        
        server_socket.listen(1)
        print(f"Servidor escuchando en {HOST}:{args.puerto}")

        conn, addr = None, None

        try:
            conn, addr = server_socket.accept()
            print(f"Conexión establecida con {addr}")
            sensorA = True
            if parado == True:
                producer.send("botones", bytearray([0x01]))
                parado = False

            while True:
                data = conn.recv(1024)
                if not data:
                    print("Cliente desconectado. Esperando nueva conexión...")
                    producer.send("botones", bytearray([0x01]))
                    print("Paso")
                    parado = True
                    break
                
                if data[0] == BEL:
                    producer.send('pararTaxi', (f"{data[1]} {id_taxi}").encode('utf-8'))
                    producer.flush()

        except KeyboardInterrupt:
            print("Cerrando servidor")
            break

        except Exception as e:
            print(f"Error en la conexión: {e}")
        
        finally:
            if conn:
                conn.close()
            server_socket.close()


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
def validarTaxi2(ip_central, puerto_central, id_taxi):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((f"{ip_central}", puerto_central))
    cliente.send(str(id_taxi).encode('utf-8'))
    
    try:
        while True:
            respuesta = cliente.recv(1024).decode('utf-8')
            if respuesta == "OK":
                print(f"Taxi {id_taxi} autenticado correctamente con EC_Central")
            else:
                print(f"Autenticación fallida para Taxi {id_taxi}")
                cliente.close()

    except Exception as e:
        print(f"Error con el taxi {id_taxi}: {e}")
    finally:
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

        if datos[0] == "Crear_Taxi":
            if int(datos[1]) not in engine.gameMap.entities:
                engine.gameMap.addEntities(entities.Taxi(int(datos[1]),entities.Position(1,1)))

        elif datos[0] == "Borrar_Cliente":
            if int(datos[1]) in engine.gameMap.entities:
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
        
        elif datos[0] == "BackB":
            e = engine.gameMap.entities[int(datos[1])]
            e.finishService(entities.Position(1,1))

        elif datos[0] == "GoD":
            e = engine.gameMap.entities[int(datos[1])]
            e.finishService(entities.Position(int(datos[2]),int(datos[3])))

        elif datos[0] == "Eliminar_Taxi":
            e = engine.gameMap.entities[int(datos[1])]
            engine.gameMap.removeEntity(e)
        
        elif datos[0] == "a_base":
            e = engine.gameMap.entities[int(datos[1])]
            e.finishService(entities.Position(1,1))

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
        orden = message.value  # Este es el diccionario deserializado
        identidad = orden["id"]
        ubicaciones = orden["ubicaciones"]  # Extraer la lista de diccionarios
        clientes = orden["clientes"]
        taxis = orden["taxis"]

        if identidad == args.id_taxi:
            print("CARGANDO MAPA...")
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
            sys.exit()
#----------------------------------------------------------------------------------------------------------

def _fast_consumer(topic: str) -> KafkaConsumer:
    global args
    return KafkaConsumer(INIT_TOPIC, bootstrap_servers=args.kafka, auto_offset_reset='earliest')


def _fast_producer(topic: str) -> KafkaProducer:
    global args
    return KafkaProducer(bootstrap_servers=args.kafka, acks=1, linger_ms=1, batch_size=100)


def _reloc_entity(msg: bytes, e_type: type):
    if (e := engine.gameMap.entities.get(msg[1])) is not None and (e.pos.x != msg[2] or e.pos.y != msg[3]):
        e.pos = 
        engine.gameMap.relocateEntity(
        engine.gameMap.relocateEntity(e, oldPos)


def _new_entity(msg: bytes) -> bool:
    enType = Taxi if msg[0] == NEW_TAXI else Client
    if engine.gameMap.entities.get(msg[1]) is not None:
        return False

    engine.gameMap.addEntities(enType(msg[1], Position(msg[2], msg[3])))
    return True


def _new_location(msg: bytes) -> bool:
    if engine.gameMap.locations.get(msg[0]) is not None:
        return False

    engine.gameMap.addLocations(Location(msg[1], Position(msg[2], msg[3])))
    return True


def _taxi_gets_client(msg: bytes):
    not_available = False
    if engine.gameMap.entities.get(msg[1]) is None:
        central_communicator.send(TOPIC, bytes([WHO_IS, msg[1]]))
        not_available = True

    if engine.gameMap.entities.get(msg[2]) is None:
        central_communicator.send(TOPIC, bytes([WHO_IS, msg[1]]))
        not_available = True

    if not_available:
        return

    engine.gameMap.entities[msg[1]].assignClient(engine.gameMap.entities[msg[2]])
    if not client_exists:
        central_communicator.send(TOPIC, bytes([WHO_IS, msg[1]]))


def _taxi_moves(msg: bytes):
    pass #TODO: When taxi moves, check for client to change condition in real time


def _update_map():
    map_events = _fast_consumer(TOPIC)
    INSTRUCTIONS = [_new_entity, _new_entity, _new_location,

    sync_lock = threading.Lock()
    for msg in map_events:
        sync_lock.acquire()
        #TODO: map sync code here
        #TODO: array of functions with the instructions
        sync_lock.release()


def start_service():
    global args
    global service_enabled
    global central_communicator

    map_updater = threading.Thread(target=_update_map)
    map_updater.start()

    sync_lock = threading.Lock()
    sync_lock.acquire()
    central_communicator.send(TOPIC, bytes(NEW_TAXI, engine.pointedEntity.id, engine.pointedEntity.pos.x, engine.pointedEntity.pos.y))
    sync_lock.release()

    while engine.isRunning:
        time.sleep(1)
        if service_enabled :
            sync_lock.acquire()
            engine.pointedEntity.move()
            central_communicator.send(TOPIC, bytes(
            sync_lock.release()
        # If not service enabled, there are some conditions with central communicator


#TODO: change by API code
def _remote_validate(taxi_id: int) -> bool:
    try:
        skvalidator = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skvalidator.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permitir reutilizar el puerto
        skvalidator.connect((args.ip_central, args.puerto_central))
        skvalidator.send(bytes([IS_TAXI_ID_OK, selected_id]))
        skvalidator.settimeout(5)
        response = skvalidator.recv(1)
        if response[0] == TAXI_ID_NOT_OK :
            return False
    except Exception as e:
        print(f"The taxi could not connect to the server: {e}")
        exit(1)
    finally:
        skvalidator.close()

    return True


def _request_valid_id() -> int:
    while selected_id <= 0 or selected_id > 99:
        try:
            selected_id = int(input("Introduzca su id de taxi: "))
        except:
            print("Que siii, que pongas un numero")
            selected_id = 0


def validate_taxi():
    global args
    global current_entity
    if args.taxi_id is None:
        args.taxi_id = _request_valid_id()

    while not _remote_validate(args.taxi_id):
        args.taxi_id = _request_valid_id()

    current_entity = Taxi(args.taxi_id, Position(1,1))
    engine.gameMap.addEntities(current_entity)
    engine.pointedEntity = current_entity


def sensor(client_sensors: socket.socket):
    global central_communicator
    global service_enabled
    sensor_lock = threading.Lock()
    try:
        while True:
            data = client_sensors.recv(2)

            service_enabled = False
            sensor_lock.acquire()
            central_communicator.send(TOPIC, bytes([SENSOR_INCONVENIENCE, current_entity.id]))
            sensor_lock.release()
            
            if not data:
                break # sensor disconnected
            if data[0] == BEL and data[1] > 0:
                time.sleep(int(data[1]))

            service_enabled = True
    except Exception as e:
        print(f"{e}")
    finally:
        print(f"WARNING: Los sensores han sido desconectados")
        client_sensors.close()


def init_sensor():
    global service_enabled
    global args
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permitir reutilizar el puerto
    srv.bind((HOST, args.puerto))
    subprocess.Popen(["$TERM", "-e", "python3", "EC_S.py", args.puerto]) # Sensores activados

    print(f"Buscando sensores")
    srv.listen()
    client_sensor, addr = server_socket.accept()
    print(f"Sensores conectados en {addr}")

    service_enabled = True
    receiver = threading.Thread(target=sensor, args=(client_sensor))
    receiver.start()


def parse_args():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument('ip_central', type=str, required=True)
    parser.add_argument('puerto_central', type=int, required=True)
    parser.add_argument('kafka', type=str, required=True)
    parser.add_argument('puerto', type=int, required=True)
    parser.add_argument('taxi_id', type=int, required=False)

    args = parser.parse_args()


def main():
    global args
    global central_communicator
    parse_args()

    central_communicator = _fast_producer(TOPIC)
    validate_taxi()
    init_sensor()
    start_service()
    # Conecta con central


if __name__ == "__main__":
    engine.start_passive(main, args.kafka)
