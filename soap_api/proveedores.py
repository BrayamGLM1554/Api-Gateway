import os
import pymysql
from datetime import datetime
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

class ProveedorResource:
    def on_post(self, req, resp):
        data = req.media
        token = data.get("token")
        nombre = data.get("nombre")
        tipo = data.get("tipo")
        direccion = data.get("direccion")
        telefono = data.get("telefono")
        email = data.get("email")

        if not token or not nombre or not tipo or not direccion or not telefono or not email:
            resp.status = falcon.HTTP_400
            resp.media = {"error": "Todos los campos son obligatorios"}
            return

        conexion = get_db_connection()
        try:
            with conexion.cursor() as cursor:
                # Verificar si el token es válido y no ha expirado
                sql = "SELECT ID, Expiracion FROM ProveedorTokens WHERE Token = %s AND Usado = FALSE"
                cursor.execute(sql, (token,))
                resultado = cursor.fetchone()

                if not resultado:
                    resp.status = falcon.HTTP_400
                    resp.media = {"error": "Token inválido o ya usado"}
                    return

                # Validar expiración del token
                expiracion = resultado["Expiracion"]
                if not expiracion or datetime.now() > expiracion:
                    resp.status = falcon.HTTP_400
                    resp.media = {"error": "Token expirado"}
                    return

                # Insertar en la tabla Proveedores
                sql = """INSERT INTO Proveedores (Nombre, Tipo, Direccion, Telefono, Email, FechaAlta, Estatus) 
                         VALUES (%s, %s, %s, %s, %s, NOW(), 'Activo')"""
                cursor.execute(sql, (nombre, tipo, direccion, telefono, email))
                proveedor_id = cursor.lastrowid

                # Marcar el token como usado y vincularlo al proveedor
                sql = "UPDATE ProveedorTokens SET Usado = TRUE, ProveedorID = %s WHERE ID = %s"
                cursor.execute(sql, (proveedor_id, resultado["ID"]))

                resp.status = falcon.HTTP_201
                resp.media = {"mensaje": f"Proveedor registrado con éxito, ID: {proveedor_id}"}

        except pymysql.Error as e:
            resp.status = falcon.HTTP_500
            resp.media = {"error": f"Error al registrar proveedor: {e}"}
        finally:
            conexion.close()
