#!/bin/bash
# Este script automatiza la configuración completa del Pod Gateway de Ficheros de Morpheus.
set -e

echo "--- [Morpheus Gateway] Iniciando script de configuración ---"

# --- PASO 1: Actualizar sistema e instalar dependencias base ---
echo "--- [Morpheus Gateway] Actualizando paquetes e instalando git y pip... ---"
apt-get update -y && apt-get install -y git python3-pip

# --- PASO 2: Clonar el repositorio del servidor de ficheros ---
# [CORRECCIÓN] Se elimina el directorio si ya existe para asegurar una copia limpia en cada reinicio.
echo "--- [Morpheus Gateway] Clonando el repositorio del servidor (asegurando una copia limpia)... ---"
rm -rf /workspace/fileserver
git clone https://github.com/ceutaseguridad/fileserver.git /workspace/fileserver

# --- PASO 3: Crear la estructura de directorios en el volumen de red ---
echo "--- [Morpheus Gateway] Asegurando la estructura de carpetas en /runpod-volume/morpheus_storage... ---"
BASE_DIR="/runpod-volume/morpheus_storage"
mkdir -p "$BASE_DIR/outputs"
mkdir -p "$BASE_DIR/assets/influencer_pids"
mkdir -p "$BASE_DIR/assets/reference_images"
mkdir -p "$BASE_DIR/assets/audio_voices"
mkdir -p "$BASE_DIR/temp"
echo "--- [Morpheus Gateway] Estructura de carpetas verificada."

# --- PASO 4: Instalar las dependencias de Python ---
echo "--- [Morpheus Gateway] Instalando dependencias de Python desde requirements.txt... ---"
python3 -m pip install -r /workspace/fileserver/requirements.txt

# --- PASO 5: Lanzar el servidor de ficheros ---
echo "--- [Morpheus Gateway] ¡Configuración completa! Lanzando el servidor Flask... ---"
# El `exec` reemplaza el proceso del script con el de python, una práctica más limpia.
exec python3 /workspace/fileserver/file_server.py
