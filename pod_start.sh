#!/bin/bash
# Este script automatiza la configuración completa del Pod Gateway de Ficheros de Morpheus.
# VERSIÓN CORREGIDA: Asume que el código ya ha sido clonado.
set -e

echo "--- [Morpheus Gateway] Iniciando script de configuración ---"

# --- PASO 1: Actualizar sistema e instalar dependencias base ---
echo "--- [Morpheus Gateway] Actualizando paquetes e instalando git y pip... ---"
apt-get update -y && apt-get install -y git python3-pip

# --- PASO 2: Crear la estructura de directorios en el volumen de red ---
echo "--- [Morpheus Gateway] Asegurando la estructura de carpetas en /runpod-volume/morpheus_storage... ---"
BASE_DIR="/runpod-volume/morpheus_storage"
mkdir -p "$BASE_DIR/outputs"
mkdir -p "$BASE_DIR/assets/influencer_pids"
mkdir -p "$BASE_DIR/assets/reference_images"
mkdir -p "$BASE_DIR/assets/audio_voices"
mkdir -p "$BASE_DIR/temp"
echo "--- [Morpheus Gateway] Estructura de carpetas verificada."

# --- PASO 3: Instalar las dependencias de Python ---
echo "--- [Morpheus Gateway] Instalando dependencias de Python desde requirements.txt... ---"
# Se asume que este script se ejecuta desde el directorio /workspace/fileserver
python3 -m pip install -r requirements.txt

# --- PASO 4: Lanzar el servidor de ficheros ---
echo "--- [Morpheus Gateway] ¡Configuración completa! Lanzando el servidor Flask... ---"
# El `exec` reemplaza el proceso del script con el de python, una práctica más limpia.
exec python3 file_server.py
