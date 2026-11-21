# Non-Functional Testing (Load, Statistical Rigor, A11y, Break-UI & Chaos)

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

Non-functional testing proves that a functionally correct system survives realistic traffic spikes, long-lived memory pressure, assistive technologies, hostile worst-case user data, and partial infrastructure outages. Every performance claim MUST rest on randomized experimental design and distribution-aware statistics rather than raw averages.

---

## 1. Decision Framework

### 1.1 Non-Functional Test Type & Quantitative Threshold Matrix

| NFR Dimension | Execution Shape | Quantitative Pass / SLO Criterion | Primary Tooling |
|---|---|---|---|
| **Load Testing** | Sustained `1x` expected peak RPS (`10–30 min`) | `p95 <= NFR SLO` (e.g. `< 250 ms`), `p99 < 600 ms`, error rate `< 0.1%`, steady CPU/RAM | `k6` / `Locust` |
| **Stress Testing** | Stepwise ramp (`1x -> 2x -> 5x -> breakpoint`) | Identifies exact saturation knee & emits clean `429`/`503` backpressure (zero OOM crash) | `k6` ramping-arrival-rate |
| **Spike Testing** | Instant surge (`1x -> 10x` in `< 10 s` -> `1x`) | Bounded queue depth; recovers to baseline `p95` within `MTTR < 2 min` | `k6` staged surge |
| **Soak (Endurance)** | Steady `0.8x–1x` load across timed checkpoints (`30m–4h`) | Heap RSS / FD / DB pool growth `<= 20%` vs `T+0` post-warmup; `< 3` consecutive rising steps | `k6` + `T+0` checkpoint sampler |
| **Accessibility (WCAG 2.2)** | Dual-engine automated scan + manual keyboard/SR/zoom | `0` Critical/Serious violations (`axe-core` + `pa11y` fail-closed) + `24x24` px targets (`AA`) | `@axe-core/cli`, `pa11y`, VoiceOver/NVDA |
| **Worst-Case UI (`break-ui`)** | Schema-backed extreme data + constrained viewports (`?data=worst`) | `0` `Broken` layout/clipping defects across `320px`, `280px` sidebar, `2560px`, `200%` zoom, RTL | Dev-only fixture toggle + Playwright |
| **Resilience / Chaos** | Fault injection (latency, 5xx, packet drop, cache/DB failover) | Bounded timeouts, `<= 3` jittered retries on idempotent calls, `OPEN -> HALF_OPEN -> CLOSED` breaker | `Toxiproxy` / `page.route()` / Chaos script |

### 1.2 Simplest High-Craft Non-Functional Strategy & Anti-Overengineering

Do not provision a multi-region distributed Kubernetes Chaos Mesh cluster or a 20-node JMeter farm for a single-region Modular Monolith or SaaS web app:
- **Simplest High-Craft Option**: Run `k6` from one isolated runner against production-like hardware, inject downstream network faults via `Toxiproxy` (or Playwright `page.route()` on the client), run a pinned dual-engine accessibility shell script (`axe-core` + `pa11y`), and stress UI layouts with a dev-only `?data=worst` fixture toggle.
- **Anti-Overengineering Self-Question**: *"Did we compare Baseline vs. Candidate using blocked, randomized runs and `p95`/`p99` + effect sizes, or are we building complex dashboards over noisy unpowered `mean` numbers?"*

---

## 2. Step-by-Step Workflow

1. **Design Statistically Valid Performance Experiments (`experimental-design` + `statistical-analysis`)**
   - **Inputs**: NFR SLO targets (`nfr-slo-matrix.md`), baseline vs candidate builds.
   - **Owner**: Performance / QA Engineer.
   - **Tool / Script**: `scipy.stats` / `statsmodels` (`tt_ind_solve_power`) + interleaved runner script.
   - **Output**: Unconfounded benchmark protocol obeying four statistical rules:
     - **Defeat Time Confounding & Pseudoreplication**: Never run Baseline A at `09:00` and Candidate B at `14:00` (infra drift confounds the delta), and never treat `10,000` correlated requests inside `1` warm-cache burst as `n = 10,000` independent trials. Use **blocked/interleaved runs** (`ABBA` or randomized order within time blocks) after discarding a fixed warm-up window.
     - **A Priori Power & Sensitivity**: Compute required independent run blocks `n` via `tt_ind_solve_power` *before* testing; run sensitivity analysis *after* (reject circular post-hoc observed power).
     - **Distribution-Appropriate Tests**: Latency is right-skewed (`p50 << p95 << p99`). Inspect Q-Q plots, Shapiro-Wilk (`n <= 5000`), and Levene (`center='median'`). Use **Welch's t-test** (`correction=True`) for symmetric unequal-variance block means, or **Mann-Whitney U** + **rank-biserial correlation (`RBC`)** / **BCa bootstrap 95% CI** (`n_resamples=9999`) for skewed request latencies.
     - **Effect Size + Practical SLO Delta**: Report `p`-value together with effect size (`Cohen's d`, `Hedges' g`, or `RBC`), `95%` confidence interval, and absolute millisecond impact (`-18 ms p95`).

   | Latency / Benchmark Shape | Primary Statistical Test | Required Effect Size & Interval |
   |---|---|---|
   | **Symmetric block-mean latency (unequal variance)** | Welch's t-test (`correction=True`) | `Hedges' g` + `95%` BCa bootstrap CI |
   | **Right-skewed per-request latency distribution** | Mann-Whitney U (independent) / Wilcoxon (paired) | Rank-biserial correlation (`RBC`) + median/`p95` diff CI |
   | **Binary error rate or timeout proportion** | Fisher exact / Wilson score interval | Risk difference + `95%` Wilson CI |

2. **Execute Load, Stress, Spike & Soak Suites (`k6` / `Locust`)**
   - **Inputs**: Parameterized auth/tenant pool (prevents single-ID DB cache hits), realistic think-time.
   - **Owner**: Backend / Performance Engineer.
   - **Tool / Script**: `k6` with explicit CI `thresholds` + `T+0` soak sampler.
   - **Output**: Machine-readable `perf-summary.json` + soak checkpoint table (`T+0, T+15, T+30, ...`). Measure heap RSS, open file descriptors, DB pool connections, and `p95` **relative to the session `T+0` post-warmup baseline** in native tool units (`soak-test`). A soak terminated early before planned checkpoints MUST emit `NOT ASSESSED` (unless a crash occurred, in which case `FAIL` outranks `NOT ASSESSED`).

3. **Run Fail-Closed Dual-Engine Accessibility Verification (WCAG 2.2 AA/AAA)**
   - **Inputs**: Built/running UI URLs covering public, authenticated, modal, and error states.
   - **Owner**: Frontend / QA Engineer.
   - **Tool / Script**: Pinned dual-engine runner (`@axe-core/cli@4.13.0` + `pa11y@9.1.1` WCAG2AA) + manual AT protocol (`accessibility-engineering`).
   - **Output**:
     - **Fail-Closed Automated Gate**: Execute BOTH `axe-core` and `pa11y`. Validate that both output JSON files are non-empty and parseable (`pa11y` exits `2` on valid violations; any other non-zero exit is an engine crash). **Abort and FAIL if either engine crashes** so a partial scan never appears green. Normalize `pa11y` `typeCode === 1` errors to `serious` (matching `axe-core`) and block release on `> 0` Critical or Serious violations.
     - **Mandatory Manual Keyboard, Screen Reader & Target-Size Audit**:
       - *Keyboard*: Logical `Tab` order, visible focus ring on every surface, `Enter`/`Space` activation, `Escape` modal dismiss with focus restoration, `Arrow` navigation in menus/tabs, zero keyboard traps.
       - *Screen Reader*: Test with named browser + AT pair (`VoiceOver` + Safari or `NVDA` + Firefox — if untested, record `manual / NOT ASSESSED`, never claim verified); verify heading hierarchy, landmarks, self-contained links, form error announcements, and `aria-live` regions.
       - *Visual & WCAG 2.2 Targets*: `4.5:1` normal text / `3:1` large text & UI borders, `200%` zoom with zero text clipping or loss of functionality, `prefers-reduced-motion`, Windows High Contrast / forced colors, and **WCAG 2.2 SC 2.5.8** `24x24` CSS px target size or spacing (`44x44` px AAA SC 2.5.5).

4. **Execute Worst-Case UI Data & Environment Stress (`break-ui`)**
   - **Inputs**: Rendered field inventory mapped against database/API schema maximums (flag unbounded schema fields as findings).
   - **Owner**: Frontend / QA Engineer.
   - **Tool / Script**: Dev-only fixture toggle (`?data=worst` — strictly stripped or disabled in production) + Playwright responsive viewports.
   - **Output**: Plausible, schema-backed worst-case rows spread across initial visible views (plus Empty `0`, One `1` pluralization, and Huge `1,000+` lists) and tested across constrained environments:
     - *Plausible Data Vectors*: Long hyphenated diacritic names (`Aleksandra Wiśniewska-Kowalczyk`), stacked Vietnamese diacritics (`Đặng Thị Ngọc Hân`), CJK (`王秀英`), RTL Arabic (`نور الهدى عبد الرحمن`), ZWJ emoji (`👩🏽‍💻 Priya`), ultra-short names (`Jo`, `J`) and suffixes (`III` breaking naive initial extractors), unbreakable email/URL tokens (`bartholomew.fitzgerald@northwind-industries-holdings.example.com`), `+30%` German/French translations, money precision (`0`, `1`, `0.1 + 0.2`, `-$0.01`, `12345678.90` tabular-nums), `page_size` vs `page_size + 1`, epoch/DST dates (`1970-01-01`, `2025-12-31T23:30:00-08:00`), `404` avatar fallback, and `4000x200` aspect distortion.
     - *Environments*: `320px` narrow mobile, `280px` sidebar shell, `2560px` ultrawide, `200%` zoom, dark mode, `dir="rtl"`, and touch (exposing hover-only action menus). Classify defects as `Broken | Ugly | Fragile` and resolve with `min-width: 0`, `overflow-wrap: anywhere`, `flex-shrink: 0`, `font-variant-numeric: tabular-nums`, and `Intl.PluralRules` / `Intl.Segmenter`.

   | `break-ui` Severity | Concrete Layout Symptom | Required CSS / Intl Remediation |
   |---|---|---|
   | **Broken** | Text overflows card boundary, overlaps sibling button, or clips primary CTA off-screen | Add `min-width: 0` on flex/grid children, `overflow-wrap: anywhere`, responsive wrap |
   | **Ugly** | Avatar squishes to oval, numbers jitter during live updates, or `+30%` German label wraps awkwardly | Set `flex-shrink: 0` + `object-fit: cover`, `font-variant-numeric: tabular-nums` |
   | **Fragile** | Initials avatar outputs `"II"` for suffix `III`, or `1 items` pluralization fails in Slavic locales | Use `Intl.Segmenter` for grapheme initials and `Intl.PluralRules` for localized counts |

5. **Inject Resilience & Chaos Faults**
   - **Inputs**: Dependency map (DB, Redis cache, payment/email webhooks, external APIs).
   - **Owner**: SRE / Backend Engineer.
   - **Tool / Script**: `Toxiproxy` / fault middleware / Playwright `page.route()` abort & delay hooks.
   - **Output**: Verified fault tolerance across four mechanisms:
     - **Bounded Timeouts**: Connect + read timeout strictly shorter than caller SLA; confirm worker/DB connection pools never saturate.
     - **Exponential Backoff + Full Jitter**: Max `<= 3` retries ONLY on transient/idempotent errors (`429`/`503`/socket reset); confirm non-idempotent `POST` without `Idempotency-Key` is NEVER blind-retried.
     - **Circuit Breaker Transitions**: Inject `100%` upstream `503` -> verify breaker trips `CLOSED -> OPEN`, serves fast fallback without queueing callers, probes `HALF_OPEN`, and restores `CLOSED` when upstream recovers.
     - **Cache / DB Failover**: Kill Redis or trigger primary failover -> confirm clean degradation or reconnect within RTO with zero corrupted/partial writes.

6. **Execute Deletion & Condensation Pass**
   - **Inputs**: Performance scripts, `?data=worst` fixture toggles, chaos harnesses.
   - **Owner**: Peer Reviewer.
   - **Tool / Script**: Production bundle grep + script audit.
   - **Output**: Verify `?data=worst` dev toggles cannot ship enabled in production builds, delete redundant load scenarios that duplicate SLO assertions, and retain concise `k6`/`a11y` CI gates.

---

## 3. Reusable Artifact & Template

Cross-reference worst-case UI/API boundary vectors in [Black-Box Test Matrix Template](../templates/black-box-test-matrix.md) and record every NFR campaign using this **Non-Functional & Statistical Signoff Schema**:

| Field | Required Content | Validation Rule |
|---|---|---|
| `run_id` / `category` | `NFR-NNN` + `Load \| Stress \| Spike \| Soak \| A11y \| Break-UI \| Chaos` | Maps to specific NFR SLO ID |
| `experimental_design` | `Blocked ABBA \| Randomized`, warm-up discard duration, independent `n` | Zero sequential A-then-B time-confounded runs |
| `percentile_and_ci` | `p50`, `p95`, `p99`, error `%`, `RBC` / `Cohen's d` + `95% BCa CI`, `p`-value | Never report mean latency alone |
| `soak_t0_delta` | Heap RSS / FD / pool growth `%` vs `T+0` across checkpoints | Incomplete checkpoint series -> `NOT ASSESSED` |
| `a11y_dual_engine` | `axe-core` + `pa11y` counts + manual keyboard/SR/200% zoom/`24x24` px status | Fail-closed if either automated engine crashed |
| `break_ui_and_chaos` | `Broken/Ugly/Fragile` counts + breaker `OPEN->HALF_OPEN->CLOSED` proof | `0` `Broken` UI defects; `0` retry storms |
| `verdict` | `PASS \| FAIL \| NOT ASSESSED` | Summarized into Release Gate Sign-Off |

---

## 4. Verification Checklist

- [ ] Performance comparisons use blocked or randomized interleaved runs with warm-up discarded.
- [ ] Latency reports include fiftieth, ninety-fifth, ninety-ninth percentiles, effect sizes, and intervals.
- [ ] Soak tests record all planned checkpoints measuring memory growth against baseline.
- [ ] Dual-engine accessibility scan executes both engines and fails closed on crashes.
- [ ] Manual accessibility checks verify keyboard navigation, screen reader semantics, and target sizes.
- [ ] Worst-case UI fixtures use schema-backed realistic strings behind dev-only toggles.
- [ ] Responsive stress validates narrow mobile, ultrawide, zoomed, dark, and RTL layouts.
- [ ] Chaos tests verify bounded timeouts, jittered retries, circuit breakers, and cache failover.

---

## 5. Hard Quality Gate

Non-functional verification passes only when statistical, accessibility, UI stress, and resilience gates all succeed together:

- **PASS**: `k6` SLO thresholds met (`p95 <= target`, error `< 0.1%`, `ABBA` delta statistically clean); soak memory and pool growth `<= 20%` vs `T+0` across all planned checkpoints; BOTH `axe-core` and `pa11y` exit cleanly with valid non-empty JSON and `0` Critical/Serious violations plus verified manual keyboard, screen reader, and `24x24` px target checks; `0` `Broken` `break-ui` issues (`?data=worst` absent from prod bundle); timeouts, jittered retries, and circuit breakers transition cleanly under chaos injection.
- **NOT ASSESSED**: Any soak terminated before its final planned checkpoint (without crashing), missing manual screen reader verification, or unexecuted load/chaos suite.
- **FAIL**: Mean-only or time-confounded benchmarks, either accessibility engine failing or returning invalid JSON, any Critical/Serious accessibility violation, `Broken` layout overflow at `320px`/`200%` zoom/`RTL`, or unbounded retry storms and OOM crashes under fault injection.
- **Fail-Closed Rule**: Always check both `axe.json` and `pa11y.json` file non-emptiness and exit codes before declaring accessibility clean.

```bash
# Run k6 threshold gate, fail-closed dual-engine a11y check, and ensure dev worst-case toggle is gated
k6 run --summary-export=test-results/perf-summary.json tests/perf/load-and-spike.js
npx --yes @axe-core/cli@4.13.0 http://127.0.0.1:3000 --exit --save test-results/axe.json
npx --yes pa11y@9.1.1 --standard WCAG2AA --reporter json http://127.0.0.1:3000 > test-results/pa11y.json || [ $? -eq 2 ]
test -s test-results/axe.json && test -s test-results/pa11y.json
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Mean-Only / Single-Run Benchmarks** | Averages hide `2s` `p99` tail spikes caused by GC pauses or lock contention | Perf report states only `avg=42ms` from 1 run | Report `p50/p95/p99`, `RBC`/`Cohen's d`, and `95%` bootstrap CI across blocks |
| **Time-Confounded A-then-B Runs** | Morning vs afternoon noisy-neighbor load creates fake speedups or regressions | Baseline run timestamp hours apart from candidate | Use interleaved `ABBA` blocks after deterministic warm-up discard |
| **Single-Engine or Crash-Swallowed A11y** | One tool misses ~30% of rules the other catches; crashed CLI looks like 0 errors | CI ignores `pa11y` exit `1` vs `2` or skips JSON parse check | Run both pinned `axe-core` + `pa11y` and fail closed on invalid/empty JSON |
| **Nonsense `"aaaa..."` UI Stress Strings** | Unbroken ASCII strings do not test diacritics, RTL, CJK wrapping, or real column widths | Fixture factories filled with `x.repeat(500)` | Use plausible schema-backed names/URLs/currencies from `break-ui` categories |
| **Shipping `?data=worst` to Production** | Exposes mock extreme datasets or triggers layout overrides for real users | Production bundle lacks `NODE_ENV !== 'production'` guard | Gate worst-case fixtures strictly behind dev-only build flags |
| **Unbounded Retries Without Jitter** | Synchronized retry storms multiply outage traffic `5x–10x` and prevent recovery | Retry loop has `for i in range(10)` with constant delay on `POST` | Cap `<= 3` retries with exponential backoff + full jitter on idempotent calls only |
| **Heavy Chaos Mesh on Simple Monoliths** | Wastes weeks operating Kubernetes chaos controllers where `Toxiproxy` suffices (Anti-Overengineering) | Complex multi-cluster chaos YAML for a 1-DB app | Inject faults cleanly with `Toxiproxy` and Playwright `page.route()` |
