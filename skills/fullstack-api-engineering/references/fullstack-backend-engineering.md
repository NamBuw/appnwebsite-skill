# Full-Stack Backend Engineering

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This module governs backend service authoring across Spiral Stages `3A`, `3B`, and `3C` (Node.js/TypeScript, Python/FastAPI, ASP.NET Core, and Edge/Worker runtimes).
It enforces **Phase 3A System-First** dependency boundaries, **Deep Module** design, **Anti-Overengineering ("Least Code, Highest Craft")**, and deterministic resilience without premature distributed infrastructure.

---

## 1. Decision Framework

### 1.1 Simplest High-Craft Backend Baseline & Anti-Overengineering Gate

Before adding a queue broker, cache cluster, microservice, or interface hierarchy, run the four simplicity checks:
1. **Option A First**:
   - Start with a **Modular Monolith** backed by a single ACID PostgreSQL database (`FOR UPDATE SKIP LOCKED` outbox/job table, CTEs, partial indexes).
   - Reject Redis, RabbitMQ, Kafka, or separate microservices unless Option A fails a measured load benchmark.
2. **Stdlib Before Dependencies**:
   - Reject any new package when standard library primitives (`crypto`, `URL`, `fetch`, `Intl`, Python `sqlite3`/`urllib`, .NET `ProblemDetails`/`AddValidation()`) solve the need in `<= 150` tested lines.
3. **Rule of Three for Abstractions**:
   - Never create `IFooService -> FooServiceImpl -> IFooRepo -> FooRepoImpl` for a single implementation.
   - Apply the seam rule: *"One adapter is a hypothetical seam; two adapters are a real seam."*
4. **Verified Constraint vs. YAGNI**:
   - Escalating to Option B requires a measured failure metric on Option A or a cited compliance/isolation rule (`NFR-xx`).
   - Document intentional simplicity bounds inline: `// shortcut: <known limit>, <when to upgrade>`.

### 1.2 Runtime, Concurrency & Durable Execution Matrix

| Workload Shape | Simplest Option A | Scale-Up Option B (Evidence Required) | Hard Runtime & Safety Constraints |
|---|---|---|---|
| **Standard CRUD & SSR API** | Node.js / ASP.NET Core Minimal API / FastAPI monolith | Edge Workers (stateless routing/transforms, `< 1ms` cold start) | Edge limits: `25s–30s` wall cap, `128 MB` RAM; stream large bodies; zero module-global request state |
| **Short Async Side Effects (`< 5 min`)** | `after()` / `ctx.waitUntil()` or Postgres `SKIP LOCKED` outbox | Managed Queues (`@vercel/queue` / Cloudflare Queues / SQS) | At-least-once delivery assumed; require `idempotency_key`, lease `visibilityTimeout`, `<= 5` retries |
| **Multi-Step Durable / HITL (`hours–weeks`)** | DB state machine + cron sweep (`shortcut: < 1k active`) | Workflow DevKit (`"use workflow"`/`"use step"`) or Temporal | Orchestration layer MUST be replay-deterministic; run all I/O strictly inside steps/activities |
| **Realtime / Per-Entity Coordination** | SSE or single-node WebSocket/SignalR hub | Multi-node pub/sub backplane or Cloudflare Durable Objects | Hubs are transport boundaries only—zero domain logic inside socket handlers; exponential reconnect |
| **Internal Service RPC** | Typed internal module calls or flat JSON over HTTPS | gRPC (`.proto` over HTTP/2) or Worker Service Bindings | Adopt `.proto` only when both ends are owned AND streaming throughput is proven necessary |

### 1.3 Clean Layering & Dependency Classification

Enforce unidirectional dependency flow matching `control-manifest.md`:

```
Transport Boundary (Route / Minimal API / Worker fetch / SignalR Hub)
        │  parses input DTO, enforces AuthN+AuthZ, maps RFC 9457 errors
        ▼
Application / Domain Core (Deep Modules: pure rules + transactions)
        │  calls ports ONLY at true external/substitutable boundaries
        ▼
Infrastructure Adapters (Typed SQL / DbContext / Pooled HTTP / Outbox)
```

Classify every dependency before writing interfaces or tests:
- **In-process pure logic**: Zero mocks; invoke directly.
- **Local-substitutable stores** (Postgres, SQLite, temp dir):
  - Test against real ephemeral instances (PGLite, test containers), not mock repos.
- **Remote-but-owned services**:
  - Define a narrow boundary port and verify contract parity separately.
- **True third-party externals** (payments, email, SMS, LLM APIs):
  - Inject a minimal interface (`2–4` methods max) for deterministic test fakes.

### 1.4 Quantitative Engineering Thresholds

- **Module & Function Shape**:
  - Target deep modules (`1–4` exported functions hiding rich invariants).
  - Split functions exceeding `~50` lines or `3` nesting levels.
- **Database & Pool Hygiene**:
  - Use connection pooling (`IHttpClientFactory`, singleton DB pool, or Cloudflare Hyperdrive).
  - Never instantiate `new HttpClient()` per request.
  - Never capture a scoped `DbContext` inside a singleton or background loop without an explicit scope factory.
- **Outbound Resilience**:
  - Set connect timeout (`<= 3s`) and read timeout (`<= 10s–15s`).
  - Use jittered exponential backoff on idempotent calls only (`<= 3` retries) paired with circuit breakers.
- **Token Economy**:
  - Co-locate vertical slices (`handler + domain + query + test`) by feature so agents inspect `1–2` files instead of `8` horizontal folders.
  - Query schemas and slices via targeted line ranges rather than full-repo scans.

---

## 2. Step-by-Step Workflow

1. **Verify Phase 3A Unlock & Simplicity Baseline** *(Owner: Backend Engineer | Inputs: `architecture.md`, `control-manifest.md`, `data-model.md` | Output: Slice plan)*
   - Confirm Phase 3A `system-foundation-gate.md` is `UNLOCKED` (unless running a `<= 2`-file Direct-mode hotfix).
   - For critical internal module seams, apply **Design It Twice**: sketch 2–3 distinct interface shapes and select the deepest interface with fewest caller assumptions.
   - Lock the Option A baseline and note bounded shortcuts (`// shortcut: <limit>, <upgrade trigger>`).

2. **Build the Thin Transport & AuthZ Boundary** *(Owner: Backend Engineer | Inputs: `api-contract-spec.md` | Output: Route / Minimal API / Worker handler)*
   - Follow strict middleware ordering (`ForwardedHeaders -> ExceptionHandler/HSTS -> HTTPS -> Static -> Routing -> CORS -> AuthN -> AuthZ -> RateLimit -> Endpoints`).
   - Parse and validate all inputs at the boundary using one typed schema (Zod, Pydantic, or .NET `AddValidation()`), rejecting unknown query sort/filter keys with `422`.
   - Enforce AuthN AND resource-ownership AuthZ inside every handler or RPC entry—never rely on gateway path matchers alone.
   - Separate public DTOs from persistence entities so internal fields (`password_hash`, `secret_token`) never serialize; map all errors to RFC 9457 `application/problem+json`.

3. **Implement Deep Domain Core, Optimistic Locking & Transactional Outbox** *(Owner: Backend Engineer | Inputs: `data-model.md` | Output: Domain module + atomic SQL)*
   - Write domain transitions as pure functions returning results instead of mutating caller inputs.
   - Prevent check-then-write lost updates with database concurrency controls:
     ```sql
     UPDATE orders
     SET status = $1, version = version + 1
     WHERE id = $2 AND tenant_id = $3 AND version = $4
     RETURNING id, status, version; -- 0 rows -> 409 Conflict
     ```
   - Persist domain mutations and outbound `outbox_events` rows inside **one ACID transaction**, polled by workers via `FOR UPDATE SKIP LOCKED`.

4. **Isolate Durable Workflows & Post-Response Work** *(Owner: Backend Engineer | Inputs: Reliability `NFR` targets | Output: Deterministic workflow + idempotent steps)*
   - Separate durable execution strictly into two layers:
     - **Workflow / Orchestrator**: Deterministic control flow (`sleep`, timers, signals/hooks). Zero `fetch()`, DB queries, `Date.now()`, or `Math.random()`.
     - **Step / Activity**: Full I/O permitted; must be idempotent; raise terminal `FatalError` on `4xx` business failures vs `RetryableError` with `retryAfter` on `429`/`5xx`.
   - Isolate debug logs from primary workflow streams (`namespace`), and apply per-tenant fairness keys on multi-tenant task queues.
   - In Edge/serverless runtimes, schedule post-response telemetry via `after()` or `ctx.waitUntil(promise)` without detaching `ctx`, and lint against floating promises.
   - Example deterministic boundary split:
     ```ts
     export async function orderWorkflow(orderId: string) {
       const charged = await chargeOrderStep(orderId); // side effects isolated here
       if (!charged.ok) return { status: "failed" };
       await sleep("24h"); // deterministic timer replayed safely
       await sendReceiptStep(orderId);
       return { status: "completed" };
     }
     ```

5. **Execute Pre-Ship Deletion & Condensation Pass + Quiet Verification** *(Owner: Backend Engineer | Tool: Test runner + linter | Output: Lean verified diff)*
   - Run focused tests quietly (`pytest -q --tb=short`, `npm test -- --silent`, or `dotnet test --verbosity minimal`).
   - Run the **Condensation Pass**:
     - Inline `< 20`-LOC pass-through wrappers and redundant 1:1 DTO mappers.
     - Delete dead exports, unused DI registrations, and packages replaceable by `<= 50` LOC of stdlib.
     - Confirm zero module-global mutable state and valid `shortcut:` annotations.
   - **Mandatory Post-Deletion Re-Test**: Re-run full typecheck, build, and tests **after** final deletions.

---

## 3. Reusable Artifact & Template

Link every backend slice and async boundary to:
- [API Contract Spec](../templates/api-contract-spec.md)
  - Section 1 (Option A Selection), Section 2 (Endpoint/AuthZ Inventory), Section 5 (Async Webhooks, Workflows & Seams)
- [Code Review Report](../templates/code-review-report.md)
  - Section 4 (Lean & Simplicity Audit) and Section 5 (Fresh Post-Edit Verification)

### Backend Module & Concurrency Contract Schema

| Field | Required Specification | Example Value |
|---|---|---|
| `module_slice` | Feature-cohesive path & narrow exported surface | `src/slices/orders/` (`createOrder`, `cancelOrder`) |
| `dependency_category` | `In-process` \| `Local-substitutable` \| `Remote-owned` \| `External` | `Local-substitutable (Postgres) + External (Stripe)` |
| `concurrency_control` | Optimistic `version`, `SKIP LOCKED`, or unique index | `Optimistic version column -> 409 on 0 rows` |
| `outbox_idempotency` | Atomic outbox table + idempotency retention window | `outbox_events` in TX + `24h` `Idempotency-Key` |
| `workflow_boundary` | Deterministic workflow vs side-effect step split | `Workflow pure state; step captures payment` |
| `resilience_budget` | Connect/read timeouts, max retries, circuit threshold | `connect 2s, read 8s, 3 jittered retries on 5xx` |
| `shortcut_annotation` | Explicit simplicity bound & upgrade metric | `// shortcut: Postgres outbox; queue > 500/min` |

---

## 4. Verification Checklist

- [ ] Phase 3A `system-foundation-gate.md` is unlocked and imports obey `control-manifest.md` dependency direction.
- [ ] Option A (Modular Monolith + Postgres `SKIP LOCKED` + stdlib) was evaluated before adding queues, caches, or new packages.
- [ ] Every endpoint validates input at the boundary, enforces AuthN + resource AuthZ internally, and separates DTOs from DB entities.
- [ ] Concurrent state mutations use optimistic `version` checks, `SELECT ... FOR UPDATE`, or unique constraints instead of check-then-write races.
- [ ] Domain writes and async events commit atomically via a transactional outbox with idempotent step execution.
- [ ] Durable workflow code contains zero non-deterministic calls (`Date.now()`, `Math.random()`, direct I/O) outside step/activity functions.
- [ ] Outbound HTTP/DB clients use shared pools/factories with explicit timeouts, bounded jittered retries, and zero floating promises or global state.
- [ ] Pre-ship Deletion/Condensation Pass collapsed shallow wrappers and the full test suite passed **after** final deletions.

---

## 5. Hard Quality Gate

- **PASS Criteria**:
  - Compiler/typechecker, linter, and unit + integration tests against a real local DB exit `0` **after** the final condensation edit.
  - Zero unauthenticated/non-AuthZ handlers.
  - Zero `IFoo -> FooImpl` single-implementation boilerplate chains.
  - Zero floating promises and documented `shortcut:` limits on every bounded baseline.
- **FAIL Criteria**:
  - Missing boundary input validation or AuthZ ownership check (`P0`).
  - Dual-write to DB + external broker/email without transactional outbox (`P1`).
  - Non-deterministic I/O inside a replay workflow (`P1`).
  - Per-request `new HttpClient()`, unbounded body buffering in Edge workers, or skipped post-deletion re-test (`FAIL`).

```bash
# Run typecheck, static hygiene scans, and quiet integration tests after final deletion pass
npx tsc --noEmit && npm test -- --silent
# Python / .NET equivalents:
# pytest -q --tb=short
# dotnet test --verbosity minimal
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Enterprise Boilerplate Cascade** | 1:1 `IUserService -> UserImpl -> IUserRepo` multiplies files without hiding complexity | Single-impl interfaces; `< 15` LOC pass-throughs | Vertical slice (`users.ts`) with typed SQL; ports only at externals |
| **Premature Microservices & Broker Sprawl** | Splitting low-QPS domains across Kafka adds network failures and dual-write bugs | Queues/services for `< 1k` req/min without NFR proof | Modular Monolith + Postgres `SKIP LOCKED` outbox |
| **Dual-Write Without Transactional Outbox** | Publishing after `COMMIT` drops events; before `COMMIT` leaks ghost events | Separate `db.save(); queue.publish();` calls | Insert domain row + `outbox_events` row in one ACID TX |
| **Non-Deterministic Replay Workflows** | `Date.now()`, `Math.random()`, or `fetch()` inside workflows breaks replay | Direct I/O or clock reads inside workflow file | Move all I/O into idempotent `"use step"` / Activity functions |
| **Module-Global State & Floating Promises** | Top-level `let currentUser` leaks across requests; unawaited calls drop errors | Mutable globals; missing `await` or `waitUntil` | Pass request context explicitly; lint `no-floating-promises` |
| **Check-Then-Write Races & Unbounded Retries** | App-memory checks lose updates; unjittered loops trigger retry storms | `SELECT` then `UPDATE` without `version`/`FOR UPDATE` | Atomic `WHERE version = $v`; bounded jittered backoff + `FatalError` |
