import os
import falcon
import pymysql
from falcon_cors import CORS
from api.resources import LoginResource
from maps_api.maps import MapsResource, active_tokens
from maps_api.map_loader import MapLoaderResource
from gateway_api.gateway import GatewayResource
from gateway_api.auth import AuthMiddleware
from soap_api.proveedores import ProveedorResource
from soap_api.generar_token import GenerarTokenResource
from dotenv import load_dotenv

load_dotenv()

# Configuración del pool de conexiones a la base de datos
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
            print(f"Error al conectar a la base de datos: {e}")
            exit(1)

    def get_connection(self):
        return self.pool

# Instancia de la base de datos
db = Database()

# Configuración de CORS
allowed_origins = os.getenv('ALLOWED_ORIGINS', '*')
print(f"🚀 CARGADO ALLOWED_ORIGINS: {allowed_origins}")
if not allowed_origins:
    allowed_origins = '*'
allowed_origins_list = allowed_origins.split(',')
print(f"🚀 ORÍGENES PERMITIDOS: {allowed_origins_list}")


cors_restricted = CORS(allow_origins_list=allowed_origins_list, allow_all_headers=True, allow_all_methods=True)

# CORS completamente abierto solo para proveedores
cors_open = CORS(allow_all_origins=True, allow_all_headers=True, allow_all_methods=True)

# Crear la aplicación Falcon con CORS restringido y autenticación
app = falcon.App(middleware=[cors_restricted.middleware, AuthMiddleware()])

# Instancias de los recursos
login_resource = LoginResource(db.get_connection(), active_tokens)
map_loader_resource = MapLoaderResource()
maps_resource = MapsResource(active_tokens, map_loader_resource)
gateway_sucursales = GatewayResource("sucursales")
gateway_proveedores = GatewayResource("proveedores")
gateway_almacen = GatewayResource("almacen")
gateway_activofijo = GatewayResource("activofijo")

# Instancias de los recursos que requieren CORS abierto
proveedor_resource = ProveedorResource()
generar_token_resource = GenerarTokenResource(active_tokens)

# Definir rutas con CORS restringido
app.add_route('/login', login_resource)
app.add_route('/maps_api/maps', maps_resource)
app.add_route('/maps_api/load_map', map_loader_resource)
app.add_route("/gateway/sucursales", gateway_sucursales)
app.add_route("/gateway/proveedores", gateway_proveedores)
app.add_route("/gateway/almacen", gateway_almacen)
app.add_route("/gateway/activofijo", gateway_activofijo)

# Definir rutas con CORS abierto
app.add_route('/api/soap/proveedores', proveedor_resource)
app.add_route('/api/generar_token', generar_token_resource)

# Servidor con Waitress
if __name__ == '__main__':
    from waitress import serve
    print("Servidor corriendo en http://0.0.0.0:8000")
    serve(app, host='0.0.0.0', port=8000)
