# Greenfield System Architecture

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

System architecture exists to absorb complexity behind clean, durable boundaries before feature code and user interfaces lock accidental coupling into place. During Spiral Q2 and Phase 3A, every structural choice must prove two things simultaneously: that it satisfies verified functional and non-functional constraints (`NFRs`), and that no simpler native topology achieves equal or higher reliability, maintainability, and latency.

---

## 1. Decision Framework

### 1.1 Anti-Overengineering & Radical Simplicity Gate ("Least Code, Highest Craft")

Before sketching containers or queues, run the four Socratic checks and surface **Option A (Simplest High-Craft Baseline)** first:

1. **Equal-or-Higher Simplicity**: Can one **Modular Monolith** backed by one **ACID PostgreSQL** DB satisfy every latency, throughput, and isolation NFR?
2. **Native-Primitive Substitution**: Which proposed brokers or caches can be replaced by PostgreSQL (`SKIP LOCKED` outbox, `tsvector`, `JSONB`), HTTP `ETag`/`Cache-Control`, and in-process calls?
3. **Verified Constraint vs. Hypothetical Scale**: Is every split or queue driven by a measured bottleneck today rather than imaginary future traffic?
4. **Conciseness & Leverage**: Does each layer hide real invariant logic behind a small interface, or merely forward arguments across boilerplate wrappers?

Escalate beyond Option A only when a concrete `NFR` threshold fails an Option A ablation test or compliance mandates physical isolation.

### 1.2 Topology Selection Matrix

| Topology | Verified Trigger Threshold | Moving Parts | Primary Failure Modes | Reversibility |
|---|---|---|---|---|
| **Option A: Modular Monolith + Single DB** | `<= 500 req/s`, small team (`<= 15`), shared transactions | 1 app process + 1 PostgreSQL (+ replica) | Boundary erosion if imports go unpoliced | High — extract at seam later |
| **Option B: Monolith + Outbox Worker** | Jobs `> 2 s` (PDF, mail, AI), webhooks, `50–1k jobs/s` | App + worker polling PG `SKIP LOCKED` | Poison-pill jobs without DLQ or backoff | High — same repo & schema |
| **Option C: Extracted Service** | `> 10x` asymmetric compute, PCI/HIPAA isolation, residency | `>= 2` deployables + RPC/events + split DBs | Partial failure, clock skew, split-brain | Low — wire contracts harden |

### 1.3 C4 Abstraction Depth by Rigor Tier

| C4 Level | Scope Captured | `minimal` Tier | `standard` Tier | `full` Tier |
|---|---|---|---|---|
| **L1: System Context** | Actors, external SaaS/APIs, trust zones | Required | Required | Required |
| **L2: Container** | Runtimes, DBs, object stores, workers, protocols | Required | Required | Required |
| **L3: Component / Module** | Bounded contexts, layers, `Owns / Exposes / Consumes` | Top modules | Required | Required |
| **L4: Code / Seam** | Port signatures, invariants, errors, `DESIGN-IT-TWICE` | Skip | Core 1–2 seams | Critical seams |

### 1.4 Deep Modules, Seams & Dependency Categories

Judge every boundary by **Depth** (behavioral leverage per unit of interface surface) and **Locality** (code read to verify a change), following MIT-licensed `mattpocock/skills/codebase-design`:

| Dependency Category | Concrete Examples | Seam & Adapter Strategy | Testing Strategy |
|---|---|---|---|
| **In-Process Domain** | Pricing math, state rules, validation | **No port/interface** — merge directly | Fast unit tests (`< 5 ms`) |
| **Local-Substitutable** | PostgreSQL (`PGLite`/Docker), SQLite, tmpfs | Direct module; **0 multi-adapter ports** | Real local DB/tmpfs; never mock SQL |
| **Remote but Owned** | Internal billing or worker HTTP API | Port at process seam; versioned wire contract | Contract tests + in-memory/HTTP stub |
| **True External** | Stripe, Twilio, OAuth IdP, LLM, SMTP | Narrow port (`1–3` methods) + fake adapter | Fake adapter in CI; sandbox smoke |

- **Two-Adapter Rule**: One implementation behind an interface is a speculative seam; two genuine runtime implementations justify a port.
- **Deletion Test**: Imagine deleting the module—if complexity vanishes, it was a pass-through wrapper; if invariant logic scatters across callers, the module earns its keep.

### 1.5 Reliability, Async, Caching & Rate-Limiting Thresholds

- **Caching**: Exhaust SQL indexes and HTTP `ETag` / `Cache-Control` first. Add Redis only when measured read `p95 > 200 ms`, with explicit invalidation owner and `<= 5 min` TTL.
- **Rate Limiting**: Enforce edge token-bucket/sliding-window limits (`100 req/min/IP` general API; `10–20 req/min` on auth/OTP) returning `429` with `Retry-After`.
- **Transactional Outbox vs. Saga**: Commit domain mutation + `outbox_events` in the **same ACID transaction** (`< 50 ms`). Use an orchestrated saga with compensating actions only across independent external systems.

---

## 2. Step-by-Step Workflow

Apply **Token Economy** throughout: establish requirement counts (`N_reqs`) before scanning large PRDs, use targeted heading greps on files `> 40 KB`, and query suite modules via `scripts/query_skill.py` rather than bulk-loading unrelated guides.

1. **Load Baseline Context & Verify Simplicity Record**
   - **Inputs**: `prd.md`, `nfr-slo-matrix.md`, `spiral-charter.md`, `simplicity-interrogation-record.md`.
   - **Owner**: System Architect / Lead Engineer.
   - **Action**:
     - Extract functional slices, NFR targets (`p95`, availability, RTO/RPO, peak load), and compliance constraints.
     - Verify Option A baseline assumptions before adding infrastructure nodes.
   - **Output**: Verified constraint baseline and risk list.

2. **Map C4 Context, Containers & Trust Zones**
   - **Inputs**: Constraint baseline and actor list.
   - **Owner**: System Architect.
   - **Action**:
     - Define actors, external SaaS, containers, and trust zones (`Public Edge -> App Runtime -> Private Data Plane`).
     - Enforce fail-closed defaults at zone crossings (TLS, auth, least-privilege DB role, zero public DB ports).
   - **Output**: L1/L2 C4 tables and container ASCII diagram.

3. **Establish Layer Rules & Exclusive Module Ownership**
   - **Inputs**: Bounded contexts and capabilities.
   - **Owner**: System Architect.
   - **Action**:
     - Enforce inward dependencies: `Presentation -> Application -> Domain <- Infrastructure` (`Platform` is OS/runtime/DB engine).
     - Assign exclusive `Owns`, `Exposes`, `Consumes`, and `Platform APIs` per module; ban cross-module direct writes.
   - **Output**: Layer map and Module Ownership Matrix.

4. **Run `DESIGN-IT-TWICE` on High-Leverage Core Seams**
   - **Inputs**: `1–2` highest-risk core seams (never trivial CRUD).
   - **Owner**: Lead Engineer.
   - **Action**:
     - Draft three distinct interface shapes: (a) minimal `1–3` entry points hiding orchestration, (b) caller-ergonomic specialized API, and (c) port-and-adapter boundary.
     - Score each variant on **Depth**, **Locality**, and **Invariants Enforced**, then pick the deepest, simplest option.
   - **Output**: Selected interface signatures with ordering, concurrency, and error-mode contracts.

5. **Author Mandatory ASCII Data-Flow, State-Machine & Boot Diagrams**
   - **Inputs**: Module ownership and core seams (following MIT `garrytan/gstack` `/plan-eng-review`).
   - **Owner**: System Architect / Backend Lead.
   - **Action**:
     - **Sync Request Path**: edge validation -> auth -> use case -> `< 50 ms` DB tx -> response, plus `400`/`401`/`403`/`504` branches.
     - **Async Outbox / Saga**: `PENDING -> PROCESSING -> SUCCEEDED | DEAD_LETTER`, showing backoff + jitter, idempotency, and compensation.
     - **Boot Order**: config/secret check -> DB readiness -> HTTP + worker start -> `/healthz` & `/readyz`, marking thread/network crossings.
   - **Output**: Annotated ASCII flow diagrams covering normal and failure paths.

6. **Define Walking-Skeleton Repo Layout & Resilience Budgets**
   - **Inputs**: Diagrams, approved stack, and NFR ceilings.
   - **Owner**: Lead Engineer.
   - **Action**:
     - Lay out `src/modules/<context>/{domain,application,infrastructure,presentation}`, `src/shared/`, and `tests/smoke/`.
     - Set HTTP/DB timeouts (`3s`–`5s`), retries (`<= 3` with jitter), circuit breakers, and rate limits.
     - Add one runnable health/DB smoke test proving end-to-end compilation and connectivity.
   - **Output**: Runnable walking-skeleton layout and resilience table.

7. **Execute Complexity Budget & Deletion/Condensation Pass**
   - **Inputs**: Draft `docs/architecture/architecture.md` and walking skeleton.
   - **Owner**: Independent Reviewer / Architect.
   - **Action**:
     - Apply the Deletion Test to every layer, service, cache, broker, and interface.
     - Delete pass-through services, single-adapter ports, speculative buses, and premature splits.
     - Confirm 100% PRD-to-module coverage and passing walking-skeleton smoke tests.
   - **Output**: Condensed `docs/architecture/architecture.md` and passing smoke receipt.

---

## 3. Reusable Artifact & Template

Instantiate [templates/system-architecture.md](../templates/system-architecture.md) to output `docs/architecture/architecture.md` for every greenfield system or major architectural revision.

### 3.1 Section-by-Section Artifact Contract

| Template Section | Required Content & Contract | Validation Rule |
|---|---|---|
| **Header Metadata** | `System Name`, `Version`, `Spiral ID`, `Rigor Tier`, `Owner`, `Linked SIR`, `Linked PRD/NFRs` | Zero missing citations; exact rigor tier declared |
| **1. Simplicity Baseline** | Option A verification + 3–5 enforceable principles | Explicit NFR proof if Option A is overridden |
| **2. C4 Context & Containers** | Trust-zone table + L2 ASCII diagram | Every external boundary specifies protocol + auth |
| **3. Layer Map & Ownership** | Module table (`Owns`, `Exposes`, `Consumes`, `Platform APIs`) | Zero tables owned by `> 1` module; inward deps intact |
| **4. Deep Modules & Seams** | Interface invariants, ordering, error modes, adapter type, `DESIGN-IT-TWICE` | Zero single-adapter ports for local/in-process code |
| **5. Data Flows & State Machines** | ASCII sync flow, async outbox/saga, boot order | Failure, timeout, and dead-letter paths explicitly drawn |
| **6. Cross-Cutting Policies** | Caching, rate limiting, idempotency, timeouts/retries | Quantitative ceilings (`ms`, `req/min`, retries) required |
| **7. Walking Skeleton & Sign-Off** | Repo tree, smoke command, Feasibility verdict | Verdict must be `PASS` or `CONCERNS` |

### 3.2 Reference Inward Layer & Outbox Skeleton

```text
Presentation (HTTP/Validation) --> Application (Use Cases/Ports) --> Domain (Pure Policy)
                                              ^
                                              |
                             Infrastructure (Postgres/Stripe/SMTP)
```

- **Walking-Skeleton Smoke Criterion**: Must boot config, verify DB readiness, return `200 OK` on `/readyz`, and pass a DB round-trip test.
- **Boundary Enforcement**: Static import-lint rules forbid `Domain -> Infrastructure` and `Presentation -> Infrastructure` imports across all modules.
- **Resilience Defaults**:
  - Set DB statement timeout `<= 5 s` and outbound HTTP timeout `<= 3 s`.
  - Cap retries at `<= 3` with exponential backoff and full jitter on idempotent calls only.
  - Require `Idempotency-Key` headers plus unique DB constraints on state-mutating external endpoints.

---

## 4. Verification Checklist

- [ ] Option A (Modular Monolith + single ACID PostgreSQL) evaluated first.
  - Confirmed via documented ablation test or accepted NFR escalation evidence.
- [ ] Every PRD requirement and NFR maps to an owning module.
  - Zero orphan requirements remain unassigned across contexts.
- [ ] Zero database tables have shared mutable write ownership across modules.
  - Cross-module reads pass exclusively through exposed ports or views.
- [ ] Dependency arrows flow strictly inward toward Domain policy.
  - Zero `Presentation -> Infrastructure` or `Domain -> ORM` imports exist.
- [ ] External integrations define timeouts, jittered retries, breakers, and idempotency.
  - All outbound HTTP/DB calls enforce bounded ceilings.
- [ ] Synchronous, async outbox/saga, and boot ASCII diagrams cover failures.
  - Timeout, compensation, and dead-letter paths are explicitly drawn.
- [ ] Every port satisfies the Two-Adapter Rule or wraps true external SaaS.
  - Single-adapter local/in-process ports were deleted during review.
- [ ] Walking skeleton compiles cleanly and passes persistence smoke tests.
  - `/readyz` and DB round-trip pass in the current session.
- [ ] Independent feasibility review verified all runtime assumptions.
  - Verdict recorded as `PASS` or `CONCERNS` (never silent `NOT ASSESSED`).

---

## 5. Hard Quality Gate

Phase 3A architectural sign-off uses the strict 4-state verdict precedence `FAIL > CONCERNS > NOT ASSESSED > PASS`:

- **PASS**: All 7 sections of `docs/architecture/architecture.md` contain verified facts, Option A simplicity check passes or includes quantitative escalation proof, zero shared-write table conflicts exist, ASCII failure/retry paths are complete, and the walking-skeleton build + smoke test exits `0`.
- **CONCERNS**: Minor non-blocking gaps remain (e.g., L4 seam signature for a post-MVP module) while all Foundation boundaries and smoke checks pass.
- **NOT ASSESSED**: `docs/product/prd.md`, `docs/product/nfr-slo-matrix.md`, or runtime smoke checks have not been executed yet — never emit `PASS` on unexamined scope.
- **FAIL**: Unpoliced cyclic imports, shared mutable tables across contexts, missing failure/timeout handling on external I/O, unverified microservice/broker sprawl, or failing walking-skeleton smoke tests.
- **Evidence Rule**: Record exact build/smoke stdout and gate exit codes before unlocking Phase 3B coding.

Run standalone project-level verification (and suite-level gate checks when running inside the full `appnwebsite-skill` suite):

```bash
# Standalone project-level verification (no parent-suite scripts required):
python3 -c "import pathlib, sys; req=['docs/architecture/architecture.md','docs/architecture/data-model.md','docs/architecture/control-manifest.md']; miss=[p for p in req if not pathlib.Path(p).is_file()]; adrs=list(pathlib.Path('docs/architecture/adr').glob('adr-*.md')); print('Missing:', miss, 'ADRs:', len(adrs)); sys.exit(1 if miss or not adrs else 0)"
# Plus your project's walking-skeleton build & smoke test command (must exit 0)

# When running inside the full appnwebsite-skill suite:
python3 scripts/validate_skill.py . --strict --json
python3 scripts/check_spiral_gates.py --stage foundation --strict --json
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Premature Microservices** | Replaces in-process calls with network latency, partial failure, and multi-repo deploys | `>= 3` services for `< 500 req/s` with no measured bottleneck | Modular Monolith (`src/modules/<context>/`) + single PG DB |
| **Shallow Pass-Through Layers** | `Controller -> Service -> Manager -> Repo` triples boilerplate with zero invariants | Deleting the middle layer loses zero invariants (`Deletion Test`) | Collapse into deep modules hiding rich business rules |
| **Speculative Single-Adapter Ports** | Wrapping one ORM behind `IRepository` + `Factory` adds indirection with zero swap value | 1 concrete impl; tests mock SQL instead of running local PG | Direct local-substitutable modules; port only 2+ adapters or external APIs |
| **Distributed Monolith (Shared DB)** | Combines shared-schema coupling with network failure modes | Separate deployables joining or writing the same tables | Exclusive table ownership per context + public ports/outbox |
| **Unbounded Synchronous Chains** | External HTTP inside open DB locks exhausts pools and drops events on crash | External `fetch` inside DB tx or missing `timeout` config | Commit aggregate + `outbox_events` in `< 50 ms`; async worker with `3s` timeout |
| **Paper-Only Architecture** | Uncompiled diagrams hide broken dependencies, config gaps, and tooling errors | Architecture approved while `src/` and `tests/smoke/` fail to boot | Require compiling walking skeleton passing `/readyz` + DB smoke test |
