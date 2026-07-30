# Axorks OS — Security Architecture

> OWASP Top 10 | Zero Trust | Defense in Depth

---

## 1. Security Principles

1. **Least privilege** — users get minimum permissions needed
2. **Defense in depth** — multiple layers, no single point of failure
3. **Zero trust** — verify every request, even internal
4. **Secure by default** — safe defaults, opt-in for risky features
5. **Audit everything** — immutable audit trail for sensitive actions
6. **AI safety** — AI never executes destructive actions without confirmation

---

## 2. Authentication

| Mechanism | Implementation |
|-----------|----------------|
| Email/password | bcrypt (cost 12) or argon2 |
| OAuth 2.0 | Google, Microsoft (PKCE flow) |
| 2FA | TOTP (RFC 6238), backup codes |
| Session tokens | JWT RS256, 15-min access, 7-day rotating refresh |
| API keys | Prefixed (`axk_live_`), hashed at rest, scoped permissions |
| Password policy | Min 12 chars, breach check via HaveIBeenPwned API |

### JWT Claims

```json
{
  "sub": "user_uuid",
  "org_id": "organization_uuid",
  "workspace_id": "workspace_uuid",
  "roles": ["admin"],
  "permissions": ["leads:read", "leads:write"],
  "iat": 1234567890,
  "exp": 1234568790
}
```

---

## 3. Authorization (RBAC)

### Permission Model

```
Resource:Action pattern
  leads:read, leads:write, leads:delete, leads:assign
  projects:read, projects:write, projects:manage
  finance:read, finance:write, finance:approve
  settings:manage, users:invite, users:remove
  ai:use, automation:manage, integrations:manage
```

### Enforcement Layers

1. **Route guard** — FastAPI dependency checks JWT + permission
2. **Service layer** — Business rule authorization (e.g., owner-only delete)
3. **Repository layer** — Tenant scoping (organization_id filter always applied)
4. **Database** — Row-level security policies (future hardening)

### Client Portal Isolation

Portal users (`role: client`) can ONLY access:
- Their company's projects, invoices, documents
- Scoped via `portal_access` table linking user → company

---

## 4. Data Protection

| Layer | Method |
|-------|--------|
| In transit | TLS 1.3 everywhere (Cloudflare → Vercel → Railway → Neon) |
| At rest | Neon encryption (AES-256), R2/Cloudinary encryption |
| Sensitive fields | Application-level encryption for OAuth tokens, API keys (Fernet/AES-GCM) |
| PII | Minimal collection, optional fields, GDPR-ready export/delete |
| Backups | Encrypted, access-restricted, tested quarterly |

### Secrets Management

- **Never** in code or git
- Platform secrets: Vercel env, Railway env
- Rotation: API keys quarterly, JWT signing keys annually
- Separate secrets per environment (dev/staging/prod)

---

## 5. OWASP Top 10 Mitigations

| Threat | Mitigation |
|--------|------------|
| A01 Broken Access Control | RBAC + tenant scoping + permission checks on every endpoint |
| A02 Cryptographic Failures | TLS 1.3, bcrypt/argon2, encrypted tokens at rest |
| A03 Injection | Parameterized queries (SQLAlchemy), Pydantic/Zod validation |
| A04 Insecure Design | Threat modeling per phase, security review checklist |
| A05 Security Misconfiguration | Secure headers, minimal permissions, hardened Docker |
| A06 Vulnerable Components | Dependabot, pip-audit, npm audit in CI |
| A07 Auth Failures | Rate limiting login, account lockout, 2FA, secure sessions |
| A08 Data Integrity Failures | Signed JWTs, webhook signature verification |
| A09 Logging Failures | Structured audit logs, Sentry alerts on anomalies |
| A10 SSRF | Allowlist outbound URLs, no user-controlled fetch without validation |

---

## 6. HTTP Security Headers

```
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; ...
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

---

## 7. Rate Limiting

| Endpoint | Limit |
|----------|-------|
| Login | 5 attempts / 15 min per IP + email |
| API (authenticated) | 1000 req / min per org |
| API (unauthenticated) | 60 req / min per IP |
| AI endpoints | 100 req / hour per user (configurable) |
| File upload | 50 MB max, 20 files / hour |
| CSV import | 10K rows max per import |

**Implementation:** Redis sliding window counters via middleware.

---

## 8. CSRF & XSS

- **CSRF:** SameSite=Strict cookies, CSRF token for cookie-based auth flows
- **XSS:** React auto-escaping, DOMPurify for rich text, CSP headers
- **CORS:** Allowlist origins (production domain only)

---

## 9. Webhook Security

```python
# Verify webhook signatures
def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

- Idempotency keys on all webhook handlers
- Replay protection via timestamp validation (5-min window)

---

## 10. AI Security

| Rule | Implementation |
|------|----------------|
| No hallucinated business data | AI responses tagged; CRM updates require confirmation |
| Destructive actions | `ai_action_confirmations` table — user must approve |
| Prompt injection defense | System prompts isolated, user input sanitized, output filtered |
| Data isolation | AI context scoped to tenant; never cross-org data in prompts |
| PII in AI | Configurable: strip PII before sending to external AI providers |
| Audit | Log all AI requests: model, tokens, user, entity context |

---

## 11. Session Management

- Access token: 15 minutes, stored in memory (not localStorage)
- Refresh token: 7 days, httpOnly secure cookie, rotating on use
- Session revocation: Redis blocklist for compromised tokens
- Concurrent session limit: 5 per user (configurable)
- Force logout on password change

---

## 12. Compliance Readiness

| Standard | Preparation |
|----------|-------------|
| GDPR | Data export, right to deletion, consent tracking |
| SOC 2 Type II | Audit logs, access controls, encryption (future) |
| PCI DSS | Stripe handles card data — never store PANs |

---

## 13. Incident Response

1. **Detect** — Sentry alerts, anomaly detection on auth failures
2. **Contain** — Revoke sessions, disable compromised API keys
3. **Investigate** — Audit log query by user/IP/timeframe
4. **Recover** — Neon point-in-time recovery
5. **Notify** — Affected users within 72 hours (GDPR)

---

## 14. Security Checklist (Per Phase)

- [ ] All endpoints require authentication (except public portal pages)
- [ ] Tenant scoping verified on every query
- [ ] Input validated via Pydantic/Zod schemas
- [ ] Permissions checked before mutations
- [ ] Audit log entry for create/update/delete on business entities
- [ ] No secrets in code or logs
- [ ] Rate limiting applied
- [ ] Error messages don't leak internal details
- [ ] File uploads validated (type, size, scan)
- [ ] AI actions requiring confirmation implemented

---

*Security is not a phase — it is a property of every phase.*
