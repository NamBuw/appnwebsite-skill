# Non-Functional Requirements (NFR) & SLI/SLO Specification

> **Canonical Output Path**: `docs/product/nfr-slo-matrix.md`

| Field | Value |
|---|---|
| **System / Product** | [e.g., Invoice Reconciliation SaaS] |
| **Spiral ID** | `SP-01` |
| **Rigor Tier** | `minimal` / `standard` / `full` |
| **Monthly Infra Cost Ceiling (1x / 3x)** | [e.g., `$50/mo` at 1x baseline / `$150/mo` at 3x burst] |
| **Gate Verdict** | `PASS` / `CONCERNS` / `NOT ASSESSED` / `FAIL` |

---

## 1. Workload Profile & Critical User Journeys (CUJs)

| Parameter | Baseline (Year-1 Estimate) | Peak / Stress Multiplier | Evidence / Calculation Basis |
|---|---|---|---|
| **Daily Active Users (DAU)** | [e.g., `500` DAU] | [e.g., `3x` campaign burst] | [Observed waitlist / current analytics] |
| **Peak Requests/sec (RPS)** | [e.g., `2` avg RPS] | [e.g., `15` peak RPS] | [`DAU * reqs_per_user / 86400 * peak_factor`] |
| **Payload & Data Growth** | [e.g., `25 KB` JSON / `10 GB/yr`] | [e.g., `25 MB` max upload] | [Row size × expected annual volume] |

**Top 3–5 Critical User Journeys (`CUJ`)**:
1. `CUJ-01`: [e.g., User sign-in and session validation (`FR-001`)]
2. `CUJ-02`: [e.g., Core import/write transaction (`FR-002`)]
3. `CUJ-03`: [e.g., Primary dashboard / landing page initial render (`FR-003`)]

---

## 2. SLI / SLO / Error Budget Matrix (`NFR-NNN`)

| NFR-ID | Category | Linked CUJ / FR | SLI Definition (Numerator / Denominator) | Target Threshold | Rolling Window & Error Budget | Burn-Rate / Freeze Policy | Verification Method & Command |
|---|---|---|---|---|---|---|---|
| `NFR-001` | `Availability` | `CUJ-01`, `CUJ-02` | `good_responses (non-5xx) / total_valid_requests` | `99.9%` | `28d` (`40.3 min` budget) | Freeze feature merges if `> 2%` budget burns in `1h` | Synthetic probe + OTel HTTP metrics check |
| `NFR-002` | `Latency` | `CUJ-02` | Request duration at origin gateway | `p50 <= 80ms`, `p95 <= 250ms`, `p99 <= 600ms` | `28d` (`99%` of 5m buckets compliant) | Alert at `> 200ms` p95 sustained `15m` | `k6 run tests/perf/core_cuj.js` |
| `NFR-003` | `Web CWV` | `CUJ-03` | Field RUM + Lighthouse lab audit | `LCP <= 2.0s`, `INP <= 150ms`, `CLS <= 0.08` | Per release + `28d` p75 RUM | Block release if mobile LCP exceeds `2.5s` | `npx lighthouse <url> --preset=perf` |
| `NFR-004` | `Throughput` | `CUJ-02` | Sustained concurrent RPS without 5xx spike | `>= 45 RPS` (`3x` peak) at `< 0.1%` 5xx | Per release load gate | Scale DB indexes or tune pool before raising infra | `k6 run --vus 50 --duration 5m tests/perf/spike.js` |

---

## 3. Availability, Disaster Recovery & Compliance Floors

| Dimension | Target Value | Operational Mechanism | Drill / Verification Cadence |
|---|---|---|---|
| **External SLA** | [e.g., `99.5%` (strictly looser than `99.9%` internal SLO)] | [Status page + contractual credit cap] | Monthly SLO/SLA reconciliation |
| **Recovery Point Objective (`RPO`)** | [e.g., `<= 15m` (`standard`) / `<= 24h` (`minimal`)] | [Postgres PITR WAL archiving / automated snapshot] | Weekly WAL continuity check |
| **Recovery Time Objective (`RTO`)** | [e.g., `<= 1h` (`standard`) / `<= 4h` (`minimal`)] | [Scripted restore into clean instance] | Quarterly `pg_restore` timed drill |
| **Security & Privacy Elevation** | [`standard`+ mandatory if Auth, PII, or Payments] | [Encryption at rest/TLS 1.3, RLS, audit trail] | Pre-release security baseline scan |

---

## 4. Capacity, Client Performance & Cost Budgets (Simplicity Check)

- **Client JS Bundle Ceiling**: [e.g., `<= 150 KB` gzipped initial route JS]
- **Database & Connection Budget**: [e.g., `<= 20` pooled connections per app instance; `< 50 GB` Year-1 storage]
- **External API / LLM Cost Cap**: [e.g., `<= $0.01` per active user session; hard rate limit at `100 req/min/workspace`]
- **Right-Sizing Simplicity Justification (Q1/Q3 Check)**: [Explicitly state why a single-region Modular Monolith + managed PostgreSQL satisfies every `NFR-NNN` above, and what exact measured breach would be required to justify caches, queues, or multi-region replication.]
