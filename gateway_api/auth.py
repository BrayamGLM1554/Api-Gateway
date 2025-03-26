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

# Tokens activos en memoria (simulación de sesión activa)
active_tokens = set()

class AuthMiddleware:
    def __init__(self, active_tokens):
        self.active_tokens = active_tokens

    def process_request(self, req, resp):
        # Validar solo rutas que comienzan con /gateway
        if req.path.startswith("/gateway"):
            token = req.get_header("Authorization")

            if not token:
                raise falcon.HTTPUnauthorized(description="Token requerido.")

            # Verificar si el token tiene formato Bearer
            if token.startswith("Bearer "):
                token = token.split("Bearer ")[-1].strip()
            else:
                raise falcon.HTTPUnauthorized(description="Token en formato incorrecto.")

            # Imprimir tokens activos y el recibido para diagnóstico
            print(f"📦 Tokens activos en el servidor: {self.active_tokens}")
            print(f"➡️ Token recibido en la solicitud: {token}")

            # Verificar si el token está en los tokens activos
            if token not in self.active_tokens:
                print("⚠️ El token no está en active_tokens.")
                raise falcon.HTTPUnauthorized(description="Token inválido o sesión expirada.")

            # Decodificar y validar el token
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
