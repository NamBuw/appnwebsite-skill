# System-First Foundation Gate (Phase 3A Hard Stop)

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This module enforces **System-First Engineering (R3)**: feature coding, business route handlers, and production UI authoring are **HARD-BLOCKED** until the system foundation—Architecture, Domain/Data Model, Boundaries, Core Contracts, Accepted ADRs, Control Manifest, and Runnable Walking Skeleton—passes deterministic verification.

---

## 1. Decision Framework

### 1.1 The Phase 3A Hard-Stop Boundary

- **Allowed BEFORE Phase 3A Unlocks**: Reading and exploring existing code, product discovery/PRD/NFRs, STRIDE threat modeling, authoring Foundation docs/contracts/ADRs, building the minimal walking-skeleton repo/CI/healthcheck, and isolated throwaway experiments inside `spikes/` or `prototypes/`.
- **STRICTLY FORBIDDEN BEFORE Phase 3A Unlocks**: Writing production feature endpoints, domain services, feature DB tables/queries, or production UI screens/components/pages. Any violation emits `SYSTEM_FIRST_VIOLATION` in `scripts/check_spiral_gates.py`.

### 1.2 The 6 Mandatory Foundation Pillars

| # | Foundation Pillar | Required Deliverables | Verification Floor (`minimal` vs. `standard`/`full`) |
|---|---|---|---|
| **1** | **System Architecture & Boundaries** | `architecture.md` (C4 Context + Container, sync/async flows, trust & failure boundaries) | `minimal`: 1-page flow & boundary doc; `standard`/`full`: full C4 + failure/retry/tenancy zones; Simplicity Option A verified |
| **2** | **Domain & Data Model** | Bounded contexts, ERD/schema (`schema.sql`/Prisma/Drizzle), PK/FK/indexes, tenancy/RLS, PII tags, migration strategy | `minimal`: core entity/content/form schema; `standard`/`full`: complete ERD + expand-and-contract migration plan |
| **3** | **Core Contracts & Interfaces** | OpenAPI/JSON Schema/GraphQL/RPC/Event contracts, RFC 9457 error model, UI `design-master.md` + W3C DTCG `tokens.json` | `minimal`: typed I/O + token contract; `standard`/`full`: versioned schema contracts + error fixtures + validated `tokens.json` |
| **4** | **ADRs & Control Manifest** | Accepted Foundation ADRs (`docs/architecture/adr/adr-*.md`) + `control-manifest.md` (allowed/forbidden imports, invariants) | `minimal`: `>= 1` core ADR + layer rules; `standard`/`full`: full Foundation ADR suite (`Status: Accepted`, acyclic `Depends On`) + manifest |
| **5** | **Repo & Infrastructure Skeleton** | Target directory tree, lockfile, `.env.example`, CI workflow, healthcheck, `>= 1` runnable smoke/unit test | **All tiers**: runnable build/lint/smoke test required (zero paper-only architectures) |
| **6** | **Simplicity, Threat & Risk Pre-Checks** | Linked `SIR-<NNN>` (`PASS`/`CONCERNS`), `RSK-SP-<NNN>` (`0` `OPEN` High/Critical), STRIDE entry points mapped | **All tiers**: mandatory before unlocking Phase 3B |

### 1.3 Simplest High-Craft Foundation Rule & Surface Calibration

Default to the **Simplest High-Craft Architecture**: a **Modular Monolith + single ACID relational DB (e.g., PostgreSQL)** with strict internal module boundaries in `control-manifest.md`. Reject distributed services, event buses, or multi-repo splits unless a verified constraint in Q3 of `simplicity-interrogation-record.md` proves a monolith cannot meet SLOs or compliance boundaries.

| Surface | `minimal` Tier Phase 3A Floor | `standard` / `full` Tier Phase 3A Floor |
|---|---|---|
| **Landing Page / Marketing** | 1-page IA + route map, lead/form schema, `design-master.md` + `tokens.json`, `>= 1` ADR (stack/hosting), runnable build + a11y/link smoke test | Add multi-locale schema, analytics event contract, security headers ADR, full CI Lighthouse/WCAG smoke |
| **Web App / SaaS / Dashboard** | C4 flow, core ERD, typed API/action I/O + RFC 9457 errors, `design-master.md`, `>= 1` ADR, runnable app + smoke test | Full C4, ERD + RLS + migration plan, OpenAPI/TS schemas, `tokens.json`, `>= 3` Accepted ADRs, `control-manifest.md`, STRIDE |
| **Mobile App** | Nav/deep-link architecture, local persistence/API sync contract, `tokens.json` + safe-area rules, `>= 1` ADR, runnable shell + test | Add offline conflict ADR, biometric/secure-storage contract, release-signing skeleton, device-matrix smoke CI |
| **Backend / API** | Service/module boundary diagram, core schema/migration, OpenAPI + RFC 9457 error contract, `>= 1` ADR, healthcheck + smoke test | Full C4, expand-contract migration strategy, idempotency/webhook contracts, `control-manifest.md`, STRIDE, Testcontainers CI |

---

## 2. Step-by-Step Workflow

### Step 1 — Verify Q1/Q2 Pre-Conditions
1. Confirm `spiral-charter.md` (`Status: ACTIVE`) and `PRE-DESIGN` `simplicity-interrogation-record.md` (`PASS` or `CONCERNS`) exist without placeholders.
2. Confirm `risk-spike-register.md` has `0` `OPEN` risks with severity `High` or `Critical` and zero production imports from `spikes/`/`prototypes/`.

### Step 2 — Author Foundation Pillars in Dependency Order
1. **Pillar 1 & 2 (Architecture & Data Model)**: Route to `skills/system-data-architecture` to produce `architecture.md` and `data-model.md` (with PK/FK, tenancy/RLS, and PII classification).
2. **Pillar 4a (Foundation ADRs)**: Author an ADR for every foundational choice (runtime, DB, auth/session, state/rendering, styling, deployment). Every ADR MUST follow the contract in Section 3 (`Status: Accepted`, explicit `Depends On`, `Simplicity & Alternatives`).
3. **Pillar 4b (Control Manifest)**: Write `control-manifest.md` specifying allowed dependency direction (e.g., `UI -> Application -> Domain <- Infrastructure`), forbidden imports (e.g., UI importing DB clients directly; production importing `spikes/`), and bundle/latency budgets.
4. **Pillar 3 (Core Contracts)**: Lock API/event schemas (including RFC 9457 `ProblemDetails` errors) AND, for UI-bearing apps/sites, invoke `skills/ui-design-craft` ONLY to lock `design-master.md` + W3C DTCG `tokens.json`.
5. **Pillar 5 (Walking Skeleton)**: Scaffold directories matching `architecture.md`, configure `.env.example`, linter/typechecker, CI pipeline, healthcheck endpoint/page, and `>= 1` passing automated smoke test.

### Step 3 — Run Deterministic Foundation, Complexity Budget & Condensation Checks
1. Run `python3 scripts/check_spiral_gates.py --project-dir <repo> --stage foundation --strict --json`.
2. Verify the deterministic ADR dependency graph passes with zero `CYCLE:`, zero `UNFILLED_DEPS`, and zero `Proposed` Foundation ADRs.
3. Verify zero production feature/UI files exist outside the walking skeleton (`SYSTEM_FIRST_VIOLATION` check).
4. **Complexity Budget & Deletion/Condensation Pass**: Audit the walking skeleton and `control-manifest.md` against the Spiral's Complexity Budget (`max external deps`, `max layers`, `0` speculative patterns) and execute a pre-unlock Deletion/Condensation Pass to remove unused scaffold helpers, single-use wrappers, or redundant abstractions before Phase 3B begins.

### Step 4 — Execute Independent Builder Check
1. Pass ONLY the Phase 3A Foundation documents to a fresh review pass (isolated from design discussions) asking: *"Where would an implementer have to guess, and where would a wrong guess break contracts or security?"*
2. Triage findings into `Answered already`, `Minor` (clarify inline), or `Theirs` (settle with decision owner) before gate sign-off.

### Step 5 — Sign Off & Unlock Phase 3B
1. Populate `docs/spiral/system-foundation-gate.md` from [System Foundation Gate template](../../templates/system-foundation-gate.md).
2. Complete the 5-question Chain-of-Verification (minimum 2 `[TOOL ACTION]` fresh file/command checks).
3. Flip `Downstream Lock` to `UNLOCKED` ONLY when `Verdict` is `PASS` (or waived `CONCERNS`), zero Section 1 rows are `FAIL`/`NOT ASSESSED`, and all Section 2 boxes are `[x]`.

---

## 3. Reusable Artifact & Template

- **Canonical Template**: [System Foundation Gate](../../templates/system-foundation-gate.md)
- **ADR Format Contract** (scanned deterministically by `check_spiral_gates.py`):

```markdown
# ADR-0001: Modular Monolith on PostgreSQL
- **Status**: Accepted
- **Depends On**: None
- **Requirements Addressed**: NFR-01, FR-01..FR-04

## Context & Simplicity Analysis
Option A (Modular Monolith + Postgres) satisfies p95 < 150ms with 0 extra network hops.
Rejected: Microservices + Kafka (violates Q3 YAGNI — no measured throughput bottleneck).
```

- **ADR Dependency Graph Rules (Zero-Cycle Invariant)**:
  - Every ADR under `docs/architecture/adr/*.md` or `docs/adr/*.md` MUST include `Status:` (`Accepted` for all Foundation ADRs) and `Depends On:` (`None` or valid sibling ADR IDs).
  - `check_spiral_gates.py` parses the directed edges and fails immediately on `CYCLE:` (`ADR-0002 -> ADR-0003 -> ADR-0002`), `UNFILLED_DEPS:` (`[TBD]`), or `PROPOSED_ADR`.
- **Control Manifest Minimum Contract** (`docs/architecture/control-manifest.md`):
  1. **Allowed Layer Graph**: e.g., `routes/ui -> application/use-cases -> domain <- infrastructure`.
  2. **Forbidden Imports**: UI never imports DB/ORM clients directly; `src/` never imports `spikes/` or `prototypes/`.
  3. **Shared Contract Source of Truth**: exact path to OpenAPI/Zod/JSON Schema + `tokens.json`.
  4. **Hard Runtime Ceilings**: JS initial bundle budget, API p95 latency budget, max new external dependencies per Spiral.
- **Concrete Walking Skeleton Checklist (Pillar 5 Minimum)**:
  - Directory tree matches `architecture.md` bounded contexts (no placeholder `utils2/` or `misc/`).
  - Reproducible dependency lockfile (`package-lock.json` / `pnpm-lock.yaml` / `poetry.lock` / `uv.lock`) + validated `.env.example`.
  - Working CI lint + typecheck + test workflow + minimal `/healthz` (or root route render test) passing freshly before Phase 3B starts.
- **Unlock Invariant**: `Downstream Lock = UNLOCKED` is strictly illegal unless every pillar meets its tier floor and the walking-skeleton smoke test passes freshly.

### Example Phase 3A Unlock Sequence (CLI Receipt)
```bash
# 1. Verify Charter & Simplicity Baseline first
python3 scripts/check_spiral_gates.py --project-dir . --stage charter --strict
python3 scripts/check_spiral_gates.py --project-dir . --stage simplicity --strict

# 2. Verify Q2 Risk Register & Zero Spike Leaks
python3 scripts/check_spiral_gates.py --project-dir . --stage q2-risk --strict

# 3. Verify All 6 Phase 3A Foundation Pillars + ADR DAG + Walking Skeleton
python3 scripts/check_spiral_gates.py --project-dir . --stage foundation --strict --json
```

Only after step 3 exits `0` (`"verdict": "PASS"`) may `Downstream Lock` switch to `UNLOCKED` and Phase 3B feature/UI files be authored.

### Builder Check Triage Protocol (Pre-Unlock Ambiguity Sweep)
When dispatching a fresh Builder Check pass over Phase 3A artifacts, classify every ambiguity returned into exactly one of three buckets:
1. **`Answered Already`**: Point to exact doc/line (`architecture.md#boundaries`) and clarify wording if subtle.
2. **`Minor` (Self-Settle)**: Pick the Option A simplest convention (e.g., ISO-8601 UTC timestamps, RFC 9457 JSON `type/title/status/detail`) and mark `[DECIDED]` in the contract.
3. **`Theirs` (Blocking Owner Decision)**: Escalate immediately before Phase 3B (e.g., multi-tenant isolation model, billing proration rule, data retention SLA) and record the settled answer as an Accepted ADR.

### Phase 3A File-Creation Order (Deterministic Greenfield Sequence)
1. `docs/spiral/spiral-charter.md` + `docs/spiral/simplicity-interrogation-record.md` (`PRE-DESIGN`)
2. `docs/spiral/risk-spike-register.md` + `docs/security/threat-model.md`
3. `docs/architecture/architecture.md` + `docs/architecture/data-model.md`
4. `docs/architecture/adr/adr-0001-*.md` (`Status: Accepted`) + `docs/architecture/control-manifest.md`
5. `docs/contracts/openapi.yaml` (or typed schema) + `docs/design/design-master.md` & `tokens.json`
6. Walking-skeleton `package.json`/`pyproject.toml`, `.env.example`, CI check, `/healthz`, `>= 1` passing test
7. `docs/spiral/system-foundation-gate.md` (`Verdict: PASS`, `Downstream Lock = UNLOCKED`)

### Concrete `SYSTEM_FIRST_VIOLATION` Scenarios & Remediation
| Violation Detected by `check_spiral_gates.py` | Root Cause | Exact Remediation Path |
|---|---|---|
| `src/routes/billing.ts` exists while `system-foundation-gate.md` is `ABSENT` | Agent started feature coding directly from user prompt | Halt feature edits; author Foundation Pillars 1–5; pass `check_spiral_gates.py --stage foundation` before resuming |
| `app/dashboard/page.tsx` authored while `Downstream Lock = LOCKED` | UI written before `design-master.md`, `tokens.json`, and API contracts locked | Move exploratory mock to `prototypes/` or freeze authoring until Pillar 3 + Gate unlock |
| `ADR-0002` has `Status: Proposed` or `Depends On: [TBD]` | Architecture left tentative into Phase 3B | Finalize decision, resolve tradeoffs via Simplicity Q1–Q4, set `Status: Accepted` & explicit `Depends On` |
| `ADR-0001 -> ADR-0002 -> ADR-0001` cycle detected | Circular coupling between foundational choices | Refactor shared dependency into `ADR-0000` root decision so graph forms a strict DAG |
| `src/lib/search.ts` imports `spikes/pg-fts/bench` | Prototype-to-prod leak violating Control Manifest | Delete cross-import; implement clean tested module under `src/` matching Phase 3A contracts; archive/delete spike |

### Brownfield Exception Rule (Existing Codebases)
When applying Phase 3A to a brownfield codebase (`Lifecycle Mode: brownfield`):
- Existing production files created **prior** to onboarding are NOT deleted, nor treated as a greenfield violation once Adopt triage is active.
- Instead, **new** feature epics or UI redesign slices remain locked until the brownfield baseline (`architecture.md`, core `data-model.md`, `control-manifest.md`, `>= 1` baseline ADR, and passing regression smoke test) is captured and `system-foundation-gate.md` unlocks `SP-001`.

---

## 4. Verification Checklist

- [ ] Zero production feature endpoints, business logic modules, or UI feature screens exist prior to Phase 3A `UNLOCKED`.
- [ ] `architecture.md` specifies C4 Context + Container, sync/async paths, and trust/failure boundaries.
- [ ] `data-model.md` defines entities, PK/FK constraints, indexes, tenancy/RLS isolation, PII tags, and migration plan.
- [ ] `control-manifest.md` enforces unidirectional module imports and blocks `spikes/`/`prototypes/` imports in `src/`.
- [ ] Core API contracts (and `design-master.md` + `tokens.json` if UI-bearing) are locked and schema-valid.
- [ ] All Foundation ADRs declare `Status: Accepted`, explicit `Depends On`, and `0` dependency cycles.
- [ ] Walking skeleton compiles/starts cleanly and executes `>= 1` passing automated smoke test in the current session.
- [ ] Independent Builder Check completed with `0` unresolved blocking ambiguities.

---

## 5. Hard Quality Gate

- **Command**: `python3 scripts/check_spiral_gates.py --project-dir <repo> --stage foundation --tier <minimal|standard|full> --strict --json`
- **PASS Criteria**: All 6 pillars `PASS` (or signed `CONCERNS`), `0` ADR cycles, `0` `Proposed` Foundation ADRs, `0` `SYSTEM_FIRST_VIOLATION`s, walking-skeleton smoke test exits `0`.
- **NOT ASSESSED Criteria**: Any pillar contains `[...]` placeholders, `Downstream Lock` is ambiguous, or walking-skeleton smoke test was never executed.
- **FAIL Criteria**:
  - Feature/UI code exists in `src/`, `app/`, `pages/`, `components/`, `server/`, or `api/` while Phase 3A is `ABSENT`, `LOCKED`, `NOT ASSESSED`, or `FAIL`.
  - Circular ADR dependency (`A -> B -> A`) or unaccepted Foundation ADR (`Status: Proposed`).
  - Missing data model, missing core contract, or broken walking-skeleton build/test.
  - `Downstream Lock` set to `UNLOCKED` while any pillar row is `FAIL`/`NOT ASSESSED` or any Section 2 checklist box is unchecked `[ ]`.

### Minimum Walking-Skeleton Verification Commands (By Stack)
| Stack | Minimum Pillar 5 Skeleton Proof Before Phase 3B |
|---|---|
| **Node / Next.js / TypeScript** | `npm run typecheck && npm run lint && npm test` (at least 1 passing health/contract test) |
| **Python / FastAPI / Django** | `python3 -m py_compile` / `ruff check` + `pytest -q --tb=short` (`>= 1` passing `/healthz` test) |
| **Mobile (Expo / Flutter)** | Typecheck/analyze + `>= 1` navigation/store smoke test passing in CI |
| **Static / Landing Site** | Build succeeds cleanly + link/HTML/a11y smoke test passes with `0` errors |
| **Go / Rust API** | `go test ./...` / `cargo test` (`>= 1` passing `/healthz` + config-parse smoke test) |
| **SQL / Migrations** | Up/down migration applies cleanly on empty test DB + seed/schema verification exits `0` |

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **UI-First / Cowboy Coding** | Hardcodes ad-hoc JSON shapes in components, forcing costly schema & route rewrites | `components/` or `pages/` authored before `data-model.md` and contracts exist | Lock Phase 3A first; explore UX concepts strictly inside throwaway `prototypes/` |
| **Paper-Only Architecture** | Uncompilable diagrams hide missing env vars, circular imports, and DB tooling bugs | 40 pages of docs with zero `package.json`/`pyproject.toml` or runnable smoke test | Pillar 5 mandates a compiling, tested walking skeleton before 3A passes |
| **Circular or `Proposed` ADRs** | Parallel workers pick conflicting auth, ORM, or state patterns mid-sprint | `Status: Proposed` or `ADR-02` <-> `ADR-03` dependency loop | Enforce `Status: Accepted` + deterministic ADR DAG check (`check_spiral_gates.py`) |
| **Spec-Free "Vibe" Contracts** | Frontend and backend invent incompatible field names, nullability, and error shapes | Untyped `any` payloads or inconsistent error JSON across endpoints | Freeze OpenAPI/TS schemas + RFC 9457 error envelope in Pillar 3 |
| **Spike-to-Prod Mutation** | Ships brittle throwaway prototype code lacking auth, validation, and error paths | `src/` imports from `spikes/` or copies prototype handlers verbatim | Rewrite production slices cleanly against `control-manifest.md` after 3A unlocks |
| **Premature Unlock Override** | Flips `Downstream Lock = UNLOCKED` while Section 1 rows remain `NOT ASSESSED` | `UNLOCKED` header paired with `[ ]` checkboxes or `[TBD]` paths | Reject illegal unlock deterministically via `check_spiral_gates.py` |
| **Unbounded Shared `utils/` Dump** | Bypasses `control-manifest.md` by dropping cross-layer DB/UI helpers into `src/utils/` | `src/utils/` imports both React/UI and DB/ORM drivers | Enforce unidirectional dependency boundaries and isolated ports/adapters |

---

## Related Governance Modules
- [Spiral Lifecycle](spiral-lifecycle.md)
- [Anti-Overengineering Simplicity Gate](anti-overengineering-simplicity-gate.md)
- [Risk, Prototyping & Spikes](risk-prototyping-and-spikes.md)
- [Orchestration Protocol](../orchestration-protocol.md)
- [System Foundation Gate Template](../../templates/system-foundation-gate.md)
