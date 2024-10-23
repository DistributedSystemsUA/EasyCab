import subprocess
import sys
import os

def create_executable(script_name):
    try:
        # Verifica si PyInstaller está instalado
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])

        # Construye el comando para PyInstaller
        command = f'pyinstaller --onefile {script_name}'
        
        # Ejecuta el comando para crear el ejecutable
        subprocess.run(command, shell=True)
        
        # Imprime la ruta del archivo generado
        dist_path = os.path.join(os.getcwd(), 'dist', os.path.splitext(script_name)[0] + '.exe')
        print(f"Ejecutable generado en: {dist_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error durante la instalación de PyInstaller: {e}")

# Reemplaza 'mi_script.py' con el nombre de tu script Python
create_executable('producer.py')
