# Secure LLM API in Kubernetes

## 1. Threat Model
LLM APIs introduce unique attack vectors:
- API key leakage
- Cost abuse (prompt flooding, replay attacks)
- Prompt injection / data exfiltration
- Denial of Service (DoS)
- Lateral movement inside cluster

---

## 2. Reference Architecture

```
[Client]
   ↓
[API Gateway / Ingress]
   ↓
[AuthN/AuthZ Layer]
   ↓
[LLM API Service]
   ↓
[LLM Provider / Model]
```

---

## 3. Ingress & Network Security

- Enforce TLS everywhere (cert-manager, Let’s Encrypt)
- Only HTTPS traffic
- Enable HSTS

### Network Policies (example)
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
spec:
  podSelector:
    matchLabels:
      app: llm-api
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: api-gateway
```

---

## 4. Authentication & Authorization

### Anti-pattern
```
Authorization: Bearer sk-xxxx
```

### Recommended
- OAuth2 / OIDC
- Short-lived JWT (5–15 min)
- Scopes:
  - llm:generate
  - llm:stream
  - llm:admin

---

## 5. Rate Limiting & Cost Control

- Per user limits
- Token-based limits
- IP-based limits
- Model-based limits

Example:
- 60 req/min
- max 8k tokens/request
- max 50k tokens/day/user

---

## 6. Secrets Management

Avoid:
- ConfigMaps
- .env files
- hardcoded secrets

Use:
- Vault / Secret Manager
- External Secrets Operator

Example:
```yaml
env:
- name: OPENAI_API_KEY
  valueFrom:
    secretKeyRef:
      name: llm-secrets
      key: openai
```

---

## 7. Prompt Injection Protection

- Hardcoded system prompts
- Function whitelist
- Input validation (regex, heuristics)
- Sandbox tool execution

---

## 8. Observability & Auditing

Log:
- user_id
- token usage
- model
- latency
- errors

Do NOT log prompts in production.

Stack:
- Prometheus
- Grafana
- Loki
- OpenTelemetry

---

## 9. Pod Security

- Run as non-root
- Read-only filesystem
- Resource limits
- seccomp / AppArmor

Example:
```yaml
securityContext:
  runAsNonRoot: true
  readOnlyRootFilesystem: true
```

---

## 10. Advanced Security

- mTLS (service-to-service)
- WAF
- Canary deployments
- Feature flags
- Kill switch

---

## TL;DR

Treat LLM APIs like financial systems, not chatbots.
