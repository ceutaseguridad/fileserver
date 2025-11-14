#!/bin/bash
# pod_start.sh para el Pod Gateway de Ficheros (Fileserver)
# VERSIÓN DEFINITIVA Y COMPLETA
set -e

# --- [CORRECCIÓN DE RUTA] ---
# Navegamos al directorio de trabajo donde RunPod clona el repositorio.
cd /workspace/fileserver

echo "--- [Morpheus Gateway] Iniciando script de configuración (Gunicorn Mode) ---"

# --- PASO 1: Actualizar sistema e instalar dependencias base ---
# (Esta sección se mantiene como estaba en el original)
echo "--- [Morpheus Gateway] Actualizando paquetes e instalando git y pip... ---"
apt-get update -y && apt-get install -y git python3-pip

# --- PASO 2: Crear la estructura de directorios en el volumen de red ---
# (Esta sección se mantiene como estaba en el original)
echo "--- [Morpheus Gateway] Asegurando la estructura de carpetas en /runpod-volume/morpheus_storage... ---"
BASE_DIR="/runpod-volume/morpheus_storage"
mkdir -p "$BASE_DIR/outputs"
mkdir -p "$BASE_DIR/assets/influencer_pids"
mkdir -p "$BASE_DIR/assets/reference_images"
mkdir -p "$BASE_DIR/assets/audio_voices"
mkdir -p "$BASE_DIR/temp"
echo "--- [Morpheus Gateway] Estructura de carpetas verificada."

# --- PASO 3: Instalar las dependencias de Python ---
# (Esta sección se mantiene como estaba en el original)
echo "--- [Morpheus Gateway] Instalando dependencias de Python desde requirements_pod.txt... ---"
python3 -m pip install -r requirements.txt

# --- PASO 4: Lanzar el servidor de ficheros con Gunicorn ---
# (Esta es la única línea modificada respecto al original)
echo "--- [Morpheus Gateway] ¡Configuración completa! Lanzando el servidor con Gunicorn... ---"
exec gunicorn --workers 4 --bind 0.0.0.0:8000 file_server:app
