import os
from dotenv import load_dotenv

MICROSERVICIOS = {
    "sucursales": os.getenv("MS_SUCURSALES_URL", "http://aleort-001-site1.ptempurl.com/api/Sucursal"),
    "proveedores": os.getenv("MS_PROVEEDORES_URL", "http://alemart-001-site1.ntempurl.com/api/Proveedor"),
    "almacen": os.getenv("MS_ALMACEN_URL", "http://alemart12-001-site1.mtempurl.com/api/Almacen"),
    "activofijo": os.getenv("MS_ACTIVOFIJO_URL", "http://alemart1-001-site1.ptempurl.com/api/ActivoFijo"),
    "reconocimiento": os.getenv("MS_RECONOCIMIENTO_URL", "http://totiquetzalcoatl.somee.com/Quetzalcoatl/api/Corn/analyze"),
}

