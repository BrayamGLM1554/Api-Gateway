import falcon
import requests
from .config import MICROSERVICIOS

class GatewayResource:
    def __init__(self, service_name):
        self.service_name = service_name
        self.service_url = MICROSERVICIOS.get(service_name)

    def forward_request(self, req, method, append_path=""):
        if not self.service_url:
            raise falcon.HTTPNotFound(description="Microservicio no encontrado.")

        url = f"{self.service_url}{append_path}"
        headers = {"Authorization": req.get_header("Authorization")}
        body = req.media if req.content_length else None

        print("🔁 Reenviando solicitud al microservicio:")
        print("📡 Servicio:", self.service_name)
        print("🌐 URL:", url)
        print("📨 Método:", method)
        print("🧾 Headers:", headers)
        print("📥 Body:", body)

        try:
            response = requests.request(method, url, headers=headers, json=body)
        except requests.RequestException as e:
            print("❌ Error al contactar el microservicio:", str(e))
            raise falcon.HTTPBadGateway(description=f"Error al contactar el microservicio: {str(e)}")

        print("✅ Respuesta recibida del microservicio:")
        print("🔢 Código de estado:", response.status_code)
        print("📃 Headers:", response.headers)
        print("📦 Contenido bruto:", response.text)

        # Preparar respuesta
        resp = falcon.Response()
        resp.status = f"{response.status_code} {response.reason}"
        try:
            resp.media = response.json()
            print("📤 Contenido JSON parseado:", resp.media)
        except ValueError:
            resp.text = response.text
            print("⚠️ Contenido no es JSON, se envía como texto plano.")

        return resp

    def on_get(self, req, resp, id=None):
        # Preferimos el ID de la ruta si existe
        append_path = f"/{id}" if id else ""
        resp_obj = self.forward_request(req, "GET", append_path)
        resp.status = resp_obj.status
        resp.media = resp_obj.media

    def on_post(self, req, resp):
        resp_obj = self.forward_request(req, "POST")
        resp.status = resp_obj.status
        resp.media = resp_obj.media

    def on_put(self, req, resp):
        resp_obj = self.forward_request(req, "PUT")
        resp.status = resp_obj.status
        resp.media = resp_obj.media

    def on_delete(self, req, resp):
        resp_obj = self.forward_request(req, "DELETE")
        resp.status = resp_obj.status
        resp.media = resp_obj.media


