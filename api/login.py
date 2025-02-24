import os
import falcon
import pymysql
import jwt
from datetime import datetime, timedelta

# Clave secreta para firmar los tokens JWT (debería ser una variable de entorno en producción)
SECRET_KEY = "Quetzalcoatl_Project:1554"
TOKEN_EXPIRATION_MINUTES = 30  # Tiempo de expiración del token en minutos

# Configuración de la conexión a la base de datos usando pymysql
def get_db_connection():
    try:
        conn = pymysql.connect(
            host=os.getenv('DB_HOST', 'sql.freedb.tech'),  # Host de la base de datos
            port=int(os.getenv('DB_PORT', 3306)),         # Puerto de MySQL
            user=os.getenv('DB_USER', 'freedb_brayam'),   # Usuario de la base de datos
            password=os.getenv('DB_PASSWORD', '8Z&DK2TVBW2MPfa'),  # Contraseña
            database=os.getenv('DB_NAME', 'freedb_TrQuetz')  # Nombre de la base de datos
        )
        return conn
    except pymysql.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        raise falcon.HTTPInternalServerError('Database error', 'No se pudo conectar a la base de datos.')

class LoginResource:
    def on_post(self, req, resp):
        # Obtener los datos del cuerpo de la solicitud
        data = req.media
        correo = data.get('correo')
        pwd = data.get('pwd')

        if not correo or not pwd:
            raise falcon.HTTPBadRequest('Datos incompletos', 'Se requieren correo y contraseña.')

        # Conectar a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Validar el usuario en la base de datos
            query = "SELECT Nombre, Rol FROM Usuarios WHERE Correo = %s AND Pwd = %s"
            cursor.execute(query, (correo, pwd))
            user = cursor.fetchone()

            if user:
                # Generar un token JWT
                token_payload = {
                    'correo': correo,
                    'rol': user[1],  # user[1] es el Rol (segundo campo de la tupla)
                    'exp': datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
                }
                token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')

                resp.media = {
                    'mensaje': 'Login exitoso',
                    'nombre': user[0],  # user[0] es el Nombre (primer campo de la tupla)
                    'rol': user[1],     # user[1] es el Rol
                    'token': token
                }
                resp.status = falcon.HTTP_200
            else:
                raise falcon.HTTPUnauthorized('Acceso denegado', 'Correo o contraseña incorrectos.')
        finally:
            cursor.close()
            conn.close()

# Crear la aplicación Falcon
app = falcon.App()

# Crear una instancia del recurso de login
login_resource = LoginResource()

# Agregar la ruta para el login
app.add_route('/login', login_resource)

# Exportar la aplicación para Vercel
handler = app