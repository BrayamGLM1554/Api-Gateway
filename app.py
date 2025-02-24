import os
import falcon
import pymysql
from api.resources import LoginResource

# Configuración de la conexión a la base de datos usando pymysql
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
        exit(1)

# Crear la aplicación Falcon
app = falcon.App()

# Crear una instancia del recurso de login con la conexión a la base de datos
login_resource = LoginResource(get_db_connection())

# Agregar la ruta para el login
app.add_route('/login', login_resource)

# Ejecutar la aplicación
if __name__ == '__main__':
    from waitress import serve
    print("Servidor corriendo en http://0.0.0.0:8000")
    serve(app, host='0.0.0.0', port=8000)