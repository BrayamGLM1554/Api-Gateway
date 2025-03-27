# metrics/metrics_resource.py
import falcon
import jwt
import os
from dotenv import load_dotenv
from common.auth_tokens import active_tokens

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "Quetzalcoatl_Project")

class MetricsResource:
    def __init__(self, middleware):
        self.middleware = middleware

    def on_get(self, req, resp):
        auth_header = req.get_header("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise falcon.HTTPUnauthorized(description="Token requerido")

        token = auth_header.split("Bearer ")[-1].strip()
        if token not in active_tokens['by_token']:
            raise falcon.HTTPUnauthorized(description="Token inválido o sesión no activa")

        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise falcon.HTTPUnauthorized(description="Token expirado")
        except jwt.InvalidTokenError:
            raise falcon.HTTPUnauthorized(description="Token inválido")

        resp.status = 200
        resp.media = self.middleware.get_metrics()
