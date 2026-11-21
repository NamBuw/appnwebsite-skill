# Test Strategy, Risk-Based Planning & Flakiness Governance

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This module establishes the end-to-end QA strategy across Spiral quadrants `Q2`, `3A`, `3B`, `3C`, and `Q4`. It replaces ad-hoc test accumulation with risk-calibrated layer allocation, deterministic isolation, regression traceability, and evidence-backed flakiness governance.

---

## 1. Decision Framework

### 1.1 Testing Topology Selector (Pyramid vs. Testing Trophy vs. Honeycomb)

Select the testing topology matching the system's coupling and failure surface rather than forcing a single ratio across every architecture:

| System / Surface Shape | Recommended Topology | Target Layer Mix (`Unit / Integration-Contract / E2E`) | Quantitative Selection Trigger |
|---|---|---|---|
| **Domain Libraries, Compilers, Pricing Engines, CLI Tools** | **Testing Pyramid** | `70%` unit / `20%` contract-integration / `10%` thin smoke E2E | `>= 60%` of complexity lives in pure deterministic functions or local parsers |
| **Full-Stack Web Apps, SaaS, BFF, React Server Components** | **Testing Trophy** | `20%` static types/lint + `25%` unit / `45%` real-DB & API integration / `10%` critical E2E | Primary bugs arise at SQL, RLS, auth, serialization, and route boundaries |
| **Microservices, Event-Driven Systems, Webhook Meshes** | **Testing Honeycomb** | `15%` unit / `70%` isolated service-boundary & consumer-driven contract / `15%` synthetic E2E | Independent deployables communicating over HTTP/gRPC/queues |
| **Static Marketing & Landing Pages** | **Lean Check Stack** | Static build + link/SEO/dual-engine a11y + `<= 3` critical lead/checkout E2E flows | Zero complex server state; primary risk is broken forms, layout overflow, or a11y |

### 1.2 Risk-Based Testing (RBT) & Slice-Type Allocation

Score **Likelihood (`1–4`)** and **Failure Impact (`1–4`)** **independently** (never compute a single averaged score that hides a catastrophic `Impact = 4` payment or auth defect behind `Likelihood = 1`). Classify every vertical slice into one of five types from the `qa-plan` model; ambiguous `Logic + Integration` slices default conservatively to `Integration`:

| Slice Type | Primary Failure Mode | Mandatory Test Evidence | `minimal` Rigor Scaling | `standard` / `full` Rigor Scaling |
|---|---|---|---|---|
| **Logic** | Incorrect math, state transitions, validation guards | Deterministic unit + EP/BVA/Decision Table suites | Waived ONLY if build/smoke passes | `>= 80%` branch coverage (`100%` on critical guards) |
| **Integration** | SQL/RLS leaks, schema drift, race conditions, webhook failure | Real-DB integration + API negative black-box probes | Critical-path smoke check (`<= 5 min`) | `100%` endpoint contract + Testcontainers isolation |
| **UI** | Broken form wiring, inaccessible controls, viewport overflow | Component interaction + Playwright `getByRole` E2E | Visual screenshot evidence retained (NEVER waived) | `390x844` + `1600x900` viewport-fit + dual-engine a11y |
| **Visual / Feel** | Animation clipping, stale loading state, broken dark/RTL layout | Retained screenshots + manual state-toggle walk-through | Visual evidence retained (NEVER waived) | `break-ui` worst-case fixtures + `200%` zoom pass |
| **Config / Data** | Missing env flags, malformed JSON/CSV, broken migration seeds | Schema validation + boot/readiness smoke probe | Blocking unless `testing.strict.config` disabled | Automated schema check + dry-run seed verify |

> **Non-Waivable Subsystem Override**: Any slice touching **Authentication**, **PII**, or **Payments / Billing** automatically elevates to at least `standard` (or `full` for production releases) regardless of sprint schedule pressure.

### 1.3 Test Tier Cadence & Quantitative SLAs

| Tier | Execution Cadence | Runtime Ceiling | Scope & Quantitative Exit Criterion |
|---|---|---|---|
| **Smoke Suite** | Every PR & pre-QA handoff | `<= 5 min` | `5–15` critical-path boot, health, auth, and primary write checks; timeout (`exit 124`/`142`) or `0` executed tests = fail/unassessed |
| **PR / Vertical Slice** | Every commit / pull request | `<= 10 min` | Changed-slice unit + black-box API + real-DB integration tests; `100%` pass |
| **Curated Regression** | Pre-release / Spiral `3C` close | `<= 25 min` | `100%` of closed `P0/P1/P2` bugs (`BUG-NNN` -> test file) + critical user journeys |
| **Soak / Endurance** | Pre-release for stateful services | `30m / 1h / 2h / 4h` | Timed `T+0` checkpoints (`10m–30m` intervals); fail on `> 20%` heap growth post-warmup or monotonic rise across `>= 3` checkpoints |

### 1.4 Simplest High-Craft Test Strategy & Anti-Overengineering

Before introducing any custom test harness, Selenium grid, distributed mock server, or synthetic browser farm, pause and verify:
- **Simplest High-Craft Option**: Use the stack's native test runner (`pytest`, `vitest`, `node --test`, `playwright`) paired with one ephemeral real database (local Postgres/Testcontainers or SQLite matching dialect) and seeded synthetic builders.
- **Anti-Overengineering Self-Question**: *"Can a fast deterministic unit or black-box API contract test prove these 12 boundary and rule permutations in `< 50 ms` instead of spinning up 12 redundant browser sessions?"* If yes, push the logic checks down to the fast layer and keep browser E2E lean.

---

## 2. Step-by-Step Workflow

1. **Enforce the Scope & `N=0` Denominator Guard**
   - **Inputs**: `prd.md`, `use-cases.md`, `feature-breakdown.md`, `nfr-slo-matrix.md`.
   - **Owner**: QA Lead / Feature Engineer.
   - **Tool / Script**: Targeted section `grep -n` (`^## Acceptance Criteria`, `^## Risks`) respecting the `40 KB` Read Guard rather than bulk-reading entire planning docs.
   - **Output**: Verified scope count `N > 0` in `master-test-plan.md`. If `N == 0` testable stories or acceptance criteria exist, **STOP immediately** and emit `NOT ASSESSED — no testable scope in sprint/spiral` (never output a misleadingly clean `0/0` test plan).

2. **Classify Slices & Allocate Test Layers**
   - **Inputs**: Scoped requirements (`N > 0`), `architecture.md`, `control-manifest.md`.
   - **Owner**: QA Engineer.
   - **Tool / Script**: Risk-Based Testing (`Likelihood x Impact`) table + Topology selector (`1.1` and `1.2`).
   - **Output**: Completed RBT & Layer Allocation Matrix assigning each slice to Unit, Integration/Contract, Black-Box techniques, and E2E/Visual checks, applying the Auth/PII/Payments elevation rule.

3. **Lock Deterministic Environment, Isolation & Seeding Rules**
   - **Inputs**: `data-model.md`, local/CI runner config.
   - **Owner**: Platform / Backend Engineer.
   - **Tool / Script**: `Testcontainers` or per-test DB transaction rollback; `freezegun` / `vi.useFakeTimers`; deterministic factory builders.
   - **Output**: Written seeding and isolation contract enforcing: (a) pinned PRNG and hash seeds (`PYTHONHASHSEED=0`, logged seed on failure), (b) frozen UTC timestamps for time-dependent tests, (c) zero production PII dumps in fixtures, and (d) strict browser context isolation (`--isolated`).

4. **Curate Smoke & Regression Manifests (`BUG-NNN` Traceability)**
   - **Inputs**: Closed bug tracker issues (`P0–P2`), critical journey inventory, existing `tests/`.
   - **Owner**: QA Engineer.
   - **Tool / Script**: Manifest audit (`tests/regression-suite.md` or `master-test-plan.md` §4).
   - **Output**: Explicit `HAS REGRESSION TEST` vs `MISSING REGRESSION TEST` ledger. Track drift indicators (new modules without tests, specs modified since last run, manifest untouched for `> 2` Spirals). If `0` critical paths or `0` executable test files exist, emit `NOT ASSESSED` instead of dividing by zero (`0%` or `100%`).

5. **Execute Flakiness Triage & Quarantine Governance**
   - **Inputs**: CI JUnit/NUnit XML reports or local `--repeat-each=10` stress runs.
   - **Owner**: QA Engineer + Module Owner.
   - **Tool / Script**: `npx playwright test --repeat-each=10` / `pytest --count=10` + 7-Cause Flake Matrix.
   - **Output**: Triaged `test_id -> [run1..runN]` matrix obeying three strict rules:
     - **Minimum 3-Run Rule**: With `< 3` observed runs, label every intermittent failure `suspected` ONLY — never quarantine or ignore on 1–2 runs.
     - **Rate Thresholds**: `> 25%` failure rate = **High** (quarantine via tracked skip annotation + immediate `P1` fix ticket with deadline); `5–25%` = **Moderate** (fix directly, do not quarantine); `1–5%` = **Low** (monitor).
     - **7-Cause Root Diagnosis**: Classify into `Timing/async`, `Order dependency`, `Random seed`, `Resource leak`, `External state`, `Floating point epsilon`, or `Load/render race`. **Quarantine never equals deletion**: never delete a flaky test file silently.

   | Observed Flake Rate (`>= 3` Runs) | Confidence & Severity Tier | Mandatory Engineering Action |
   |---|---|---|
   | **Any rate (`< 3` runs)** | `suspected` only | Re-run with `--repeat-each=10`; never quarantine on 1–2 samples |
   | **`1% – 5%`** | Low confirmed | Log in Flakiness Registry and monitor across next 3 PRs |
   | **`5% – 25%`** | Moderate confirmed | Fix root cause directly without quarantining |
   | **`> 25%`** | High confirmed | Quarantine non-critical test with tracked `P1` fix ticket & deadline (`0%` allowed on Auth/Pay/P0) |

6. **Run Complexity Budget & Test-Suite Deletion/Condensation Pass**
   - **Inputs**: Drafted test suites and fixture helpers.
   - **Owner**: Peer Reviewer / QA Lead.
   - **Tool / Script**: Test runner (`pytest -q --tb=short` / `vitest run`) + `git diff --stat`.
   - **Output**: Lean, high-signal suite with redundant E2E permutations pushed to API/unit tests, `> 3`-times repeated boilerplate collapsed into one factory helper, arbitrary `sleep()` calls replaced by condition-based waits, and a fresh passing test run recorded **after** the final deletion edit.

---

## 3. Reusable Artifact & Template

Instantiate [Master Test Plan Template](../templates/master-test-plan.md) at the start of Spiral `3A`/`3B` and update through `3C` before release gating.

| Field / Section | Required Type / Format | Validation Rule |
|---|---|---|
| `Plan ID` / `Spiral ID` / `Surface` | String slugs (`MTP-NNN`, `SP-NNN`) + enum | Must map to active Spiral Charter and primary surface |
| `Rigor Tier` / `Selected Topology` | `minimal \| standard \| full` + topology enum | Auth/PII/Payments forces `>= standard` |
| `Requirements In Scope (N > 0)` | Positive integer + Req ID list | `N == 0` forces immediate `NOT ASSESSED` halt |
| `RBT & Layer Allocation Matrix` | Markdown table (`Likelihood 1–4`, `Impact 1–4`) | Likelihood and Impact scored separately; slice type assigned |
| `Seeding & Isolation Contract` | Isolation tier + pinned seed + clock freeze | Zero production PII dumps; pinned PRNG seed required |
| `Smoke & Regression Manifest` | Critical paths + `BUG-NNN` -> test path table | Every closed `P0/P1` bug maps to a real test file |
| `Flakiness Quarantine Registry` | Table (`Runs >= 3`, `Fail %`, `7-Cause`, `Deadline`) | Zero silent deletions; `< 3` runs labeled `suspected` |
| `Deletion Pass & Verdict` | Condensed tests summary + fresh exit code | Must execute tests after final cleanup before `APPROVED` |

---

## 4. Verification Checklist

- [ ] Scope denominator `N > 0` verified against requirements before generating test plan verdicts.
- [ ] Likelihood and Failure Impact scored independently without averaging away catastrophic risk.
- [ ] All Authentication, PII, and Payments slices automatically elevated to standard or full rigor.
- [ ] Selected topology matches system coupling rather than duplicating slow E2E UI tests.
- [ ] Deterministic PRNG seeds, frozen clocks, and synthetic PII-free test factories documented cleanly.
- [ ] Every closed P0, P1, and P2 defect maps to an executable regression test path.
- [ ] Flakiness triage enforces the three-run minimum rule and logs quarantine tickets with owners.
- [ ] Complexity budget deletion pass completed and test suite re-executed cleanly afterward.

---

## 5. Hard Quality Gate

Release readiness for test strategy and planning is binary-gated before Slice execution or release sign-off:

- **PASS**: `N > 0` stories mapped in the RBT matrix; `0` unassessed Auth, PII, or Payment overrides; deterministic PRNG seeds and frozen clocks locked; Smoke suite executes `> 0` real tests in `<= 5 min` with exit `0`; `100%` of closed `P0/P1` bugs mapped to executable regression tests; zero silent test deletions.
- **NOT ASSESSED**: `N == 0` testable stories in scope, or `0` executable tests discovered by the runner (`testcasecount="0"`). Never coerce `NOT ASSESSED` into a clean pass.
- **FAIL**: Smoke suite exceeds `5 min` or times out (`exit 124`/`142`), any test failure occurs, production PII dumps appear in fixtures, or Auth/PII/Payment slices are waived to `minimal`.
- **Gate Rule**: Delete stale XML artifacts (`rm -f test-results/smoke.xml`) before each run so previous green outputs cannot mask a failed or zero-test execution.

```bash
# Verify real test discovery (> 0 tests), run smoke suite with timeout guard, and reject empty JUnit denominators
rm -f test-results/smoke.xml
timeout 300 pytest -q --tb=short --junitxml=test-results/smoke.xml tests/smoke/
python3 -c '
import xml.etree.ElementTree as ET, sys
root = ET.parse("test-results/smoke.xml").getroot()
suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
total = sum(int(s.attrib.get("tests", 0)) for s in suites)
failures = sum(int(s.attrib.get("failures", 0)) + int(s.attrib.get("errors", 0)) for s in suites)
assert total > 0, "NOT ASSESSED: 0 tests executed"
assert failures == 0, f"FAIL: {failures} smoke failures"
print(f"PASS: {total} smoke tests passed")
'
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Ice-Cream Cone / Inverted Pyramid** | Hundreds of slow browser E2E tests check rules better tested in `50 ms` API/unit tests | E2E suite `> 30 min`, frequent DOM timing flakes, thin API/unit layer | Push EP, BVA, and Decision Table rules to unit/API layers; keep E2E to critical journeys |
| **Empty-Denominator `PASS` Illusion** | Empty `tests/` dir or `0` scoped stories exits `0` and looks green | `testcasecount="0"` or `0` stories mapped in test plan | Enforce `N=0` guard and XML `tests > 0` check; emit `NOT ASSESSED` |
| **Averaged Risk Score Masking** | `Likelihood=1, Impact=4` averages to `2.5` and drops auth/payment tests to `minimal` | Single composite `Risk Score` column without separate `Impact` column | Score Likelihood and Impact separately; auto-elevate `Impact=4` / Auth / PII / Pay |
| **Silent Flaky Test Deletion** | Deleting or `.skip()`-ing without a ticket hides real concurrency/race bugs in prod | Git diff deletes test assertions without replacement or quarantine ledger entry | Enforce 3-run rule, 7-cause diagnosis, and tracked Quarantine Registry with deadline |
| **Over-Engineered Custom Test Harness** | Writing a bespoke YAML/DSL test runner over `pytest`/`playwright` doubles maintenance cost | Custom wrapper >500 LOC around native assertions (violates Radical Simplicity) | Use native framework fixtures and standard parameterized tables |
| **Production Database Dumps in QA** | Leaks real user PII, breaks GDPR/CCPA, and makes test outcomes non-deterministic | `pg_dump prod` scripts or real customer emails in `fixtures/` | Use schema-backed synthetic factories with pinned PRNG seeds |
