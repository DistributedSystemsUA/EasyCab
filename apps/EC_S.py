import socket
import argparse
import time
from random import randint

BEL = 0x07
HOST = 'localhost' 

def socket_client():
    # Crear socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, args.puerto))
    print("Conectado con taxi")
    try:
        while True:
            # Verificar si el servidor ha cerrado la conexión
            try:
                data = client_socket.recv(1, socket.MSG_PEEK)
                if len(data) == 0:
                    print("El servidor ha cerrado la conexión. Cerrando el cliente.")
                    break
            except BlockingIOError:
                # La operación no está lista aún, continuar
                pass
            
            time.sleep(randint(6,10))
            if randint(0,1) == 0:
                tiempo = randint(1,3)
                client_socket.send(bytearray([BEL,tiempo]))
                print(f"Pausate: {tiempo} segundos")

    except KeyboardInterrupt:
        print("Cerrando conexión")
        client_socket.close()

    except Exception as e:
        print(f"Cerrando conexión por {e}")
        client_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('puerto', type=int)

    args = parser.parse_args()

    socket_client()


