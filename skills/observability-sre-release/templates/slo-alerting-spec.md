# SLO, Telemetry & Burn-Rate Alerting Specification (`SLO-SPEC-<NNN>`)

- **Service Name**: [service-name]
- **Rigor Tier**: [minimal | standard | full]
- **Spiral ID**: [SP-001]
- **Release SHA / Version**: [git-sha-or-semver]
- **Owner Role**: [SRE / Platform Lead]
- **Updated (UTC)**: [YYYY-MM-DDTHH:MM:SSZ]
- **Verdict**: [NOT ASSESSED | PASS | CONCERNS | FAIL] *(Precedence: `FAIL > CONCERNS > NOT ASSESSED > PASS`)*

---

## 1. Simplicity & Telemetry Complexity Budget (Option A First)

- **Selected Option A Baseline**: [e.g., Native OTel SDK (`OTLP/HTTP`) + JSON stdout logs with `trace_id`/`request_id` + managed error tracker (Sentry) & platform drains + 3 user-journey SLOs]
- **Rejected Telemetry Complexity**: [e.g., Self-hosted Prometheus/Thanos/Loki/Tempo/Kafka cluster rejected — current load `< 500k` req/day does not justify multi-cluster collector ops]
- **Latency & Cost Budget**: `Instrumentation Overhead < 2% p95` | `Production Trace Head-Sampling Rate: [0.05–0.10]` | `Dashboard Cap: [1 overview dashboard per service]`

---

## 2. User-Facing SLI / SLO & Error Budget Table (3–5 Critical Journeys)

| SLO ID | User Journey | SLI Formula (`good_events / valid_events`) | Exclusions (Client 4xx / Health Probes) | Target % | Rolling Window | Monthly Error Budget | Canonical Source Query |
|---|---|---|---|---|---|---|---|
| `SLO-01` | [API / Checkout Availability] | [HTTP 2xx–3xx / total valid requests] | [Exclude `/healthz`, client `400/401/403/404`] | [99.9%] | [30d] | [43.2 min / 0.1%] | [PromQL / HogQL / Metrics filter] |
| `SLO-02` | [Core Read / Write Latency] | [Requests `< 300ms` / total valid 2xx] | [Exclude batch exports / uploads] | [99.0%] | [30d] | [1.0% slow requests] | [histogram / p95 query] |
| `SLO-03` | [Async Job / Webhook Freshness] | [Jobs completed `< 60s` / total enqueued] | [Exclude paused / dead-lettered test tenants] | [99.5%] | [30d] | [0.5% delayed jobs] | [queue lag / completion query] |
| `SLO-04` | [Real-User Web Vitals (CWV)] | [Sessions `LCP < 2.5s && INP < 200ms && CLS < 0.1`] | [Exclude synthetic bots] | [75.0% p75] | [28d] | [25% p75 margin] | [RUM / PostHog / Vercel query] |

---

## 3. Multi-Window Multi-Burn-Rate Alert Policy

| Alert ID | Linked SLO | Severity (`Page` \| `Ticket`) | Short / Long Window | Burn Rate | Error Budget Consumed | Notification Channel | Linked Runbook Anchor |
|---|---|---|---|---|---|---|---|
| `ALR-01` | `SLO-01` | `Page (SEV1/2)` | `5m` AND `1h` | `14.4x` | `2.0%` in 1h | [Pager / On-Call Webhook] | [operational-runbook.md](../templates/operational-runbook.md) |
| `ALR-02` | `SLO-01` | `Page (SEV2)` | `30m` AND `6h` | `6.0x` | `5.0%` in 6h | [Pager / On-Call Webhook] | [operational-runbook.md](../templates/operational-runbook.md) |
| `ALR-03` | `SLO-01` | `Ticket (Freeze Check)` | `6h` AND `3d` | `1.0x` | `10.0%` in 3d | [Eng Triage Channel] | [operational-runbook.md](../templates/operational-runbook.md) |

- **Error-Budget Freeze Rule**: [If remaining 30d error budget `< 20%`, freeze non-reliability feature launches until `SLO-01` stabilizes or reliability slice lands.]

---

## 4. Structured Logging, Trace Propagation & PII Scrubbing Contract

- **OTLP Collector / Drain Endpoint**: `[https://otel-collector.example.internal/v1/traces]` *(Env Ref: `OTEL_EXPORTER_OTLP_ENDPOINT`)*
- **Context Propagation Headers**: W3C `traceparent` + `tracestate`, plus explicit `X-Correlation-ID` (`crypto.randomUUID()` fallback for deep chains exceeding `100` edge spans)
- **Mandatory JSON Log Fields**: `timestamp`, `level`, `service`, `env`, `release`, `trace_id`, `span_id`, `request_id`, `route`, `http_status`, `duration_ms`, `error_code`
- **Log Entry Size & Non-Blocking Rules**: Enforce `<= 256 KB` payload ceiling; flush telemetry asynchronously via `waitUntil` on serverless/edge runtimes
- **Mandatory Scrubbed PII & Secret Keys (Pre-Emission)**: `Authorization`, `Cookie`, `Set-Cookie`, `email`, `ip_address`, `phone`, `ssn`, `token`, `password`, `api_key`, `card_pan`
- **Drain / Webhook Signature Verification**: Verify `x-vercel-signature` (or provider signature) via HMAC-SHA1/256 against the **raw request body bytes** using constant-time `crypto.timingSafeEqual` (never post-`JSON.parse`)
- **Sampled Aggregation Rule**: Edge/Analytics Engine queries MUST use `SUM(_sample_interval)` rather than `COUNT(*)` when sampling is active

---

## 5. Telemetry Cardinality & Deletion Audit Ledger

| Audit Check | Metric / Log Target | Action Taken (`Retained | Deleted | Aggregated`) | Evidence / Outcome |
|---|---|---|---|
| **High-Cardinality Label Audit** | [Check for `user_id`, `email`, `request_id`, raw URL paths in OTel/metric labels] | [Removed unbounded labels from metrics; kept in logs/traces only] | [0 unbounded label series] |
| **Noisy Alert Pruning** | [Audit threshold alerts (`CPU > 80%`, single `5xx`) not tied to SLO burn] | [Deleted non-actionable CPU/memory pages] | [Alert-to-action ratio >= 90%] |
| **Live Telemetry Verification** | [Run `sentry issue list` / `vercel logs` / `curl /healthz` post-instrument] | [Verified trace + log correlation and PII redaction] | [Exit 0; zero PII in output] |

---

## References
- Reference Module: [Observability, Telemetry & SLO Burn-Rate Alerting](../references/observability-and-slo-alerting.md)
- Companion Checklist: [Release Checklist](release-checklist.md) | [Operational Runbook](operational-runbook.md)
- Skill Router: [SKILL.md](../SKILL.md)
