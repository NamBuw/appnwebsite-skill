# Spiral Charter (`SP-<NNN>`)

- **Spiral ID**: [SP-001]
- **Project / Product Name**: [Product or Repository Name]
- **Primary Surface**: [Landing Page | Web App / SaaS | Mobile App | Dashboard | Design System | UI Redesign | Backend / API | Full-Stack Product]
- **Lifecycle Mode**: [greenfield | brownfield]
- **Rigor Tier**: [minimal | standard | full] *(Aliases: micro -> minimal, standard -> standard, enterprise -> full. Tier scales doc breadth ONLY; NEVER waives Phase 3A Foundation Floor or Simplicity Gate)*
- **Status**: [DRAFT | ACTIVE | COMPLETED | ABORTED]
- **Updated (UTC)**: [YYYY-MM-DDTHH:MM:SSZ]
- **Owner**: [Lead Engineer / Architect / Product Owner]

<!-- CHECKPOINT -->
- **Active Spiral**: [SP-001] | **Tier**: [minimal | standard | full] | **Mode**: [greenfield | brownfield]
- **Current Quadrant**: [Q1 | Q2 | 3A | 3B | 3C | Q4]
- **Phase 3A Lock**: [LOCKED | UNLOCKED]
- **Simplicity Gate**: [NOT ASSESSED | PASS | CONCERNS | FAIL] (`SIR-001`)
- **Current Slice**: [Slice name or none before 3A]
- **Next Action**: [Single concrete next step]
- **Blockers**: [None or IDs]
- **Files In Progress**: [Comma-separated paths]
<!-- /CHECKPOINT -->

---

## 1. Objectives, Scope & Explicit Non-Goals

- **Primary Objective**: [One sentence: Observable Outcome + Target Actor/User + Primary Constraint]
- **Target Vertical Slice(s)**:
  - [Slice 1: End-to-end thin slice spanning Schema -> API/Logic -> UI -> Tests]
- **Non-Goals / Out of Scope (Anti-Goals)**:
  - [Explicit exclusion 1 — what this Spiral will NOT build or abstract]
  - [Explicit exclusion 2 — deferred capabilities for later Spirals]

### Measurable Exit Criteria

| Criterion ID | Behavior / Outcome | Target Threshold | Verification Method | Evidence Locator |
|---|---|---|---|---|
| EC-01 | [Core user or system capability] | [Quantitative target e.g. p95 < 200ms, 0 P0/P1] | [Command / Test suite / Audit] | [Path or CI log] |
| EC-02 | [Security / A11y / Craft criterion] | [e.g. WCAG 2.2 AA, 0 critical STRIDE] | [Tool / Check] | [Report path] |

---

## 2. Constraints & Operating Mode

- **Spiral Budget**:
  - **Timebox**: [1–3 days minimal | 1–2 weeks standard | 2–4 weeks full]
  - **Complexity Ceiling**: [Max new external deps: N | Max new services/stores: 0 | Max new endpoints/screens: N]
  - **Token-Economy Rule**: Query via `python3 scripts/query_skill.py` before bulk-reading modules; keep checkpoints `<= 25` lines.
- **Tech Stack & Platform Envelope**:
  - [Runtime, language, framework, database, target browsers/devices, compliance/privacy boundaries]
- **Greenfield vs. Brownfield Baseline**:
  - *If `greenfield`*: [Clean-slate system boundary, target repo layout, initial CI & walking-skeleton smoke target]
  - *If `brownfield`*: [Existing stack/versions, Stage Detect & Adopt audit summary (`BLOCKING/HIGH` gaps resolved), baseline metrics (test pass rate, Lighthouse/a11y, error rate), backward-compatibility constraints]

---

## 3. Alternatives & Simplest High-Craft Option

- **Linked Simplicity Record**: [Path to filled SIR-001 based on `simplicity-interrogation-record.md`]

| Option | Moving Parts & Dependencies | Quality / Craft Impact | Reversibility | Verdict |
|---|---|---|---|---|
| Option A (Simplest High-Craft) | [e.g. Modular monolith + Postgres + native HTML/CSS] | [High — minimal failure modes, fast iteration] | [High] | [SELECTED | REJECTED] |
| Option B (Complex Alternative) | [e.g. Separate microservices + queue + state lib] | [Adds ops/latency/boilerplate overhead] | [Low] | [REJECTED | SELECTED] |

- **Selection Rationale**: [2–3 sentences proving Option A (Simplest High-Craft) was chosen, or citing an Accepted ADR with measured evidence justifying any added complexity.]

---

## 4. Cross-Quadrant Gate Ledger & Q4 Spiral Exit

- **Linked Artifacts**:
  - Simplicity Record: [simplicity-interrogation-record instance path]
  - Risk & Spike Register: [risk-spike-register instance path]
  - Phase 3A Foundation Gate: [system-foundation-gate instance path]
- **Q4 Scope & Exit Telemetry**:
  - **Planned Items**: [N] | **Delivered Items**: [N] | **Scope Delta (%)**: [<=10% PASS | 10-25% CONCERNS | >25% FAIL | NOT ASSESSED — NO DATA]
  - **Defects Open (P0/P1/P2)**: [0/0/N] | **Complexity Budget Delta**: [New Deps: N | Net LOC Delta: N]
- **Spiral Exit Verdict**: [NOT ASSESSED | PASS | CONCERNS | FAIL] *(Precedence: `FAIL > CONCERNS > NOT ASSESSED > PASS`)*
- **Next-Spiral Carryover (`<= 5` Owned Action Items)**:
  1. [Action | Owner | Deadline | Verification Command]

---

## References
- Governance: [Spiral Lifecycle](../references/00-spiral-governance/spiral-lifecycle.md) | [Token Economy](../references/00-spiral-governance/token-economy-and-progressive-disclosure.md)
- Sibling Templates: [Simplicity Record](simplicity-interrogation-record.md) | [Risk & Spike Register](risk-spike-register.md) | [System Foundation Gate](system-foundation-gate.md)
- Validator: `python3 scripts/check_spiral_gates.py --stage charter --file <this-file>`
- Parent Router: [SKILL.md](../SKILL.md)
