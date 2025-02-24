import os
import falcon
import pymysql
from resources import LoginResource

# Configuración de la conexión a la base de datos
def get_db_connection():
    try:
        conn = pymysql.connect(
            host=os.getenv('DB_HOST', 'sql.freedb.tech'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'freedb_brayam'),
            password=os.getenv('DB_PASSWORD', '8Z&DK2TVBW2MPfa'),
            database=os.getenv('DB_NAME', 'freedb_TrQuetz')
        )
        return conn
    except pymysql.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        raise falcon.HTTPInternalServerError('Database error', 'No se pudo conectar a la base de datos.')

# Crear la aplicación Falcon
app = falcon.App()

# Crear una instancia del recurso de login
login_resource = LoginResource(get_db_connection())

# Agregar la ruta para el login
app.add_route('/login', login_resource)

# Exportar la aplicación Falcon como un manejador WSGI
def handler(event, context):
    return app(event, context)
