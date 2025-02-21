import falcon
from api.resources import LoginResource
import pyodbc
import os

# Configuración de la conexión a la base de datos
def get_db_connection():
    try:
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={os.getenv('DB_SERVER', 'sql.bsite.net\\MSSQL2016')};"
            f"DATABASE={os.getenv('DB_NAME', 'lenn343_')};"
            f"UID={os.getenv('DB_USER', 'lenn343_')};"
            f"PWD={os.getenv('DB_PASSWORD', '!@#qwerty123')};"
        )
        return pyodbc.connect(connection_string)
    except pyodbc.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        exit(1)

# Crear la aplicación Falcon
app = falcon.App()

# Crear una instancia del recurso de login con la conexión a la base de datos
login_resource = LoginResource(get_db_connection())

# Agregar la ruta para el login
app.add_route('/login', login_resource)

# Ejecutar la aplicación (usando WSGI)
if __name__ == '__main__':
    from wsgiref import simple_server
    httpd = simple_server.make_server('127.0.0.1', 8000, app)
    print("Servidor corriendo en http://0.0.0.0:8000")
    httpd.serve_forever()