#Se conecta a la BD
#Paremetros de entrada PuertoEscucha, IP y Puerto Brocker.

#Se conecta, se queda en espera:

#Conforme vaya validando taxis, se autentifican en la bd y aparecen el mapa.
#Los clientes pueden ir haciendo peticiones haya taxis o no, pero claramente solo recibiran respuesta una vez que haya taxis.

#DEMO:
#Lo pongo en escucha y compruebo que le llegan correctamente los taxis y los clientes.
#Voy creando la BD y conforme vaya llegando los taxis los valido y cuando se desconecten los desvalido.
#Los clientes son mas simples por que la comprobacion es solo saber si estan intentando conectar.

import mariadb 
import sys

conn = mariadb.connect(
    user="Manuel",
    password="manmun",
    host="localhost",
    port = 3306,
    database="prueba")
cur = conn.cursor() 

# Conexión a la base de datos
try:
    #connection = mariadb.connect(**conn)
    print("Conexión exitosa a la base de datos")
    
    # Crear un cursor y ejecutar una consulta
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM TAXI")
    
    # Obtener y mostrar los resultados
    for row in cursor.fetchall():
        print(row)
        
    cursor.close()
    
except mariadb.Error as err:
    print(f"Error: {err}")
    sys.exit(1)
    
finally:
    if cur:
        cur.close()
        print("Conexión cerrada")