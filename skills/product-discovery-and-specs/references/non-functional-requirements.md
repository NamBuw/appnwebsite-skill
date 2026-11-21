# Non-Functional Requirements (NFRs), SLIs, SLOs, and Cost Budgets

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

Qualitative wishes like `"the system must be fast, scalable, and highly available"`
are architecture traps. They cannot be load-tested, cannot trigger alerts, and
routinely provoke cargo-cult overengineering such as multi-region active-active
clusters and distributed message buses for a 200-user SaaS product.

This module turns non-functional constraints into falsifiable **SLI / SLO / Error
Budget** contracts, realistic capacity and client budgets, concrete **RPO / RTO**
disaster recovery floors, and strict **Least Code, Highest Craft** cost ceilings
before Phase 3A architecture starts.

---

## 1. Decision Framework

### 1.1 SLI, SLO, SLA, and Error Budget Contract

Keep the four reliability primitives strictly separated so engineering targets never
blur into legal penalties or unmeasured wishes:

1. **SLI (Service Level Indicator)**: Exact mathematical ratio
   `good_events / valid_events` measured at a named boundary (origin HTTP gateway,
   worker queue, or client RUM), never a raw unnormalized average.
2. **SLO (Service Level Objective)**: Internal engineering target percentage or
   percentile threshold paired with an explicit rolling window (e.g., `99.9%`
   availability over `28` days = `40.32` minutes of permissible downtime).
3. **SLA (Service Level Agreement)**: External contractual commitment with customer
   remedies; **always looser** than the internal SLO (`99.5%` SLA vs `99.9%` SLO) so
   engineering detects and fixes burn before breaching contracts.
4. **Error Budget & Burn-Rate Policy**: `100% - SLO` defines the quantitative budget
   spent on releases and experiments; once rapid burn consumes `> 2%` of the 28-day
   budget within 1 hour, feature merges pause in favor of reliability work.

### 1.2 Rigor-Tier Quantitative Baseline Matrix

Use these calibrated baselines as **Option A defaults** unless measured traffic or
domain contracts prove a stricter target is required:

| Quality Dimension | `minimal` (Single-Surface / MVP) | `standard` (Multi-Feature SaaS / App) | `full` (High-Scale / Regulated) |
|---|---|---|---|
| **Availability SLO (`28d`/`30d`)** | `99.5%` (~`3.6h` downtime / 30d) | `99.9%` (~`43m` downtime / 30d) | `99.95%`–`99.99%` (~`21m`–`4.3m` / 30d) |
| **API Latency (`p50 / p95 / p99`)** | `<= 150ms / 500ms / 1000ms` | `<= 80ms / 250ms / 600ms` | `<= 50ms / 150ms / 350ms` |
| **Web Core Web Vitals (`LCP / INP / CLS`)** | `<= 2.5s / <= 200ms / <= 0.1` | `<= 2.0s / <= 150ms / <= 0.08` | `<= 1.8s / <= 100ms / <= 0.05` |
| **Throughput & Headroom** | Baseline peak + `2x` burst | Measured peak × `3x` sustained | Sustained load + `5x` spike + chaos drill |
| **Disaster Recovery (`RPO / RTO`)** | `RPO <= 24h` / `RTO <= 4h` (snapshot) | `RPO <= 15m` / `RTO <= 1h` (Postgres PITR) | `RPO <= 1m` / `RTO <= 15m` (multi-AZ failover) |
| **Client Initial JS Budget** | `<= 180 KB` gzipped | `<= 150 KB` gzipped | `<= 120 KB` gzipped |

**Mandatory Security Elevation**: Any workload handling Auth, PII, or Payments
automatically inherits `standard` + security, encryption (`TLS 1.3`, AES-256 at
rest), auditability, and `RPO <= 15m` floors even in an otherwise `minimal` Spiral.

### 1.3 Radical Simplicity ("Least Code, Highest Craft") NFR Gate

Each additional `"9"` of availability (`99.9% -> 99.99%`) multiplies infrastructure
cost, replication complexity, and operational paging burden roughly tenfold. Enforce
three **Anti-Overengineering NFR Rules**:

- **Simplicity Q1 (Single-Region Modular Monolith Default)**: Prohibit multi-region
  active-active databases, Kafka clusters, or distributed Redis caches in
  `nfr-slo-matrix.md` unless concrete workload math (`DAU`, `RPS`, `p99` failure)
  proves a single-region Modular Monolith + managed PostgreSQL with Point-in-Time
  Recovery (PITR) cannot meet the SLO.
- **Simplicity Q2 (Tail vs. Mean Discipline)**: Specify `p95` and `p99` tail targets
  on core user journeys instead of demanding arbitrary sub-50ms `p99` on
  low-frequency admin endpoints.
- **Simplicity Q3 (Unit-Cost Ceiling)**: Pair every latency, throughput, and AI/LLM
  capability with an explicit monthly infrastructure and per-session API cost cap
  (`$/month` at `1x` and `3x` peak).

---

## 2. Step-by-Step Workflow

1. **Inventory Critical User Journeys (`CUJ`) & Workload Baseline**
   - *Inputs*: `docs/product/prd.md`, `docs/product/use-cases.md`.
   - *Output*: Section 1 of `docs/product/nfr-slo-matrix.md`.
   - *Owner*: Architect / SRE / PM | *Tool*:
     [nfr-slo-spec.md](../templates/nfr-slo-spec.md).
   - Identify the top `3–5` revenue, activation, or trust-critical user journeys:
     - `CUJ-01`: Authentication and session validation;
     - `CUJ-02`: Core domain write or import transaction;
     - `CUJ-03`: Primary landing or dashboard initial render.
   - Estimate realistic Year-1 `DAU`, average daily requests per user, peak burst
     factor (`3x–5x` over average), payload size (`KB`/`MB`), and annual data growth
     (`GB/year`):
     - `Peak RPS = (DAU * avg_reqs / 86400) * peak_factor`.
   - Document the empirical evidence basis (waitlist count, existing analytics, or
     domain proxy) for every workload assumption.

2. **Define Quantitative SLIs, Percentiles (`p50/p95/p99`) & Error Budgets**
   - *Inputs*: `CUJ` list, Rigor Tier baseline.
   - *Output*: Section 2 of `docs/product/nfr-slo-matrix.md`.
   - *Owner*: SRE / Tech Lead | *Tool*: Threshold matrix.
   - Author numbered `NFR-NNN` rows linking each Critical User Journey to:
     - a mathematical SLI formula (`good_events / valid_events`);
     - a measurement boundary (edge CDN, origin gateway, or client RUM);
     - explicit numeric percentiles (`p50`, `p95`, `p99`) and rolling window (`28d`
       or `30d`).
   - Compute the exact downtime allowance in minutes/events (`Error Budget`) and
     specify a binding **Burn-Rate / Freeze Policy**.
   - Assign an executable verification command (`k6`, `Locust`, `Lighthouse`,
     `pytest-benchmark`, synthetic probe) to every single `NFR-NNN` row.

3. **Lock Availability, Disaster Recovery (`RPO/RTO`) & Compliance Floors**
   - *Inputs*: Data sensitivity profile, `FR-NNN`.
   - *Output*: Section 3 of `docs/product/nfr-slo-matrix.md`.
   - *Owner*: Security / Infra Lead | *Tool*: DR matrix.
   - Specify `External SLA` (only when contractual remedies apply; strictly looser
     than internal SLO), `RPO` (max tolerable data loss window), and `RTO` (max
     elapsed restore time).
   - Pair every `RPO` /`RTO` target with its concrete operational mechanism
     (automated Postgres WAL archiving + PITR) and scheduled restore drill cadence
     (quarterly timed `pg_restore`).
   - Verify whether Auth, PII, or Payments trigger automatic security/audit floor
     elevation.

4. **Set Capacity, Client Bundle & Monthly Cost Ceilings**
   - *Inputs*: Workload baseline, surface type | *Output*: Section 4 of
     `docs/product/nfr-slo-matrix.md` | *Owner*: FinOps / Tech Lead | *Tool*: Budget
     sheet.
   - Lock concrete ceilings for initial gzipped client JS bundle (`<= 120–180 KB`),
     database connection pool size (`<= 20` per instance), Year-1 storage cap, and
     external API / LLM token spend per user session.
   - Establish monthly infrastructure cost ceilings at both `1x` baseline and `3x`
     peak traffic so architectural choices stay anchored to unit economics.

5. **Run NFR Right-Sizing & Deletion Pass**
   - *Inputs*: Draft `nfr-slo-matrix.md`.
   - *Output*: Frozen `docs/product/nfr-slo-matrix.md`.
   - *Owner*: Principal Architect | *Tool*: Q1/Q3 ablation check.
   - Challenge every `NFR-NNN` exceeding `standard` defaults: *"Which observed
     customer requirement fails if we relax `99.99%` to `99.9%` or `50ms` to `250ms`?"*
   - Delete speculative multi-region, sub-second global sync, or cold-start
     perfection targets lacking business justification.
   - Record a concise **Right-Sizing Simplicity Justification** explaining why a
     single-region Modular Monolith + managed Postgres satisfies all targets, then
     write `docs/product/nfr-slo-matrix.md` cleanly to disk.

### Worked Example: Workload Math Grounding Option A Infrastructure

- **Assumptions**: `1,000` Year-1 DAU averaging `40` requests/day with a `4x`
  morning burst yields `(1000 * 40 / 86400) * 4 = 1.85` peak RPS (`~5.5` RPS at `3x`
  headroom).
- **Simplicity Outcome**: Single-region Modular Monolith + managed Postgres (`<= 20`
  pooled connections, PITR `RPO <= 15m`) clears `p95 <= 250ms` and `99.9%` SLO for
  `< $60/mo` — rejecting Kafka and multi-region clusters.

---

## 3. Reusable Artifact & Template

All non-functional targets live in `docs/product/nfr-slo-matrix.md` authored from
[nfr-slo-spec.md](../templates/nfr-slo-spec.md). Follow these authoring discipline
rules:
- Link each `NFR-NNN` row to an existing `CUJ` and `FR-NNN` ID instead of copying
  feature descriptions.
- Keep `External SLA` strictly looser than `Internal SLO` (`99.5%` SLA vs `99.9%`
  SLO) whenever contractual terms exist.
- Include the `Right-Sizing Simplicity Justification` block so Phase 3A architects
  see why simpler infrastructure suffices.

| Section / Field | Cardinality | Mandatory Contract |
|---|---|---|
| `Metadata & Cost Ceiling` | `1` header table | `System Name`, `Spiral ID`, `Rigor Tier`, `Monthly Infra Cost Ceiling (1x/3x)`, `Gate Verdict` |
| `Workload & CUJs` | `3` metrics + `3–5` CUJs | `DAU`, `Peak RPS` formula, `Payload & Growth/yr`, numbered `CUJ-01..05` linked to `FR-NNN` |
| `SLI / SLO Matrix (NFR-NNN)` | `>= 3` rows | `NFR-ID`, `Category`, `Linked CUJ/FR`, `SLI Formula`, `Target`, `Window & Error Budget`, `Burn Policy`, `Verification Command` |
| `DR & Compliance Floors` | `4` dimensions | `External SLA` (looser than SLO), `RPO`, `RTO`, `Restore Drill Cadence`, `Auth/PII/Payments Elevation` |
| `Capacity & Simplicity Check` | `4` budgets | `JS Bundle KB`, `DB Connections/Storage`, `External API/LLM Cap`, `Right-Sizing Simplicity Justification` |

---

## 4. Verification Checklist

- [ ] Top `3–5` Critical User Journeys (`CUJ`) link directly to `FR-NNN` IDs and realistic Year-1 `DAU` / `Peak RPS` math.
- [ ] Every `NFR-NNN` defines a numeric threshold, explicit percentile or ratio (`p95`, `p99`, `%`), and rolling window (`28d` or `30d`) with zero vague adjectives.
- [ ] Every availability SLO specifies an exact Error Budget in minutes/events and a concrete merge-freeze policy on fast burn.
- [ ] External SLA (if present) is strictly looser than the internal engineering SLO to preserve intervention headroom.
- [ ] `RPO` and `RTO` targets cite concrete backup/WAL mechanisms and a recurring timed restore drill cadence.
- [ ] Monthly infrastructure and external API/LLM cost ceilings (`1x` and `3x`) plus client JS bundle caps are explicitly recorded.
- [ ] Right-Sizing Simplicity Justification verified that no speculative five-nines or multi-region infrastructure was requested without math.

---

## 5. Hard Quality Gate

NFR specification unlocks Phase 3A architecture **ONLY** when binary evaluation
yields `PASS` (`FAIL > CONCERNS > NOT ASSESSED > PASS`):

- **PASS**: `docs/product/nfr-slo-matrix.md` exists on disk with zero stub markers
  (`TODO`, `TBD`, `FIXME`, `[placeholder]`):
  - declares `CUJ`, `SLI`, `SLO`, `p95`, `RPO`, `RTO`, and Error Budget rules;
  - specifies numeric units (`ms|%|RPS|KB|$`) and an executable verification command
    per `NFR`;
  - locks `1x`/`3x` monthly infra cost ceilings and client JS bundle cap;
  - includes a grounded `Right-Sizing Simplicity Justification`.
- **CONCERNS**: `minimal` tier omits external SLA or `5x` chaos spike while
  preserving latency, availability, `RPO/RTO`, and cost caps.
- **NOT ASSESSED**: Verification command column blank, `RPO` /`RTO` unverified, or
  workload math missing.
- **FAIL**: Qualitative wishlists (`"highly scalable"`, `"fast"`) lacking numeric
  targets, average-only latency hiding `p95` /`p99`, SLA tighter than SLO, or
  ungrounded `99.999%` demands violating Simplicity Q3.

```bash
python3 - <<'PY'
from pathlib import Path
import re, sys

nfr = Path("docs/product/nfr-slo-matrix.md")
if not nfr.is_file():
    print("FAIL: missing docs/product/nfr-slo-matrix.md"); sys.exit(1)
text = nfr.read_text(encoding="utf-8")
for pat in (r"\bTODO\b", r"\bTBD\b", r"\bFIXME\b", r"\[placeholder\]", r"\bLorem ipsum\b"):
    if re.search(pat, text):
        print(f"FAIL: stub marker {pat!r} found"); sys.exit(1)
for req in ("NFR-", "SLI", "SLO", "p95", "RPO", "RTO", "Error Budget"):
    if req not in text:
        print(f"FAIL: missing required NFR element {req!r}"); sys.exit(1)
if not re.search(r"\d+(?:\.\d+)?\s*(?:ms|s|%|RPS|KB|MB|\$)", text):
    print("FAIL: missing numeric threshold units"); sys.exit(1)
print("PASS: NFR & SLI/SLO gate satisfied.")
PY
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Mean-Only Latency Targets** | Average response time masks severe tail latency harming the slowest `5%` of real users | Spec states `"average latency < 200ms"` with zero `p95` or `p99` values | Specify `p50`, `p95`, and `p99` thresholds per Critical User Journey |
| **Cargo-Cult Five-Nines (`99.999%`)** | Forces multi-region active-active databases and ~10x cloud/ops overhead nobody pays for | `99.99%` or `99.999%` SLO copied without traffic math or budget approval | Default to `99.5%` (`minimal`) or `99.9%` (`standard`) unless math proves need |
| **Error Budget Without Consequence** | Reliability targets become decorative prose when teams keep shipping during outages | Matrix lists `99.9%` SLO but leaves burn-rate action blank | Bind fast-burn alerts directly to a merge freeze on non-reliability work |
| **Paper-Only `RPO` / `RTO` Numbers** | Unverified backup policies routinely fail during incidents due to broken WAL chains | `RPO <= 15m` declared with zero backup mechanism or timed restore drill | Pair every `RPO/RTO` with WAL/PITR config and a scheduled `pg_restore` drill |
| **Zero Cloud & AI Cost Ceiling** | Unbounded retries, bloated JS bundles, or unrestricted LLM loops blow unit economics | `nfr-slo-matrix.md` omits monthly `$/mo` cap, token cap, and bundle ceiling | Lock `1x` and `3x` monthly spend limits, rate caps, and gzipped JS budget |
| **Qualitative NFR Wishlists** | `"Scalable"` and `"resilient"` cannot fail a CI gate or guide database design | NFR section uses prose adjectives with zero `ms`, `%`, `RPS`, `KB`, or command | Convert every wish into an `NFR-NNN` row with SLI formula and test command |
