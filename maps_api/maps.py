import falcon

class MapsResource:
    def __init__(self, active_tokens, map_loader_resource):
        self.active_tokens = active_tokens  # {'by_token': set(), 'by_user': dict()}
        self.map_loader_resource = map_loader_resource

    def on_get(self, req, resp):
        # Verificar si el token está presente
        token = req.get_header('Authorization')
        if not token:
            raise falcon.HTTPUnauthorized(description="Se requiere un token.")
        token = token.split(" ")[1] if token.startswith("Bearer ") else token

        # Verificar si el token está activo
        if token not in self.active_tokens['by_token']:
            raise falcon.HTTPUnauthorized(description="Token inválido o sesión expirada.")

        # Responder con datos de ejemplo (solo si la validación del token pasa)
        resp.media = {
            "message": "Acceso a la API de mapas exitoso",
            "data": {
                "latitud": 19.4326,
                "longitud": -99.1332
            }
        }
        resp.status = falcon.HTTP_200

        # Delegar la solicitud al recurso MapLoaderResource para cargar el mapa
        self.map_loader_resource.on_get(req, resp)
