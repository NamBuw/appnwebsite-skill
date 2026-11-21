# Parent-to-Child Orchestration Protocol

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This protocol governs how the Parent Orchestrator ([SKILL.md](../SKILL.md)) routes, gates, dispatches, compacts, and reconciles work across the **11 standalone Child Skills** registered in [registry.json](../registry.json). It enforces three non-negotiable invariants across every transition: **System-First Foundation (Phase 3A)**, **Least Code, Highest Craft ("ít nhất mà tốt nhất")**, and **Maximum Signal, Minimum Tokens** (strictly `<= 2` Child Skills loaded concurrently).

---

## 1. Decision Framework

### 1.1 Execution Mode Selection (Simplicity-First Routing)

Before dispatching any Child Skill, classify the incoming request into the narrowest execution mode matching actual complexity, risk, and blast radius:

| Execution Mode | Trigger & Task Complexity | Orchestration Overhead | Target Routing |
|---|---|---|---|
| **Direct Mode** | Localized edit or bugfix (`<= 1–2` files, zero schema, API, auth, boundary, or UX-pattern impact) | **Zero subagents or multi-doc ceremony** — apply Simplicity Q1/Q2 + TDD/verification directly | Parent Governance floor only (do NOT invoke `meta-plan-goal-teamwork`) |
| **Plan-First Mode (`/plan`)** | Multi-file feature, greenfield slice, or architectural change needing ordered verification | Bite-sized step plan (`Consumes`/`Produces` contracts) + Builder Check before coding | `skills/meta-plan-goal-teamwork` (`plan-first-execution`) + active 1–2 domain children |
| **Goal-Completion Evidence Loop (`/goal`)** | Ambiguous, multi-constraint, or iterative optimization target requiring falsifiable receipts | Hypothesis -> execute -> fresh command evidence -> close remaining gaps iteratively | `skills/meta-plan-goal-teamwork` (`goal-completion-evidence-loop`) |
| **Multi-Agent Teamwork Mode (`/teamwork`)** | High-complexity cross-domain build (`>= 3` independent subsystems or `> 5k`-token exploration) | Disjoint file ownership across isolated fresh-context workers + 5-component handoff | `skills/meta-plan-goal-teamwork` (`multi-agent-teamwork-orchestration`) |

**Simplest High-Craft Rule**: Default to **Direct Mode** for simple fixes and **Plan-First Mode** for standard slices. Escalate to **Multi-Agent Teamwork Mode** only when parallel lanes have disjoint write surfaces and genuine independence.

### 1.2 Active-Context Ceiling & Child Skill Dispatch Matrix

Never load all 11 Child Skills into context. Enforce an **Active-Context Ceiling of Parent `SKILL.md` + at most 2 Child Skills** at any moment, querying first via [query_skill.py](../scripts/query_skill.py).

| Spiral Stage | Execution Topology | Active Child Skills (`<= 2` Loaded Together) | Hard Entry Prerequisite | Mandatory Exit Artifact(s) |
|---|---|---|---|---|
| **Q1 — Objectives & Charter** | Sequential | `product-discovery-and-specs` (plus `meta-plan-goal-teamwork` if `/plan`, `/goal`, or `/teamwork`) | Repo state scanned (`greenfield` vs `brownfield`) | `spiral-charter.md`, `prd.md`, `use-cases.md`, `feature-breakdown.md`, `simplicity-interrogation-record.md` (`PRE-DESIGN`) |
| **Q2 — Risk, Threat & Spikes** | Parallel (2 lanes max) | `system-data-architecture` + `security-engineering` (STRIDE lane); `risk-prototyping-and-spikes` governance | Q1 Charter + Non-Goals + Simplicity Option A | `risk-spike-register.md`, `threat-model.md`, isolated `SPIKE-NOTE.md` (if spiked) |
| **3A — System-First Foundation** | **HARD SERIAL GATE** | `system-data-architecture` -> `ui-design-craft` (tokens & `design-master.md` ONLY) | `0` `OPEN` High/Critical risks; Builder Check | `architecture.md`, `data-model.md`, Accepted ADRs, `control-manifest.md`, walking skeleton, `system-foundation-gate.md` (`UNLOCKED`) |
| **3B — Vertical Slice Build** | Parallel after 3A `UNLOCKED` (`<= 2` per worker) | Backend: `fullstack-api-engineering` \| UI/Figma: `ui-design-craft` + (`figma-design-to-code` or `frontend-surfaces-and-redesign`) \| Specialized: `advanced-web-app-capabilities` | **Phase 3A `Verdict: PASS` & `UNLOCKED`** | Thin end-to-end vertical slice (`Schema -> API -> UI -> automated tests`) |
| **3C — Condensation & Multi-Layer QA** | Sequential Condensation -> Parallel Verification | `multi-layer-qa-testing` + `security-engineering` | Slice builds cleanly; Deletion Pass executed | `simplicity-interrogation-record.md` (`PRE-SHIP-CONDENSATION`), `black-box-test-matrix.md`, `security-audit-report.md` |
| **Q4 — Release, SRE & Next Spiral** | Sequential | `observability-sre-release` (+ `product-discovery-and-specs` for `SP-<N+1>`) | `0` unresolved `P0/P1` defects; fresh receipts | `telemetry-slo-config.md`, `operational-runbooks.md`, `changelog.md`, `spiral-charter.md` (`Q4 Exit`) |

### 1.3 Rigor Tier & Verdict Precedence Contract

- **Standardized Rigor Tiers**: `minimal | standard | full` (aliases: `micro -> minimal`, `standard -> standard`, `enterprise -> full`). Tier scales *documentation breadth* ONLY — it NEVER bypasses Phase 3A Foundation, Simplicity Self-Interrogation, or Auth/PII/Payments security elevation.
- **Verdict Precedence**: `FAIL > CONCERNS > NOT ASSESSED > PASS`. `NOT ASSESSED` strictly outranks `PASS` whenever any required artifact contains `[...]` placeholders, a check did not run, or telemetry is absent.

### 1.4 Concrete Dispatch Routing Scenarios

1. **Greenfield SaaS Web App + Billing (`standard` tier, `/plan` mode)**:
   - Q1: `product-discovery-and-specs` -> `prd.md`, `nfr-slo-matrix.md`, `spiral-charter.md`, `SIR-001`. Unload.
   - Q2: `security-engineering` (STRIDE on tenant isolation & Stripe webhooks) + `system-data-architecture` -> `risk-spike-register.md`. Unload.
   - 3A (Serial): `system-data-architecture` -> C4, ERD + RLS, Accepted ADRs, OpenAPI, walking skeleton; `ui-design-craft` ONLY for `design-master.md` + `tokens.json`. Run `check_spiral_gates.py --stage foundation --strict` -> `UNLOCKED`. Compact context.
   - 3B: Backend lane (`fullstack-api-engineering` + `advanced-web-app-capabilities` for webhook idempotency); UI lane (`figma-design-to-code` + `frontend-surfaces-and-redesign` consuming locked `tokens.json` + OpenAPI).
   - 3C & Q4: Deletion Pass -> `multi-layer-qa-testing` + `security-engineering` -> `observability-sre-release`.
2. **Marketing Landing Page (`minimal` tier, `/plan` mode)**:
   - Q1–3A condensed: `product-discovery-and-specs` (1-page offer/CTA brief) + `ui-design-craft` (`design-master.md` + `tokens.json`) + `system-data-architecture` (1-page IA/form schema/1 ADR/smoke test) -> unlock 3A.
   - 3B–Q4: `frontend-surfaces-and-redesign` (landing surface) -> Deletion Pass -> `multi-layer-qa-testing` (a11y/CWV/SEO).
3. **Single-Component CSS Bugfix (Direct Mode)**:
   - Zero Child Skill orchestration overhead: verify `SIR` Q1/Q2 inline (use native CSS instead of JS), TDD/repro, run fresh test/build check, done.
4. **Brownfield Security & Redesign Audit (`standard` tier, `/goal` mode)**:
   - Q1: Run Stage Detect + Adopt 4-tier triage (`BLOCKING` fixed first) -> `spiral-charter.md` (`brownfield`).
   - Q2–3A: Load `security-engineering` + `ui-design-craft` to establish baseline threat gaps and target `tokens.json`.
   - 3B–3C: Load `frontend-surfaces-and-redesign` (9-domain Scan -> Diagnose -> Fix) + `multi-layer-qa-testing` (regression + WCAG 2.2 AA).

### 1.5 Dependency Graph & Parallel Safety Rules

Every Child Skill declares `depends_on` in [registry.json](../registry.json). Never dispatch a downstream skill until its upstream `outputs` exist on disk and pass validation:

| Child Skill ID | Hard Upstream Dependencies | Can Run in Parallel With | Maximum Concurrency Rule |
|---|---|---|---|
| `product-discovery-and-specs` | None (entry Q1) | `meta-plan-goal-teamwork` | 1 product lane + optional meta planner |
| `system-data-architecture` | `product-discovery-and-specs` | `security-engineering` (Q2 STRIDE only) | Serial owner of Phase 3A foundation lock |
| `ui-design-craft` | `product-discovery-and-specs` | `system-data-architecture` (tokens/brief in 3A) | Max 2 skills active together in 3A |
| `fullstack-api-engineering` | `system-data-architecture` (3A `UNLOCKED`) | `figma-design-to-code` or `frontend-surfaces-and-redesign` | Disjoint write directories (`server/` vs `ui/`) |
| `figma-design-to-code` | `ui-design-craft`, `system-data-architecture` | `fullstack-api-engineering` | Consumes frozen `tokens.json` + OpenAPI |
| `frontend-surfaces-and-redesign` | `ui-design-craft`, `system-data-architecture` | `fullstack-api-engineering` | Consumes frozen `tokens.json` + contracts |
| `advanced-web-app-capabilities` | `system-data-architecture`, `fullstack-api-engineering` | `frontend-surfaces-and-redesign` | Loaded ONLY for specialized slice (billing/AI/PWA/SEO) |
| `security-engineering` | `system-data-architecture` | `multi-layer-qa-testing` (in 3C) | Read/test only during 3C verification; fixes route back to 3B owner |
| `multi-layer-qa-testing` | `product-discovery-and-specs`, `system-data-architecture` | `security-engineering` (in 3C) | Read/test only during 3C verification |
| `observability-sre-release` | `fullstack-api-engineering`, `multi-layer-qa-testing`, `security-engineering` | `product-discovery-and-specs` (`SP-<N+1>`) | Serial Q4 release gate owner |
| `meta-plan-goal-teamwork` | None (meta-execution wrapper) | Any 1 domain Child Skill | Never replaces Phase 3A or Simplicity Gate |

---

## 2. Step-by-Step Workflow

### Step 1 — Detect State & Select Execution Mode
1. Inspect workspace state (`ls`, `git status`, existing schemas/tests) — never assume greenfield if `>= 3` source files exist.
2. Run `python3 scripts/query_skill.py --stage <Q1|Q2|3A|3B|3C|Q4> --surface <surface> --summary` to resolve exact Child Skill IDs from [registry.json](../registry.json) without bulk-reading docs.
3. Choose **Direct**, **`/plan`**, **`/goal`**, or **`/teamwork`** per Section 1.1.

### Step 2 — Run Q1 & Q2 Governance via the Handoff Artifact Bus
All Parent <-> Child and Child <-> Child handoffs pass exclusively through **disk-backed canonical files**, never ephemeral chat memory:
1. Author `docs/spiral/spiral-charter.md` and `PRE-DESIGN` `docs/spiral/simplicity-interrogation-record.md`.
2. Dispatch `product-discovery-and-specs` to author `prd.md`, `use-cases.md`, `feature-breakdown.md`, and `nfr-slo-matrix.md`.
3. Dispatch `system-data-architecture` + `security-engineering` in Q2 to lock `risk-spike-register.md` and `threat-model.md`. Run any required throwaway spikes (`<= 4h` / `<= 1d`) strictly inside `spikes/` or `prototypes/`.

### Step 3 — Enforce the Serial Phase 3A System-First Foundation Gate
1. Dispatch `system-data-architecture` to produce C4 `architecture.md`, `data-model.md`, Accepted ADRs (acyclic `Depends On`), `control-manifest.md`, OpenAPI/shared contracts, and the runnable walking-skeleton repo + CI smoke test.
2. For UI-bearing surfaces, load `ui-design-craft` ONLY to lock `design-master.md` and W3C DTCG `tokens.json` — **zero feature screens or components yet**.
3. Run `python3 scripts/check_spiral_gates.py --project-dir <repo> --stage foundation --strict --json`.
4. **HARD STOP**: Do NOT dispatch `fullstack-api-engineering`, `figma-design-to-code`, `frontend-surfaces-and-redesign`, or `advanced-web-app-capabilities` for Phase 3B coding until `system-foundation-gate.md` records `Verdict: PASS` (or waived `CONCERNS`) and `Downstream Lock = UNLOCKED`.

### Step 4 — Execute Phase 3B Vertical Slice & Compact Context at Boundaries
1. Dispatch Phase 3B Child Skills with **explicit disjoint file ownership** and exact `Inputs -> Outputs` paths from [registry.json](../registry.json).
2. Before switching domains (e.g., Architecture -> UI -> QA), overwrite the `<= 25`-line `<!-- CHECKPOINT -->` block in `spiral-charter.md`, compact conversation context, and unload finished Child Skills to honor the `<= 2` ceiling.

### Step 5 — Execute Phase 3C Condensation, Security & Black-Box QA
1. Run the mandatory **Pre-Ship Deletion/Condensation Pass** (`simplicity-interrogation-record.md` stage `PRE-SHIP-CONDENSATION`), deleting dead exports, single-use wrappers, and redundant dependencies, then **re-run full build and tests**.
2. Dispatch `multi-layer-qa-testing` + `security-engineering` in parallel read/test lanes against the built slice (`black-box-test-matrix.md`, `security-baseline-report.json`, `security-audit-report.md`).

### Step 6 — Execute Q4 Telemetry, Release & Standalone Child Fallback
1. Dispatch `observability-sre-release` for OpenTelemetry/SLO configuration, release pipeline checks, runbooks, and changelog.
2. Record Q4 Exit Telemetry & Scope Delta in `spiral-charter.md` (`<= 5` owned carryover action items).
3. **Standalone Child Invocation Fallback**: When a user invokes any Child Skill directly without Parent `SKILL.md`, that Child Skill MUST still execute a lightweight 3-check pre-flight before coding:
   - (a) Verify architecture/data/API/token contracts exist on disk (or lock a concise `minimal` Phase 3A contract first);
   - (b) Answer Simplicity Q1 & Q2 ("Least Code, Highest Craft") before adding dependencies or layers;
   - (c) Record fresh command verification output before claiming completion (`verification-before-completion`).

### Step 7 — Failure, Escalation & Reroute Rules

| Failure / Escalation Event | Trigger Signal | Mandatory Reroute Action |
|---|---|---|
| **`SYSTEM_FIRST_VIOLATION`** | Feature/UI files written while 3A is `ABSENT`/`LOCKED`/`FAIL` | Halt 3B immediately; quarantine uncontracted code; complete 3A + `check_spiral_gates.py` before resuming |
| **Builder Guess / Spec Ambiguity** | Implementer unsure of auth rule, error shape, or token behavior | Stop coding; escalate to `system-data-architecture` or `product-discovery-and-specs` to update canonical ADR/contract |
| **`P0/P1` Security or Contract Defect** | SAST/DAST PoC or Black-Box contract test fails in 3C | Reroute to owning 3B Child Skill with exact failing test/PoC; re-verify all affected layers after fix |
| **3 Consecutive Spike Pivots** | `Pivot Count >= 3` on same risk in `risk-spike-register.md` | Trigger `KILL` confirmation checklist and archive in `GRAVEYARD.md` rather than looping |
| **Context Pressure > 70%** | Active context approaches ceiling mid-Spiral | Write `<= 25`-line `<!-- CHECKPOINT -->` to disk, compact at next boundary, reload ONLY active 1–2 Child Skills |

---

## 3. Reusable Artifact & Template

### Handoff Artifact Bus Schema (11 Child Skills)

| Producer Skill | Canonical Artifact(s) on Disk | Downstream Consumers |
|---|---|---|
| Parent Governance (`00`) | `docs/spiral/spiral-charter.md`, `simplicity-interrogation-record.md`, `risk-spike-register.md`, `system-foundation-gate.md` | All 11 Child Skills |
| `product-discovery-and-specs` | `docs/product/prd.md`, `use-cases.md`, `feature-breakdown.md`, `nfr-slo-matrix.md` | `system-data-architecture`, `ui-design-craft`, `multi-layer-qa-testing` |
| `system-data-architecture` | `docs/architecture/architecture.md`, `adr/adr-*.md`, `control-manifest.md`, `data-model.md`, `migration-plan.md`, `dpia-privacy.md` | `fullstack-api-engineering`, `security-engineering`, `observability-sre-release` |
| `ui-design-craft` | `docs/design/design-master.md`, `tokens.json`, `typography-grid-spec.md`, `anti-slop-audit.json` | `figma-design-to-code`, `frontend-surfaces-and-redesign` |
| `fullstack-api-engineering` | `docs/contracts/openapi.yaml` (or schema), backend services, frontend routes, `i18n/`, `code-review-log.md` | `frontend-surfaces-and-redesign`, `security-engineering`, `multi-layer-qa-testing` |
| `figma-design-to-code` | `figma-token-sync.json`, `code-connect-map`, `parity-components`, `visual-parity-report.md` | `frontend-surfaces-and-redesign`, `multi-layer-qa-testing` |
| `frontend-surfaces-and-redesign` | Production UI implementation, `design-system-kit`, `redesign-audit-report.md` | `security-engineering`, `multi-layer-qa-testing` |
| `security-engineering` | `threat-model.md`, `security-baseline-report.json`, `security-audit-report.md`, `poc-verifications` | `observability-sre-release`, Parent Q4 Exit |
| `multi-layer-qa-testing` | `test-strategy.md`, `black-box-test-matrix.md`, automated test suites, `nonfunctional-test-report.md`, `release-qa-verdict.md` | `observability-sre-release`, Parent Q4 Exit |
| `observability-sre-release` | `telemetry-slo-config.md`, CI/CD release pipeline, `operational-runbooks.md`, `changelog.md`, `postmortem-template.md` | Parent Q4 Exit & `SP-<N+1>` |
| `advanced-web-app-capabilities` | `capability-integration-spec.md`, `idempotency-state-machine`, `ai-guardrails-report.md`, `seo-cwv-audit.md` | `security-engineering`, `multi-layer-qa-testing`, `observability-sre-release` |
| `meta-plan-goal-teamwork` | `execution-plan.md`, `goal-evidence-ledger.md`, `teamwork-handoff.md` | Parent & Parallel Workers |

Use [Spiral Charter](../templates/spiral-charter.md) and [System Foundation Gate](../templates/system-foundation-gate.md) to track bus state cleanly.

### Subagent Dispatch Contract (For `/teamwork` Mode)
Every `/teamwork` worker dispatch MUST declare: (1) `Spiral Stage` & `Rigor Tier`, (2) `Active Child Skill(s)` (`<= 2`), (3) `Exclusive Write Paths` (disjoint across parallel workers), (4) `Input Artifact Paths` on the Handoff Bus, (5) `Verification Command`, and (6) `Return Format` (5-component `handoff.md` path + concise `send_message`).

```yaml
task_id: SP001-3B-backend
spiral_stage: 3B
rigor_tier: standard
active_child_skills: [fullstack-api-engineering]
exclusive_write_paths: [src/server/**, tests/api/**]
inputs:
  - docs/spiral/system-foundation-gate.md
  - docs/architecture/data-model.md
  - docs/contracts/openapi.yaml
verification_command: pytest -q --tb=short tests/api/
return_handoff: handoff.md
```

---

## 4. Verification Checklist

- [ ] Active context holds at most Parent `SKILL.md` + `<= 2` Child Skills concurrently.
- [ ] Execution Mode (`Direct`, `/plan`, `/goal`, `/teamwork`) fits task complexity without over-orchestrating simple edits.
- [ ] All cross-child handoffs pass through canonical files on the Handoff Artifact Bus (zero verbal assumptions).
- [ ] Phase 3A serial gate (`check_spiral_gates.py --stage foundation`) returned `PASS` (or waived `CONCERNS`) and `UNLOCKED` before any 3B feature/UI dispatch.
- [ ] Parallel 3B workers hold strictly disjoint file ownership.
- [ ] `PRE-SHIP-CONDENSATION` Deletion Pass executed and full tests re-run before 3C/Q4 sign-off.
- [ ] Standalone Child Skill invocations executed the lightweight Phase 3A + Simplicity + fresh verification fallback.

---

## 5. Hard Quality Gate

- **Suite Integrity Command**: `python3 scripts/validate_skill.py . --strict --json`
- **Project Gate Command**: `python3 scripts/check_spiral_gates.py --project-dir <repo> --stage all --strict --json`
- **PASS Criteria**: `registry.json` parity is 100% (Parent + all 11 Child Skills), active Child Skill ceiling (`<= 2`) respected, Phase 3A unlocked cleanly prior to 3B files, all handoff bus artifacts non-placeholder, and fresh test/security/QA receipts recorded.
- **FAIL Criteria**:
  - Phase 3B implementation dispatched while Phase 3A is `LOCKED`, `FAIL`, or `NOT ASSESSED` (`SYSTEM_FIRST_VIOLATION`).
  - Bulk-loading `> 2` Child Skills or all reference directories simultaneously.
  - Child Skill invoked standalone skips architecture/contract/simplicity pre-checks.
  - Any `[...]` placeholder or unverified claim treated as `PASS`.

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Monolithic Context Stuffing** | Loads 5–11 Child Skills upfront, burning context and degrading instruction adherence | Agent reads `> 2` `skills/*/SKILL.md` files in one turn | Enforce `<= 2` Child Skill ceiling + `python3 scripts/query_skill.py` targeted queries |
| **Over-Orchestrating Trivial Fixes** | Spawns `/teamwork` subagents and 6 planning docs for a 1-line copy or CSS fix | Multi-agent dispatch for `<= 2`-file edit with zero boundary impact | Use **Direct Mode** with Simplicity Q1/Q2 check + fresh verification |
| **Bypassing Phase 3A via Child Shortcut** | Direct UI/backend coding invents incompatible payloads and breaks data integrity | `src/` or `components/` commits before `system-foundation-gate.md` unlocks | Enforce Phase 3A serial gate (even standalone children run lightweight contract check) |
| **Verbal Handoff Drift** | Downstream QA/UI relies on chat memory instead of canonical schema/PRD files | UI field names or status codes contradict backend OpenAPI responses | Pass all contracts exclusively via Handoff Artifact Bus files on disk |
| **Premature Parallelism on Shared Files** | Two concurrent workers overwrite the same schema, router, or token file | Merge conflicts or clobbered edits across parallel 3B agents | Serialize Phase 3A contracts first; parallelize 3B only across disjoint file ownership |

---

## Related Governance Modules
- [Spiral Lifecycle](00-spiral-governance/spiral-lifecycle.md)
- [System-First Foundation Gate](00-spiral-governance/system-first-foundation-gate.md)
- [Anti-Overengineering Simplicity Gate](00-spiral-governance/anti-overengineering-simplicity-gate.md)
- [Token Economy & Progressive Disclosure](00-spiral-governance/token-economy-and-progressive-disclosure.md)
- [Risk, Prototyping & Spikes](00-spiral-governance/risk-prototyping-and-spikes.md)
