import falcon
import requests
import json
import re
from .config import MICROSERVICIOS

# --- AppSensor detección básica ---
def contiene_inyeccion(valor):
    if not isinstance(valor, str):
        return False
    patrones = [
        r"<script.*?>.*?</script>",
        r"<.*?on\w+=.*?>",
        r"(?i)UNION\s+SELECT", r"(?i)DROP\s+TABLE", r"(?i)INSERT\s+INTO",
        r"' OR '1'='1", r"--", r";"
    ]
    return any(re.search(p, valor) for p in patrones)

def registrar_evento_ia(tipo, descripcion, usuario):
    print(f"[AppSensor] ALERTA | Tipo: {tipo} | Usuario: {usuario} | Detalle: {descripcion}")

def analizar_payload(payload, usuario):
    eventos = []
    if isinstance(payload, dict):
        for k, v in payload.items():
            if isinstance(v, (dict, list)):
                eventos += analizar_payload(v, usuario)
            elif isinstance(v, str) and contiene_inyeccion(v):
                eventos.append((k, v))
    return eventos

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

        body = None
        if method in ("POST", "PUT"):
            try:
                raw_json = req.bounded_stream.read()
                decoded = raw_json.decode("utf-8") if raw_json else None
                print("JSON decodificado:", decoded)

                usuario = req.context.get("user", {}).get("correo", "desconocido")
                if body:
                    eventos_detectados = analizar_payload(body, usuario)
                    if eventos_detectados:
                        for campo, valor in eventos_detectados:
                            registrar_evento_ia("IAST-Injection", f"Campo '{campo}' contiene patrón sospechoso", usuario)
                        raise falcon.HTTPForbidden(
                            title="Solicitud rechazada",
                            description="Se detectaron posibles patrones de ataque en los datos enviados."
                        )
            except falcon.HTTPForbidden:
                raise
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
