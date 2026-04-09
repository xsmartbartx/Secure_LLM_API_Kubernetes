from fastapi import FastAPI
from app.db.session import init_db
from app.routes.health import router as health_router
from app.routes.llm import router as llm_router
from app.routes.auth import router as auth_router
from app.telemetry.logging import configure_logging
from app.telemetry.metrics import instrument_request, metrics_endpoint

configure_logging()

app = FastAPI(
    title="Secure LLM API",
    description="A Kubernetes-ready, secure API for LLM access.",
    version="0.1.0",
)

app.middleware("http")(instrument_request)
app.add_api_route("/metrics", metrics_endpoint, methods=["GET"], include_in_schema=False)

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(llm_router, prefix="/llm", tags=["llm"])

@app.on_event("startup")
async def startup_event():
    init_db()

@app.on_event("shutdown")
async def shutdown_event():
    pass
