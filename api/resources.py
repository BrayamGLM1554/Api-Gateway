import os
import falcon
import jwt
from datetime import datetime, timedelta
import pymysql

# Clave secreta para JWT
SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
TOKEN_EXPIRATION_MINUTES = 30

class LoginResource:
    def __init__(self, db_connection, active_tokens):
        self.db_connection = db_connection
        self.active_tokens = active_tokens  # 🔥 Lista de tokens activos en memoria


    def on_post(self, req, resp):
        """Maneja el login de usuario y genera un token JWT."""
        try:
            data = req.media
            correo = data.get('correo')
            pwd = data.get('pwd')

            if not correo or not pwd:
                raise falcon.HTTPBadRequest('Datos incompletos', 'Se requieren correo y contraseña.')

            # Buscar usuario en la base de datos
            with self.db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
                query = "SELECT Nombre, Rol, Pwd FROM Usuarios WHERE Correo = %s"
                cursor.execute(query, (correo,))
                user = cursor.fetchone()

            if user is None:
                raise falcon.HTTPUnauthorized('Acceso denegado', 'Correo no encontrado.')

            if user['Pwd'] != pwd:  # 🔥 Comparación directa sin hash
                raise falcon.HTTPUnauthorized('Acceso denegado', 'Contraseña incorrecta.')

            # Generar el token JWT
            token_payload = {
                'correo': correo,
                'rol': user['Rol'],
                'exp': datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
            }
            token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')

            # 🔥 Guardar el token en memoria usando el metodo add_active_token
            self.add_active_token(token)

            resp.media = {
                'mensaje': 'Login exitoso',
                'nombre': user['Nombre'],
                'rol': user['Rol'],
                'token': token
            }
            resp.status = falcon.HTTP_200

        except pymysql.Error as e:
            raise falcon.HTTPInternalServerError('Error en la base de datos', str(e))

    def add_active_token(self, token):
        """Añadir el token al conjunto de tokens activos."""
        self.active_tokens.add(token)
        # Imprimir los tokens activos después de agregar uno nuevo
        print("Tokens activos:", self.active_tokens)

    def on_delete(self, req, resp):
        """Cierra sesión eliminando el token de la memoria."""
        token = req.get_header('Authorization')

        if not token:
            raise falcon.HTTPBadRequest('Error', 'Se requiere un token para cerrar sesión.')

        if token in self.active_tokens:
            self.active_tokens.remove(token)
            resp.media = {'mensaje': 'Sesión cerrada correctamente'}
        else:
            raise falcon.HTTPUnauthorized('Error', 'Token inválido o sesión ya cerrada.')

        resp.status = falcon.HTTP_200
