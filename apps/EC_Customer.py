from kafka import KafkaConsumer,KafkaProducer
import time
import threading
import argparse

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
        group_id='clientes_recibir'
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



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('id', type=str)
    parser.add_argument('kafka', type=str)

    args = parser.parse_args()

    ip = args.kafka
    id = args.id

    peticiones = []
    ind = 0
    cargarPeticiones()
    Hilo_M = threading.Thread(target=recibirMensajes)
    enviarMensajes(0)
    Hilo_M.start()