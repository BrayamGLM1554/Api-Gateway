import falcon
import requests
from .config import MICROSERVICIOS

class GatewayResource:
    def __init__(self, service_name):
        self.service_url = MICROSERVICIOS.get(service_name)

    def forward_request(self, req, method):
        """Reenvía la solicitud al microservicio correspondiente."""
        if not self.service_url:
            raise falcon.HTTPNotFound(description="Microservicio no encontrado.")

        url = f"{self.service_url}{req.path}"
        headers = {"Authorization": req.get_header("Authorization")}
        body = req.media if req.content_length else None

        response = requests.request(method, url, headers=headers, json=body)

        resp = falcon.Response()
        resp.status = f"{response.status_code} {response.reason}"
        resp.media = response.json() if response.content else None
        return resp

    def on_get(self, req, resp):
        resp_obj = self.forward_request(req, "GET")
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