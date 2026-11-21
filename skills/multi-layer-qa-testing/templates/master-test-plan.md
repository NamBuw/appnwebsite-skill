# Master Test Plan — `<product-or-feature-slug>`

> **Plan ID**: `<MTP-001>` | **Spiral ID**: `<SP-001>` | **Primary Surface**: `<web-app | mobile-app | dashboard | backend-api | fullstack | landing-page>`
> **Rigor Tier**: `<minimal | standard | full>` | **Selected Topology**: `<Pyramid | Testing Trophy | Honeycomb | Lean Check Stack>`
> **Owner**: `<qa-owner-role>` | **Updated (UTC)**: `<YYYY-MM-DDTHH:MM:SSZ>`

---

## 1. Scope & Denominator Guard

> **N=0 Scope Guard**: If zero testable acceptance criteria or vertical slices exist in scope, STOP immediately and record verdict `NOT ASSESSED — no testable scope defined`. Never emit a clean pass over an empty denominator.

- **Source Artifacts**: `<prd.md#section>`, `<use-cases.md>`, `<feature-breakdown.md>`, `<nfr-slo-matrix.md>`, `<openapi.yaml>`
- **Requirements / Stories In Scope (`N > 0`)**: `<N = integer count>` (`<REQ-001..REQ-NNN>`)
- **Explicit Testing Non-Goals (Out of Scope for This Spiral)**: `<list deferred surfaces, third-party sandbox internals, or unbuilt future epics>`
- **Rigor Override Check (`Auth | PII | Payments`)**: `<Yes — auto-elevated to standard/full | No — standard tier rules apply>`

---

## 2. Risk-Based Testing (RBT) & Layer Allocation Matrix

> Score `Likelihood (1-4)` and `Failure Impact (1-4)` **independently** (never average away a catastrophic `Impact=4` auth/data-loss risk). Classify every slice into `Logic | Integration | UI | Visual/Feel | Config/Data` (ambiguous `Logic+Integration` defaults to `Integration`).

| Req / Slice ID | Slice Type | Likelihood (1-4) | Impact (1-4) | Auth / PII / Pay Override | Unit / TDD | Integration / Contract | Black-Box Technique(s) | E2E / Visual | Target Test File(s) |
|---|---|---|---|---|---|---|---|---|---|
| `<REQ-001>` | `<Integration>` | `<3>` | `<4>` | `<Yes -> full>` | `<Branch + MC/DC>` | `<Testcontainers Postgres>` | `<EP, 3-BVA, State, API Negative>` | `<1 Playwright journey>` | `<tests/integration/billing.test.ts>` |
| `<REQ-002>` | `<Logic>` | `<2>` | `<3>` | `<No>` | `<TDD + Mutation>` | `<None>` | `<Decision Table, Pairwise>` | `<None>` | `<tests/unit/pricing.test.ts>` |
| `<REQ-003>` | `<UI>` | `<3>` | `<2>` | `<No>` | `<Component>` | `<None>` | `<Exploratory, E2E, break-ui>` | `<390x844 + 1600x900>` | `<tests/e2e/checkout.spec.ts>` |

---

## 3. Environment, Test Data & Deterministic Seeding Contract

- **Isolation Tier Selected**: `<In-Memory Fake | Per-Test DB Transaction Rollback | Ephemeral Schema / Testcontainers | Isolated Ephemeral Staging>`
- **Deterministic PRNG / Hash Seed**: `<e.g., PYTHONHASHSEED=0, FAKER_SEED=20261121 — logged on failure>`
- **Clock Freeze Mechanism**: `<e.g., freezegun / vi.useFakeTimers('2026-11-21T12:00:00Z')>`
- **Synthetic Data & PII Policy**: `<100% synthetic schema-backed factories; zero production database dumps or real PII>`
- **Browser / Session Isolation**: `<e.g., Playwright fresh browserContext per test, --isolated>`

---

## 4. Tier Execution Plan (`Smoke` / `Regression` / `Soak`)

### 4.1 Smoke Suite (`<= 5 min` Runtime Gate)

| Check ID | Critical Path / Boot Verification | Command | Expected Signal | Strict Mode (`blocking | advisory`) |
|---|---|---|---|---|
| `<SMK-01>` | `<App boot + /healthz + DB ready>` | `<curl -sf http://127.0.0.1:8080/healthz>` | `<HTTP 200 + db:ok>` | `<blocking>` |
| `<SMK-02>` | `<Primary login + core write path>` | `<npx playwright test tests/e2e/smoke.spec.ts>` | `<exit 0, tests > 0>` | `<blocking>` |

### 4.2 Curated Regression Manifest (`100%` Closed `P0/P1/P2` Bugs)

| Bug / Critical ID | Severity | Root Cause Summary | Regression Test Path | Status (`HAS REGRESSION TEST | MISSING`) |
|---|---|---|---|---|
| `<BUG-001>` | `<P1>` | `<Double-charge on retry without Idempotency-Key>` | `<tests/api/idempotency.test.ts>` | `<HAS REGRESSION TEST>` |

### 4.3 Soak / Endurance Plan (Stateful / Long-Lived Services Only)

- **Tier & Interval**: `<N/A | 30m (10m steps) | 1h (15m steps) | 2h (20m steps) | 4h (30m steps)>`
- **T+0 Baseline Metrics**: `<Heap RSS MB, DB pool active conns, p95 ms>`
- **Abort / Fail Threshold**: `<Growth > 20% post-warmup OR monotonic heap increase across >= 3 consecutive checkpoints>`

---

## 5. Flakiness Triage & Quarantine Registry

> Rule: `< 3` observed runs = `suspected` only (never quarantine on 1–2 runs). Quarantine ONLY confirmed high-rate flakes (`> 25%`) with an active remediation owner and deadline; **never delete flaky test files silently**.

| Test ID | Runs Analyzed (`>= 3`) | Fail Rate (%) | Confidence (`suspected | confirmed`) | Root Cause (7-Cause Taxonomy) | Action (`Fix-Direct | Quarantined | Monitor`) | Owner & Deadline |
|---|---|---|---|---|---|---|
| `<tests/e2e/cart.spec.ts#L42>` | `<10>` | `<30%>` | `<confirmed>` | `<Timing/async — fixed sleep>` | `<Quarantined -> replace with waitForResponse>` | `<@qa-eng, YYYY-MM-DD>` |

---

## 6. Complexity Budget, Deletion Pass & Sign-Off

- **Redundant Tests Deleted / Condensed**: `<Count and list of duplicate E2E or over-mocked unit tests collapsed>`
- **Post-Condensation Verification Command**: `<pytest -q --tb=short tests/ | vitest run>` -> **Exit Code**: `<0>`
- **Plan Verdict**: `<APPROVED | HOLD (NOT ASSESSED) | REJECTED>`
