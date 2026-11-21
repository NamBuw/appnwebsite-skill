---
name: multi-layer-qa-testing
description: "Multi-layer QA engineering: test strategy, all 8 black-box techniques (EP, BVA, state transitions, decision tables, pairwise, exploratory, E2E/UAT, API negative), white-box/integration/mutation testing, non-functional (load, WCAG 2.2 a11y, chaos), flakiness triage, and release quality gates."
license: MIT
metadata:
  suite: appnwebsite-skill
  version: "1.0.0"
  spiral_stages: "Q2, 3B, 3C, Q4"
---

# Multi-Layer QA & Testing

> **Progressive Disclosure Rule**: Read ONLY the single reference module and template matching your active QA task. Never bulk-load all five reference modules into context.

## Minimal-Token CLI Quick Query

When running inside the full `appnwebsite-skill` suite, project headings or exact sections before reading full files:

```bash
python3 scripts/query_skill.py --headings skills/multi-layer-qa-testing/references/black-box-testing-techniques.md
python3 scripts/query_skill.py --extract skills/multi-layer-qa-testing/references/release-quality-gates.md "5. Hard Quality Gate"
```

## Task -> Reference -> Template Dispatch Table

| Active Task / Spiral Stage | Read ONLY This Reference Module | Instantiate Template |
|---|---|---|
| **Q2 / 3A / 3B — Test Strategy, Topology, RBT Matrix & Flake Policy** | [Test Strategy & Planning](references/test-strategy-and-planning.md) | [Master Test Plan](templates/master-test-plan.md) |
| **3B / 3C — Black-Box Design (EP, BVA, State, Decision, Pairwise, Exploratory, E2E/UAT, API Negative)** | [Black-Box Testing Techniques](references/black-box-testing-techniques.md) | [Black-Box Test Matrix](templates/black-box-test-matrix.md) |
| **3B / 3C — TDD Unit, MC/DC, Testcontainers, Contracts, Mutation, Viz QA & Root-Cause Debug** | [White-Box & Integration QA](references/white-box-and-integration-qa.md) | [Black-Box Test Matrix](templates/black-box-test-matrix.md) |
| **3C — Load/Stress/Soak, Statistical Rigor, WCAG 2.2 Dual-Engine, Break-UI & Chaos** | [Non-Functional Testing](references/non-functional-testing.md) | [Black-Box Test Matrix](templates/black-box-test-matrix.md) |
| **3C / Q4 — 6-Phase Verification Loop, `pass^k`, Content-Hash Receipts & Release Gate** | [Release Quality Gates](references/release-quality-gates.md) | [Release Gate Sign-Off](templates/release-gate-signoff.md) |

## Negative Triggers (When NOT to Load This Skill)

- Do **NOT** load for pure visual token, palette, or typography work (route to `ui-design-craft`) or STRIDE/SAST/DAST security engineering (route to `security-engineering`, exchanging only handoff artifacts in 3C).
- Do **NOT** trigger `full` release-gate ceremony for a localized `<= 2`-file bugfix (`Direct Mode` needs only a targeted RED-to-GREEN regression test and fresh verification output).

## Standalone Pre-Flight Contract

When invoked standalone without the Parent Orchestrator:
1. **Verify Contracts & Denominator First**: Confirm acceptance criteria, schemas, or UI specs exist (`N > 0`). If zero testable requirements are in scope, emit `NOT ASSESSED` rather than a vacuous pass.
2. **Radical Simplicity ("Least Code, Highest Craft")**: Push partition, boundary, and decision-table checks down to fast `< 50 ms` API or pure domain tests; reserve browser E2E strictly for wiring, storage/cookies, and viewport/visual behavior.
3. **Iron Law (`verification-before-completion`)**: Never emit `PASS` or `GO` without fresh command exit codes and outputs observed in the active session; unrun checks MUST report `NOT ASSESSED`.
