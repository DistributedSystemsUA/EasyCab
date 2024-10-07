#Le paso una ID que lo identifique
#Espero a que se conecte con su sensor correspondiente
#Paso autentificacion a Central
import argparse
import requests
import time


def main():
    parser = argparse.ArgumentParser(description="Taxis")
    parser.add_argument("--ID", type=int, help="La ID del Taxi")
    args = parser.parse_args()

    print(f"Hola, {args.ID}.")

# Configura tu subdominio y token de DuckDNS
#SUBDOMAIN = 'pruebasdspractica1'  # Reemplaza con tu subdominio
#TOKEN = '0df02128-4445-43d7-bf8b-3ba42c2a797d'  # Reemplaza con tu token

#def update_duckdns():
#    url = f'https://www.duckdns.org/update?domains={SUBDOMAIN}&token={TOKEN}&ip='
#    #url = f'pruebasSDP1.giize.com'
#   response = requests.get(url)
#    print(response.text)  # Para ver la respuesta de DuckDNS

# Actualiza la IP cada 5 minutos
#while True:
#    update_duckdns()
#    time.sleep(300)  # Espera 5 minutos (300 segundos)


if __name__ == "__main__":
    main()