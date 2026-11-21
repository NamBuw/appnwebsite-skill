---
name: observability-sre-release
description: "Observability (OpenTelemetry traces, RED/USE metrics, PII-safe JSON logs, multi-window SLO burn-rate alerts), CI/CD provenance and progressive releases (canary, blue-green, feature flags, rollback), technical and user changelogs, operational DR/hotfix runbooks, and SEV/ICS blameless postmortems across Spiral stages 3A, 3C, and Q4."
license: MIT
metadata:
  suite: appnwebsite-skill
  version: "1.0.0"
  milestone: M5
  spiral_stages: "3A,3C,Q4"
---

# Observability, Release Engineering & Production SRE (`observability-sre-release`)

Standalone Child Skill governing telemetry, SLO alerting, signed CI/CD pipelines, progressive delivery, documentation/changelogs, operational runbooks, and incident/postmortem operations across Spiral stages **3A**, **3C**, and **Q4**.

---

## 1. Progressive Disclosure & Lazy-Loading Rule

1. **Load On Demand Only**: Read ONLY the single reference module and template required for the active Spiral stage or operational task. NEVER bulk-load all five `references/*.md` files into context.
2. **Zero `@path` Imports**: Never use eager `@path` directives. All relative links stay strictly inside this skill directory.
3. **Reference Sibling Skills by Name Only**: Upstream skills (`fullstack-api-engineering`, `multi-layer-qa-testing`, `security-engineering`) and the parent suite (`appnwebsite-orchestrator`) are cited by name or backticked path only—never via external relative links.

---

## 2. Standalone Pre-Flight Fallback (When Invoked Without Parent Orchestrator)

When invoked directly outside `appnwebsite-orchestrator`, execute these 3 checks before authoring configs, pipelines, or runbooks:

1. **Contract Check (`3A` Baseline)**: Verify `nfr-slo-matrix.md`, `architecture.md`, `release-qa-verdict.md`, and `security-audit-report.md` exist on disk—or lock a concise `minimal`-tier SLO, rollback, and logging contract first (`NOT ASSESSED — NO DATA` for missing inputs; never fabricate paths or metrics).
2. **Simplicity Self-Interrogation ("Least Code, Highest Craft")**: Before proposing any observability stack, deployment orchestrator, doc portal, or incident tooling, construct **Option A (Simplest High-Craft)** first using native platform primitives, hosted OTel/logs, and single-workflow CI/CD. Add complexity only when a measured `NFR` constraint disproves Option A.
3. **Fresh Verification Iron Law**: Capture live CLI/pipeline/smoke outputs (`sentry`, `vercel`, `gh`, `git`, `curl`, `openssl`) after final edits—never infer pass status from memory or stale logs.

---

## 3. Routing Table (5 Reference Modules & 4 Templates)

| Spiral Stage / Task Domain | When to Load | Reference Module | Reusable Template |
|---|---|---|---|
| **3A / Q4 — Telemetry, OTel, Logs & SLO Alerts** | Instrumenting traces/metrics/logs, PII scrubbing, drains, CWV, or burn-rate alerts | [Observability & SLO Alerting](references/observability-and-slo-alerting.md) | [SLO & Alerting Spec](templates/slo-alerting-spec.md) |
| **3A / 3C / Q4 — CI/CD, Provenance & Releases** | Building pipelines, SBOM/signing, expand-only migrations, canary/blue-green, or rollback | [CI/CD & Release Engineering](references/cicd-and-release-engineering.md) | [Release Checklist](templates/release-checklist.md) |
| **3C / Q4 — Docs, Onboarding & Changelogs** | Authoring Diataxis docs, OpenAPI parity, 15m onboarding, or provenance-filtered release notes | [Documentation & Changelogs](references/documentation-and-changelogs.md) | [Release Checklist (Section 6)](templates/release-checklist.md#6-changelog-user-release-notes-and-docs-freshness-sign-off) |
| **3C / Q4 — Runbooks, DR, Rotation & Hotfixes** | Authoring 03:00 UTC runbooks, PITR restore drills, dual-key rotation, DLQ replay, or hotfixes | [Operational Runbooks](references/operational-runbooks.md) | [Operational Runbook](templates/operational-runbook.md) |
| **Q4 / Live Ops — Incidents & Postmortems** | Running SEV1–SEV4 ICS triage, status comms, 5-Whys, `Where We Got Lucky`, or `TD-NNN` actions | [Incident & Postmortems](references/incident-and-postmortems.md) | [Postmortem Report](templates/postmortem-report.md) |

---

## 4. Suite Input / Output Contract

- **Upstream Dependencies**: `fullstack-api-engineering`, `multi-layer-qa-testing`, `security-engineering`.
- **Canonical Inputs Consumed**:
  - `nfr-slo-matrix.md` — quantitative availability, latency (`p95`/`p99`), freshness, RPO/RTO, and error-budget targets.
  - `architecture.md` — service topology, data stores, edge boundaries, and deployment targets.
  - `release-qa-verdict.md` — multi-layer QA & black-box test pass verdict (`0` unresolved `P0/P1`).
  - `security-audit-report.md` — SAST/DAST/supply-chain clearance and secret-handling requirements.
- **Canonical Outputs Produced**:
  - `telemetry-slo-config.md` (via [SLO & Alerting Spec](templates/slo-alerting-spec.md))
  - `cicd-release-pipeline` + release sign-off (via [Release Checklist](templates/release-checklist.md))
  - `operational-runbooks.md` (via [Operational Runbook](templates/operational-runbook.md))
  - `changelog.md` + user release notes (via [Release Checklist Section 6](templates/release-checklist.md#6-changelog-user-release-notes-and-docs-freshness-sign-off))
  - `postmortem-template.md` / active incident report (via [Postmortem Report](templates/postmortem-report.md))

---

## 5. Radical Simplicity & Non-Negotiable SRE Invariants

1. **Verdict Precedence**: Always evaluate gates using `FAIL > CONCERNS > NOT ASSESSED > PASS`. Never treat `NOT ASSESSED` (missing telemetry, unrun drill, or zero-hit scan lacking a file denominator) as `PASS`.
2. **Correlation & PII Hygiene**: Propagate W3C `traceparent` plus explicit `X-Correlation-ID` (`crypto.randomUUID()`) across deep edge chains (`> 100` spans) and async queues; scrub `Authorization`, `Cookie`, `email`, `ip_address`, and tokens **before** emission; enforce `<= 256 KB` log entry limits and non-blocking `waitUntil` flushing.
3. **Raw-Body Drain Security & Sampled Queries**: Verify webhook/log-drain HMAC signatures against **raw request bytes** via `crypto.timingSafeEqual` (never post-`JSON.parse`); aggregate sampled edge telemetry with `SUM(_sample_interval)`, never `COUNT(*)`.
4. **Build Once, Promote Many**: Produce one immutable `--standalone` / OCI digest artifact with SBOM and keyless OIDC provenance; promote the exact tested artifact from protected preview (`vercel curl`) to production without rebuilding.
5. **Expand-Before-Deploy & Tested Rollback**: Apply additive expand migrations before code rollout; never couple destructive `DROP`/`RENAME` operations to live deployments; confirm an instant (`< 5m`) rollback command or feature-flag kill switch before promotion.
6. **CI Triage & Cache Discipline**: Classify CI failures as **transient vs. deterministic** before retrying; avoid `{{ epoch }}`/SHA write-only cache keys; ensure CircleCI/GHA tag-triggered deploy jobs and all upstream `requires` jobs carry matching tag filters.
7. **Hotfix & Provenance Discipline**: Branch emergency hotfixes strictly from the **live release tag** (never `main` head), verify backports to BOTH `main` and `release/*`, and filter bounded `git log` history so internal refactors never leak into user release notes.
8. **Mitigate First, Blameless Always**: Stabilize customer bleeding before deep debugging; conduct blameless 5-Whys within `48h–72h`, capture `Where We Got Lucky`, and cap follow-ups at `3–5` owned, time-bound preventive actions.

---

## 6. Quick CLI Pre-Check Reference

```bash
# 1. Read-only production error & deployment triage
sentry issue list --query "is:unresolved environment:production" --period 24h --limit 20 --json --fields shortId,title,priority,level,status
vercel logs <deployment-url> --level error --since 1h --json

# 2. CI checks & bounded changelog provenance
gh pr checks --json name,state,bucket,link,workflow
git log --oneline "$(git describe --tags --abbrev=0)..HEAD"

# 3. Hotfix backport (AND logic: main + active release/*) & TLS expiry check
git branch -a --contains HEAD | grep -qE '(^|[[:space:]/])main$' && { [ -z "$(git branch -a --list 'release/*' '*/release/*')" ] || [ -n "$(git branch -a --contains HEAD --list 'release/*' '*/release/*')" ]; } && echo "Backport PASS" || { echo "Backport FAIL"; false; }
openssl s_client -connect "${PROD_HOST}:443" -servername "${PROD_HOST}" </dev/null 2>/dev/null | openssl x509 -noout -dates -checkend 1209600
```
