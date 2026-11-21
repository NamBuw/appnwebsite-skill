# Spiral Lifecycle Master Workflow (Q1–Q4)

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This module defines the iterative **Spiral Model** execution engine governing greenfield and brownfield entry, rigor tier scaling (`minimal | standard | full`), vertical slice delivery, 4-state verdict precedence, and Spiral-exit telemetry.

---

## 1. Decision Framework

### 1.1 Entry Mode Selection (Greenfield vs. Brownfield)

Never assume a repository is greenfield if files already exist. Inspect workspace state before creating artifacts:

| Repo State | Detection Signal | Required Entry Action |
|---|---|---|
| **Greenfield** | Empty repo or scaffold-only (`< 3` source files, no existing schema/specs) | Initialize [Spiral Charter](../../templates/spiral-charter.md) (`SP-001`) -> Q1 Objectives & Simplicity -> Q2 Risk/Threat/Spikes -> Phase 3A System-First Foundation Gate -> Q3B Slice Build -> Q3C Condensation/QA -> Q4 Exit |
| **Brownfield (Unstructured)** | Existing code (`>= 3` source files) with missing/stale architecture, ADRs, or tests | Run **Stage Detect** (observed artifacts vs declared stage; mismatch -> `CONCERNS`) -> Run **Adopt Audit** (4-tier `BLOCKING > HIGH > MEDIUM > LOW` gap triage) -> Fix `BLOCKING` contract gaps BEFORE adding features -> Enter Q1 |
| **Brownfield (Structured)** | Valid architecture, ADRs, and passing baseline tests exist | Run `python3 scripts/check_spiral_gates.py --project-dir .` -> verify baseline & Scope Check -> enter Q1 for next incremental Spiral (`SP-<N+1>`) |
| **Trivial Hotfix / Direct Mode** | Localized fix (`<= 2` files, zero schema, API, auth, boundary, or UX-pattern impact) | **Direct Mode Fast Path**: Simplicity Q1/Q2 check -> TDD red-green -> fresh verification command (`verification-before-completion`) -> Exit |

#### Brownfield 4-Tier Adopt Triage Matrix
1. **`BLOCKING`** (fix immediately): Broken build/test command, missing lockfile/env contract, unmitigated auth/injection hole, or schema/API mismatch breaking downstream tools silently.
2. **`HIGH`** (fix in Spiral 1 Phase 3A): Missing `data-model.md`, missing `control-manifest.md`, `Proposed` or contradictory ADRs, or missing smoke test harness.
3. **`MEDIUM`** (schedule in Spiral 1–2): Incomplete NFRs/SLOs, inconsistent design tokens, or sparse black-box test coverage.
4. **`LOW`** (backlog): Cosmetic doc formatting or optional telemetry enhancements.

*Brownfield Preservation Rule*: Run deterministic existence checks (`PRESENT`, `ABSENT`, `SHORT`, `PATTERN_MISS`) before editing; preserve in-flight stories and working code during Adopt — never bulldoze working production paths without an Accepted ADR.

### 1.2 Rigor Tiers (`minimal | standard | full`)

| Rigor Tier | Aliases | Trigger Scope | Spiral Duration Target | Mandatory Phase 3A Foundation Floor |
|---|---|---|---|---|
| **`minimal`** | `micro` | Single-surface landing page, utility, MVP slice (`<= 2` subsystems) | 1–3 days / spiral | 1-page `Spiral Charter` + `Simplicity Record`, core data/content schema, typed I/O or token contract, `>= 1` core ADR (if non-trivial tradeoff), runnable walking skeleton + smoke test |
| **`standard`** | `standard` | Multi-feature web/mobile SaaS (`3–8` subsystems, auth/DB/API) | 1–2 weeks / spiral | Full PRD & NFRs, C4 architecture, DDD/ERD + migration plan, OpenAPI/DTCG contracts, Foundation ADRs (`Status: Accepted`), `control-manifest.md`, STRIDE threat model, multi-layer QA |
| **`full`** | `enterprise` | Regulated, high-scale, or multi-team (`>= 8` subsystems, multi-region, compliance) | 2–4 weeks / spiral | All `standard` deliverables + DPIA/privacy governance, complete ADR suite, full Design System, load/chaos testing, formal SRE runbooks & SLO burn-rate alerts |

**Non-Waivable Invariants**:
1. Rigor tier scales *documentation breadth* ONLY — it **never** waives what must *work* or bypasses Phase 3A Foundation or Simplicity Self-Interrogation.
2. **Additive Subsystem Overrides**: Any slice touching **Authentication/Authorization**, **PII/Privacy**, or **Payments/Billing** automatically elevates that subsystem to `standard`/`full` security & QA rigor regardless of project tier.
3. **Zero-Requirement Guard**: If tier reductions leave zero verifiable artifacts for a transition, emit `NOT ASSESSED` (never silent `PASS`).

### 1.3 4-State Gate Verdict Precedence

Every Spiral gate evaluates deterministically in strict precedence order (first match wins):

`FAIL` > `CONCERNS` > `NOT ASSESSED` > `PASS`

- **`FAIL`**: Broken build/tests, Phase 3A bypassed (`SYSTEM_FIRST_VIOLATION`), unresolved `P0/P1` security/functional defect, circular ADR dependency, or `> 25%` unapproved scope bloat.
- **`CONCERNS`**: Non-blocking drift (`10–25%` scope delta) or explicitly waived `Medium`/`Low` risk with owner + remediation deadline.
- **`NOT ASSESSED`**: Outranks `PASS` whenever any required artifact contains `[...]` placeholders, telemetry is missing (`NOT ASSESSED — NO DATA`), a check did not run, or a baseline denominator is `0` (`0%` creep on an empty baseline is `NOT ASSESSED`, never `PASS`).
- **`PASS`**: All tier-required artifacts exist without placeholders, all deterministic checks and tests pass with fresh command receipts, and `0` `P0/P1` blockers remain.

### 1.4 Simplest High-Craft Check at Spiral Entry

Before locking Q1 scope or selecting `standard`/`full` machinery, answer the 4 Socratic Simplicity Questions in [Anti-Overengineering Simplicity Gate](anti-overengineering-simplicity-gate.md) and surface **Option A (Simplest High-Craft)** first inside the Charter (e.g., Modular Monolith + Postgres over premature microservices; native `<dialog>` + CSS Grid over heavy widget libraries).

---

## 2. Step-by-Step Workflow

### Quadrant 1 (`Q1`) — Objectives, Constraints & Charter
1. **Audit Entry State**: Inspect repo layout and git history. If brownfield, run Stage Detect (compare declared vs. observed artifacts; disagreement -> `CONCERNS`) + Adopt 4-tier gap classification (`BLOCKING` fixed before new scope).
2. **Define Target Vertical Slice & Non-Goals**: State a 1-sentence objective (`Outcome + Actor + Constraint`), thin end-to-end slice(s), explicit **Non-Goals / Anti-Goals**, quantitative exit criteria, and **Complexity Budget** (max new dependencies, layers, files).
3. **Run Pre-Design Simplicity Interrogation**: Populate `PRE-DESIGN` [Simplicity Interrogation Record](../../templates/simplicity-interrogation-record.md).
4. **Lock Spiral Charter**: Write `docs/spiral/spiral-charter.md` using [Spiral Charter template](../../templates/spiral-charter.md) (`Status: ACTIVE`). Dispatch `skills/product-discovery-and-specs` if full PRD/use-case/NFR breakdown is needed.

### Quadrant 2 (`Q2`) — Risk Analysis, Threat Modeling & Spikes
1. **Enumerate Risks Separately**: Score `Likelihood` and `Severity` (`Low | Med | High | Critical`) independently inside [Risk & Spike Register](../../templates/risk-spike-register.md) — never hide fatal impact inside an average score.
2. **Threat Model Boundaries**: Route new/changed trust boundaries and data paths through `skills/security-engineering` (STRIDE & attack trees).
3. **Run Timeboxed Throwaway Spikes**: Only for `High`/`Critical` unverified assumptions (`<= 4h` technical spike or `<= 1d` concept prototype inside isolated `spikes/` or `prototypes/`).
4. **Builder Check**: Verify specs leave zero ambiguous guesses that would force implementers to invent contracts.

### Quadrant 3A (`3A`) — System-First Foundation Gate (HARD BLOCK)
1. **Build the 6 Foundation Pillars** (via `skills/system-data-architecture` and, if UI-bearing, `skills/ui-design-craft` tokens/brief ONLY):
   - System Architecture & Boundaries -> Domain & Data Model -> Core Contracts -> Accepted ADRs (acyclic) & Control Manifest -> Repo & Infra Walking Skeleton + passing smoke test -> Simplicity/Risk Pre-Checks.
2. **Enforce Gate**: Run `python3 scripts/check_spiral_gates.py --project-dir <repo> --stage foundation --strict`.
3. **Unlock Rule**: Feature coding and UI component authoring remain **LOCKED** until `Verdict` is `PASS` (or waived `CONCERNS`) and `Downstream Lock = UNLOCKED`.

### Quadrant 3B (`3B`) — Vertical Slice Engineering & UI Authoring
1. **Build End-to-End Thin Slices**: Implement `Schema/Migration -> Domain Logic -> API Contract -> UI Surface -> Automated Tests` in bite-sized steps (`Consumes`/`Produces` interfaces, TDD red-green-refactor). Cut scope before cutting quality (`Day 3` sunk-cost checkpoint on multi-week slices).
2. **Enforce Surface & Engineering Rigor**: Route to the active `<= 2` Child Skills (`fullstack-api-engineering`, `ui-design-craft`, `figma-design-to-code`, `frontend-surfaces-and-redesign`, `advanced-web-app-capabilities`).
3. **Checkpoint Between Slices**: Update the `<= 25`-line `<!-- CHECKPOINT -->` block in `spiral-charter.md` and compact context at stage transitions.

### Quadrant 3C (`3C`) — Pre-Ship Condensation & Multi-Layer Verification
1. **Execute Deletion / Condensation Pass**: Complete `PRE-SHIP-CONDENSATION` in `simplicity-interrogation-record.md` (delete dead exports, single-use wrappers, bloated deps; collapse redundant UI/CSS into native primitives) and **re-run full build/tests afterward**.
2. **Run Multi-Layer QA & Security Verification**: Dispatch `skills/multi-layer-qa-testing` (Black-Box EP/BVA/State/Decision/E2E + White-Box + Non-Functional) and `skills/security-engineering` (SAST/DAST/supply-chain/PoC).
3. **Enforce Verification-Before-Completion Iron Law**: Zero completion claims without fresh command execution output observed in the current session (`1. IDENTIFY -> 2. RUN freshly -> 3. READ full exit/output -> 4. VERIFY -> 5. CLAIM`).

### Quadrant 4 (`Q4`) — Review, Exit Telemetry & Next-Spiral Planning
1. **Run Scope Check**: Compute `Scope Delta % = (Current - Original) / Original`: `<= 10% PASS`, `> 10–25% CONCERNS`, `> 25% FAIL` (zero baseline -> `NOT ASSESSED`).
2. **Record Exit Telemetry**: Capture planned vs. delivered items, open defects (`P0/P1/P2`), complexity budget delta, SLO/performance delta, and `TODO/FIXME` debt delta. Missing telemetry MUST be recorded as `NOT ASSESSED — NO DATA`.
3. **Run 5-Question Chain-of-Verification (CoV)**: Generate 5 adversarial challenge questions (at least 2 requiring `[TOOL ACTION]` file re-reads or command re-runs) before issuing final `Spiral Exit Verdict`.
4. **Plan `SP-<N+1>`**: Capture `<= 5` owned, dated action items and feed carryover into the next Spiral Charter (or trigger `skills/observability-sre-release` production launch).

#### Example Q4 Chain-of-Verification (5-Question Self-Audit)
1. `[TOOL ACTION]` Re-run `pytest -q --tb=short` (or `npm test`) — did every post-deletion test pass freshly?
2. `[TOOL ACTION]` Run `python3 scripts/check_spiral_gates.py --project-dir . --stage all --strict` — are all gates `PASS` with zero placeholders?
3. Did Scope Delta stay `<= 10%` against `SP-001` baseline items (with non-zero denominator)?
4. Are `0` `P0/P1` security or black-box defects open, and did Auth/PII subsystems meet `standard`/`full` overrides?
5. What `<= 5` concrete action items (`Owner | Deadline | Verification`) carry into `SP-002`?

#### Exit Telemetry & Scope Delta Matrix

| Telemetry Metric | Measurement Method | Healthy Target (`PASS`) | Drift / Failure Threshold |
|---|---|---|---|
| **Planned vs. Delivered Ratio** | Delivered slice items / Q1 baseline items | `>= 90%` (`Scope Delta <= 10%`) | `> 10–25% CONCERNS`, `> 25% FAIL`, `0` baseline -> `NOT ASSESSED` |
| **Open Defect Ceiling** | Issue tracker / QA matrix counts by severity | `0` `P0`, `0` `P1` | Any open `P0`/`P1` -> `FAIL` |
| **Complexity Budget Delta** | `git diff` on deps, architectural layers, net LOC | Within Charter ceiling; `PRE-SHIP-CONDENSATION` ran | Unjustified dep/layer bloat -> `FAIL` |
| **Technical Debt Delta** | `grep -rn "TODO\|FIXME\|HACK" src/` delta vs. Q1 | `<= 0` net new unowned `TODO`/`FIXME` | Unowned `FIXME`/`HACK` in critical path -> `CONCERNS` |
| **SLO / Perf Baseline** | Fresh benchmark/CWV/p95 command run | Meets `nfr-slo-matrix.md` targets | Missing measurement -> `NOT ASSESSED — NO DATA` |

#### Multi-Spiral Progression Cadence (Typical SaaS Product)
| Spiral | Primary Focus | Target Vertical Slice | Exit Milestone |
|---|---|---|---|
| **SP-001** | Core Foundation + Thin End-to-End Loop | Auth/session + 1 primary entity CRUD + clean UI shell + CI smoke | Phase 3A locked + Slice 1 deployed to staging |
| **SP-002** | Core Business Workflow + Black-Box QA | Primary user workflow + edge-case BVA/state tests + Stripe/billing (if applicable) | Full multi-layer QA + security baseline `PASS` |
| **SP-003** | Polish, Performance, SRE & Launch Readiness | CWV/p95 optimization, WCAG 2.2 AA audit, OpenTelemetry SLOs, runbooks, changelog | Production launch gate + `SP-004` growth/iteration |

---

## 3. Reusable Artifact & Template

- **Canonical Template**: [Spiral Charter](../../templates/spiral-charter.md)
- **Single-Canonical-Record Rule**: Maintain one canonical `docs/spiral/SP-<NNN>-charter.md` per active Spiral and update it across Q1–Q4 rather than spawning contradictory duplicate status docs.
- **Field-by-Field Contract**:
  - **Header Metadata**: `Spiral ID` (`SP-001`), `Project / Product Name`, `Primary Surface` (8 surface enums), `Lifecycle Mode` (`greenfield | brownfield`), `Rigor Tier` (`minimal | standard | full`), `Status` (`DRAFT | ACTIVE | COMPLETED | ABORTED`), `Updated (UTC)` (ISO-8601), `Owner`.
  - **Bounded `<!-- CHECKPOINT -->` (`<= 25` lines)**: Active Spiral, Tier, Mode, Current Quadrant, Phase 3A Lock, Simplicity Gate verdict, Current Slice, Next Action, Blockers, Files In Progress.
  - **Section 1 (Objectives & Non-Goals)**: 1-sentence `Primary Objective`, `Target Vertical Slice(s)`, `Non-Goals / Out of Scope`, and `Measurable Exit Criteria` table (`Criterion ID | Behavior | Target Threshold | Verification Method | Evidence Locator`).
  - **Section 2 (Constraints & Baseline)**: `Spiral Budget` (Timebox, Complexity Ceiling, Token Rule), `Tech Stack & Platform Envelope`, and `Greenfield` vs. `Brownfield` baseline capture.
  - **Section 3 (Alternatives & Option A)**: `Linked Simplicity Record`, `Candidate Approaches` table (Option A Simplest High-Craft surfaced first), and `Selection Rationale`.
  - **Section 4 (Cross-Quadrant Ledger & Q4 Exit)**: Linked artifact paths (`SIR`, `RSK`, `SFG`), Q4 Scope & Exit Telemetry, `Spiral Exit Verdict`, and `<= 5` owned carryover action items.

### Zero-Denominator & Insufficient-Input Guard Examples
- If `Planned Items == 0` in Q4 Scope Check -> emit `NOT ASSESSED — NO BASELINE`, never `0% Scope Delta = PASS`.
- If `Lighthouse` or `k6` load test was never run -> record `NOT ASSESSED — NO DATA`, never `0 errors = PASS`.
- If a brownfield repo declares `Phase 3B` in config but `architecture.md` and `data-model.md` are missing on disk -> downgrade Stage Confidence to `CONCERNS` and block new features until Adopt `HIGH`/`BLOCKING` gaps are resolved.

### Concrete Stage-Transition Gate Matrix (`Q1 -> Q4`)
| Transition | Required Artifacts on Disk | Deterministic Verification Command | Blocking Condition (`FAIL` / `NOT ASSESSED`) |
|---|---|---|---|
| **Entry -> Q1** | Workspace detection (`greenfield` or Adopt audit) | `ls -la`, test baseline run | Brownfield `BLOCKING` gap unaddressed |
| **Q1 -> Q2** | `spiral-charter.md`, `simplicity-interrogation-record.md` (`PRE-DESIGN`) | `python3 scripts/check_spiral_gates.py --stage charter` & `--stage simplicity` | Missing Non-Goals or `[...]` placeholders |
| **Q2 -> 3A** | `risk-spike-register.md`, `threat-model.md` | `python3 scripts/check_spiral_gates.py --stage q2-risk` | Any `OPEN` `High`/`Critical` risk or `SPIKE_LEAK` |
| **3A -> 3B** | All 6 Pillars + `system-foundation-gate.md` (`UNLOCKED`) | `python3 scripts/check_spiral_gates.py --stage foundation --strict` | `SYSTEM_FIRST_VIOLATION`, `Proposed` ADR, ADR cycle, broken skeleton |
| **3B -> 3C** | Thin end-to-end vertical slice + unit/integration tests | Project test command (`pytest -q --tb=short` / `npm test`) | Broken build/test or slice incomplete |
| **3C -> Q4** | `PRE-SHIP-CONDENSATION`, Black-Box QA + Security audit | `check_spiral_gates.py --stage simplicity --strict` + QA/Sec runs | Unrun Deletion Pass, open `P0/P1`, failed PoC |
| **Q4 -> Next** | Scope Delta, Exit Telemetry, 5-Q CoV, `<= 5` Action Items | `check_spiral_gates.py --stage all --strict` | Missing telemetry marked `PASS` instead of `NOT ASSESSED` |

### Brownfield Stage-Detect Confidence Calibration
When onboarding an existing repository, cross-check declared status against deterministic file heuristics:
- **Match** (declared `3B` and `architecture.md` + `data-model.md` + `adr/*.md` + tests exist cleanly) -> Stage Confidence `HIGH`; enter next Spiral directly.
- **Disagreement** (declared `3B` or `prod` but ADRs/contracts/tests are absent or placeholder-only) -> Stage Confidence `CONCERNS`; pause feature additions and run Adopt remediation to close `BLOCKING`/`HIGH` foundation gaps without rewriting working features.

---

## 4. Verification Checklist

- [ ] Entry state inspected on disk before selecting `greenfield` or `brownfield` (`BLOCKING` adopt gaps resolved if brownfield).
- [ ] Rigor Tier (`minimal | standard | full`) declared, with automatic `standard`/`full` elevation on Auth, PII, or Payments subsystems.
- [ ] `Spiral Charter` contains explicit Non-Goals, Quantitative Exit Criteria, Complexity Budget, and Option A Simplest High-Craft rationale.
- [ ] Q2 Risk & Threat Model completed and all `High`/`Critical` risks mitigated or spiked before Phase 3A.
- [ ] Phase 3A Foundation Gate (`check_spiral_gates.py --stage foundation`) exited `0` (`UNLOCKED`) prior to any 3B feature/UI commits.
- [ ] Every Q3 slice delivered end-to-end (`backend + API + UI + tests`) and passed `PRE-SHIP-CONDENSATION` Deletion Pass.
- [ ] Q4 Scope Delta, Exit Telemetry, and 5-question Chain-of-Verification populated with fresh evidence (`NOT ASSESSED` used wherever data is absent).

---

## 5. Hard Quality Gate

- **Command**: `python3 scripts/check_spiral_gates.py --project-dir <repo> --stage all --strict --json`
- **Entry Criteria (`Q1 -> Q2 -> 3A`)**: `PASS` requires valid Charter (`minimal | standard | full`), Non-Goals, `PRE-DESIGN` Simplicity Record, and brownfield Adopt clearance if applicable.
- **Phase 3A Gate (`3A -> 3B`)**: Enforced by [System-First Foundation Gate](system-first-foundation-gate.md); exit code `0` mandatory before coding/UI authoring.
- **Exit Gate (`Q4 -> S_{k+1} / Release`)**:
  - `PASS`: All tier artifacts complete (zero `[...]` placeholders), `0` `P0/P1` defects, Scope Delta `<= 10%`, fresh passing tests + security + CoV verified.
  - `CONCERNS`: Scope Delta `10–25%` or signed non-critical waivers recorded with deadlines.
  - `NOT ASSESSED`: Any unrun check, hollow metric, or zero-item baseline denominator.
  - `FAIL`: Broken build/tests, `SYSTEM_FIRST_VIOLATION`, unresolved `P0/P1`, or `> 25%` unapproved scope creep.

### Spiral Completion & Carryover Protocol
Before closing `SP-<N>` and opening `SP-<N+1>`:
1. Set `Status: COMPLETED` (never leave completed charters `ACTIVE`) and freeze `Spiral Exit Verdict`.
2. Verify every deferred item is listed under `Next-Spiral Carryover` (`<= 5` items, each with `Owner`, `Deadline`, and `Verification Command`).
3. Archive completed spike/prototype notes and verify `git status` is clean before tagging or releasing.

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Waterfall Disguised as Spiral** | Defers integration, UI, and verification until final weeks; causes catastrophic late rework | Spiral 1 runs `> 2` weeks with `0` runnable vertical slices | Deliver a thin end-to-end slice inside every Q3B after Phase 3A unlocks |
| **Silent `PASS` on Missing Data** | Missing telemetry or empty baselines masquerade as `0` errors or `0%` scope creep | `0%` drift on empty baseline; `PASS` with unrun checks | Enforce `FAIL > CONCERNS > NOT ASSESSED > PASS` and `NOT ASSESSED — NO DATA` |
| **Brownfield Bulldozing** | Rewrites working production paths or overwrites active user stories blindly | Broken existing tests or discarded WIP during onboarding | Run Stage Detect + 4-tier Adopt audit; fix `BLOCKING` format gaps while preserving WIP |
| **Gate Artifact Fabrication** | Auto-generates `[TBD]` stub files to pass an existence check | Stub markdown created moments before gate with placeholder brackets | Never auto-fabricate gate artifacts; treat `[...]` placeholders as `NOT ASSESSED` |
| **Over-Scoped Spiral 1** | Packs 8 epics into `SP-001`, causing `> 50%` scope overrun and skipped verification | `SP-001` lists `> 3` epics or `> 2` weeks estimated work | Cut features (`Non-Goals`), never cut Phase 3A Foundation or QA rigor |
| **Tier-Waived Security/Auth** | Applies `minimal` checks to Auth/PII/Payments because the overall repo is small | Password reset, JWT, or Stripe routes lack STRIDE or black-box checks | Enforce additive subsystem elevation (`standard`/`full`) on Auth, PII, and Payments |

---

## Related Governance Modules
- [System-First Foundation Gate](system-first-foundation-gate.md)
- [Anti-Overengineering Simplicity Gate](anti-overengineering-simplicity-gate.md)
- [Token Economy & Progressive Disclosure](token-economy-and-progressive-disclosure.md)
- [Risk, Prototyping & Spikes](risk-prototyping-and-spikes.md)
- [Orchestration Protocol](../orchestration-protocol.md)
