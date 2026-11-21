---
name: product-discovery-and-specs
description: "Run product discovery, frontier design-tree grilling, Jobs-to-be-Done framing, PRDs, explicit non-goals, domain glossaries, structured use cases, vertical feature breakdowns, acceptance criteria, and quantitative NFR/SLO budgets. Use during Spiral Q1/Q2/Q4 or when defining scope before architecture."
license: MIT
metadata:
  suite: appnwebsite-skill
  version: "1.0.0"
  milestone: M2
  spiral_stages: "Q1,Q2,Q4"
---

# Product Discovery, Specs, Use Cases, and Quantitative NFRs

Convert fuzzy product ideas into falsifiable requirements, vertical slices, and measurable reliability/cost budgets **before** system architecture (Phase 3A) or coding (Phase 3B) begins.

> **Progressive Disclosure Rule**: Read ONLY the single reference module and template needed for the active Spiral stage or task below. NEVER bulk-load all four reference modules simultaneously.

---

## 1. Rigor Tier Scaling (`minimal | standard | full`)

| Rigor Tier | Discovery & PRD Scope | Use Cases & Breakdown | Quantitative NFR / SLO Floor |
|---|---|---|---|
| `minimal` | 1-round grill (`<= 5` Qs), 1-page `prd.md`, **Option A** Wedge, `>= 3` `NG-NNN` | `1` MVP build-order list, `coarse` stories (`5–10` ACs), explicit `Out of Scope` | Baseline availability (`99.5%`), latency (`p95 <= 500ms`), `RPO <= 24h`, cost cap |
| `standard` | `2–3` grill rounds, `<= 2` personas, `<= 3` JTBDs, OST, `GLOSSARY.md`, 5-vector edge matrix | `UC-NNN` + `EP-NNN` (`<= 3` epics), `balanced` stories (`2–4` ACs), `PR-EPIC` + `QL-STORY-READY` | `99.9%` SLO + error budget, `p95 <= 250ms`, CWV targets, `RPO <= 15m` PITR |
| `full` | Multi-persona evidence synthesis, full `FR-NNN` matrix, external spec score `>= 7/10` | `balanced`/`fine` (`1` AC) stories, strict `Accepted` ADR traceability, full gates | `99.95%–99.99%` SLO, burn-rate freeze, `RPO <= 1m` / `RTO <= 15m`, load/chaos target |

*Security Elevation Invariant*: Any slice touching authentication, PII, or payments automatically elevates spec, edge-case, and NFR security/audit floors to `standard` (or `full` for multi-tenant compliance).

---

## 2. Progressive Disclosure Routing Table

| Active Need / Spiral Q1–Q4 Task | Load Reference (`references/`) | Output Template (`templates/`) | Canonical Output (`docs/product/`) |
|---|---|---|---|
| Problem framing, JTBD, personas, OST, narrowest wedge, frontier grilling | [product-discovery-and-jtbd.md](references/product-discovery-and-jtbd.md) | [prd-spec.md](templates/prd-spec.md) *(Section 1)* | `docs/product/prd.md` *(Section 1)* |
| PRDs, `FR-NNN`, implicit behaviors, `NG-NNN` non-goals, `GLOSSARY.md`, edge matrix | [prd-and-functional-specs.md](references/prd-and-functional-specs.md) | [prd-spec.md](templates/prd-spec.md) *(Sections 2–6)* | `docs/product/prd.md` + `docs/product/GLOSSARY.md` |
| `UC-NNN` main/alt/exception flows, vertical `EP-NNN`, `ST-NNN` stories, ACs | [use-cases-and-feature-breakdown.md](references/use-cases-and-feature-breakdown.md) | [use-case-spec.md](templates/use-case-spec.md) | `docs/product/use-cases.md` + `docs/product/feature-breakdown.md` |
| Workload math, SLIs/SLOs, error budgets, `p50/p95/p99`, `RPO/RTO`, JS/cost caps | [non-functional-requirements.md](references/non-functional-requirements.md) | [nfr-slo-spec.md](templates/nfr-slo-spec.md) | `docs/product/nfr-slo-matrix.md` |

---

## 3. Negative Triggers (When NOT to Load This Skill)

- **Localized bugfix or `<= 2`-file CSS/UI adjustment** with zero requirement or contract change -> stay in Direct Mode.
- **Greenfield architecture, C4 diagrams, ERDs, migrations, or ADRs** -> hand off to `system-data-architecture`.
- **Visual design tokens, typography, color contrast, or Figma parity** -> hand off to `ui-design-craft` or `figma-design-to-code`.
- **Test execution, black-box QA runs, or security audits** -> hand off to `multi-layer-qa-testing` or `security-engineering`.

---

## 4. Spiral Q1 / Q2 / Q4 Integration & Standalone Fallback

- **Spiral Q1 (Objectives & Charter)**: Consume `spiral-charter.md` and `simplicity-interrogation-record.md` (when orchestrated); execute frontier grilling + Simplicity Q1/Q2; lock `prd.md`, `GLOSSARY.md`, `use-cases.md`, `feature-breakdown.md`, and `nfr-slo-matrix.md`.
- **Spiral Q2 (Risk & Ambiguity Triage)**: Surface open `Missing Information` items, technical feasibility guesses, and unverified NFR assumptions for spike/risk resolution before Phase 3A.
- **Spiral Q4 (Scope Delta & Carryover)**: Compute `Scope Delta % = (Delivered - Baseline) / Baseline` (`<= 10% PASS`, `10–25% CONCERNS`, `> 25% FAIL`, `0` baseline -> `NOT ASSESSED`) and feed deferred `NG-NNN` items cleanly into `SP-<N+1>`.
- **Standalone Child Fallback (3 Pre-Flight Checks)**: When invoked directly without the parent orchestrator:
  1. Scan the workspace read-only (`< 3` source files = greenfield; `>= 3` = brownfield) before asking questions.
  2. Enforce Simplicity Q1/Q2 (**Option A Narrowest Wedge** first, `>= 3` Non-Goals cut) before expanding scope or SLOs.
  3. Run the deterministic Python gate checks in Pillar 5 of the active reference module before declaring specs `READY`.

---

## 5. Radical Simplicity & Token-Economy Rules

1. **Cut Scope Before Quality**: Protect testability, error handling, and Phase 3A contracts; shrink feature surface via `NG-NNN` instead.
2. **Tool-First Fact Discovery**: Inspect existing files before asking users for repo facts; grill strictly along unsettled frontier branches.
3. **Single Source of Truth**: Reference `FR-NNN`, `UC-NNN`, and `NFR-NNN` IDs across documents rather than copying prose.
4. **Incremental Disk Writes**: Flush finalized PRD, use-case, and NFR sections directly to `docs/product/*` instead of echoing long drafts in chat.
5. **Zero Hollow Specs**: Reject subjective adjectives (`fast`, `intuitive`, `scalable`) and stub markers (`TODO`, `TBD`, `FIXME`, `[placeholder]`) outside code spans.
