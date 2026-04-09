# Secure LLM API Kubernetes App

A secure LLM API project built in FastAPI and designed for Kubernetes deployment.

This app is intentionally structured as a secure API gateway for LLM access, with a focus on:
- authentication and JWT issuance
- rate limiting and token usage tracking
- prompt validation and prompt injection protection
- observability via Prometheus metrics
- Kubernetes deployment manifests and autoscaling

## Features
- JWT-based auth with `/auth/token` and `/auth/register`
- Protected `/llm/generate` endpoint
- Prompt safety checks for forbidden terms and injection patterns
- Rate limiting per user with request and token quotas
- Usage logging and quota-aware tracking
- Metrics endpoint for Prometheus at `/metrics`
- Kubernetes manifests for Deployment, Service, Ingress, NetworkPolicy, and HPA

## Project structure

```text
Dockerfile
requirements.txt
README.md
infra/k8s/
  deployment.yaml
  service.yaml
  ingress.yaml
  network-policy.yaml
  hpa.yaml
src/
  main.py
  app/
    config.py
    routes/
      auth.py
      health.py
      llm.py
    db/
      models.py
      repository.py
      session.py
    schemas/
      auth.py
      llm.py
    services/
      auth_service.py
      prompt_safety_service.py
      rate_limit_service.py
      token_service.py
    telemetry/
      logging.py
      metrics.py
```

## Running locally

1. Build the Docker image:
   ```bash
   docker build -t secure-llm-api .
   ```
2. Run the container:
   ```bash
   docker run --rm -p 8000:8000 secure-llm-api
   ```
3. Access the API at `http://localhost:8000`
4. Access metrics at `http://localhost:8000/metrics`

## API endpoints
- `POST /auth/register` — create a user and return a JWT
- `POST /auth/token` — authenticate and receive a JWT
- `POST /llm/generate` — generate LLM output (requires `Authorization: Bearer <token>`)
- `GET /health/ready` — readiness probe
- `GET /health/live` — liveness probe

## Notes
- The app currently uses SQLite for local data persistence.
- Production deployments should replace SQLite with a managed database and secure secret storage.
- Kubernetes manifests are intentionally minimal and should be hardened with TLS and vault-backed secrets.

## Final status
- All major features are implemented in the scaffolded app.
- Remaining work is production hardening, testing, and deployment automation.

## Next steps
1. Add end-to-end tests and CI automation
2. Harden Kubernetes manifests with TLS, secrets, and pod security policies
3. Add distributed tracing and more advanced telemetry
