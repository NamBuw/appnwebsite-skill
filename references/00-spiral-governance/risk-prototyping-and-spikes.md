# Risk Analysis, Prototyping & Throwaway Spikes (Q2 Governance)

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This module governs **Quadrant 2 (Q2)** uncertainty reduction: separating engineering bugs from real architectural risks, scoring Likelihood and Severity independently, executing strictly isolated timeboxed **Throwaway Spikes** (`<= 4h`) and **Concept Prototypes** (`<= 1d`), enforcing the **3-PIVOT-to-KILL** circuit breaker, and preventing prototype-to-production contamination.

---

## 1. Decision Framework

### 1.1 Failure-Before-Gap Diagnostic Triage

Never mistake a local bug, typo, bad environment variable, or stale cache for a fundamental architectural risk or failed concept. Before concluding an approach is unviable, execute this 6-step diagnostic order:
1. **Input & Data Integrity** -> 2. **Implementation Fidelity** -> 3. **Configuration & Protocol Alignment** -> 4. **Mechanical Sanity** -> 5. **Minimal Reference Baseline** -> 6. **Independent Check**.
- Classify the failure explicitly: `implementation_error` (fix directly), `protocol_mismatch` (align contract), or `real_risk / method_boundary` (log in Risk Register and spike/mitigate).

### 1.2 Validation Vehicle Selection Matrix

| Uncertainty / Risk Type | Correct Vehicle | Hard Timebox Cap | Strict Isolation & Disposition Rule |
|---|---|---|---|
| **Narrow Technical Feasibility / Latency** (*"Can Postgres FTS / WebWorker / SDK do X under 50ms?"*) | **Throwaway Spike** | **`<= 4 hours`** *(split question if larger)* | Lives strictly in `spikes/<id>/`. Emits `SPIKE-NOTE.md` (`YES \| NO \| PARTIAL`). **Never merged or imported into `src/`** |
| **UX Flow / Desirability / IA Comprehension** (*"Can first-time users finish onboarding without help?"*) | **Concept Prototype** (Paper, wireframe, or single-file HTML mock) | **`<= 1 day`** *(`2h` stuck reframe check)* | Targets **riskiest assumption first**. Verdict: `PROCEED \| PIVOT \| KILL \| NOT ASSESSED`. `PROCEED` rewrites cleanly from scratch after Phase 3A |
| **End-to-End Stack & Integration Proof** (*"Does auth -> DB -> API -> UI loop hold at production bar?"*) | **Vertical Slice** (Post-Phase 3A ONLY) | **`1–3 weeks`** *(Day 3 sunk-cost check)* | Cut scope before cutting quality. Never skips contracts, tests, or security baseline |
| **Concurrency, Network Lag, Mobile Throttling** (*"Does optimistic UI hold at 250ms RTT & 10k rows?"*) | **Realistic-Condition Benchmark** | **`<= 4 hours`** | **NEVER** accept `0ms` localhost feel with 5 mock rows as proof of production behavior |

### 1.3 Mandatory Hypothesis Grammar & 3-PIVOT-to-KILL Circuit Breaker

- **Falsifiable Hypothesis Grammar** (every spike/prototype MUST declare this BEFORE coding):
  > *"If `[actor/system performs X]` under `[realistic constraint]`, `[outcome Y]` will occur — measured by `[quantitative/observable signal Z]`."*
  - Reject vague hypotheses like *"Let's build a prototype to see if it feels good."*
- **Separate Likelihood & Severity**: Score `Likelihood (L | M | H)` and `Severity (Low | Med | High | Critical)` separately. Any `High` or `Critical` risk with `Status == OPEN` **blocks Phase 3A Foundation unlock**.
- **3-PIVOT-to-KILL Circuit Breaker**: `3` consecutive `PIVOT` verdicts on the same underlying concept or mechanism **automatically force a `KILL` evaluation** (5-box confirmation; if `>= 2` boxes confirm structural dead-end -> `Verdict: KILL` + permanent entry in `GRAVEYARD.md` so future Spirals do not repeat the mistake).
- **Zero-Evidence Guard**: Any unexecuted spike or untested prototype MUST be marked `NOT ASSESSED` — never `GO` or `PROCEED`.

### 1.4 Simplest High-Craft & Anti-Overengineering Risk Triage

Before authoring a throwaway spike or adopting an external service/library to mitigate a Q2 risk, interrogate the **Simplest High-Craft Option** first (*"Least Code, Highest Craft"*):
- **Native Elimination Check (Simplicity Q1/Q2)**: Ask whether a native platform, database, or stdlib primitive (e.g., PostgreSQL `tsvector` or `SKIP LOCKED` instead of a new search cluster or message broker) removes the operational and security risk surface outright without introducing new dependencies.
- **Anti-Overengineering YAGNI Filter**: Do not spike speculative multi-region, distributed cache, or premature abstraction risks unless a verified Q1 PRD/NFR constraint proves single-node simplicity cannot meet the target threshold.

---

## 2. Step-by-Step Workflow

### Step 1 — Populate the Q2 Risk & Threat Register
1. Open [Risk & Spike Register template](../../templates/risk-spike-register.md) for the active Spiral (`RSK-SP-<NNN>`).
2. Enumerate top risks across all 7 domains: `Architecture`, `Data`, `UI/UX`, `Perf`, `Security`, `Supply-Chain`, `Scope`.
3. Coordinate with `skills/security-engineering` (STRIDE threat modeling) for trust boundaries, auth flows, and PII paths.
4. Ensure every `High` or `Critical` row receives either a concrete deterministic mitigation or a bounded Spike ID (`SPK-<NNN>`).

### Step 2 — Freeze Falsifiable Question & Simplicity Baseline
1. Before opening `spikes/`, ask **Simplicity Q1**: *"Can an existing native primitive solve this without the risky new library/architecture?"* and verify the candidate solution stays within the Spiral's **Complexity Budget**.
2. Write the 1-sentence **Falsifiable Hypothesis** and explicit **Falsifier / Kill Condition** in Section 2 of `risk-spike-register.md`.

### Step 3 — Build Strictly Isolated Throwaway Experiment
1. Create `spikes/SPK-<NNN>-<slug>/` (or `prototypes/SPK-<NNN>-<slug>/`) with header banner:
   `THROW-AWAY SPIKE — DO NOT IMPORT OR MERGE INTO PRODUCTION`.
2. **Enforce Hard Isolation**:
   - Production code (`src/`, `app/`, `pages/`, `components/`, `lib/`, `server/`, `api/`) MUST **NEVER** import from `spikes/` or `prototypes/`.
   - Throwaway spikes MUST **NEVER** import production domain modules to mutate live state.
3. Skip polish, exhaustive unit tests, and unrelated navigation unless UX clarity *is* the risk under test.
4. Respect the **2-hour / 4-hour cutoff**: if blocked at `2h` (concept) or `4h` (spike), stop immediately, run failure triage, and reframe or kill rather than sinking days into a spike.

### Step 4 — Measure Under Realistic Conditions & Challenge Result
1. For UX prototypes: brief once, observe silently (*do NOT coach the user*), ask *"What felt unclear?"* rather than *"Did you like it?"*; `>= 3` users hitting the same blocker = confirmed failure.
2. For performance/sync spikes: inject realistic latency (`100–300ms`), payload sizes, and concurrency — never trust `127.0.0.1` `0ms` empty-table timings.
3. If the spike fails, run Section 1.1 **Failure-Before-Gap Triage** to confirm the failure is real and not a missing env var or typo.
4. Run an adversarial kill check: write the strongest argument why the spike result could be a false positive (e.g., mocked auth, tiny dataset).

### Step 5 — Emit Verdict, Clean Up & Re-Enter Phase 3A
1. Update the Spike Card verdict (`GO | PIVOT | KILL | NOT ASSESSED`) and update `Unmitigated High/Critical Risks` count.
2. Execute disposition:
   - **`GO`**: Write `SPIKE-NOTE.md` summarizing constraints learned -> execute a **Deletion/Condensation Pass** removing `spikes/SPK-<NNN>/` cleanly -> return to Phase 3A (`system-first-foundation-gate.md`) to lock ADRs/contracts -> build production code **from scratch** in Phase 3B.
   - **`PIVOT`**: Record `PIVOT-NOTE.md` (`What worked`, `Single biggest change`, `Revised hypothesis`), increment `Pivot Count`. If `Pivot Count >= 3`, trigger **KILL Evaluation** immediately.
   - **`KILL`**: Record in `GRAVEYARD.md` (`Kill reason`, `What worked`, `What failed`, `Rule for next time`) and remove spike code.
3. Run `python3 scripts/check_spiral_gates.py --project-dir <repo> --stage q2-risk --strict` before entering Phase 3A sign-off.

---

## 3. Reusable Artifact & Template

- **Canonical Template**: [Risk & Spike Register](../../templates/risk-spike-register.md)
- **Required Sections & Invariants**:
  1. Header metadata: `Register ID`, `Spiral ID`, `Updated (UTC)`, `Unmitigated High/Critical Risks` (`0` required before Phase 3A unlock), `Verdict`.
  2. Section 1 (`Risk & Threat Trigger Register`): Independent `Likelihood` and `Severity` columns; `High`/`Critical` + `Status == OPEN` blocks Phase 3A.
  3. Section 2 (`Throwaway Spike & Concept Prototype Cards`): Falsifiable Hypothesis, Timebox, Isolation Path, Observed Evidence, `Pivot Count` (`>= 3` MUST yield `Verdict: KILL`), `Verdict`.
  4. Section 3 (`Throwaway Artifact Isolation & Cleanup Verification`): 5 falsifiable checkboxes verifying zero prod <-> spike imports and clean rewrite from Phase 3A contracts.

### Worked Spike Lifecycle Example (`SPK-001`: `GO` vs `3-PIVOT-to-KILL`)

- **Scenario**: Team questions whether PostgreSQL full-text search (`tsvector` + GIN) meets `< 40ms` p95 on `250,000` catalog records (avoiding adding Elasticsearch/Meilisearch per Simplicity Q2).
- **Hypothesis (`If/Then/Signal`)**: *"If PostgreSQL 16 queries `250k` seeded product rows using a weighted `tsvector` GIN index under `25` concurrent clients, p95 query latency will stay `<= 40ms` with `>= 0.90` top-5 relevance."*
- **Isolation**: Built in `spikes/SPK-001-pg-fts/bench.py` with throwaway seed data; zero imports from or into `src/`.
- **Measured Result (`2h 15m`)**: `p95 = 18.4ms`, `p99 = 29.1ms` -> `Verdict: GO` -> `SPIKE-NOTE.md` records exact GIN config and query plan -> `spikes/SPK-001-pg-fts/` deleted -> ADR-0002 (`Postgres FTS over Elasticsearch`) locked in Phase 3A -> production repository implemented cleanly from scratch in Phase 3B.
- **Alternative Outcome (`3-PIVOT-to-KILL`)**: If `Pivot 1` (trigram index), `Pivot 2` (query rewrite), and `Pivot 3` (materialized summary) all failed latency targets, `Pivot Count == 3` triggers the 5-box `KILL` confirmation -> `Verdict: KILL` -> logged in `GRAVEYARD.md` with measured evidence justifying external search engine in ADR-0002.

### 5-Box `KILL` & `GRAVEYARD.md` Minimum Contract
Whenever `Pivot Count >= 3` or a spike falsifies a premise, record in `docs/spiral/GRAVEYARD.md`:
1. **Killed Concept / Mechanism & Date** (`SPK-NNN`)
2. **Falsified Hypothesis & Measured Evidence** (exact latency, failure rate, or user-test observation)
3. **What Worked (Keep)** vs. **What Failed (Never Repeat)**
4. **Rule for Future Spirals** (e.g., *"Do not attempt client-side SQLite sync for >50MB blobs on iOS Safari without OPFS spike"*)
5. **5-Box Confirmation** (check at least 2 before killing): `[ ]` Hypothesis falsified under realistic load/users; `[ ]` Env/config bugs ruled out via Step 4 triage; `[ ]` Simpler native baseline exists; `[ ]` `Pivot Count >= 3`; `[ ]` Timebox exhausted without positive trajectory.

### Concrete `SPIKE-NOTE.md` Schema (`<= 30` Lines)
```markdown
# SPIKE-NOTE: SPK-001 — Postgres Weighted FTS Benchmark
- **Linked Risk**: RSK-002 | **Timebox Used**: 2h 15m / 4h cap
- **Question**: Can Postgres 16 GIN tsvector stay <= 40ms p95 at 250k rows, 25 conc?
- **Environment**: Docker PG 16, 250,000 synthetic rows, simulated 50ms client RTT
- **Observed Signal**: p50=7.2ms, p95=18.4ms, p99=29.1ms, top-5 recall=0.94
- **Verdict**: YES (GO) — Elasticsearch unnecessary (saves 1 service + sync pipeline)
- **Cleanup**: `spikes/SPK-001-pg-fts/` deleted; ADR-0002 locks GIN migration in Phase 3A
```

### Realistic Condition Calibration Table (Anti-Localhost-Illusion)
| Behavior Under Test | Invalid Localhost Test | Required Realistic Spike Condition |
|---|---|---|
| **DB Search / Dashboard Queries** | 12 seed rows on empty local DB | `>= 50k–250k` synthetic rows + `EXPLAIN (ANALYZE, BUFFERS)` |
| **API / Optimistic UI Sync** | `0ms` `127.0.0.1` loopback | Injected `150–300ms` RTT + `5%` transient 503 failure simulation |
| **Mobile Scroll / Gestures / Offline** | Desktop Chrome wide viewport | Throttled `4x` CPU + mobile viewport + airplane-mode offline toggle |
| **UX / Onboarding Concept** | Author clicking their own prototype | `3–5` uncoached users given 1 sentence goal; record silent confusion points |
| **Third-Party Webhook / AI Latency** | Mocked `200 OK` JSON stub | Live sandbox replay + timeout (`> 5s`) + duplicate delivery + malformed payload |

### Concrete `PIVOT-NOTE.md` Schema (Between Spikes `1 -> 2 -> 3`)
Whenever a spike yields `PIVOT`, record a terse `<= 15`-line `PIVOT-NOTE.md` before starting the next attempt so learnings accumulate without repeating failed parameters:
```markdown
# PIVOT-NOTE: SPK-002 (Pivot #1 of max 3)
- **Previous Hypothesis**: Client-side PDF rendering via pdf.js stays < 1.2s on mid-tier mobile.
- **What Failed**: Memory peaked at 380MB on 12MB PDF; iOS Safari tab crashed after 4s.
- **What Worked (Keep)**: Exact HTML print layout template and page-break CSS rules.
- **Single Biggest Change**: Move rendering to server-side headless Chromium endpoint with cache key.
- **Revised Hypothesis**: Server render + CDN cache delivers PDF in <= 900ms p95 under 20 req/s.
```

### Escalation Matrix When Risks Cannot Be Mitigated in Q2
| Unmitigated Condition | Mandatory Action Before Phase 3A |
|---|---|
| `High`/`Critical` Security Threat (`STRIDE`) | Escalate to `skills/security-engineering` for compensating architectural control; block 3A unlock until `Mitigated` or `Accepted` by owner |
| External Vendor API Unstable / Rate-Limited | Add adapter port + circuit breaker + fallback ADR in `system-data-architecture`, or cut scope in `spiral-charter.md` |
| UX Flow Fails `>= 3` Uncoached Users | Simplify Information Architecture (`skills/ui-design-craft`) and re-test within `<= 1d` before locking Phase 3A |
| `Pivot Count == 3` Triggered | Execute 5-box `KILL` confirmation -> log `GRAVEYARD.md` -> select Option A fallback or remove feature from Spiral |

---

## 4. Verification Checklist

- [ ] Every `High` and `Critical` risk in Q2 has a concrete mitigation or assigned Spike (`0` remain `OPEN`).
- [ ] Every spike/prototype declares a falsifiable hypothesis (`If [X] -> [Y] measured by [Z]`) and explicit Kill Condition before build.
- [ ] Timebox limits respected (`<= 4h` spike, `<= 1d` concept prototype; `2h` stuck reframe triggered).
- [ ] Zero production source files import from `spikes/` or `prototypes/` (verified by `check_spiral_gates.py`).
- [ ] Realistic network latency, dataset volume, and error cases tested (no `0ms` localhost illusion).
- [ ] Engineering-vs-gap triage ruled out setup/config bugs before recording `PIVOT` or `KILL`.
- [ ] `Pivot Count >= 3` triggered formal `KILL` verdict and `GRAVEYARD.md` log.
- [ ] `GO` findings were re-authored cleanly from Phase 3A contracts rather than copying spike files into `src/`.

---

## 5. Hard Quality Gate

- **Command**: `python3 scripts/check_spiral_gates.py --project-dir <repo> --stage q2-risk --strict --json`
- **PASS Criteria**:
  - `risk-spike-register.md` populated with non-placeholder values (`Unmitigated High/Critical Risks == 0`).
  - Zero `High`/`Critical` table rows in `Status == OPEN`.
  - Zero cross-imports between `spikes/`/`prototypes/` and production directories (`src/`, `app/`, `pages/`, `components/`, `lib/`, `server/`, `api/`).
  - Zero spike cards with `Pivot Count >= 3` and `Verdict != KILL`.
  - Every `GO`/`PROCEED` card cites `Observed Evidence` and points to a deleted/archived spike rewritten cleanly via Phase 3A contracts.
- **NOT ASSESSED Criteria**: Unfilled `[...]` register fields, missing `Unmitigated High/Critical Risks` integer, or spike marked `GO` without `Observed Evidence`.
- **FAIL Criteria**:
  - Any `High`/`Critical` risk left `OPEN` at Phase 3A entry.
  - Production code imports from `spikes/`/`prototypes/` (`SPIKE_LEAK`).
  - `Pivot Count >= 3` without `Verdict: KILL` (sunk-cost loop).

### Concrete Gate Failure Remediation Examples
- **`Unmitigated High/Critical Risks: 2` (`RSK-001 OPEN`)**: Either execute a bounded `<= 4h` spike (`Status: SPIKING` -> `MITIGATED` with `SPIKE-NOTE.md`) or add an Accepted ADR mitigation before locking Phase 3A.
- **`SPIKE_LEAK` in `src/lib/search.ts`**: Remove the import from `spikes/`, re-implement the verified algorithm inside `src/` against `control-manifest.md` and unit tests, delete `spikes/`, and re-run `check_spiral_gates.py`.
- **Concept Prototype Rejected (`3` users confused)**: Keep zero UI spike code; simplify Information Architecture inside `skills/ui-design-craft` and log `PIVOT-NOTE.md`.
- **Local `0ms` Benchmark Rejected**: Re-run spike against seeded `>= 50k`-row dataset + injected `200ms` latency before marking `Observed Evidence` valid.
- **`Pivot Count == 3` with `Verdict: PIVOT`**: Complete 5-box `KILL` confirmation, switch `Verdict` to `KILL`, append entry to `GRAVEYARD.md`, and remove spike directory.

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Prototype-to-Production Drift** | Ships unvalidated, untested, insecure throwaway code straight to users | Prod routes live in `prototypes/` or spike code copied into `src/` without ADRs/tests | Strict directory isolation; delete/archive spike and rewrite cleanly from Phase 3A contracts |
| **Unfalsifiable "Vibe" Spikes** | Burns days polishing styling/menus without proving whether the core risk works | Hypothesis lacks quantitative signal `Z`; 4h spike includes auth/theming | Freeze `If [X] -> [Y] measured by [Z]`; zero polish unless UX clarity is the hypothesis |
| **Sunk-Cost Pivot Loop (`Pivot #4+`)** | Keeps patching a broken premise out of attachment instead of cutting losses | `Pivot Count >= 3` with flat/negative evidence and no `KILL` check | Enforce **3-PIVOT-to-KILL** circuit breaker + `GRAVEYARD.md` postmortem |
| **Localhost `0ms` Illusion** | Hides N+1 queries, mobile CPU/network stalls, and race conditions | Benchmarks run only on `127.0.0.1` with 5 seed rows | Inject realistic latency, pagination scale, and concurrency in spike benchmarks |
| **Killing Good Ideas Over Env Bugs** | Abandons a sound design because a bad env var or stale cache broke the spike | Spike aborted on import/config error without input/env/sanity triage | Run 6-step Failure-Before-Gap Triage before issuing `PIVOT`/`KILL` |
| **Silent Unmeasured Promotion** | Declares `GO` on intuition after a spike crashed or never ran under load | `Observed Evidence` is blank or `[TBD]` while `Verdict == GO` | Enforce `NOT ASSESSED` until reproducible measurements exist |
| **Averaging Risk Likelihood × Impact** | Hides a catastrophic `Critical` security/data-loss risk inside a medium composite score | Risk table prints single `Score: 2.5` without separate `Severity` column | Keep `Likelihood` and `Severity` strictly separate; block 3A on any `OPEN` High/Critical |
| **Infinite "Just One More Day" Spike** | Turns a `4h` feasibility spike into an unreviewed 4-day mini-product | Spike branch lives `> 1` day with `SPIKE-NOTE.md` still missing | Enforce `2h` stuck cutoff and `4h` hard cap; split question or issue `NO`/`KILL` |
| **Mocking the Risk Away** | Tests a spike against happy-path stubs that omit the exact failure mode under investigation | Auth, rate limit, or concurrency mocked out of the spike benchmark | Test the real risky constraint directly under realistic load and failure injection |
| **Promoting Unverified Prototypes** | Ships mock data or bypassed auth checks after a UX prototype looks polished | UI routes call hardcoded arrays inside `prototypes/` | Keep throwaway boundary strict; re-author through Phase 3A contracts and real QA |
| **Ignoring Supply-Chain Risk in Q2** | Discovers GPL/copyleft or unmaintained CVE dependencies only at pre-release | New core SDK added in spike without license/CVE triage | Log external dependency risks in Q2 register and verify via `security-engineering` |

---

## Related Governance Modules
- [Spiral Lifecycle](spiral-lifecycle.md)
- [System-First Foundation Gate](system-first-foundation-gate.md)
- [Anti-Overengineering Simplicity Gate](anti-overengineering-simplicity-gate.md)
- [Orchestration Protocol](../orchestration-protocol.md)
- [Risk & Spike Register Template](../../templates/risk-spike-register.md)
