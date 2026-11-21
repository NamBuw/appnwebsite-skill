# Experiment, Feature Flag & Measurement Specification

> Reusable Spiral Q1/Q2/3B/3C contract for server-evaluated feature flags, KPI governance, and experiment data-quality gates. Replace `<angle-bracket>` slots before shipping.

## 1. Flag Metadata & Ownership

| Field | Specification |
|---|---|
| **Flag Key** | `<kebab-or-snake-flag-key>` |
| **Owner / Team** | `<owner_role_or_handle>` |
| **Target Spiral Slice** | `<spiral_slice_id>` |
| **Created Date** | `<YYYY-MM-DD>` |
| **Mandatory Retirement Date** | `<YYYY-MM-DD>` (<= 30 days post-100% rollout or kill decision) |
| **Default / Static Fallback** | `<false | control | baseline_variant>` |

---

## 2. Simplicity Classification & Server Evaluation Mode

Choose the simplest mechanism that satisfies the requirement without client flicker or SDK bloat:

| Mode Selected | When Valid | Implementation Contract |
|---|---|---|
| `<static_env_var>` | Release/environment boolean with zero per-user targeting | Plain `process.env.<FLAG>` read server-side; zero flag SDK dependency |
| `<edge_config>` | Global instant kill-switch without user bucketing | Single key read at edge; zero experimentation library |
| `<vercel_flags_server>` | Per-user/tenant rollout, A/B test, or Flags Explorer override | Server-only `flag()` (`flags` v4+), `dedupe(identify)` once/request, `FLAGS_SECRET` (`32`-byte base64), `.well-known/vercel/flags` |

- **Zero Call-Site Arguments**: `decide()` reads only the deduped `entities` returned by `identify()` (never pass ad-hoc booleans from components).
- **Static Route Precomputation (If Public/ISR Route)**: Register flags in `precompute()` / `generatePermutations()` and read via `getPrecomputed()` so edge caching remains intact without layout shift or loading spinners.

---

## 3. Measurement Plan (Strict `1-3` KPI Ceiling)

Reject vanity-metric sprawl; every experiment defines at most **3** primary decision metrics:

| Tier | Metric Name | Exact Formula & Grain | Direction / Target |
|---|---|---|---|
| **Primary KPI 1** | `<activation_or_checkout_rate>` | `COUNT(DISTINCT converted_user_id) / COUNT(DISTINCT assigned_user_id)` (grain: `<user_id>`) | `<+X% relative | p < 0.05>` |
| **Primary KPI 2 (Optional)** | `<retention_or_revenue_per_user>` | `<sum_cents / assigned_users>` (grain: `<tenant_id>`) | `<non-inferior or +Y%>` |
| **Diagnostic Driver 1** | `<step_completion_rate>` | `<step_2_users / step_1_users>` | `Informational` |
| **Guardrail 1 (CWV)** | `INP & CLS` | `p75 INP <= 200ms; p75 CLS <= 0.10` | `MUST NOT regress` |
| **Guardrail 2 (Reliability)** | `HTTP 5xx & Client Error Rate` | `5xx_requests / total_requests` | `<= <0.1%>` |

---

## 4. Experiment Data-Quality & Telemetry Gate

Run these deterministic checks before interpreting any experiment readout:

| Check | Expected Invariant | Diagnostic Query / Method | Status |
|---|---|---|---|
| **Grain Consistency** | Numerator and denominator share `<user_id | org_id>` grain | Compare assignment grain vs outcome grain | `<pass | fail>` |
| **Sample Ratio Mismatch (SRM)** | Observed split matches configured weights (`chi-square p >= 0.001`) | Run chi-square goodness-of-fit on `COUNT(DISTINCT entity_id)` by variant | `<pass | fail>` |
| **Duplicate Assignments** | `0` entities assigned to `> 1` variant in experiment window | `GROUP BY entity_id HAVING COUNT(DISTINCT variant) > 1` | `<pass | fail>` |
| **Exposure Without Assignment** | `0` exposure events lacking an assignment record | Anti-join `exposures` against `assignments` on `(entity_id, flag_key)` | `<pass | fail>` |
| **Pre-Assignment Outcome Events** | `0` attributed conversions with `outcome_ts < first_assignment_ts` | Filter `outcome.ts < assignment.first_ts` | `<pass | fail>` |
| **Person-Property Semantics** | Ingestion-time vs current user traits distinguished | Explicit note when querying PostHog `person.properties.*` (PoE) | `<pass | fail>` |

---

## 5. Cleanup & Retirement Plan

- **Decision Trigger**: Roll to `100%` winning variant or revert to `0%` within `7` days of reaching sample size or hitting a guardrail breach.
- **Deletion PR Scope**: Remove flag key from code, delete losing branch JSX/handlers, remove permutation entry, and archive flag in dashboard by `<retirement_date>`.
- **Post-Retirement Check**: Verify zero references remain via `rg "<flag_key>" src/` and confirm bundle/CWV trace shows no dead code.

