import os
import falcon
import jwt
from datetime import datetime, timedelta
import pymysql
from dotenv import load_dotenv
from marshmallow import ValidationError
from schemas.login_schema import LoginSchema  # 🔥 Importar esquema

# Cargar variables de entorno
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

SECRET_KEY = os.getenv('SECRET_KEY', 'Quetzalcoatl_Project')
TOKEN_EXPIRATION_MINUTES = 30

class LoginResource:
    def __init__(self, db_connection, active_tokens):
        self.db_connection = db_connection
        self.active_tokens = active_tokens
        self.schema = LoginSchema()  # 🔥 Instancia del validador

    def on_post(self, req, resp):
        """Maneja el login de usuario y genera un token JWT."""
        try:
            raw_data = req.media
            data = self.schema.load(raw_data)  # 🔥 Validación Marshmallow

            correo = data['correo']
            pwd = data['pwd']

            with self.db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
                query = "SELECT Nombre, Rol, Pwd FROM Usuarios WHERE Correo = %s"
                cursor.execute(query, (correo,))
                user = cursor.fetchone()

            if user is None:
                raise falcon.HTTPUnauthorized('Acceso denegado', 'Correo no encontrado.')

            if user['Pwd'] != pwd:
                raise falcon.HTTPUnauthorized('Acceso denegado', 'Contraseña incorrecta.')

            # Generar JWT
            token_payload = {
                'correo': correo,
                'rol': user['Rol'],
                'exp': datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
            }
            token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')

            self.add_active_token(token)

            resp.media = {
                'mensaje': 'Login exitoso',
                'nombre': user['Nombre'],
                'rol': user['Rol'],
                'token': token
            }
            resp.status = falcon.HTTP_200

        except ValidationError as err:
            raise falcon.HTTPBadRequest('Datos inválidos', str(err.messages))
        except pymysql.Error as e:
            raise falcon.HTTPInternalServerError('Error en la base de datos', str(e))

    def add_active_token(self, token):
        self.active_tokens.add(token)
        print("Tokens activos:", self.active_tokens)

    def on_delete(self, req, resp):
        token = req.get_header('Authorization')

        if not token:
            raise falcon.HTTPBadRequest('Error', 'Se requiere un token para cerrar sesión.')

        if token in self.active_tokens:
            self.active_tokens.remove(token)
            resp.media = {'mensaje': 'Sesión cerrada correctamente'}
        else:
            raise falcon.HTTPUnauthorized('Error', 'Token inválido o sesión ya cerrada.')

        resp.status = falcon.HTTP_200
