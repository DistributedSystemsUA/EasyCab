import socket
import argparse as argp

from common.net_instructions import *
from common.entities import *
from confluent_kafka import Consumer, Producer

NET_TIMEOUT = 10.0

own_data: Entity = None


#TODO: change the default port to something set in common.__init__.py to import from common

if __name__ == "__main__":
    parser = argp.ArgumentParser(description="Client application for Taxi's digital engine")
    parser.add_arguments("--ip", help="Ipv4 where to connect to the validation server", default="localhost")
    parser.add_arguments("--port", help="Port where to connect to the validation server", default="9091")

    #TODO: main thread will be consuming map events with a consumer
    #TODO: secondary thread will be Producing the taxi events
