# Execution Plan Schema (`execution-plan.md`)

> Instantiate this template to produce the runtime artifact `execution-plan.md` before mutating code on `M/L` multi-file tasks (`3–8` files). If scope exceeds `8` files or spans `>= 2` independent subsystems, split into separate subsystem plans first.

## Metadata Header

| Field | Value |
|---|---|
| **Plan ID** | `<PLAN-001>` |
| **Feature / Scope** | `<concise feature or subsystem name>` |
| **Spec Path** | `<path/to/prd-or-spec.md>` |
| **Phase 3A Gate Ref** | `<path/to/system-foundation-gate.md>` |
| **Simplicity Record Ref** | `<path/to/simplicity-interrogation-record.md>` |
| **Execution Approach** | `<Inline \| Teamwork>` |
| **Status** | `<DRAFT \| READY \| IN_PROGRESS \| COMPLETE>` |
| **Target Runtime Artifact** | `execution-plan.md` |

---

## 1. Architecture & Data Flow

- **Goal (1 sentence)**: `<exact user-visible capability and verifiable end state>`
- **Architecture Summary (2–3 sentences)**: `<simplest high-craft design, native primitives used, and rejected unnecessary layers>`
- **Dependency Order (Bottom-Up)**: `<Schema/Migrations -> Shared Contracts/Types -> Domain Services/APIs -> UI Surfaces -> E2E Verification>`

```text
<Client / Trigger> --> <Boundary Validation> --> <Domain Logic> --> <Persistence / Response>
       |                                              |
       +--> <Error / Edge Path> ----------------------+
```

---

## 2. Global Constraints (Verbatim From Spec)

- `<Constraint 1: exact numeric threshold, latency/bundle budget, or retention rule>`
- `<Constraint 2: exact API status/error schema, auth boundary, or naming rule>`
- `<Constraint 3: exact platform/browser support, font/icon policy, or compliance bound>`

---

## 3. Review Focus (Top 5 Uncovered Edge / Failure Modes)

1. `<Edge Mode 1: malformed/empty input condition -> expected fail-closed behavior -> owning Task N + pinning test name>`
2. `<Edge Mode 2: boundary numeric/length limit -> expected clamping or rejection -> owning Task N + pinning test name>`
3. `<Edge Mode 3: concurrency/idempotency/retry race -> expected atomic outcome -> owning Task N + pinning test name>`
4. `<Edge Mode 4: authz/ownership/tenant boundary -> expected 403/404 handling -> owning Task N + pinning test name>`
5. `<Edge Mode 5: downstream timeout/partial failure -> expected rollback or graceful fallback -> owning Task N + pinning test name>`

---

## 4. Vertical-Sliced Tasks

### Task 1: `<Specific Vertical Slice Title Without Compound Conjunction>`

- **Size**: `<XS (1 file) \| S (1-2 files) \| M (3-5 files)>`
- **Dependencies**: `<None \| Task N>`
- **Files**:
  - Create: `<exact/path/to/new_file.ext>`
  - Modify: `<exact/path/to/existing_file.ext>`
  - Test: `<exact/path/to/test_file.ext>`
- **Interfaces**:
  - Consumes: `<exact symbol names, types, or endpoints consumed>`
  - Produces: `<exact exported symbols, routes, or schema tables produced>`
- **Acceptance Criteria**: `<falsifiable behavior + edge case pinned from Review Focus>`
- **TDD Steps**:
  1. **RED**: Write failing test `<test_name>` in `<exact/path/to/test_file.ext>` covering happy + boundary behavior.
  2. **Verify RED**: Run `<exact test command>` -> Expected: exit non-zero (`<expected failure message>`).
  3. **GREEN**: Implement minimal cohesive code in `<exact/path/to/source_file.ext>`.
  4. **Verify GREEN**: Run `<exact test command>` -> Expected: exit `0` (`<N passed, 0 failed>`).
  5. **Commit / Checkpoint**: Stage only task `Files`, commit or log checkpoint in `progress.md`.

### Task 2: `<Next Vertical Slice Title>`

- **Size**: `<XS \| S \| M>`
- **Dependencies**: `<Task 1>`
- **Files**: `<Create / Modify / Test exact paths>`
- **Interfaces**: `<Consumes / Produces exact signatures>`
- **Acceptance Criteria**: `<falsifiable outcome>`
- **TDD Steps**: `<1..5 RED -> Verify RED -> GREEN -> Verify GREEN -> Checkpoint>`

---

## 5. Pre-Flight Cross-Task Conflict & Readiness Table

| Pair / Check | Shared Interface or File | Conflict / Readiness Finding | Ruling / Verdict |
|---|---|---|---|
| `<Task 1 <-> Task 2>` | `<shared schema, route, or symbol>` | `<verified exact signature match or discrepancy>` | `<READY \| NEEDS WORK \| BLOCKED \| NOT ASSESSED>` |
| `<Plan Readiness Check>` | `<Design / Architecture / Scope / Open Questions / Assets / DoD>` | `<0 unresolved design questions; all asset paths verified>` | `<READY \| NEEDS WORK \| BLOCKED \| NOT ASSESSED>` |

---

## 6. Re-Plan Triggers, Condensation Pass & Rulings Ledger

- **Re-Plan If**:
  - `<Trigger 1: e.g., an assumed API/library contract behaves differently than read-only survey showed>`
  - `<Trigger 2: e.g., any task exceeds 5 modified files or requires a new unbudgeted dependency>`
- **Pre-Ship Deletion & Condensation Pass**:
  - `Files Deleted`: `<0 or exact paths>`
  - `Deps Removed`: `<none or exact packages>`
  - `Net LOC Reduced`: `<exact git diff --stat delta>`
  - `Post-Deletion Test Command`: `<exact command> -> exit 0`
- **Execution Rulings Log**:
  - `Task <N>: Ruling: <decision made> — <rationale> — <cost if wrong>`
