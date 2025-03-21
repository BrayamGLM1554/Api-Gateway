import os
import falcon
import jwt
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la clave secreta del .env
SECRET_KEY = os.getenv("SECRET_KEY", 'Quetzalcoatl_Project')

# 🔥 Mover `active_tokens` a un nivel más alto para que sea compartido
active_tokens = set()

class AuthMiddleware:
    """Middleware para validar tokens en cada petición."""

    def process_request(self, req, resp):
        # Verificar si la ruta pertenece a la API Gateway
        if req.path.startswith("/gateway"):
            token = req.get_header("Authorization")

            if not token:
                raise falcon.HTTPUnauthorized(description="Token requerido.")

            # Verificar que el token esté en formato "Bearer <token>"
            if token.startswith("Bearer "):
                token = token.split("Bearer ")[-1].strip()
            else:
                raise falcon.HTTPUnauthorized(description="Token en formato incorrecto.")

            print("Token recibido:", token)  # Agregado para verificar el token recibido

            # Verificar si el token está activo
            if token not in active_tokens:
                raise falcon.HTTPUnauthorized(description="Token inválido o sesión expirada.")

            try:
                # Decodificar el token usando la clave secreta
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

                # Almacenar la carga útil del token en el contexto de la petición
                req.context["user"] = payload
                print("Token válido:", token)  # Agregado para verificar que el token es válido
            except jwt.ExpiredSignatureError:
                raise falcon.HTTPUnauthorized(description="Token expirado.")
            except jwt.InvalidTokenError:
                raise falcon.HTTPUnauthorized(description="Token inválido.")
