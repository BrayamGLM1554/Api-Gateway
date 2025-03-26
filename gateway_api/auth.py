import os
import falcon
import jwt
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Obtener la clave secreta del .env
SECRET_KEY = os.getenv("SECRET_KEY", 'Quetzalcoatl_Project')
print("🔐 Clave secreta cargada desde .env:", SECRET_KEY)

class AuthMiddleware:
    def __init__(self, active_tokens):
        self.active_tokens = active_tokens  # {'by_token': set(), 'by_user': dict()}

    def process_request(self, req, resp):
        if req.path.startswith("/gateway"):
            token = req.get_header("Authorization")

            if not token:
                raise falcon.HTTPUnauthorized(description="Token requerido.")

            if token.startswith("Bearer "):
                token = token.split("Bearer ")[-1].strip()
            else:
                raise falcon.HTTPUnauthorized(description="Token en formato incorrecto.")

            print("📦 Tokens activos en el servidor:", self.active_tokens['by_token'])
            print(f"➡️ Token recibido en la solicitud: {token}")

            if token not in self.active_tokens['by_token']:
                print("⚠️ El token no está en active_tokens.")
                raise falcon.HTTPUnauthorized(description="Token inválido o sesión expirada.")

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                req.context["user"] = payload
                print("✅ Token válido:", token)
            except jwt.ExpiredSignatureError:
                print("⏰ Token expirado.")
                raise falcon.HTTPUnauthorized(description="Token expirado.")
            except jwt.InvalidTokenError as e:
                print("❌ Token inválido:", str(e))
                raise falcon.HTTPUnauthorized(description="Token inválido.")
