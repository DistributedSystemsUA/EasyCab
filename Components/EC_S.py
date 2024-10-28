import socket
import time
from random import randint

BEL = 0x07
HOST = 'localhost' 
PORT = 9991

def socket_client():
    

    # Crear socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    try:
        while True:
            time.sleep(randint(3,5))
            if randint(0,1) == 0:
                client_socket.send(bytearray([BEL,randint(1,3)]))

    except KeyboardInterrupt:
        print("Cerrando conexión")
        client_socket.close()

if __name__ == "__main__":
    socket_client()

