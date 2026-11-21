# System Architecture: [System Name]

> **Canonical Output Path**: `docs/architecture/architecture.md`

- **Version**: `[1.0.0]`
- **Spiral ID**: `[S01 / Phase 3A]`
- **Rigor Tier**: `[minimal | standard | full]`
- **Last Updated**: `[YYYY-MM-DD]`
- **Owner**: `[Technical Architect / Lead Engineer]`
- **Linked Simplicity Record**: `[SIR-001]`
- **Linked PRD & NFR Baseline**: `[prd.md, nfr-slo-matrix.md]`

---

## 1. Architecture Principles & Simplicity Baseline

- **Option A Verification (Simplest High-Craft Baseline)**: `[Confirm Modular Monolith + single ACID relational DB or document measured NFR/compliance threshold justifying any split.]`
- **Governing Principle 1 (Inward Dependency Rule)**: `[Domain policy depends on zero frameworks, ORMs, or UI packages; infrastructure adapts to domain ports.]`
- **Governing Principle 2 (Exclusive Data Ownership)**: `[Each bounded context/module owns its tables exclusively; cross-module reads use defined interfaces.]`
- **Governing Principle 3 (Fail-Closed & Bounded I/O)**: `[All outbound calls define explicit timeouts, bounded retries with jitter, and idempotency keys.]`

---

## 2. C4 Context & Container Architecture

### 2.1 System Context (L1) & Trust Zones

| Actor / External System | Trust Zone | Protocol & Auth | Direction | Purpose |
|---|---|---|---|---|
| `[End User Browser / Mobile]` | `Public Edge` | `HTTPS + Session / OAuth 2.1` | `Inbound` | `[Primary product surface]` |
| `[Payment / Identity Provider]` | `External Third-Party` | `HTTPS + Webhook HMAC + mTLS/API Key` | `Bidirectional` | `[Billing, auth federation]` |

### 2.2 Container Diagram (L2)

```text
+-------------------------------------------------------------------+
| Public Edge (CDN / WAF / TLS Termination)                         |
+---------------------------------+---------------------------------+
                                  | HTTPS (rate-limited, timeouts)
                                  v
+-------------------------------------------------------------------+
| App Runtime Container (Modular Monolith)                          |
|  [Presentation / API] -> [Application] -> [Domain] <- [Infra]     |
|  Background Worker (in-process or separate worker reading outbox) |
+---------------------------------+---------------------------------+
                                  | TLS, pooled (PgBouncer), least-priv role
                                  v
+-------------------------------------------------------------------+
| Private Data Plane (Single ACID PostgreSQL + Object Storage)      |
+-------------------------------------------------------------------+
```

---

## 3. System Layer Map & Module Ownership

Stack layers follow strict inward dependency: `Presentation -> Application -> Domain <- Infrastructure` (`Platform` is the runtime, OS, and database engine—not project code).

| Module / Context | Layer | Owns (Exclusive State) | Exposes (Public Interface) | Consumes | Platform / External APIs |
|---|---|---|---|---|---|
| `[identity]` | `Domain / App` | `[users, sessions, memberships]` | `[AuthService, verifySession()]` | `[crypto, mail port]` | `[PostgreSQL, OIDC/SMTP]` |
| `[billing]` | `Domain / App` | `[subscriptions, invoices, outbox]` | `[BillingService, handleWebhook()]` | `[identity read port]` | `[PostgreSQL, Stripe API]` |

---

## 4. Deep Modules, Seams & Interface Contracts

For the 1–2 highest-leverage seams evaluated with `DESIGN-IT-TWICE`, record the selected interface and adapter category (`In-Process` | `Local-Substitutable` | `Remote-Owned` | `True-External`).

| Module / Seam | Interface & Invariants | Ordering & Concurrency | Error Modes | Adapter Strategy |
|---|---|---|---|---|
| `[PaymentPort]` | `[charge(idempotencyKey, amountCents, currency) -> Receipt]` | `[Idempotent per key; never inside DB tx]` | `[TransientTimeout, CardDeclined, DuplicateKey]` | `[True-External: injected port + mock adapter]` |
| `[OutboxQueue]` | `[enqueue(tx, topic, payload) -> eventId]` | `[Atomic with aggregate write; SKIP LOCKED]` | `[MaxRetriesExhausted -> DLQ]` | `[Local-Substitutable: real Postgres in test]` |

- **`DESIGN-IT-TWICE` Summary**: `[State the 3 candidate interface designs explored for core seam(s), why shallow wrappers were deleted, and why the chosen interface maximizes depth and caller locality.]`

---

## 5. Data Flows, State Machines & Failure Paths

### 5.1 Synchronous Request Path (With Thread / Network Crossings)

```text
Client --[HTTPS/JSON]--> API Edge (validate schema + auth + rate-limit)
  --[in-process call]--> Application Use Case (load aggregate, enforce invariants)
  --[DB tx < 50ms]--> PostgreSQL (write aggregate + outbox row, COMMIT)
  --[200/201 JSON]--> Client
  (Failure: validation -> 400 RFC 9457; auth -> 401/403; timeout -> 504 + traceId)
```

### 5.2 Asynchronous Outbox / Saga State Machine

```text
[PENDING] --(worker claims via SKIP LOCKED)--> [PROCESSING]
   |                                                |
   | (permanent 4xx / max_attempts exceeded)        |--(external 200 OK)--> [SUCCEEDED]
   v                                                |
[DEAD_LETTER] <--(retry budget exhausted)-----------+--(transient 5xx/timeout, backoff+jitter)--> [PENDING]
```

### 5.3 Boot & Initialization Order

1. `[Load and validate typed environment config + KMS/secret references (fail fast on missing keys).]`
2. `[Verify PostgreSQL connectivity and schema migration version readiness.]`
3. `[Start HTTP listener and background outbox worker; expose /healthz and /readyz.]`

---

## 6. Cross-Cutting Infrastructure Policies

| Concern | Chosen Policy & Quantitative Budget | Rationale & Deletion Check |
|---|---|---|
| `Caching` | `[HTTP ETag / Cache-Control; DB indexes before Redis]` | `[Avoid separate Redis cluster until p95 read > 200 ms]` |
| `Rate Limiting` | `[Token bucket at edge: 100 req/min/IP; 20 auth/min]` | `[Protects auth & expensive writes without custom broker]` |
| `Idempotency` | `[Idempotency-Key header + unique DB constraint, 24h TTL]` | `[Prevents double charge/mutation on client retries]` |
| `Timeouts & Retries` | `[DB stmt 5s; HTTP outbound 3s; max 3 retries + full jitter]` | `[Prevents thread/pool exhaustion under downstream stalls]` |

---

## 7. Walking-Skeleton Repo Layout & Sign-Off

```text
src/
  modules/
    <context>/
      domain/         # Pure entities, value objects, domain invariants (0 framework imports)
      application/    # Use cases, port interfaces, transaction boundaries
      infrastructure/ # Postgres repositories, external adapters
      presentation/   # HTTP/API handlers, schema validation
  shared/             # Strictly minimal cross-cutting primitives (logger, error types, db pool)
tests/
  smoke/              # End-to-end walking skeleton test against real DB
```

- **Walking-Skeleton Smoke Command**: `[e.g., npm test -- tests/smoke/ or pytest -q tests/smoke/]`
- **Technical Feasibility Sign-Off**: `[PASS | CONCERNS | NOT ASSESSED | FAIL]` — `[Reviewer role, date, and verification receipt]`

## References

- [Greenfield System Architecture Guide](../references/greenfield-system-architecture.md)
- [ADRs & Control Manifest Guide](../references/adrs-and-control-manifest.md)
- [System & Data Architecture Router](../SKILL.md)
