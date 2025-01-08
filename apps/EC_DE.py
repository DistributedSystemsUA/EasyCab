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

    if not_available: return

    engine.gameMap.entities[msg[1]].assignClient(engine.gameMap.entities[msg[2]])
    if not client_exists:
        central_communicator.send(TOPIC, bytes([WHO_IS, msg[1]]))


def _taxi_moves(msg: bytes):
    #TODO: check for every attribute to be ok and aligned with taxi condition, if something wrong, change in real time
    pass


def _update_map():
    map_events = _fast_consumer(TOPIC)
    INSTRUCTIONS = [_new_entity, _new_entity, _new_location, #TODO: finish instructions

    sync_lock = threading.Lock()
    sync_lock.acquire()
    central_communicator.send(TOPIC, bytes([REQUEST_MAP_INFO]))
    sync_lock.release()

    for msg in map_events:
        sync_lock.acquire()
        #TODO: map sync code here
        sync_lock.release()


def check_integrity(e_id: int, origin: tuple[int, int], dst: tuple[int, int ] = None) -> bool:
    if engine.gameMap.entities.get(e_id) is None:
        check_integrity.lock.acquire()
        central_communicator.send(TOPIC, bytes([WHO_IS, e_id]))
        check_integrity.lock.release()
        return False

    cur_e = engine.gameMap.entities.get(e_id)
    if cur_e.pos.toTuple() != origin:
        oldPos = cur_e.pos
        cur_e.pos = Position(*origin)
        engine.gameMap.relocateEntity(cur_e, oldPos)

    if dst and cur_e.dst.toTuple() != dst:
        pass #TODO: how to change the direction

    return True


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
            central_communicator.send(TOPIC, bytes([TAXI_MOVE, engine.pointedEntity.id, engine.pointedEntity.clientId(), *engine.pointedEntity.pos.toTuple()]))
            sync_lock.release()
        # If not service enabled, there are some conditions with central communicator

    sync_lock.acquire()
    central_communicator.send(TOPIC, bytes([TAXI_DISCONNECTED, engine.pointedEntity.id, engine.pointedEntity.clientId()]))
    sync_lock.release()


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

            if data[0] == BEL and data[1] > 0:
                sensor_lock.acquire()
                service_enabled = False
                central_communicator.send(TOPIC, bytes([SENSOR_INCONVENIENCE, current_entity.id]))
                sensor_lock.release()
                time.sleep(int(data[1]))

            if not data:
                break # sensor disconnected

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

    check_integrity.lock = threading.Lock()         # Function's static attribute
    central_communicator = _fast_producer(TOPIC)
    validate_taxi()
    init_sensor()
    start_service()
    # Conecta con central


if __name__ == "__main__":
    engine.start_passive(main, args.kafka)
