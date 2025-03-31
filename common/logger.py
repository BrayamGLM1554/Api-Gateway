import logging
import os

# Asegura la carpeta para logs de archivo
os.makedirs("logs", exist_ok=True)

# Crear logger
logger = logging.getLogger("API")
logger.setLevel(logging.INFO)

# Formato único para todos los destinos
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Log a consola (Railway captura stdout)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Log también a archivo (útil en local)
file_handler = logging.FileHandler("logs/api.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
