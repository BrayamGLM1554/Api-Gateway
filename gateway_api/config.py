import os

MICROSERVICIOS = {
    "sucursales": os.getenv("MS_SUCURSALES_URL", "https://sucursales-api.railway.app"),
    "proveedores": os.getenv("MS_PROVEEDORES_URL", "https://proveedores-api.railway.app"),
    "almacen": os.getenv("MS_ALMACEN_URL", "https://almacen-api.railway.app"),
    "activofijo": os.getenv("MS_ACTIVOFIJO_URL", "https://activofijo-api.railway.app"),
}

