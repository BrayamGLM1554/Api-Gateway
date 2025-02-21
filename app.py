import os
import falcon
import pymssql
from api.resources import LoginResource

# Configuración de la conexión a la base de datos usando pymssql
def get_db_connection():
    try:
        conn = pymssql.connect(
            server=os.getenv('DB_SERVER', 'sql.bsite.net'),
            user=os.getenv('DB_USER', 'lenn343_'),
            password=os.getenv('DB_PASSWORD', '!@#qwerty123'),
            database=os.getenv('DB_NAME', 'lenn343_')
        )
        return conn
    except pymssql.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        exit(1)

# Crear la aplicación Falcon
app = falcon.App()

# Crear una instancia del recurso de login con la conexión a la base de datos
login_resource = LoginResource(get_db_connection())

# Agregar la ruta para el login
app.add_route('/login', login_resource)

# Ejecutar la aplicación con Gunicorn en Render
if __name__ == '__main__':
    from wsgiref import simple_server
    httpd = simple_server.make_server('0.0.0.0', 8000, app)
    print("Servidor corriendo en http://0.0.0.0:8000")
    httpd.serve_forever()
