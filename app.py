import os
import falcon
import pymysql
from dotenv import load_dotenv
from falcon_cors import CORS
from common.auth_tokens import active_tokens
from api.resources import LoginResource
from maps_api.maps import MapsResource
from maps_api.map_loader import MapLoaderResource
from gateway_api.gateway import GatewayResource
from gateway_api.auth import AuthMiddleware
from soap_api.proveedores import ProveedorResource
from soap_api.generar_token import GenerarTokenResource
from common.error_handler import handle_exception, handle_http_error
from common.metrics_middleware import MetricsMiddleware
from metrics.metrics_resource import MetricsResource
from common.rate_limit import RateLimitMiddleware

# Cargar variables de entorno
load_dotenv()

# 🛠Configuración del pool de conexiones
class Database:
    def __init__(self):
        self.pool = None
        self.create_pool()

    def create_pool(self):
        try:
            self.pool = pymysql.connect(
                host=os.getenv('DB_HOST'),
                port=int(os.getenv('DB_PORT', 3306)),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME'),
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
        except pymysql.Error as e:
            raise RuntimeError(f"Error al conectar a la base de datos: {e}")

    def get_connection(self):
        return self.pool

db = Database()

# CORS completamente abierto
cors_abierto = CORS(
    allow_all_origins=True,
    allow_all_headers=True,
    allow_all_methods=True
)

# Middleware de métricas
metrics_middleware = MetricsMiddleware()

# Middlewares globales
app = falcon.App(
    middleware=[
        cors_abierto.middleware,                   # 🔓 CORS abierto globalmente
        AuthMiddleware(active_tokens),             # Seguridad: tokens JWT
        metrics_middleware,                        # Monitoreo: tiempo, errores, rutas
        RateLimitMiddleware(limit=20, window=60),  # Protección: Rate Limiting global por IP
    ]
)

# Manejadores de errores globales
app.add_error_handler(Exception, handle_exception)
app.add_error_handler(falcon.HTTPError, handle_http_error)

# Instancias de recursos
login_resource = LoginResource(db.get_connection(), active_tokens)
map_loader_resource = MapLoaderResource()
maps_resource = MapsResource(active_tokens, map_loader_resource)
gateway_sucursales = GatewayResource("sucursales")
gateway_proveedores = GatewayResource("proveedores")
gateway_almacen = GatewayResource("almacen")
gateway_activofijo = GatewayResource("activofijo")
gateway_reconocimiento = GatewayResource("reconocimiento")
proveedor_resource = ProveedorResource()
generar_token_resource = GenerarTokenResource(active_tokens)
metrics_resource = MetricsResource(metrics_middleware)

# Rutas con CORS abierto
app.add_route('/login', login_resource)
app.add_route('/maps_api/maps', maps_resource)
app.add_route('/maps_api/load_map', map_loader_resource)
app.add_route("/gateway/sucursales", gateway_sucursales)
app.add_route("/gateway/sucursales/{id}", gateway_sucursales)
app.add_route("/gateway/proveedores", gateway_proveedores)
app.add_route("/gateway/proveedores/{id}", gateway_proveedores)
app.add_route("/gateway/almacen", gateway_almacen)
app.add_route("/gateway/almacen/{id}", gateway_almacen)
app.add_route("/gateway/activofijo", gateway_activofijo)
app.add_route("/gateway/activofijo/{id}", gateway_activofijo)
app.add_route("/gateway/reconocimiento", gateway_reconocimiento)
app.add_route('/api/generar_token', generar_token_resource)
app.add_route('/metrics', metrics_resource)
app.add_route('/api/soap/proveedores', proveedor_resource)

# Servidor local
if __name__ == '__main__':
    from waitress import serve
    print("servidor corriendo en ")
    serve(app, host='0.0.0.0', port=8000)
