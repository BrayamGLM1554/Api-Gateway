import time
import falcon
from collections import defaultdict

class RateLimitMiddleware:
    def __init__(self, limit=10, window=60):
        self.limit = limit  # Máximo de peticiones
        self.window = window  # Ventana de tiempo en segundos
        self.clients = defaultdict(list)

    def process_request(self, req, _resp):
        client_ip = req.access_route[0]  # IP cliente
        now = time.time()

        # Limpiar timestamps viejos
        self.clients[client_ip] = [
            timestamp for timestamp in self.clients[client_ip]
            if now - timestamp < self.window
        ]

        # Si supera el límite
        if len(self.clients[client_ip]) >= self.limit:
            raise falcon.HTTPTooManyRequests(
                title="Demasiadas solicitudes",
                description=f"Máximo {self.limit} solicitudes cada {self.window} segundos"
            )

        # Registrar timestamp actual
        self.clients[client_ip].append(now)
