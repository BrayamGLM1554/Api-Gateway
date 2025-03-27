import falcon
from common.logger import logger

def handle_http_error(req, resp, ex, params):
    resp.status = ex.status
    resp.content_type = 'application/json'
    resp.media = {
        "title": ex.title,
        "description": ex.description
    }

    status = ex.status
    tipo = ex.__class__.__name__

    if 500 <= ex.status_code < 600:
        logger.error(f"🛑 Error HTTP {status} ({tipo}): {ex.title} - {ex.description}")
    elif 400 <= ex.status_code < 500:
        logger.warning(f"⚠️ Error HTTP {status} ({tipo}): {ex.title} - {ex.description}")

def handle_exception(req, resp, ex, params):
    """Captura cualquier excepción inesperada no controlada"""
    logger.error(f"❌ Excepción no manejada: {str(ex)}")
    resp.status = falcon.HTTP_500
    resp.content_type = 'application/json'
    resp.media = {
        "title": "Error interno del servidor",
        "description": "Ocurrió un error inesperado. Intenta más tarde."
    }
