# Morpheus AI - Pod Gateway de Ficheros

Este repositorio contiene el código y la configuración para desplegar el **Pod Gateway de Ficheros** del proyecto Morpheus AI Suite.

## Propósito

Este pod actúa como un puente estable y persistente entre la aplicación local del usuario y el almacenamiento en red de RunPod (`Network Volume`). Sus responsabilidades son:

-   **Gestionar subidas:** Recibir archivos desde el cliente local y guardarlos en el almacenamiento compartido.
-   **Gestionar descargas:** Servir los archivos generados por los workers serverless para que el cliente local pueda descargarlos.
-   **Limpieza:** Eliminar directorios de trabajos cuando ya no son necesarios.

Funciona con una instancia de **CPU-only** para minimizar los costes, ya que no realiza ninguna tarea de IA.

## Despliegue Automatizado

Para desplegar este pod, sigue los siguientes pasos en la interfaz de RunPod:

1.  **Ve a `My Pods`** y haz clic en `+ New Pod`.
2.  **Elige una máquina `CPU`**. La opción más económica es suficiente (ej: "Community Cloud" con 2 vCPU y 8 GB de RAM).
3.  **Configura el Almacenamiento:**
    -   **Volume:** Selecciona el mismo `Network Volume` que utilizan tus workers serverless.
    -   **Volume Mount Path:** Asegúrate de que esté montado en `/runpod-volume`.
4.  **Configura la Plantilla (Template):**
    -   **Docker Image Name:** `runpod/base:0.7.0-ubuntu20.04`
    -   **Port:** Expón el puerto `8000`.
5.  **Pega el siguiente comando** en el campo **`Container Start Command`**:
    ```bash
    bash -c "rm -rf /workspace/fileserver && git clone https://github.com/ceutaseguridad/fileserver.git /workspace/fileserver && cd /workspace/fileserver && chmod +x pod_start.sh && ./pod_start.sh"
    ```
6.  **Despliega el pod.** El comando de inicio se encargará de toda la configuración automáticamente. Puedes ver el progreso en los logs del pod.

Una vez desplegado, el pod estará listo para recibir y servir archivos.
