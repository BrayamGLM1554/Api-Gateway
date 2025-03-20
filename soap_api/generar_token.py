import os
import pymysql
import secrets
from datetime import datetime, timedelta
import falcon
from dotenv import load_dotenv

load_dotenv()
active_tokens = set()

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

class GenerarTokenResource:
    def __init__(self, active_tokens):
        self.active_tokens = active_tokens

    def on_post(self, req, resp):
        """Genera un nuevo token para un proveedor si la sesión está activa."""
        # Verificar si el token está presente en la cabecera
        token = req.get_header('Authorization')
        if not token:
            raise falcon.HTTPUnauthorized(description="Se requiere un token.")
        token = token.split(" ")[1] if token.startswith("Bearer ") else token

        # Verificar si el token está activo
        if token not in self.active_tokens:
            raise falcon.HTTPUnauthorized(description="Token inválido o sesión expirada.")

        # Generar un nuevo token para el proveedor
        nuevo_token = secrets.token_urlsafe(32)
        expiracion = datetime.now() + timedelta(hours=24)

        conexion = get_db_connection()
        try:
            with conexion.cursor() as cursor:
                sql = "INSERT INTO ProveedorTokens (Token, Usado, Expiracion) VALUES (%s, FALSE, %s)"
                cursor.execute(sql, (nuevo_token, expiracion))

            resp.status = falcon.HTTP_201
            resp.media = {"token": nuevo_token, "expiracion": expiracion.strftime("%Y-%m-%d %H:%M:%S")}

        except pymysql.Error as e:
            resp.status = falcon.HTTP_500
            resp.media = {"error": f"Error al generar token: {e}"}

        finally:
            conexion.close()