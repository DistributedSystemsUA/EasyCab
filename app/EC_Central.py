import json
from common import net_instructions

# APLICACION CENTRAL

# Modulo Validacion de Taxis

#Modulo Conexion de Cliente

def clientConexion(ip):
    consumer = KafkaConsumer(
            'clientes',
            bootstrap_servers= ip,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='clientes'
        )

    for message in consumer:
        
        pass

#Modulo Carga de Localizaciones
def localizationCharge():
    with open('localizations.json', 'r') as file:
        localizations = json.load(file)



# Main
if __name__ == "__main__":
    localizationCharge()