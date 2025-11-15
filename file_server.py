# file_server.py (VERSIÓN FINAL Y COHERENTE)

import os
import shutil
from flask import Flask, request, jsonify, send_from_directory
import logging

# --- Configuración ---
VERSION = "1.1" # Versión actualizada
# --- [CAMBIO CLAVE 1] ---
# La base es el volumen, y el directorio de trabajo es 'job_outputs' para ser coherente con el worker.
BASE_STORAGE_PATH = "/workspace"
JOB_FILES_DIR = os.path.join(BASE_STORAGE_PATH, "job_outputs")

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')
logger = logging.getLogger('MorpheusGateway')

# Crear el directorio base si no existe al arrancar
os.makedirs(JOB_FILES_DIR, exist_ok=True)

app = Flask(__name__)

logger.info("==========================================================")
logger.info(f"==      MORPHEUS FILE GATEWAY v{VERSION} INICIADO         ==")
logger.info("==========================================================")
logger.info(f"Modo de operación: Activo y escuchando.")
logger.info(f"Ruta de almacenamiento gestionada: {JOB_FILES_DIR}")
logger.info("==========================================================")

# --- Endpoints de la API ---

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar que el servidor está vivo."""
    return jsonify({"status": "ok", "message": "File server is running."}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Maneja la subida de archivos. Los guarda en la carpeta coherente 'job_outputs'.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    worker_job_id = request.form.get('worker_job_id')
    if not worker_job_id:
        return jsonify({"error": "worker_job_id is required"}), 400
    try:
        # --- [CAMBIO CLAVE 2] ---
        # Usamos JOB_FILES_DIR en lugar del antiguo OUTPUTS_DIR
        job_directory = os.path.join(JOB_FILES_DIR, worker_job_id)
        os.makedirs(job_directory, exist_ok=True)
        
        save_path = os.path.join(job_directory, file.filename)
        file.save(save_path)
        logger.info(f"Archivo guardado: {save_path}")
        
        # La ruta devuelta también debe ser coherente
        pod_path = os.path.join("job_outputs", worker_job_id, file.filename)
        return jsonify({"message": "File uploaded successfully", "pod_path": pod_path, "worker_job_id": worker_job_id}), 201
    except Exception as e:
        logger.error(f"Error al subir el archivo: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@app.route('/download/<path:filepath>', methods=['GET'])
def download_file(filepath):
    """
    Sirve un archivo para su descarga desde la raíz del pod, que es donde el
    runpod_client construirá la ruta.
    """
    logger.info(f"Solicitud de descarga para: {filepath}")
    
    # La ruta completa que se busca en el disco. El file server se ejecuta desde '/'
    absolute_path = os.path.join("/", filepath)

    if not os.path.exists(absolute_path):
        logger.error(f"Archivo no encontrado en la ruta de descarga: {absolute_path}")
        return jsonify({"error": "File not found"}), 404

    directory = os.path.dirname(absolute_path)
    filename = os.path.basename(absolute_path)
    
    logger.info(f"Sirviendo archivo '{filename}' desde el directorio '{directory}'")
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/cleanup/<worker_job_id>', methods=['POST'])
def cleanup_job_files(worker_job_id):
    """
    Elimina el directorio completo asociado a un trabajo en 'job_outputs'.
    """
    logger.info(f"Solicitud de limpieza para el job ID: {worker_job_id}")
    
    # Probamos las dos rutas posibles debido a la dualidad /workspace vs /runpod-volume
    path1 = os.path.join("/runpod-volume/job_outputs", worker_job_id)
    path2 = os.path.join("/workspace/job_outputs", worker_job_id)

    job_directory = None
    if os.path.isdir(path1):
        job_directory = path1
    elif os.path.isdir(path2):
        job_directory = path2
    
    if not job_directory:
        logger.error(f"Directorio del trabajo no encontrado en ninguna de las rutas posibles: {path1} o {path2}")
        return jsonify({"error": "Job directory not found"}), 404

    try:
        shutil.rmtree(job_directory)
        logger.info(f"Directorio eliminado con éxito: {job_directory}")
        return jsonify({"message": f"Successfully cleaned up files for job {worker_job_id}"}), 200
    except Exception as e:
        logger.error(f"Error durante la limpieza de {job_directory}: {e}", exc_info=True)
        return jsonify({"error": f"Failed to cleanup directory: {e}"}), 500

# --- Bloque de Ejecución ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
