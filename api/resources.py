import falcon
import jwt
from datetime import datetime, timedelta
import pymysql  # Usamos pymysql para MySQL

# Clave secreta para firmar los tokens JWT (debería ser una variable de entorno en producción)
SECRET_KEY = "Quetzalcoatl_Project:1554"
TOKEN_EXPIRATION_MINUTES = 30  # Tiempo de expiración del token en minutos

class LoginResource:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def on_post(self, req, resp):
        # Obtener los datos del cuerpo de la solicitud
        data = req.media
        correo = data.get('correo')
        pwd = data.get('pwd')

        if not correo or not pwd:
            raise falcon.HTTPBadRequest('Datos incompletos', 'Se requieren correo y contraseña.')

        # Validar el usuario en la base de datos
        cursor = self.db_connection.cursor()
        query = "SELECT Nombre, Rol FROM Usuarios WHERE Correo = %s AND Pwd = %s"  # Usamos %s para MySQL
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