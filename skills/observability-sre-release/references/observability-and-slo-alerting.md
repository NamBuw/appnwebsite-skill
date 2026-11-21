# Observability, Telemetry & SLO Burn-Rate Alerting

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

Production observability exists to answer two operational questions in under five minutes:
1. **Are users experiencing degraded journeys right now?**
2. **Which deployment, dependency, or code path caused the degradation?**

This module covers Spiral stages **3A** (instrumentation baseline, structured JSON logs, correlation headers, and PII scrubbing) and **Q4** (multi-window burn-rate alerting, real-user Core Web Vitals, and exit telemetry) with zero enterprise collector bloat.

---

## 1. Decision Framework

### 1.1 Simplest High-Craft Telemetry Option & Anti-Overengineering Gate

Before deploying any telemetry collector, log aggregator, or APM agent, run the **Simplest High-Craft Option** self-interrogation:

- **Option A (Default Simplest High-Craft for `minimal` and `standard` tiers)**:
  - Native **OpenTelemetry SDK (`OTLP/HTTP`)** exporting to managed platform observability.
  - Single-line **JSON stdout logs** carrying `trace_id` and `request_id`.
  - Hosted error and UX tracking (**Sentry** for exceptions; **PostHog** or platform RUM for Core Web Vitals).
  - **3–5 user-journey SLOs** with multi-window burn-rate alerts.
  - Zero self-hosted log/metric clusters, zero Kafka ingest tiers, and zero custom collector operators.
- **Earned Evidence Required for Option B (Self-Hosted / Tail-Sampling Collector Cluster)**:
  - Only introduce dedicated OpenTelemetry Collector gateways, tail-based sampling clusters, or self-hosted Prometheus/Loki/Tempo stacks when a measured `NFR` constraint disproves Option A:
    - Traffic exceeds `> 10M` requests/day where hosted egress costs exceed engineering ops budget.
    - Strict VPC data-residency rules prohibit SaaS telemetry sinks.
    - Multi-region compliance mandates custom audit retention pipelines.

### 1.2 Telemetry Stack Selection Matrix by Rigor Tier

| Rigor Tier & Scale | Distributed Traces & Sampling | Metrics (RED & USE) | Structured Logs & Drains | Error & Real-User UX Telemetry | Complexity & Overhead Guard |
|---|---|---|---|---|---|
| **`minimal`** (`< 100k` req/day, single app) | `1%–5%` head sampling + `100%` error/slow (`> 1s`) trace capture; W3C `traceparent` | Platform HTTP status/duration counts + DB CPU/connection count | JSON stdout (`level`, `requestId`, `route`, `http_status`, `duration_ms`); `<= 256 KB`/line | Sentry read-only CLI triage + CWV (`LCP < 2.5s`, `INP < 200ms`, `CLS < 0.1`) | `0` self-hosted telemetry containers; `< 1%` CPU overhead |
| **`standard`** (`100k–10M` req/day, SaaS/API) | OTel SDK `5%–10%` production head sampling (`1.0` in dev/staging); `X-Correlation-ID` fallback | Route-level **RED** (Rate, Errors, Duration) + infra **USE** (Utilization, Saturation, Errors) | OTLP/NDJSON log drains verified via **raw-body** HMAC-SHA1/256 `crypto.timingSafeEqual` | Sentry release-tagged issues + PostHog error tracking & narrow-window HogQL queries | `<= 1` overview dashboard/service; `0` unbounded metric labels |
| **`full`** (`> 10M` req/day, multi-region/regulated) | Tail-based OTel collector keeping `100%` error/anomaly traces + `5%` baseline; edge span guard | Multi-region RED/USE + `SUM(_sample_interval)` sampled Analytics Engine queries | Tamper-evident audit sink + `waitUntil` non-blocking edge flush + newline-buffered NDJSON streams | Multi-region synthetic probes + real-user CWV p75 tracking + automated release regression | Instrumentation overhead `< 2%` p95 latency; isolated collector failure |

### 1.3 Multi-Window Multi-Burn-Rate Alerting Matrix

Static threshold alerts (`CPU > 80%` or `single 5xx spike`) wake engineers for non-events and miss slow brownouts. Configure multi-window burn-rate alerts (Google SRE standard) where **both** a long window and a short window (`1/12` of long window) must breach simultaneously:

| Alert Tier | Severity & Route | Error Budget Consumed | Long Window | Short Window | Burn Rate Multiplier | Mandatory Action & Runbook Rule |
|---|---|---|---|---|---|---|
| **Fast Exhaustion** | `Page (SEV1 / SEV2)` | `2.0%` of 30d budget | `1 hour` | `5 min` | `14.4x` | Immediate pager wake; check recent deploys/flags first; rollback `< 5m` |
| **Sustained High Burn** | `Page (SEV2)` | `5.0%` of 30d budget | `6 hours` | `30 min` | `6.0x` | Immediate pager wake; trigger rollback or load-shedding runbook |
| **Slow Chronic Burn** | `Ticket (Triage)` | `10.0%` of 30d budget | `3 days` | `6 hours` | `1.0x` | Next-business-day fix; freeze non-reliability launches if budget `< 20%` |

### 1.4 Platform-Specific Telemetry Thresholds & Edge Traps

- **Core Web Vitals (CWV) Production Targets (p75 Real-User)**:
  - `LCP < 2.5s`, `INP < 200ms`, `CLS < 0.1`, `FCP < 1.8s`, `TTFB < 800ms`.
- **Cloudflare Workers & Edge Limits**:
  - Log lines truncate silently at **`256 KB`**.
  - Distributed trace context propagation stops at **`100` spans** — always inject an explicit `X-Correlation-ID` UUID via `crypto.randomUUID()` for deep service chains.
  - Spectre V8 mitigations coarsen `Date.now()` and `performance.now()` to **`100` microseconds** — never rely on sub-millisecond timing diffs in Workers.
  - Query sampled Analytics Engine datasets using **`SUM(_sample_interval)`**, never `COUNT(*)`.
- **Vercel & Serverless Drains**:
  - Guard `instrumentation.ts` startup hooks with `NEXT_RUNTIME === 'nodejs'` so edge bundles never import Node-only OTel SDKs.
  - Flush edge telemetry inside `waitUntil` so response TTFB stays unaffected.
  - Enforce `--max-time` / `AbortController` plus newline buffering on NDJSON log streams because the streaming endpoint is unbounded.
- **Sentry & PostHog Triage Rules**:
  - Pass Sentry **short IDs** (`ABC-123`) to CLI commands (`sentry issue view`) and numeric `id`s only to REST endpoints; never print `SENTRY_AUTH_TOKEN`.
  - Treat PostHog `person.properties.*` on event payloads as ingestion-time snapshots rather than live person state.

---

## 2. Step-by-Step Workflow

- **Inputs**: `nfr-slo-matrix.md`, `architecture.md`, `security-audit-report.md` (PII/secret boundaries).
- **Outputs**: `telemetry-slo-config.md`, `instrumentation.ts` / OTel SDK bootstrap, scrubbed JSON logger, burn-rate alert rules, single overview dashboard.
- **Owners**: Platform / Backend Engineer (3A instrumentation) and SRE / Release Lead (Q4 alerting & verification).
- **Primary Tools**: OpenTelemetry SDK, `sentry` CLI, `vercel` CLI (`logs`, `metrics`), `curl`, `grep`.

1. **Translate NFRs into 3–5 User-Journey SLIs & Error Budgets (Owner: SRE + Product)**:
   - Map critical user journeys from `nfr-slo-matrix.md` to ratio SLIs (`good_events / valid_events`).
   - Cover **Availability** (server `5xx` vs. valid requests excluding client `400/401/403/404` and synthetic `/healthz` probes), **Latency** (`p95`/`p99` completion), **Freshness/Correctness** (async jobs or webhooks within SLA), and **Web Vitals** (`p75` CWV).
   - Cap at `3–5` SLOs per service so error budgets remain actionable.

2. **Establish W3C Trace Propagation & Explicit Correlation Fallback (Owner: Backend)**:
   - Initialize OpenTelemetry in the application startup hook (`instrumentation.ts` guarded by `NEXT_RUNTIME === 'nodejs'` or service entrypoint).
   - Propagate W3C `traceparent` and `tracestate` across HTTP requests, queues, and background jobs.
   - Generate an explicit `X-Correlation-ID` (`crypto.randomUUID()` or upstream `x-vercel-id` / `cf-ray`) at ingress and propagate it across async job payloads to survive the `100`-span edge propagation cap.
   - Flush serverless/edge spans via `waitUntil`.

3. **Implement PII-Safe Structured JSON Logging Baseline (Owner: Backend)**:
   - Replace scattered `console.log` calls with one shared structured logger (`<= 40` LOC wrapper around stdout JSON).
   - Emit exact allowlisted fields: `timestamp`, `level`, `service`, `env`, `release` (Git SHA), `trace_id`, `span_id`, `request_id`, `route`, `http_status`, `duration_ms`, and `error_code`.
   - Enforce a **pre-emission PII & secret scrubber** stripping `Authorization`, `Cookie`, `Set-Cookie`, `email`, `ip_address`, `phone`, `ssn`, `password`, `api_key`, and card PAN patterns (`EMAIL_RE`, `IP_RE`).
   - Truncate oversized payloads below `256 KB` so edge/cloud log lines never break mid-JSON.

4. **Instrument Bounded-Cardinality RED & USE Metrics (Owner: Backend / Platform)**:
   - Emit route-level **RED** metrics (`http_server_requests_total`, `http_server_request_duration_seconds`) and infra **USE** metrics (DB connection pool active/idle/wait count, queue depth, worker saturation, memory RSS).
   - Restrict metric label dimensions strictly to bounded enums (`service`, `env`, `route_template`, `status_class`, `method`) — forbid `user_id`, `tenant_id`, `email`, `request_id`, or unparameterized URLs in metric labels.
   - Set production trace head-sampling to `0.05–0.10` (retaining `100%` of error traces) instead of `1.0`.

5. **Wire Error Tracking, Raw-Body Drains & Live Diagnostics (Owner: SRE)**:
   - Configure Sentry with release SHA tags (`--release`), `sendDefaultPii: false`, and `beforeSend` scrubbing removing cookies, auth headers, and sensitive stack frames.
   - Verify Vercel/Cloudflare NDJSON or OTLP drain signatures (e.g., `x-vercel-signature`) using HMAC-SHA1/256 over the **raw request body Buffer** with `crypto.timingSafeEqual` — never post-`JSON.parse`.
   - For PostHog analytics and error tracking, batch narrow-window live CLI/MCP queries and apply `SUM(_sample_interval)` on sampled edge datasets.

6. **Configure Burn-Rate Alerts & Single-Pane Overview Dashboard (Owner: SRE)**:
   - Attach `14.4x` (`5m/1h`), `6.0x` (`30m/6h`), and `1.0x` (`6h/3d`) alerts from Section 1.3 to the SLOs.
   - Enforce the **5-Minute Actionability Rule**: every paging alert MUST embed a direct link to its executable runbook, recent deployment SHA, and overview dashboard.
   - Maintain strictly **one** overview dashboard per service showing the 4 Golden Signals (Latency, Traffic, Errors, Saturation) plus Remaining Error Budget %.

7. **Telemetry Complexity Budget & Deletion/Condensation Pass (Owner: SRE + Backend)**:
   - Before Q4 sign-off, delete duplicate logging wrappers, unused APM agents, high-cardinality custom metrics, unactionable `CPU > 80%` threshold pages, and redundant per-endpoint dashboards.
   - Confirm total instrumentation latency overhead stays `< 2%` at `p95` and `grep` finds zero unstructured `console.log` calls in production handlers.
   - Execute live read-only telemetry checks (`sentry issue list`, `vercel logs`, `curl /healthz`) to record concrete verification receipts.

---

## 3. Reusable Artifact & Template

Instantiate [SLO & Alerting Spec Template](../templates/slo-alerting-spec.md) to produce `telemetry-slo-config.md` in Spiral **3A** and verify it in **Q4**.

| Template Section | Required Fields | Validation & Completeness Rule |
|---|---|---|
| **Header & Verdict** | `service_name`, `rigor_tier`, `spiral_id`, `release_sha`, `owner`, `updated_utc`, `verdict` | Verdict follows `FAIL > CONCERNS > NOT ASSESSED > PASS`; `NOT ASSESSED` if live query unrun |
| **1. Simplicity Budget** | `option_a_baseline`, `rejected_complexity`, `overhead_budget`, `sampling_rate`, `dashboard_cap` | Option A documented first; overhead `< 2%` p95; `dashboard_cap <= 1` per service |
| **2. SLI / SLO Table** | `slo_id`, `journey`, `sli_formula`, `exclusions`, `target_pct`, `window`, `monthly_budget`, `source_query` | `3–5` rows max; explicit 4xx/health-probe exclusions; exact query string recorded |
| **3. Burn-Rate Alerts** | `alert_id`, `linked_slo`, `severity`, `short_long_window`, `burn_rate`, `budget_pct`, `channel`, `runbook_link` | Includes `14.4x` (`5m/1h`), `6.0x` (`30m/6h`), `1.0x` (`6h/3d`); every page links to runbook |
| **4. Logging & Scrubbing** | `otel_endpoint`, `correlation_headers`, `mandatory_fields`, `cap_kb`, `scrubbed_keys`, `drain_hmac_rule` | Enforces `traceparent` + `X-Correlation-ID`, `<= 256 KB`, raw-body `timingSafeEqual`, PII scrub list |
| **5. Deletion Audit** | `high_cardinality_audit`, `noisy_alerts_pruned`, `live_verification_receipt` | Confirms `0` unbounded metric labels and records actual live CLI output |

---

## 4. Verification Checklist

- [ ] Three to five user-journey SLOs define exact good-over-valid formulas with explicit 4xx and health-probe exclusions.
- [ ] W3C `traceparent` and fallback `X-Correlation-ID` headers propagate across HTTP, serverless `waitUntil`, and async job queues.
- [ ] Single structured JSON logger emits mandatory correlation fields and enforces the 256 KB payload size cap.
- [ ] Pre-emission PII scrubber strips `Authorization`, `Cookie`, `email`, `ip_address`, and secret tokens before logging or Sentry capture.
- [ ] Metric labels use bounded enums only with zero `user_id`, `email`, `request_id`, or raw URL cardinality explosions.
- [ ] Log drain receivers verify HMAC signatures against raw request body bytes using constant-time `crypto.timingSafeEqual`.
- [ ] Multi-window burn-rate alerts (`14.4x`, `6.0x`, `1.0x`) link directly to tested operational runbooks and pass actionability review.
- [ ] Telemetry Deletion Pass removed noisy threshold alerts, duplicate wrappers, and unstructured `console.log` statements with live checks re-run.

---

## 5. Hard Quality Gate

Execute live read-only telemetry verification after instrumentation and post-deploy (report file denominators on scans; mark unrun probes `NOT ASSESSED — NO DATA` rather than guessing):

```bash
# 1. Audit production request handlers for unstructured console.log (denominator-first)
SRC_COUNT=$(find src -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.py" \) 2>/dev/null | wc -l)
LOG_HITS=$(grep -rnE "console\.(log|debug)\(" src/ 2>/dev/null | wc -l)
echo "Unstructured log scan: scanned ${SRC_COUNT} files, ${LOG_HITS} hits"

# 2. Verify live health endpoint & recent deployment error logs (read-only)
curl -sS -o /dev/null -w "healthz_status=%{http_code} time_total=%{time_total}s\n" "https://${PROD_HOST}/healthz"
vercel logs "${PROD_DEPLOYMENT_URL}" --level error --since 1h --json | head -n 40
vercel metrics vercel.function_invocation.count -f "http_status ge 500" --since 1h --format=json

# 3. Read-only Sentry unresolved production issue check (uses SENTRY_AUTH_TOKEN env var, never printed)
sentry issue list --query "is:unresolved environment:production" --period 24h --limit 20 --json --fields shortId,title,priority,level,status
```

- **PASS**: All `3–5` SLOs have live queries, `traceparent` + `X-Correlation-ID` correlation verified end-to-end, PII scrubbing passes payload test, `0` unbounded metric labels, raw-body HMAC verified on drains, multi-window burn-rate alerts link to runbooks, Telemetry Deletion Pass complete, and live probes exit `0` with `0` critical regressions.
- **CONCERNS**: Minor telemetry gaps (e.g., `1–2` non-critical `console.log` hits in dev scripts or missing RUM CWV on an internal admin surface) with documented remediation date and no PII exposure.
- **NOT ASSESSED**: Live telemetry endpoints or drain signatures were not queried (`SRC_COUNT == 0`, missing `PROD_HOST`, or offline sandbox); MUST emit `NOT ASSESSED — NO DATA`, never `PASS`.
- **FAIL**: Unscrubbed PII/secrets (`Authorization`, `email`, `ip_address`, tokens) in logs/Sentry, parsed-JSON drain signature verification, `100%` unsampled prod tracing exceeding overhead budget, high-cardinality metric labels (`user_id`), or zero burn-rate/runbook linkage on critical user journeys.

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Self-Hosted Collector Cluster for Small/Medium SaaS (Anti-Overengineering)** | Burns weeks operating Prometheus/Thanos/Loki/Tempo/Kafka before product-market scale exists | `> 2` telemetry infra containers for `< 10M` req/day | Native OTel SDK (`OTLP`) + JSON stdout logs + managed Sentry/PostHog (`Option A`) |
| **High-Cardinality Metric Label Explosion** | Putting `user_id`, `email`, `request_id`, or raw URLs in metric labels causes OOM and billing spikes | Metric series count grows linearly with user/request count | Keep bounded enums (`route_template`, `status_class`) in metrics; keep IDs in traces/logs |
| **Threshold Pager Fatigue (`CPU > 80%` / Single `5xx`)** | Wakes engineers at 03:00 UTC for transient blips while missing slow 4-hour brownouts | Alert-to-action ratio `< 50%`; engineers mute alert channel | Multi-window burn-rate alerts (`14.4x` `5m/1h`, `6.0x` `30m/6h`) tied to SLOs |
| **PII & Auth Secret Leakage in Logs or Sentry** | Exposes user emails, IPs, JWTs, and cookies in third-party log sinks and violates privacy law | `Authorization`, `Cookie`, or raw email found in log/event JSON | Pre-emission allowlist + `EMAIL_RE`/`IP_RE` scrubber + `sendDefaultPii: false` |
| **Parsed-JSON Webhook/Drain HMAC Verification** | `JSON.stringify(req.body)` alters whitespace/key order and silently rejects valid drains | Drain returns HTTP `401`/`403` despite matching secret | Compute HMAC against raw `Buffer` bytes and compare with `crypto.timingSafeEqual` |
| **Unsampled `100%` Prod Tracing & `COUNT(*)` on Sampled Stores** | Exceeds `256 KB` / `100`-span edge budgets, adds tail latency, and undercounts sampled traffic by `10–20x` | Elevated `TTFB`, truncated traces, or flat `COUNT(*)` charts | Set `0.05–0.10` head sampling + `X-Correlation-ID` + `SUM(_sample_interval)` queries |
