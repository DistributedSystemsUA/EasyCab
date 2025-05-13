import socket
import argparse as argp
import random
import time
import threading

from common.net_instructions import *
from common.entities import *
from confluent_kafka import Consumer, Producer

#TODO: add values for default ports and addresses if needed on argparse
KAFKA_BROKER_TIMEOUT = 10.0
KAFKA_MAP_TOPIC = 'map-events'

CONNECTION_RETRY_TIME = 2.0

VALIDATION_ATTEMPS = 10
VALIDATION_RESPONSE_TIMEOUT = 5

cur_entity: Entity = None
close_application: bool = False
event_producer: Producer = None
event_consumer: Consumer = None


#TODO: change by API code (when finished v1)
def validateTaxi(taxi_id: int, net_params: tuple[str, int]):
    for i in range(VALIDATION_ATTEMPS):
        try:
            sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permitir reutilizar puerto
            sk.connect(net_params)
            sk.send(bytes([IS_TAXI_ID_OK, taxi_id]))
            sk.settimeout(VALIDATION_RESPONSE_TIMEOUT)
            response = skvalidator.recv(1)
            if response[0] == TAXI_ID_NOT_OK :
                print(f"The selected taxi id: {taxi_id} is incorrect and cannot login to de taxi database")
                exit(0)
            else:
                break # Validation ok
        except Exception as e:
            print(f"ATTEMP {i+1}: The taxi could not connect to the server {net_params}")
            if i == VALIDATION_ATTEMPS -1:
                exit(1)
            time.sleep(CONNECTION_RETRY_TIME)
        finally:
            sk.close()


def initSensor(net_params: tuple[str, int]):
    global close_application
    global event_producer
    for i in range(VALIDATION_ATEMPS):
        try:
            input_sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            input_sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            input_sk.connect(net_params)
            input_sk.settimeout(VALIDATION_RESPONSE_TIMEOUT)
        except Exception as e:
            print(f"ERROR: the Taxi couldn't connect to the sensor. Connect the sensor")
            if i == VALIDATION_ATTEMPS -1 :
                close_application = True
                exit(1)
            time.sleep(CONNECTION_RETRY_TIME)

    try:
        input_sk.settimeout(None)
        while not close_application :
            stop_time = input_sk.recv(1)
            if not stop_time:
                close_application = True
                continue
            #TODO: use producer to make the event public
            #TODO: catch specific exceptions and the KeyboardInterrupt for the better
    except Exception as e:
        print(str(e))
        close_application = True
    finally:
        input_sk.close()
        exit(0)


def startService():
    global event_producer
    global close_application
    global cur_entity
    #TODO: if sensor inconvenience: set the Entity state to LogType.Inconvenience


def readMapEvents():
    global event_consumer
    global close_application
    global cur_entity



if __name__ == "__main__":
    global event_consumer
    global event_producer
    global cur_entity

    parser = argp.ArgumentParser(description="Client application for Taxi's digital engine")
    parser.add_arguments("--srv", help="ip:port of the validation server", default="localhost:9091")
    parser.add_arguments("--bootstrap-srv", help="ip:port of the event queue server", default="localhost:9092")
    parser.add_arguments("--sensor", help="ip:port of the sensor", default="localhost:9093")
    parser.add_arguments("--id", help="number from 1 to 99 to assign to the taxi", default=str(random.randInt(1, 99)))

    args = parser.parse_args()
    validateTaxi(int(args.id), _makeNetParams(args.srv))
    cur_entity = Entity(int(args.id), 1, 1, EnType.Taxi)

    producer_conf = { 'bootstrap.servers' : args.bootstrap_srv }
    consumer_conf = {
            'bootstrap.servers' : args.bootstrap_srv,
            # ommited 'group.id' for the moment
            'auto.offset.reset' : 'earliest'
            }

    event_producer = Producer(producer_conf)
    event_consumer = Consumer(consumer_conf)
    event_consumer.subscribe([KAFKA_MAP_TOPIC])

    sensor_thread = threading.Thread(target=initSensor, params=(_makeNetParams(args.sensor),))
    service_thread = threading.Thread(target=startService)

    sensor_thread.start()
    service_thread.start()
    readMapEvents()


def _makeNetParams(params: str) -> tuple[str,int]:
    net_params = params.split(":")
    net_params[1] = int(net_params[1])
    return tuple(net_params)
