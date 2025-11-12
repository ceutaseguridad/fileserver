import os
import shutil
from flask import Flask, request, jsonify, send_from_directory
import logging

# --- Configuración ---
VERSION = "1.0"
BASE_STORAGE_PATH = "/runpod-volume/morpheus_storage"
OUTPUTS_DIR = os.path.join(BASE_STORAGE_PATH, "outputs")

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')
logger = logging.getLogger('MorpheusGateway')

# Crear los directorios base si no existen al arrancar
os.makedirs(OUTPUTS_DIR, exist_ok=True)

app = Flask(__name__)

# --- [NUEVO] Log de inicio para confirmar que el servidor está activo ---
logger.info("==========================================================")
logger.info(f"==      MORPHEUS FILE GATEWAY v{VERSION} INICIADO         ==")
logger.info("==========================================================")
logger.info(f"Modo de operación: Activo y escuchando.")
logger.info(f"Ruta de almacenamiento gestionada: {BASE_STORAGE_PATH}")
logger.info("==========================================================")

# --- Endpoints de la API ---

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar que el servidor está vivo."""
    return jsonify({"status": "ok", "message": "File server is running."}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Maneja la subida de archivos. Los guarda en una subcarpeta única
    basada en el ID del trabajo (worker_job_id).
    """
    # ... (El resto del código de la función no cambia)
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    worker_job_id = request.form.get('worker_job_id')
    if not worker_job_id:
        return jsonify({"error": "worker_job_id is required"}), 400
    try:
        job_directory = os.path.join(OUTPUTS_DIR, worker_job_id)
        os.makedirs(job_directory, exist_ok=True)
        save_path = os.path.join(job_directory, file.filename)
        file.save(save_path)
        logger.info(f"Archivo guardado: {save_path}")
        pod_path = os.path.join("outputs", worker_job_id, file.filename)
        return jsonify({"message": "File uploaded successfully", "pod_path": pod_path, "worker_job_id": worker_job_id}), 201
    except Exception as e:
        logger.error(f"Error al subir el archivo: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@app.route('/download/<path:filepath>', methods=['GET'])
def download_file(filepath):
    """
    Sirve un archivo para su descarga. La ruta completa se reconstruye
    a partir de la ruta relativa proporcionada.
    """
    # ... (El resto del código de la función no cambia)
    logger.info(f"Solicitud de descarga para: {filepath}")
    directory = os.path.join(BASE_STORAGE_PATH, os.path.dirname(filepath))
    filename = os.path.basename(filepath)
    if not os.path.exists(os.path.join(directory, filename)):
        logger.error(f"Archivo no encontrado en la ruta de descarga: {directory}/{filename}")
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/cleanup/<worker_job_id>', methods=['POST'])
def cleanup_job_files(worker_job_id):
    """
    Elimina el directorio completo asociado a un trabajo para limpiar espacio.
    """
    # ... (El resto del código de la función no cambia)
    job_directory = os.path.join(OUTPUTS_DIR, worker_job_id)
    logger.info(f"Solicitud de limpieza para el directorio: {job_directory}")
    if not os.path.isdir(job_directory):
        return jsonify({"error": "Job directory not found"}), 404
    try:
        shutil.rmtree(job_directory)
        logger.info(f"Directorio eliminado con éxito: {job_directory}")
        return jsonify({"message": f"Successfully cleaned up files for job {worker_job_id}"}), 200
    except Exception as e:
        logger.error(f"Error durante la limpieza: {e}", exc_info=True)
        return jsonify({"error": f"Failed to cleanup directory: {e}"}), 500

# --- Bloque de Ejecución ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
