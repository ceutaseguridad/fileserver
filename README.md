# Morpheus AI - Pod Gateway de Ficheros

Este repositorio contiene el código y la configuración para desplegar el Pod Gateway de Ficheros del proyecto Morpheus AI Suite.

## Propósito

Este pod actúa como un puente estable y persistente entre la aplicación local del usuario y el almacenamiento en red de RunPod (Network Volume). Sus responsabilidades son:

-   **Gestionar subidas:** Recibir archivos desde el cliente local y guardarlos en el almacenamiento compartido.
-   **Gestionar descargas:** Servir los archivos generados por los workers serverless para que el cliente local pueda descargarlos.
-   **Limpieza:** Eliminar directorios de trabajos cuando ya no son necesarios.

Funciona con una instancia de CPU-only para minimizar los costes, ya que no realiza ninguna tarea de IA.

## Despliegue Automatizado

Para desplegar este pod, sigue los siguientes pasos en la interfaz de RunPod:

1.  Ve a `My Pods` y haz clic en `+ New Pod`.
2.  Elige una máquina **CPU**. La opción más económica es suficiente (ej: "Community Cloud" con 2 vCPU y 8 GB de RAM).
3.  **Configura el Almacenamiento:**
    -   **Volume:** Selecciona el mismo Network Volume que utilizan tus workers serverless.
    -   **Volume Mount Path:** Asegúrate de que esté montado en `/workspace`.
        -   **¡Este paso es crítico!** Es la fuente de la "dualidad de rutas". Este pod **DEBE** montar el volumen en `/workspace`.

4.  **Configura la Plantilla (Template):**
    -   **Docker Image Name:** `runpod/base:0.7.0-ubuntu20.04`
    -   **Port:** Expón el puerto `8000`.
    -   Pega el siguiente comando en el campo **Container Start Command**:
        ```bash
        bash -c "rm -rf /workspace/fileserver && git clone https://github.com/ceutaseguridad/fileserver.git /workspace/fileserver && cd /workspace/fileserver && chmod +x pod_start.sh && ./pod_start.sh"
        ```
5.  Despliega el pod. El comando de inicio se encargará de toda la configuración automáticamente. Puedes ver el progreso en los logs del pod.

Una vez desplegado, el pod estará listo para recibir y servir archivos.

---

## Lógica Final y Puntos Clave (A Fuego)

Esta sección documenta el conocimiento esencial para entender y depurar este servicio.

### 1. La Dualidad de Rutas: `/workspace`

-   Este Pod Persistente ve el volumen de almacenamiento de red montado en la ruta `/workspace`.
-   El Worker Serverless, en cambio, ve este **mismo volumen** en la ruta `/runpod-volume`.
-   El `file_server.py` está programado para buscar y servir archivos partiendo de que el volumen está en `/workspace`. Por este motivo, el cliente local debe "traducir" las rutas que recibe del worker (`/runpod-volume/...`) a rutas que este servidor entienda (`/workspace/...`) antes de solicitar una descarga.

### 2. Lógica del `file_server.py`

-   **Base de Operaciones:** El script utiliza `/runpod-volume` como la ruta base para crear y eliminar carpetas, ya que es la ruta canónica del volumen. Sin embargo, gracias a la dualidad, estas operaciones se reflejan en `/workspace`.
-   **Endpoint de Descarga `/download/<path:filepath>`:**
    -   Esta es una **ruta de API**, no una carpeta real.
    -   El servidor espera recibir la ruta completa al archivo dentro del contenedor, por ejemplo: `workspace/job_outputs/ID_DEL_TRABAJO/imagen.png`.
    -   La lógica interna del endpoint es robusta y comprueba la existencia del archivo tanto en `/runpod-volume/...` como en `/workspace/...` para asegurar la compatibilidad.
-   **Coherencia de Directorios:** Todas las operaciones (subida, descarga, limpieza) están estandarizadas para usar el directorio `job_outputs` dentro del volumen, que es el mismo directorio que utiliza el Worker Serverless.
