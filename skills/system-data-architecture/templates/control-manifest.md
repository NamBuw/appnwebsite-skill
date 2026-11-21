# Programmer Control Manifest

> **Canonical Output Path**: `docs/architecture/control-manifest.md`

- **Manifest Version**: `[YYYY-MM-DD]`
- **Last Updated**: `[YYYY-MM-DD]`
- **Status**: `[Active | Draft — Pending Foundation Acceptance]`
- **ADRs Covered (Accepted Only)**: `[ADR-0001, ADR-0002]`
- **ADRs Excluded & Status**: `[None | ADR-0003 (Proposed)]`

> **Purpose**: Flat, non-prose programmer rule sheet extracted strictly from `Accepted` ADRs and verified runtime configs. ADRs explain *why*; this manifest states *what* engineers must and must never do. If `Last Updated` lags behind any newly accepted ADR date, regenerate before starting implementation.

---

## 1. Allowed Dependency Graph & Layer Rules

```text
[Presentation / HTTP / UI] ---> [Application / Use Cases] ---> [Domain Policy]
                                          ^                          ^
                                          |                          |
                                [Infrastructure / DB / External Adapters]
```

| Source Layer | Allowed Imports | Forbidden Imports | Source Citation |
|---|---|---|---|
| `Domain` | `Language stdlib, pure domain types` | `HTTP frameworks, ORMs, SQL drivers, UI, spikes/` | `[ADR-0001]` |
| `Application` | `Domain, port interfaces` | `Concrete DB clients, HTTP request objects, UI components` | `[ADR-0001]` |
| `Infrastructure` | `Application ports, Domain, approved SDKs/drivers` | `Presentation controllers, cross-module internal tables` | `[ADR-0001]` |
| `Presentation` | `Application use cases, DTO schemas` | `Direct SQL/ORM queries, Infrastructure adapters, spikes/` | `[ADR-0001]` |

---

## 2. Layer-by-Layer Must-Do & Never-Do Rules

### 2.1 Foundation Layer (Persistence, Pooling, Security, Migrations)

| Rule Type | Directive | Source Citation |
|---|---|---|
| `Must-Do` | `[Use parameterized queries and least-privilege app DB role (no superuser).]` | `[ADR-0002]` |
| `Must-Do` | `[Set lock_timeout = '2s' and statement_timeout = '10s' on production DDL.]` | `[ADR-0003]` |
| `Never-Do` | `[Never concatenate variables into SQL or run bare CREATE INDEX without CONCURRENTLY.]` | `[ADR-0002, ADR-0003]` |

### 2.2 Core / Domain Layer (Bounded Contexts, Invariants, Errors)

| Rule Type | Directive | Source Citation |
|---|---|---|
| `Must-Do` | `[Enforce aggregate invariants in domain constructors/methods; reference other contexts by ID.]` | `[ADR-0001]` |
| `Never-Do` | `[Never perform network I/O or hold DB transactions across external HTTP calls.]` | `[ADR-0001]` |

### 2.3 Application & Feature Layer (Workflows, Outbox, Idempotency)

| Rule Type | Directive | Source Citation |
|---|---|---|
| `Must-Do` | `[Require Idempotency-Key on state-mutating external endpoints and webhooks.]` | `[ADR-0004]` |
| `Never-Do` | `[Never mutate another bounded context's tables directly; emit domain event or call exposed port.]` | `[ADR-0001]` |

### 2.4 Presentation / API Boundary Layer (Validation, Caching, Masking)

| Rule Type | Directive | Source Citation |
|---|---|---|
| `Must-Do` | `[Validate all inputs at edge; set Cache-Control: no-store on PII/sensitive responses.]` | `[ADR-0005]` |
| `Never-Do` | `[Never log raw user objects, tokens, passwords, or stack traces in client responses.]` | `[ADR-0005]` |

---

## 3. Shared Contracts & Source-of-Truth Paths

| Artifact | Canonical Repo Path | Owner Module | Drift Check |
|---|---|---|---|
| `System Architecture` | `docs/architecture/architecture.md` | `Platform / Architect` | `[Verified against walking skeleton]` |
| `Data Model` | `docs/architecture/data-model.md` | `Data / Backend` | `[Verified against schema & RLS tests]` |
| `Migration Plan` | `docs/architecture/migration-plan.md` | `Data / Backend` | `[Verified via schema migration CI]` |
| `Foundation ADRs` | `docs/architecture/adr/adr-*.md` | `Platform / Architect` | `[Status: Accepted & acyclic DAG]` |
| `API Contract` | `docs/contracts/openapi.yaml` | `API / Application` | `[Contract test suite]` |
| `DPIA & Privacy Matrix` | `docs/architecture/dpia-privacy.md` | `Security / Privacy` | `[PII tag audit]` |
| `Foundation Gate` | `docs/spiral/system-foundation-gate.md` | `Platform / Architect` | `[Unlocked prior to Phase 3B]` |

---

## 4. Global Naming, Runtime Ceilings & Approved Libraries

- **Naming Conventions**: `[PostgreSQL identifiers in lowercase snake_case; domain modules named after bounded contexts.]`
- **Runtime Ceilings**: `[API read p95 <= 150 ms; API write p95 <= 300 ms; DB transaction hold <= 50 ms; PgBouncer pool <= (cores * 2) + spindles.]`
- **Approved Libraries**: `[List exact pinned packages per runtime — reject unapproved duplicate utilities.]`
- **Scoped Forbidden / Deprecated APIs**: `[List only APIs relevant to the chosen runtime/database stack with their approved replacement.]`

## References

- [ADRs & Control Manifest Guide](../references/adrs-and-control-manifest.md)
- [ADR Template](adr.md)
- [System & Data Architecture Router](../SKILL.md)
