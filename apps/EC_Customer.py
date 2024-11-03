from path_load import *

from kafka import KafkaConsumer,KafkaProducer
import time
import threading
import argparse
import json

import entities
import engine

def cargarPeticiones():
    global peticiones
    f = open('Peticiones'+ id + ".txt",'r')
    lineas = f.readlines()
    for linea in lineas:
        # Enviar un mensaje
        texto = linea.strip()
        peticiones.append(f"{id} {texto}")
        

def enviarMensajes(ind):
    global peticiones

    producer = KafkaProducer(bootstrap_servers= ip)
    if isinstance(ind, int):
        producer.send('clientes', peticiones[ind].encode('utf-8'))
    else:
        producer.send('clientes', f"{id} {ind}".encode('utf-8'))
    producer.flush()
    producer.close()

def recibirMensajes():
    global peticiones
    global ind

    en_curso = False
    direccion = ""

    consumer = KafkaConsumer(
        f'clientes{id}',
        bootstrap_servers= ip,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id=f'clientes_recibir{args.id}'
    )

    for message in consumer:
        print(f"Received message: {message.value.decode('utf-8')}")
        mens = message.value.decode('utf-8')
        if mens == "OK":
            if len(peticiones) != 0:
                direccion = peticiones.pop(ind)
                en_curso = True

        elif len(peticiones) > 0 and mens == "KO" and en_curso == False:
            time.sleep(4)
            ind += 1  # Incrementa el índice
            if ind >= len(peticiones):  # Verifica después de incrementar
                ind = 0  # Reinicia el índice si se sale del rango
            enviarMensajes(ind)
        
        elif mens == "Servicio Completado":
            print(f"El cliente ya ha llegado a {direccion}")
            en_curso = False

            if len(peticiones) == 0:
                print("Todas las peticiones completadas")
                enviarMensajes("Todas_las_peticiones_completadas")
                exit()
            else:
                time.sleep(4)
                if ind >= len(peticiones):  # Verifica después de incrementar
                    ind = 0  # Reinicia el índice si se sale del rango
                enviarMensajes(ind)

#----------------------------------------------------------------------------------------------------------
def carga_mapa():
    consumer = KafkaConsumer(
        'escucha_mapa',
        bootstrap_servers=args.kafka,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=f'clientes_recibir{args.id}Customer',
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
        group_id=f'clientes_recibir{args.id}Customer2',
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
    cargarPeticiones()
    Hilo_M = threading.Thread(target=recibirMensajes)
    enviarMensajes(0)
    Hilo_M.start()
    Hilo_Mapa = threading.Thread(target=escucha_mapa)
    Hilo_Mapa.start()
    Hilo_Mapa.join()  # Espera a que Hilo_M termine
    Hilo_M2 = threading.Thread(target=carga_mapa)
    Hilo_M2.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('id', type=str)
    parser.add_argument('kafka', type=str)

    args = parser.parse_args()

    ip = args.kafka
    id = args.id

    peticiones = []
    ind = 0
    
    engine.start(main)
    #main()