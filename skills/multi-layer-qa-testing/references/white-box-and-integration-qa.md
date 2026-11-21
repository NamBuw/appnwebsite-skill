# White-Box, Integration, Contract & Visualization QA

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

White-box and integration QA verifies internal structural logic, database/RLS semantics, cross-service schema contracts, data-visualization transforms, and root-cause defect resolution. It enforces strict TDD discipline and realistic integration boundaries while preventing mock-heavy, tautological test bloat.

---

## 1. Decision Framework

### 1.1 White-Box & Integration Technique Matrix

| Code / Boundary Scope | Primary Technique | Coverage & Strength Target | Simplest High-Craft Default |
|---|---|---|---|
| **Pure domain math, parsers, state reducers, validators** | **TDD Unit Tests (`Red-Green-Refactor`)** | `>= 80%` branch coverage (`100%` on critical domain rules) | Pure functions tested directly with hand-derived literals (`0` mocks) |
| **Multi-clause auth, billing, or safety boolean guards** | **MC/DC (Modified Condition / Decision Coverage)** | `100%` independent clause effect in $N+1$ minimal vectors | Explicit MC/DC truth-flip table over $N+1$ cases (avoids $2^N$ blowup) |
| **SQL queries, Postgres RLS, transactions, migrations, queues** | **Integration Tests with Real Ephemeral DB** | `100%` tenant isolation, migration up/down, rollback checks | `Testcontainers` Postgres or isolated schema-per-test (**never** mock SQL) |
| **HTTP / Event / GraphQL boundaries across deployables** | **OpenAPI Schema Diff / Consumer-Driven Pact** | `100%` endpoint response & error-schema compatibility | OpenAPI schema validation for modular monoliths; Pact only for independent teams |
| **Critical pricing, ledger, crypto, or security core** | **Mutation Testing (`Stryker` / `mutmut`)** | `>= 75–80%` mutation score on targeted core modules | Run `--mutate` strictly on `src/core/**` changed files, not DTOs/config |
| **Charts, Canvas/WebGL, statistical dashboards** | **Layered Visualization QA** | Unit transforms + semantic component contract + stable baselines | Unit test bins/scales; never snapshot generated SVG `<path>` strings |

### 1.2 Simplest High-Craft White-Box Strategy & Anti-Overengineering

Before creating elaborate mock hierarchies, custom in-memory SQL emulators, or Pact broker clusters, apply three checks:
- **Mock-Size Stop Rule**: *"Does mock setup in this unit test exceed the size or complexity of the real database/component interaction?"* If yes, delete the mock scaffolding and convert the test into a real `Testcontainers` or SQLite-dialect integration test.
- **No Broker Tax on Monoliths**: Adopt a Pact broker ONLY when producer and consumer teams deploy on independent release schedules. Inside a Modular Monolith or single repo, validating real requests/responses against `openapi.yaml` delivers equivalent contract safety with zero infrastructure overhead.
- **Targeted Mutation Scope**: Never burn `20 min` mutating framework glue, DTO types, or generated files; restrict `Stryker`/`mutmut` to core business algorithms and auth guards.

---

## 2. Step-by-Step Workflow

1. **Enforce the TDD Iron Law (`Red-Green-Refactor` + `Name the Break`)**
   - **Inputs**: Locked slice acceptance criteria, domain contracts, and boundary vectors.
   - **Owner**: Feature / Backend Engineer.
   - **Tool / Script**: `pytest` / `vitest` / `node --test`.
   - **Output**: Verified RED-to-GREEN commits obeying two core rules from `test-driven-development`:
     - **Iron Law**: `NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST`. Any production logic written prior to a failing test MUST be deleted and re-driven from RED. Verify RED fails for the *expected missing behavior*, not a typo or import error.
     - **Name the Break & Hand-Derived Literals**: Name every test for the exact behavior that breaks (`test_refund_rejects_expired_window_with_409`), derive expected outputs independently by hand (never call the production helper inside `expect(...)`), and never write change-detector tests asserting static copy or config constants.

2. **Derive Structural Coverage & MC/DC Vectors for Critical Guards**
   - **Inputs**: Complex boolean guard expressions (`>= 2` atomic conditions).
   - **Owner**: Domain / QA Engineer.
   - **Tool / Script**: Branch coverage runner (`pytest --cov-branch` / `vitest --coverage`) + MC/DC derivation table.
   - **Output**: Coverage hierarchy verification (`Statement < Branch < Condition < MC/DC`). For an expression with $N$ atomic boolean conditions, MC/DC proves **each condition independently toggles the final decision** in $N+1$ tests instead of $2^N$.
   - *Worked MC/DC Example* (`isEligible = (isActive && !isSuspended) || hasAdminOverride`, $N = 3 \implies 4$ vectors):

| Test Vector | `isActive (A)` | `isSuspended (B)` | `hasAdminOverride (C)` | `isEligible` | Independent Flip Proven |
|---|---|---|---|---|---|
| `T1` | `True` | `False` | `False` | `True` | Baseline `A=T, B=F -> True` |
| `T2` | `False` | `False` | `False` | `False` | **Proves `A`** (`T1` vs `T2`: only `A` flips, output flips) |
| `T3` | `True` | `True` | `False` | `False` | **Proves `B`** (`T1` vs `T3`: only `B` flips, output flips) |
| `T4` | `False` | `False` | `True` | `True` | **Proves `C`** (`T2` vs `T4`: only `C` flips, output flips) |

3. **Apply the 5-Type Test Doubles Taxonomy & Real-Thing Boundary Rule**
   - **Inputs**: External I/O boundaries (payment gateways, SMTP, clocks, third-party APIs).
   - **Owner**: Feature Engineer.
   - **Tool / Script**: Dependency injection ports / in-memory Fakes / `msw` HTTP boundary stubs.
   - **Output**: Clean double usage obeying strict boundary hygiene:

| Double Type | Definition | Allowed Use Case | Forbidden Misuse |
|---|---|---|---|
| **Dummy** | Passed solely to satisfy parameter signature; never read | Unused logger/context arg in unit call | Passing `null` where runtime checks non-null contract |
| **Stub** | Returns canned data/errors without verifying calls | Fixed `ClockStub`, FX rate stub | Stubbing internal domain collaborators to force code paths |
| **Spy** | Wraps real implementation and records call metadata | Counting audit-event emissions alongside real DB write | Asserting internal helper call order instead of output behavior |
| **Fake** | Working lightweight implementation (in-memory repo, local FS) | Fake SMTP outbox, in-memory key-value store | Re-implementing complex SQL joins or Postgres RLS in JS/Python |
| **Mock** | Pre-programmed expectation verifier (`toHaveBeenCalledWith`) | Verifying outbound webhook dispatch at external port ONLY | Asserting mocks returned the value you programmed (testing the mock) |

   > Never add test-only methods (`resetForTest()`, `destroy()`) to production classes, and always mirror **complete real payload shapes** (never partial `{ id: 1 }` stubs that hide missing-field `TypeError` bugs).

4. **Execute Ephemeral Real-DB Integration & Contract Suites**
   - **Inputs**: SQL migrations, repository modules, RLS policies, `openapi.yaml` / event schemas.
   - **Owner**: Backend / Platform Engineer.
   - **Tool / Script**: `Testcontainers` (Postgres/Redis), schema-per-worker isolation, `schemathesis` / `pact-js`.
   - **Output**: Passing real-DB suites testing transaction boundaries, unique constraints, deadlock retries, row-level security (`Tenant A` vs `Tenant B` sessions), and backward-compatible producer/consumer schemas.

5. **Run Targeted Mutation Testing (`Stryker` / `mutmut`)**
   - **Inputs**: Critical core domain modules and security/billing guards.
   - **Owner**: QA / Senior Engineer.
   - **Tool / Script**: `npx stryker run` (TS/JS) or `mutmut run` (Python).
   - **Output**: Surviving-mutant audit separating **Killed** mutants, **Equivalent** mutants (documented), and **Test Gaps** (write a new RED test killing the surviving boundary/operator mutant until core score reaches `>= 75–80%`).
   - **High-Signal Mutant Triage Categories**: Focus remediation on flipped relational guards (`<` vs `<=`), inverted boolean returns, deleted boundary throws, and arithmetic `+`/`-` swaps rather than equivalent log-string mutations.

6. **Verify Data Visualizations & Dashboards Without Brittle SVG Snapshots**
   - **Inputs**: Chart transforms, scales, Canvas/WebGL components, live telemetry feeds.
   - **Owner**: Frontend / QA Engineer.
   - **Tool / Script**: Unit runner + React/Testing Library + Playwright visual baseline (for stable states only).
   - **Output**: Layered visualization coverage (`testing-data-visualizations`): (a) unit test binning, domain scales, tooltips math, and empty/null series transforms; (b) component test `getByRole` legends, axis labels, loading/empty/stale/error states, and cross-filter callbacks; (c) Canvas/WebGL non-blank pixel & context-loss recovery checks; (d) visual baselines locked to fixed viewport, font, timezone, `prefers-reduced-motion`, and masked live timestamps (**never** assert generated SVG `<path d="...">` strings or library internals).

7. **Follow the 4-Phase Systematic Root-Cause Debugging Protocol for Every Failure**
   - **Inputs**: Failing test trace, production bug report, or intermittent CI error.
   - **Owner**: Assigned Engineer.
   - **Tool / Script**: `git diff`, boundary instrumentation logs, condition-based wait helpers.
   - **Output**: Permanent root-cause fix (`systematic-debugging`):
     - **Phase 1 — Root Cause First**: Read complete stack traces, reproduce deterministically, inspect `git diff`, trace corrupted values backward to the originating call site (`root-cause-tracing`).
     - **Phase 2–3 — Pattern & Single Hypothesis**: Compare working vs failing execution and test one minimal falsifiable hypothesis at a time.
     - **Phase 4 — Regression Test + Defense-in-Depth**: Write a failing test BEFORE patching, fix the source cause, add multi-layer guards (Entry -> Business Logic -> Environment Guard -> Diagnostics), and replace any `sleep()` with **Condition-Based Waiting** (`10 ms` readiness polling + explicit timeout).
     - **3-Fix Architectural Stop Rule**: If `>= 3` consecutive fixes fail, **STOP** — escalate an architectural flaw instead of stacking symptomatic patches.

8. **Execute Complexity Budget & Test-Suite Deletion/Condensation Pass**
   - **Inputs**: Newly added unit, integration, and visualization tests.
   - **Owner**: Code Reviewer.
   - **Tool / Script**: Coverage report + test runtime profiler (`--durations=10`).
   - **Output**: Remove tautological tests, change-detector assertions, and `> 50%` mock-setup tests (replacing with real integration tests); eliminate `sleep()` waits; verify all tests remain green after cleanup.

---

## 3. Reusable Artifact & Template

Cross-reference boundary vectors from [Black-Box Test Matrix Template](../templates/black-box-test-matrix.md) and attach the following **White-Box & Integration Evidence Contract** inside the pull request or test plan:

| Field | Required Value / Format | Verification Rule |
|---|---|---|
| `module_or_boundary` | Exact source path (`src/core/billing.ts`) | Must match files touched in `git diff` |
| `test_layer` | `Unit-TDD \| MC/DC \| Integration-DB \| Contract \| Viz \| Mutation` | Pure math uses `Unit-TDD`; SQL/RLS uses `Integration-DB` |
| `coverage_and_mutation` | Branch `%`, MC/DC vectors (`N+1`), Mutation `%` (`>= 75%` core) | Zero `0`-assertion vacuous tests allowed |
| `double_and_isolation` | `Real \| Testcontainers \| Fake \| External-Mock` + DB isolation mode | Zero SQL repository mocks; zero prod class test hooks |
| `flakiness_guard` | `Transaction-Rollback \| Condition-Wait (10ms) \| Frozen-Clock` | Zero `sleep()` or `waitForTimeout()` calls |
| `command_and_exit` | Exact test + coverage CLI command + observed exit code (`0`) | Must be freshly executed after final edit |

---

## 4. Verification Checklist

- [ ] Production code changes preceded by failing RED test demonstrating missing behavior.
- [ ] Test expectations computed independently by hand rather than mirroring production code.
- [ ] Multi-clause auth, safety, and billing guards satisfy MC/DC independent flip vectors.
- [ ] Database queries, transactions, and RLS policies tested against real ephemeral Postgres.
- [ ] Mock setup avoided for internal collaborators with external boundaries mirroring real payloads.
- [ ] Data visualization tests check transforms and semantics without brittle SVG path snapshots.
- [ ] Bug fixes follow four-phase root-cause tracing with condition-based waiting instead of sleeps.
- [ ] Complexity budget deletion pass removed tautological or mock-heavy tests before final run.

---

## 5. Hard Quality Gate

White-box, integration, and visualization suites must satisfy every structural and behavioral gate prior to merge:

- **PASS**: `100%` unit, integration, contract, and visualization tests green (`tests > 0`); `>= 80%` branch coverage on core domain modules (`100%` MC/DC on critical boolean guards); `>= 75%` mutation score when core logic is mutated; `0` SQL repository mocks; `0` `time.sleep` or `setTimeout` polling hacks in test suites; every bugfix backed by a failing-then-passing regression test.
- **NOT ASSESSED**: Required coverage report missing, DB integration suite skipped due to missing container daemon, or `0` executable tests collected.
- **FAIL**: Any failing test, untested SQL/RLS migration, `0`-assertion vacuous test, `>= 3` failed patch attempts without architectural escalation, brittle SVG `<path>` snapshot assertions, or flaky `sleep()` timing dependencies.
- **Scope Rule**: Verify `git diff` confirms every bugfix commit includes its regression test and leaves zero test-only hooks inside production modules.

```bash
# Execute unit + branch coverage + Testcontainers integration tests and reject sleep hacks in tests/
! grep -rnE "waitForTimeout|time\.sleep\(|setTimeout\(" tests/
pytest -q --tb=short --cov=src --cov-branch --cov-fail-under=80 tests/unit/ tests/integration/
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Testing Mocks Instead of Real Behavior** | Asserts pre-programmed mock returns while real serialization, SQL, or wiring is broken | Test contains `expect(mockRepo.save).toHaveBeenCalled()` with >50% mock setup | Use real `Testcontainers` DB or in-memory Fake; assert persisted state and outputs |
| **Mirror / Tautological Assertions** | Calls the production formula inside `expected = calcTotal(x)` so bugs validate themselves | Expected value computed dynamically via module under test | Hardcode hand-derived literal expectations (`assert total_cents == 1099`) |
| **Mocking the Database / SQL Layer** | Masks SQL syntax bugs, constraint violations, N+1 queries, and Postgres RLS leaks | `jest.mock('./db')` or mocked ORM query builder in integration tests | Run against ephemeral Postgres (`Testcontainers`) with rollback/schema isolation |
| **Chasing 100% Coverage on Trivial Code** | Bloats suites with change-detector tests on getters, DTOs, and framework wiring (Anti-Overengineering) | Tests asserting static constants, prop defaults, or copy strings | Enforce `>= 80%` branch target on core logic + MC/DC on critical guards; delete fluff |
| **Brittle SVG Path / Full-DOM Chart Snapshots** | Minor library version or font subpixel updates break every snapshot without real defects | Assertions matching `<path d="M12.4...">` or giant HTML snapshots | Unit test chart data transforms; component test accessible labels and error states |
| **Symptom-Patching Without Root Cause** | Adds null checks at crash site instead of fixing upstream invariant violation | Three quick-fix PRs on the same bug; zero regression test reproducing original failure | Enforce 4-phase root-cause tracing, 3-fix stop rule, and Defense-in-Depth |
| **Fixed `sleep()` Synchronization** | Causes sporadic timeouts on loaded CI runners and wastes execution time | `time.sleep(2)` or `await new Promise(r => setTimeout(r, 1000))` in tests | Poll readiness condition every `10 ms` with explicit timeout diagnostic |
