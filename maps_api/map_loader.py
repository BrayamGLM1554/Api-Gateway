import falcon
import requests

class MapLoaderResource:
    def __init__(self):
        self.nominatim_url = 'https://nominatim.openstreetmap.org/search'
        self.reverse_geocode_url = 'https://nominatim.openstreetmap.org/reverse'

    def on_get(self, req, resp):
        # Obtener los parámetros de la solicitud
        address = req.get_param('address')
        lat = req.get_param('lat')
        lon = req.get_param('lon')

        if address:
            # Búsqueda por dirección
            params = {
                'q': address,
                'format': 'json',
                'addressdetails': 1,
                'countrycodes': 'MX',
                'limit': 1
            }
            response = requests.get(self.nominatim_url, params=params)
            data = response.json()
            if data:
                result = data[0]
                resp.media = {
                    'display_name': result['display_name'],
                    'lat': result['lat'],
                    'lon': result['lon'],
                    'boundingbox': result['boundingbox']
                }
            else:
                resp.media = {'error': 'Dirección no encontrada.'}
        elif lat and lon:
            # Búsqueda por coordenadas
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'addressdetails': 1
            }
            response = requests.get(self.reverse_geocode_url, params=params)
            data = response.json()
            if 'error' not in data:
                resp.media = {
                    'display_name': data['display_name'],
                    'address': data['address']
                }
            else:
                resp.media = {'error': 'Coordenadas no encontradas.'}
        else:
            # Mostrar mapa de México por defecto
            resp.media = {
                'message': 'Mapa centrado en México.',
                'boundingbox': ['14.3895', '32.7187', '-118.6523', '-86.8123']  # Coordenadas aproximadas de México
            }

        resp.status = falcon.HTTP_200
