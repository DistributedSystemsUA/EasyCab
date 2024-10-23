import sqlite3
import socket

conexion = sqlite3.connect("EasyCab.db")

def leerFichero():
    fichero = open("Taxis.txt")
    print(fichero.readline())

def insertarTaxis():
    try:
        conexion.execute()

    except sqlite3.OperationalError:
        print("ERROR")
    conexion.close

leerFichero()

def manejar_taxi(conexion, direccion):
    print(f"Autenticando taxi desde {direccion}...")
    id_taxi = conexion.recv(1024).decode('utf-8')
    # Aquí se valida el ID del taxi (puede ser más complejo según tu lógica)
    if id_taxi:
        print(f"Taxi {id_taxi} autenticado correctamente")
        conexion.send("OK".encode('utf-8'))
    else:
        conexion.send("KO".encode('utf-8'))
    conexion.close()

def ec_central():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('0.0.0.0', 8888))  # Puerto para EC_Central
    servidor.listen(5)
    print("EC_Central esperando taxis...")
    
    while True:
        conexion, direccion = servidor.accept()
        manejar_taxi(conexion, direccion)

if __name__ == "__main__":
    ec_central()

