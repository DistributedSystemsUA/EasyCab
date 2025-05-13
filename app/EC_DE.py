import socket
import argparse as argp
import random
import time

from common.net_instructions import *
from common.entities import *
from confluent_kafka import Consumer, Producer

#TODO: change the default port to something set in common.__init__.py to import from common
KAFKA_BROKER_TIMEOUT = 10.0

CONNECTION_RETRY_TIME = 2.0

VALIDATION_ATTEMPS = 10
VALIDATION_RESPONSE_TIMEOUT = 5

cur_entity: Entity = None


#TODO: change by API code (when finished v1)
def validateTaxi(taxi_id: int, net_params: tuple[str, int]) -> bool:
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
                return False
            else:
                break
        except Exception as e:
            print(f"ATTEMP {i+1}: The taxi could not connect to the server {net_params}")
            if i == VALIDATION_ATTEMPS -1 :
                return False
            time.sleep(CONNECTION_RETRY_TIME)
        finally:
            sk.close()
    return True


def initSensor(net_params: tuple[str, int]):
    #TODO: set sensor connection attemps (or make a function that returns a connected socket)
    for i in range(VALIDATION_ATEMPS):
    try:
        input_sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        input_sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        input_sk.connect(net_params)
        input_sk.settimeout(VALIDATION_RESPONSE_TIMEOUT)
    except Exception as e:
        print(f"ERROR: the Taxi couldn't connect to the sensor. Ensure the sensor is connected.")
        time.sleep(CONNECTION_RETRY_TIME)


def startService(taxi_id: int, net_params: tuple[str,int]):
    pass


if __name__ == "__main__":
    parser = argp.ArgumentParser(description="Client application for Taxi's digital engine")
    parser.add_arguments("--srv", help="ip:port of the validation server", default="localhost:9091")
    parser.add_arguments("--bootstrap-srv", help="ip:port of the event queue server", default="localhost:9092")
    parser.add_arguments("--sensor", help="ip:port of the sensor", default="localhost:9093")
    parser.add_arguments("--id", help="number from 1 to 99 to assign to the taxi", default=str(random.randInt(1, 99)))

    args = parser.parse_args()
    if not validateTaxi(int(args.id), _makeNetParams(args.srv)) :
        exit(1)

    initSensor(_makeNetParams(args.sensor))
    #TODO: the main thread will consume events, while another thread will produce them
    startService(int(args.id), _makeNetParams(args.bootstrap_srv))


def _makeNetParams(params: str) -> tuple[str,int]:
    net_params = params.split(":")
    net_params[1] = int(net_params[1])
    return tuple(net_params)
