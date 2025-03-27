# common/metrics_middleware.py
import time
from collections import defaultdict
from common.logger import logger

class MetricsMiddleware:
    def __init__(self):
        self.total_requests = 0
        self.total_errors = 0
        self.request_times = []
        self.by_route = defaultdict(lambda: {"count": 0, "errors": 0, "total_time": 0.0})

    def process_request(self, req, resp):
        req.context.start_time = time.time()

    def process_response(self, req, resp, resource, req_succeeded):
        duration = time.time() - req.context.start_time
        self.total_requests += 1
        self.request_times.append(duration)

        route = req.path
        self.by_route[route]["count"] += 1
        self.by_route[route]["total_time"] += duration

        if not req_succeeded or resp.status_code >= 400:
            self.total_errors += 1
            self.by_route[route]["errors"] += 1
            logger.warning(f"📉 {req.method} {req.path} - FALLO ({resp.status}) - {duration:.3f}s")
        else:
            logger.info(f"📈 {req.method} {req.path} - {resp.status} - {duration:.3f}s")

    def get_metrics(self):
        return {
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "average_response_time": round(sum(self.request_times) / len(self.request_times), 4) if self.request_times else 0,
            "routes": {
                route: {
                    "requests": info["count"],
                    "errors": info["errors"],
                    "average_time": round(info["total_time"] / info["count"], 4) if info["count"] > 0 else 0
                } for route, info in self.by_route.items()
            }
        }
