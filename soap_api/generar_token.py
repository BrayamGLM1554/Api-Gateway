import os
import pymysql
import secrets
from datetime import datetime, timedelta
import falcon
from dotenv import load_dotenv

load_dotenv()

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
    def on_post(self, req, resp):
        """Genera un nuevo token para un proveedor y lo guarda en la base de datos."""
        token = secrets.token_urlsafe(32)  # Genera un token seguro
        expiracion = datetime.now() + timedelta(hours=24)  # Expira en 24 horas

        conexion = get_db_connection()
        try:
            with conexion.cursor() as cursor:
                sql = "INSERT INTO ProveedorTokens (Token, Usado, Expiracion) VALUES (%s, FALSE, %s)"
                cursor.execute(sql, (token, expiracion))

            resp.status = falcon.HTTP_201
            resp.media = {"token": token, "expiracion": expiracion.strftime("%Y-%m-%d %H:%M:%S")}

        except pymysql.Error as e:
            resp.status = falcon.HTTP_500
            resp.media = {"error": f"Error al generar token: {e}"}

        finally:
            conexion.close()
