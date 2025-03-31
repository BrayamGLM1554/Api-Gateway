import os
import falcon
import jwt
import pymysql
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from marshmallow import ValidationError
from schemas.login_schema import LoginSchema
from common.logger import logger  # ✅ Registro de eventos

# Cargar variables de entorno desde .env (solo útil en local)
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Claves desde entorno (Railway las necesita definidas en el dashboard)
SECRET_KEY = os.getenv('SECRET_KEY', 'Quetzalcoatl_Project')
TOKEN_EXPIRATION_MINUTES = 60

class LoginResource:
    def __init__(self, db_connection, active_tokens):
        self.db_connection = db_connection
        self.active_tokens = active_tokens  # {'by_token': set(), 'by_user': dict()}
        self.schema = LoginSchema()

    def on_post(self, req, resp):
        try:
            raw_data = req.media
            data = self.schema.load(raw_data)  # Validación Marshmallow

            correo = data['correo']
            pwd = data['pwd']

            logger.info(f"Intento de login: {correo}")

            with self.db_connection.cursor(pymysql.cursors.DictCursor) as cursor:
                query = "SELECT Nombre, Rol, Pwd FROM Usuarios WHERE Correo = %s"
                cursor.execute(query, (correo,))
                user = cursor.fetchone()

            if user is None:
                logger.warning(f" Login fallido - correo no encontrado: {correo}")
                raise falcon.HTTPUnauthorized(
                    title='Acceso denegado',
                    description='Correo no encontrado.'
                )

            if user['Pwd'] != pwd:
                logger.warning(f" Login fallido - contraseña incorrecta: {correo}")
                raise falcon.HTTPUnauthorized(
                    title='Acceso denegado',
                    description='Contraseña incorrecta.'
                )

            token_payload = {
                'correo': correo,
                'rol': user['Rol'],
                'exp': datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
            }
            token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')

            self.add_active_token(correo, token)

            logger.info(f"Login exitoso: {correo} (rol: {user['Rol']})")

            resp.media = {
                'mensaje': 'Login exitoso',
                'nombre': user['Nombre'],
                'rol': user['Rol'],
                'token': token
            }
            resp.status = falcon.HTTP_200

        except ValidationError as err:
            logger.warning(f"Datos inválidos en login: {err.messages}")
            raise falcon.HTTPBadRequest(
                title='Datos inválidos',
                description=str(err.messages)
            )
        except pymysql.MySQLError as e:
            logger.error(f"Error en base de datos: {e}")
            raise falcon.HTTPInternalServerError(
                title='Error en la base de datos',
                description='Error de conexión o consulta.'
            )
        except falcon.HTTPError as http_err:
            raise http_err  # Re-lanzar errores Falcon sin atraparlos como genéricos
        except Exception as e:
            logger.error(f" Excepción inesperada: {e}")
            raise falcon.HTTPInternalServerError(
                title='Error inesperado',
                description='Ocurrió un error desconocido.'
            )

    def add_active_token(self, correo, token):
        self.active_tokens['by_user'][correo] = token
        self.active_tokens['by_token'].add(token)
        logger.info(f"Token generado y activado para: {correo}")

    def on_delete(self, req, resp):
        token = req.get_header('Authorization')

        if not token:
            raise falcon.HTTPBadRequest(
                title='Error',
                description='Se requiere un token para cerrar sesión.'
            )

        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            correo = decoded.get('correo')
        except jwt.ExpiredSignatureError:
            raise falcon.HTTPUnauthorized(
                title='Token expirado',
                description='Inicia sesión nuevamente.'
            )
        except jwt.InvalidTokenError:
            raise falcon.HTTPUnauthorized(
                title='Token inválido',
                description='No se pudo validar el token.'
            )

        if token in self.active_tokens['by_token']:
            self.active_tokens['by_token'].remove(token)
            self.active_tokens['by_user'].pop(correo, None)
            logger.info(f"Cierre de sesión exitoso para: {correo}")
            resp.media = {'mensaje': 'Sesión cerrada correctamente'}
        else:
            raise falcon.HTTPUnauthorized(
                title='Error',
                description='Token inválido o sesión ya cerrada.'
            )

        resp.status = falcon.HTTP_200
