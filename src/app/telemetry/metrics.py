from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from starlette.requests import Request

request_counter = Counter(
    "llm_api_requests_total",
    "Total number of LLM API requests",
    ["method", "path", "status"],
)
request_latency = Histogram(
    "llm_api_request_duration_seconds",
    "Request duration in seconds",
    ["method", "path"],
)


def metrics_endpoint() -> Response:
    data = generate_latest()
    return Response(data, media_type=CONTENT_TYPE_LATEST)


async def instrument_request(request: Request, call_next):
    method = request.method
    path = request.url.path
    with request_latency.labels(method=method, path=path).time():
        response = await call_next(request)
    request_counter.labels(method=method, path=path, status=str(response.status_code)).inc()
    return response
