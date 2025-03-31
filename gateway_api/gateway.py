import falcon
import requests
import json
from .config import MICROSERVICIOS
from schemas.proveedor_schema import ProveedorSchema
from marshmallow import ValidationError

class GatewayResource:
    def __init__(self, service_name):
        self.service_name = service_name
        self.service_url = MICROSERVICIOS.get(service_name)

    def forward_request(self, req, method, append_path=""):
        if not self.service_url:
            raise falcon.HTTPNotFound(description="Microservicio no encontrado.")

        url = f"{self.service_url}{append_path}"
        headers = {
            "Authorization": req.get_header("Authorization"),
            "Content-Type": "application/json"
        }

        # Leer y preparar el cuerpo solo para POST o PUT
        body = None
        if method in ("POST", "PUT"):
            try:
                raw_json = req.bounded_stream.read()
                print("JSON crudo recibido:", raw_json)  # DEBUG: ver si llega algo
                decoded = raw_json.decode("utf-8") if raw_json else None
                print("JSON decodificado:", decoded)

                data = json.loads(decoded) if decoded else None
                if data:
                    body = data
                    print("JSON enviado al microservicio:", json.dumps(body, indent=2))
                else:
                    raise falcon.HTTPBadRequest(title="Cuerpo vacío", description="El cuerpo no puede estar vacío.")
            except Exception as e:
                print("Error al procesar JSON:", str(e))
                raise falcon.HTTPBadRequest(title="Invalid JSON", description="Cuerpo mal formado.")

        print("Reenviando solicitud al microservicio:")
        print("Servicio:", self.service_name)
        print("URL:", url)
        print("Método:", method)
        print("Headers:", headers)
        print("Body:", body)

        try:
            response = requests.request(method, url, headers=headers, json=body)
        except requests.RequestException as e:
            print("Error al contactar el microservicio:", str(e))
            raise falcon.HTTPBadGateway(description=f"Error al contactar el microservicio: {str(e)}")

        print("Respuesta recibida del microservicio:")
        print("Código:", response.status_code)

        resp = falcon.Response()
        resp.status = f"{response.status_code} {response.reason}"
        try:
            resp.media = response.json()
        except ValueError:
            resp.text = response.text

        return resp

    def on_get(self, req, resp, id=None):
        append_path = f"/{id}" if id else ""
        resp_obj = self.forward_request(req, "GET", append_path)
        resp.status = resp_obj.status
        resp.media = resp_obj.media

    def on_post(self, req, resp):
        resp_obj = self.forward_request(req, "POST")
        resp.status = resp_obj.status
        resp.media = resp_obj.media

    def on_put(self, req, resp, id=None):
        append_path = f"/{id}" if id else ""
        resp_obj = self.forward_request(req, "PUT", append_path)
        resp.status = resp_obj.status
        resp.media = resp_obj.media

    def on_delete(self, req, resp, id=None):
        append_path = f"/{id}" if id else ""
        resp_obj = self.forward_request(req, "DELETE", append_path)
        resp.status = resp_obj.status
        resp.media = resp_obj.media

