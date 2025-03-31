import os
import re
import falcon
import jwt
from dotenv import load_dotenv

# Cargar variables de entorno
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

SECRET_KEY = os.getenv("SECRET_KEY", 'Quetzalcoatl_Project')
JWT_PATTERN = re.compile(r'^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$')

class AuthMiddleware:
    def __init__(self, active_tokens):
        self.active_tokens = active_tokens  # {'by_token': set(), 'by_user': dict()}

    def process_request(self, req, _resp):
        if req.path.startswith("/gateway") and req.method != "OPTIONS":
            print("Petición recibida:")
            print("Método:", req.method)
            print("Ruta:", req.path)
            print("IP:", req.remote_addr)
            print("Headers:", dict(req.headers))

            token_header = req.get_header("Authorization")

            if not token_header:
                print("No se recibió header Authorization.")
                raise falcon.HTTPUnauthorized(
                    title="Token requerido",
                    description="Debe incluir un token en la cabecera Authorization."
                )

            if not token_header.startswith("Bearer "):
                print("Formato Bearer incorrecto:", token_header)
                raise falcon.HTTPUnauthorized(
                    title="Formato incorrecto",
                    description="El token debe estar en formato Bearer <token>."
                )

            token = token_header.split("Bearer ")[-1].strip()

            if not JWT_PATTERN.match(token):
                print("Token con formato inválido:", token)
                raise falcon.HTTPUnauthorized(
                    title="Token mal formado",
                    description="El token no tiene un formato válido."
                )

            print("Tokens activos:", self.active_tokens['by_token'])
            print(f"Token recibido: {token}")

            if token not in self.active_tokens['by_token']:
                print("Token no está activo.")
                raise falcon.HTTPUnauthorized(
                    title="Token inválido",
                    description="Token inválido o sesión expirada."
                )

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                req.context["user"] = payload
                print("Token válido:", token)
            except jwt.ExpiredSignatureError:
                print("Token expirado.")
                raise falcon.HTTPUnauthorized(
                    title="Token expirado",
                    description="Debe volver a iniciar sesión."
                )
            except jwt.InvalidTokenError as e:
                print("Token inválido:", str(e))
                raise falcon.HTTPUnauthorized(
                    title="Token inválido",
                    description="No se pudo validar el token."
                )
