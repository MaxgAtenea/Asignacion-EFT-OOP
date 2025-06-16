import os
from datetime import datetime

def exportar_log_errores(errores: list[str], nombre_archivo_log: str = "validacion.log") -> None:
    """
    Exporta una lista de errores a un archivo de log en ../output/logs/.

    Parámetros:
        errores (list): Lista de strings con mensajes de error.
        nombre_archivo_log (str): Nombre del archivo a crear o modificar.
    """
    if not errores:
        return  # Nada que exportar

    # Crear directorio si no existe
    ruta_logs = os.path.join("..", "output", "logs")
    os.makedirs(ruta_logs, exist_ok=True)

    # Ruta completa del log
    ruta_completa = os.path.join(ruta_logs, nombre_archivo_log)

    # Escribir errores en el archivo
    with open(ruta_completa, "a", encoding="utf-8") as log_file:
        log_file.write(f"\n--- LOG DE VALIDACIÓN ({datetime.now()}): ---\n")
        for error in errores:
            log_file.write(f"- {error}\n")
        print(f"Los errores quedaron logeados en: {ruta_completa}")
