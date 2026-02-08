

from fastapi import FastAPI
from fastapi import HTTPException
from prometheus_client import Counter, Histogram , generate_latest
from prometheus_client import CONTENT_TYPE_LATEST
from starlette.responses import Response
import time
import random

app = FastAPI(title="Personal Reliability Lab")

REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total HTTP requests",
    ["endpoint" , "method" , "status"]
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Request latency",
    ["endpoint"]
)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    Response = await call_next(request)
    latency = time.time() - start_time

    REQUEST_COUNT.labels(
        endpoint=request.url.path,
        method=request.method,
        status=str(Response.status_code)
    ).inc()

    REQUEST_LATENCY.labels(endpoint=request.url.path).observe(latency)
    return Response

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/work")
def work():
    sleep_time = random.uniform(0.1, 1.5)
    if random.random() < 0.2:
        return Response(status_code=500, content="Something broke")

    return {"message": "Work completed", "latency": sleep_time}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)