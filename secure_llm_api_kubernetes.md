# Secure LLM API in Kubernetes

A concise security guide for running large language model APIs safely in Kubernetes. This document covers threat modeling, network protection, identity and access controls, cost governance, secret handling, prompt injection mitigation, observability, pod security, and advanced defenses.

---

## 1. Threat model
LLM APIs introduce new risks beyond traditional web services. Key attack vectors include:

- **API key leakage**: exposed credentials or secrets in logs, containers, or misconfigured storage.
- **Cost abuse**: prompt flooding, replay attacks, or malicious payloads that inflate usage.
- **Prompt injection / data exfiltration**: adversarial input altering prompt behavior or extracting sensitive data.
- **Denial of Service (DoS)**: malformed requests, token exhaustion, or model overload.
- **Lateral movement**: compromised pods using cluster networking to reach other services.

---

## 2. Reference architecture
A secure LLM API deployment should separate concerns and minimize trust boundaries.

```text
[Client]
   ↓
[API Gateway / Ingress]
   ↓
[Authentication / Authorization]
   ↓
[LLM API Service]
   ↓
[LLM Provider / Model]
```

---

## 3. Ingress and network security
Protect the edge and internal traffic with strong transport and network controls.

- Enforce TLS everywhere with cert-manager or a managed certificate issuer.
- Allow only HTTPS traffic at the ingress layer.
- Enable HSTS to reduce protocol downgrade risks.
- Use Kubernetes NetworkPolicies to restrict which pods can reach the LLM service.

### Example NetworkPolicy
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: llm-api-ingress
spec:
  podSelector:
    matchLabels:
      app: llm-api
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: api-gateway
```

---

## 4. Authentication and authorization
Treat every request as untrusted and enforce fine-grained identity controls.

### Anti-pattern
Avoid sending provider secrets directly in API requests:

```http
Authorization: Bearer sk-xxxx
```

### Recommended approach
- Use OAuth2 / OIDC for user and service identity.
- Issue short-lived JWT tokens (5–15 minutes).
- Enforce minimal scopes, for example:
  - `llm:generate`
  - `llm:stream`
  - `llm:admin`

---

## 5. Rate limiting and cost control
Limit usage by identity, client, and model to avoid runaway costs.

- Enforce per-user and per-tenant limits.
- Apply token-based quotas to control prompt/input size.
- Use IP-based throttling for anonymous or legacy clients.
- Apply model-specific limits for expensive workloads.

### Example quotas
- `60 requests / minute`
- `max 8k tokens per request`
- `max 50k tokens per day / user`

---

## 6. Secrets management
Store credentials securely and never bake them into plain text files or container images.

Avoid:
- ConfigMaps for secrets
- `.env` files checked into source
- hardcoded keys in code

Use:
- Vault, AWS Secrets Manager, Azure Key Vault, or Google Secret Manager
- External Secrets Operator or secrets CSI drivers

### Kubernetes secret usage
```yaml
env:
  - name: OPENAI_API_KEY
    valueFrom:
      secretKeyRef:
        name: llm-secrets
        key: openai
```

---

## 7. Prompt injection protection
Defend against malicious input that can alter behavior or cause data leakage.

- Keep system prompts static and controlled by the service.
- Whitelist allowed functions and tool calls.
- Validate user input with regex, heuristics, and length limits.
- Run any external tool execution in isolated sandboxes.

---

## 8. Observability and auditing
Track behavior, usage, and failures without exposing sensitive prompt content.

Log essential metadata only:
- `user_id`
- token usage
- model selection
- request latency
- error conditions

> Do not log raw prompts or responses in production.

Recommended observability stack:
- Prometheus
- Grafana
- Loki
- OpenTelemetry

---

## 9. Pod security
Harden Kubernetes workloads with runtime and filesystem protections.

- Run containers as non-root.
- Enable a read-only root filesystem where possible.
- Set CPU and memory resource limits.
- Use seccomp and AppArmor profiles.

### Example security context
```yaml
securityContext:
  runAsNonRoot: true
  readOnlyRootFilesystem: true
```

---

## 10. Advanced security controls
For mature deployments, add stronger isolation and operational safeguards.

- Use mutual TLS for service-to-service communication.
- Deploy a web application firewall (WAF) at the edge.
- Use canary deployments to test changes safely.
- Add feature flags for rapid rollout and rollback.
- Implement a kill switch to disable the API under emergency conditions.

---

## 11. Data model and database schema
A normalized schema supports identity, audit, rate control, usage tracking, and model settings.

### Core tables

#### `tenants`
- `id` (PK)
- `name`
- `domain`
- `status`
- `created_at`
- `updated_at`

#### `users`
- `id` (PK)
- `tenant_id` (FK → tenants.id)
- `email`
- `username`
- `password_hash`
- `is_active`
- `created_at`
- `updated_at`

#### `api_clients`
- `id` (PK)
- `tenant_id` (FK → tenants.id)
- `name`
- `type` (`service`, `user`, `machine`)
- `redirect_uri`
- `created_at`
- `updated_at`

#### `api_keys`
- `id` (PK)
- `client_id` (FK → api_clients.id)
- `key_hash`
- `secret_hash`
- `expires_at`
- `is_revoked`
- `created_at`
- `revoked_at`

#### `oauth_tokens`
- `id` (PK)
- `user_id` (FK → users.id)
- `client_id` (FK → api_clients.id)
- `token_type`
- `access_token_hash`
- `refresh_token_hash`
- `expires_at`
- `scopes`
- `created_at`
- `revoked_at`

#### `scopes`
- `id` (PK)
- `name`
- `description`

#### `client_scopes`
- `client_id` (FK → api_clients.id)
- `scope_id` (FK → scopes.id)
- primary key (`client_id`, `scope_id`)

#### `roles`
- `id` (PK)
- `name`
- `description`

#### `user_roles`
- `user_id` (FK → users.id)
- `role_id` (FK → roles.id)
- primary key (`user_id`, `role_id`)

### Usage and quota tables

#### `rate_limit_profiles`
- `id` (PK)
- `name`
- `requests_per_minute`
- `tokens_per_request`
- `tokens_per_day`
- `created_at`

#### `usage_quotas`
- `id` (PK)
- `tenant_id` (FK → tenants.id)
- `user_id` (FK → users.id, nullable)
- `profile_id` (FK → rate_limit_profiles.id)
- `max_requests_per_minute`
- `max_tokens_per_request`
- `max_tokens_per_day`
- `created_at`
- `updated_at`

#### `usage_records`
- `id` (PK)
- `tenant_id` (FK → tenants.id)
- `user_id` (FK → users.id, nullable)
- `client_id` (FK → api_clients.id)
- `request_id`
- `model_name`
- `request_tokens`
- `response_tokens`
- `total_tokens`
- `status`
- `latency_ms`
- `created_at`

### Security and audit tables

#### `request_logs`
- `id` (PK)
- `tenant_id` (FK → tenants.id)
- `user_id` (FK → users.id, nullable)
- `client_id` (FK → api_clients.id)
- `path`
- `method`
- `status_code`
- `source_ip`
- `user_agent`
- `tokens_used`
- `model_name`
- `error_code`
- `created_at`

#### `audit_events`
- `id` (PK)
- `tenant_id` (FK → tenants.id)
- `user_id` (FK → users.id, nullable)
- `event_type`
- `resource_type`
- `resource_id`
- `details`
- `ip_address`
- `created_at`

#### `allowed_functions`
- `id` (PK)
- `tenant_id` (FK → tenants.id)
- `name`
- `description`
- `enabled`
- `created_at`

#### `model_configurations`
- `id` (PK)
- `tenant_id` (FK → tenants.id)
- `model_name`
- `max_tokens`
- `temperature`
- `top_p`
- `created_at`
- `updated_at`

### Indexes and constraints
- Unique indexes on `users.email`, `api_clients.name`, `api_keys.key_hash`, `oauth_tokens.access_token_hash`
- Foreign keys to enforce tenant isolation
- Partition or daily rollups for `usage_records` and `request_logs` on high-volume workloads

---

## 12. Optimal folder structure
Organize the app for separation of concerns, testability, and Kubernetes deployment.

### Recommended root layout

```
/README.md
/Dockerfile
/docker-compose.yml
/helm/ or /k8s/
/infra/             # manifests, policies, deployment templates
/src/
  /api/
    __init__.py
    main.py
    config.py
  /routes/
    health.py
    auth.py
    llm.py
  /controllers/
    auth_controller.py
    llm_controller.py
  /services/
    auth_service.py
    llm_service.py
    rate_limit_service.py
    prompt_safety_service.py
  /db/
    models.py
    repositories.py
    migrations/
  /auth/
    oidc.py
    jwt.py
    tokens.py
  /security/
    secrets.py
    network_policy.py
    policy.py
  /telemetry/
    logging.py
    metrics.py
    tracing.py
  /schemas/
    request.py
    response.py
    audit.py
  /utils/
    validators.py
    timing.py
/tests/
  /unit/
  /integration/
  /e2e/
/scripts/
  deploy.sh
  migrate.sh
  seed_data.sh
```

### Kubernetes and deployment layout

```
/infra/k8s/
  ingress.yaml
  network-policy.yaml
  deployment.yaml
  service.yaml
  hpa.yaml
  secrets.yaml
/infra/helm/
  charts/
/infra/cert-manager/
  clusterissuer.yaml
```

### Notes
- Keep prompt templates and injection rules in `/src/security`.
- Keep observability exporters in `/src/telemetry`.
- Put provider-specific wrappers and client code behind `/src/services` so the API layer remains framework-agnostic.
- Use `/src/db/migrations` for schema migrations and `/src/db/repositories.py` for data access.

---

## Summary
Secure your LLM API like a production financial service: protect secrets, control costs, validate inputs, and monitor behavior continuously.
