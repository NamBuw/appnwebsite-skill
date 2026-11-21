# Product Requirements Document (PRD) & Discovery Brief

> **Canonical Output Path**: `docs/product/prd.md` (alongside `docs/product/GLOSSARY.md`)

| Field | Value |
|---|---|
| **Product / Feature Name** | [e.g., Invoice Reconciliation Workspace] |
| **Spiral ID** | `SP-01` |
| **Rigor Tier** | `minimal` / `standard` / `full` (auto-elevate to `standard`+ for Auth, PII, or Payments) |
| **Status** | `DRAFT` / `REVIEW` / `LOCKED` |
| **Owner** | [Product Lead / Role] |
| **Updated (UTC)** | `YYYY-MM-DDTHH:MM:SSZ` |

---

## 1. Discovery Brief & Narrowest Wedge

### 1.1 Concrete Pain Evidence (Observed vs. Inferred)

- **Problem Statement (1 sentence)**: [Who experiences what measurable friction, under which workflow, costing what time/money/error rate.]
- **Observed Evidence**: [Direct user quote, support ticket count, funnel drop-off %, or recorded workaround observed in repo/telemetry.]
- **Inferred Hypotheses (Unverified)**: [Explicitly tagged assumptions requiring validation before locking scope.]

### 1.2 Target Persona(s) (Maximum 2 Behavioral Archetypes)

| Persona ID | Behavioral Archetype | Primary Context & Constraint | Success Outcome |
|---|---|---|---|
| `P-01` | [e.g., Solo Operations Manager] | [e.g., Reconciles 80 CSV rows/week under 15-min deadline] | [e.g., Zero manual formula errors] |
| `P-02` | [Optional secondary persona; omit for `minimal` tier] | [Context and operational constraint] | [Measurable outcome] |

### 1.3 Jobs-to-be-Done (JTBD) Statements (Maximum 3)

1. `JTBD-01`: When [situation], I want to [motivation/action], so I can [expected measurable outcome].
2. `JTBD-02`: When [situation], I want to [motivation/action], so I can [expected measurable outcome].

### 1.4 Ranked Opportunity Solution Tree (OST)

| Opportunity ID | Pain / Friction | Evidence Type | Severity (1–5) | Frequency (1–5) | Confidence | Product Leverage | Horizon |
|---|---|---|---|---|---|---|---|
| `OPP-01` | [Specific bottleneck] | `Observed` | `5` | `4` | `High` | `High` | `Fix This Week` |
| `OPP-02` | [Secondary gap] | `Inferred` | `3` | `3` | `Low` | `Medium` | `Fix Next Quarter` |

### 1.5 Candidate Approaches (Surface Simplest High-Craft Option First)

1. **Option A — Narrowest Wedge (Recommended Default)**: [Single core capability delivering >= 80% of target outcome in <= 20% of build surface; effort estimate in days.]
2. **Option B — Expanded Scope**: [Broader capability; state exact `NFR` or validated evidence justifying added complexity.]
3. **Option C — Minimal Manual/Bridge**: [Lowest-code operational workaround if Option A is still unvalidated.]

### 1.6 Binary / Quantitative Success Validator

- **Target Metric & Threshold**: [e.g., `>= 85%` of uploaded CSVs auto-matched in `< 2.0s` p95 with `0` silent rounding mismatches.]
- **Verification Method**: [Exact test command, telemetry query, or UAT measurement.]

---

## 2. Domain Glossary Reference & Core Terms

- **Canonical Glossary File**: `docs/product/GLOSSARY.md` (strictly free of database tables, framework names, or code details).

| Canonical Term | Precise Domain Definition | Forbidden / Conflicting Aliases |
|---|---|---|
| `[e.g., Workspace]` | [Billing and data isolation boundary owned by one Customer.] | `Account`, `Org`, `Tenant` |
| `[e.g., Member]` | [Authenticated User holding one role inside one Workspace.] | `User`, `Profile`, `Operator` |

---

## 3. Functional Requirements (`FR-NNN`)

| FR-ID | Priority | Actor | Observable Requirement & Trigger | Implicit Behaviors Included | Linked UC / NFR |
|---|---|---|---|---|---|
| `FR-001` | `P0` | `P-01` | When [trigger], the system must [observable, testable action within numeric threshold]. | [e.g., File size > 25MB rejected with 413; cancel control exposed] | `UC-001` / `NFR-001` |
| `FR-002` | `P1` | `P-01` | When [trigger], the system must [observable behavior]. | [e.g., Empty state displays single primary action] | `UC-002` / `NFR-002` |

---

## 4. Explicit Non-Goals & Scope Cuts (`NG-NNN`)

> Every Spiral MUST explicitly state what is excluded to protect Simplicity (`Option A`) and prevent scope creep.

| NG-ID | Excluded Feature / Edge Case / Config | Why Cut (Simplicity / YAGNI / Evidence Gap) | Target Spiral |
|---|---|---|---|
| `NG-001` | [e.g., Multi-currency real-time FX conversion] | [Zero observed P0 demand; adds external FX feed & rounding drift] | `SP-02` |
| `NG-002` | [e.g., Custom role-builder UI] | [Fixed 2-role model (`Owner`, `Member`) satisfies 100% of Wedge] | `SP-03` |
| `NG-003` | [e.g., White-label custom domain routing] | [No validated enterprise SLA; high TLS/DNS operational toil] | `Deferred` |

---

## 5. Edge Cases, Failure Modes & Error Semantics

| Scenario ID | Linked FR | Trigger / Boundary Condition | Expected System State | User-Visible Error & Recovery Path |
|---|---|---|---|---|
| `EDGE-001` | `FR-001` | Empty dataset / zero matching rows | Zero crash; state remains clean | Empty-state card explaining reason + 1-click sample/import action |
| `EDGE-002` | `FR-001` | Duplicate submit / concurrent write | Idempotent single record preserved | Inline confirmation of existing record; no duplicate charge/row |
| `EDGE-003` | `FR-001` | Upstream timeout or validation failure | Transaction rolled back cleanly | Actionable message stating failing field/step + safe retry button |

---

## 6. Ambiguity & Clarification Ledger + Readiness Verdict

| Ledger Type | Item ID | Question / Gap / Conflict | Blocking Impact | Working Assumption or Resolution | Status |
|---|---|---|---|---|---|
| `Clarification` | `AMB-01` | [Ambiguous rule] | [Which `FR` / story] | [Concrete Option A default] | `RESOLVED` / `OPEN` |
| `Missing Info` | `AMB-02` | [Missing threshold or policy] | [Blocks `ST-003` if open] | [Owner + deadline] | `RESOLVED` / `OPEN` |
| `Conflict` | `AMB-03` | [`FR-002` vs `FR-005` constraint] | [Auth / data boundary] | [Chosen precedence rule] | `RESOLVED` / `OPEN` |

- **Builder Check Readiness Verdict**: `READY` / `NEEDS_WORK` / `NOT ASSESSED`
- **Blocking Open Items Count**: `0` (must equal `0` before Phase 3A handoff)
