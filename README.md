# Secure LLM API Kubernetes App

This repository is a secure LLM API implementation designed for Kubernetes deployment.

It is being built step-by-step with a focus on security, authentication, rate limiting, prompt validation, observability, and Kubernetes deployment.

## Current status
- Project scaffolding created
- Base FastAPI app initialized
- Authentication and JWT issuance implemented
- Rate limiting and usage tracking added
- Prompt safety and validation added
- Kubernetes manifests and observability scaffolding added

## How to run locally
1. Build the container:
   ```bash
   docker build -t secure-llm-api .
   ```
2. Run locally:
   ```bash
   docker run --rm -p 8000:8000 secure-llm-api
   ```
3. The app will be available at `http://localhost:8000`.
4. Metrics are exposed at `http://localhost:8000/metrics`.

## Next steps
1. Add production-ready observability and tracing
2. Harden Kubernetes manifests with secrets and ingress TLS
3. Add end-to-end tests and deployment automation
