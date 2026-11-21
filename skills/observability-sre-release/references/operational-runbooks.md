# Operational Runbooks, DR Drills & Emergency Patching

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

An operational runbook exists for **03:00 UTC cognitive load**. When production is degraded, an on-call engineer needs:
1. **Exact read-only diagnostic commands** with healthy vs. broken reference outputs.
2. **Copy-paste mitigation steps** with clear blast-radius warnings.
3. **A pre-verified inverse rollback** before mutating live state.

This module governs Disaster Recovery (DR) restore drills, zero-downtime secret/TLS rotation, load-shedding, dead-letter replay, and emergency **Hotfix** vs. **Day-One Patch** execution across Spiral **3C** and **Q4**.

---

## 1. Decision Framework

### 1.1 Simplest High-Craft Runbook Option & Anti-Overengineering Gate

Apply **Least Code, Highest Craft** before building custom operational automation:

- **Option A (Default Simplest High-Craft)**:
  - Versioned Markdown runbooks co-located in `docs/runbooks/` containing copy-pasteable standard CLI commands (`curl`, `psql`/`pg_restore`, `vercel`, `git`, `openssl`).
  - Managed database Point-In-Time Recovery (PITR) paired with a **`<= 40`-LOC quarterly restore-verification script**.
  - Existing feature-flag kill switches and platform rollback commands.
  - Zero custom ChatOps bots, zero bespoke failover controllers.
- **Earned Evidence Required for Option B (Multi-Region Active-Active / Automated Failover Controllers)**:
  - Only build custom DR orchestration or multi-region failover engines when a measured `NFR` constraint disproves Option A:
    - Contractual `RTO < 5 min` or `>= 99.99%` availability across regional cloud outages.

### 1.2 Operational Runbook & Drill Cadence Matrix

| Failure / Maintenance Scenario | Trigger Threshold | Target RTO / RPO | Mandatory Drill Cadence | Minimum Safe Mitigation |
|---|---|---|---|---|
| **DB Backup & PITR Restore** | Data corruption, accidental `DELETE`/migration fault | `RTO <= 30m` / `RPO <= 5m` (`standard`) | **Quarterly** restore into isolated scratch DB | Snapshot + WAL restore to scratch -> schema/checksum verify -> cutover |
| **Secret & TLS Certificate Rotation** | TLS `< 14d` expiry, scheduled `90d` rotation, key leak | `0s` downtime (`dual-active`) | **Automated `30d/14d/7d` alerts** + staging ACME test | Dual-key overlap (`[old, new]`) for `>= 1` max token TTL before revoke |
| **Traffic Spike & Pool Saturation** | DB pool `> 85%` active, `p95 > 1.5x`, `14.4x` burn | Stabilize `< 5 min` | **Pre-launch** load-shedding flag test | Shed non-critical flags (exports, AI, heavy analytics) BEFORE scaling DB |
| **Dependency / Queue Outage & DLQ** | Downstream `5xx > 5%` or DLQ depth climbing | Degrade `< 2 min`; replay bounded | **Semi-annual** GameDay + idempotency check | Trip circuit breaker / cached fallback -> fix poison pill -> `50`-batch replay |
| **Emergency Hotfix / Day-One Patch** | Live `SEV1/SEV2` or post-release `S1/S2` bug | Fix `< 4h` (escalate if `> 4h`) | **Pre-launch** tag-branch & backport check | Branch from **live release tag**, rollback plan pre-coded, backport to `main` + `release/*` |

### 1.3 Emergency Change Triage Decision Tree (`Rollback` vs `Hotfix` vs `Day-One Patch` vs `Sprint`)

```
Production Issue Detected
 ├─ Caused by deploy < 2h ago OR crosses quantitative launch trigger?
 │    └─ YES -> IMMEDIATE ROLLBACK / KILL-SWITCH FLAG (< 5m; never debug forward first)
 ├─ Live SEV1/SEV2 outage, data loss, or security flaw not fixable by rollback?
 │    ├─ Estimated fix <= 4h & minimal diff? -> EMERGENCY HOTFIX (branch from live release tag)
 │    └─ Estimated fix > 4h or architectural? -> ESCALATE + mitigate/degrade + Normal Sprint
 └─ Post-launch S1/S2 / config/data bug after base release passed QA gate?
      ├─ Each fix < 4h, total <= 1 day, ZERO new code paths/architecture? -> DAY-ONE PATCH
      └─ S3/S4 or > 4h structural change -> DEFER explicitly to Next Release (logged table)
```

### 1.4 Non-Negotiable Hotfix & Day-One Patch Rules

- **Hotfix Base-Ref Discipline**: Branch strictly from the **live release tag** (`git tag --list`) or active `release/*` branch — NEVER from `main` head (which ships unvetted unreleased commits).
- **Pre-Code Approval & Rollback**: Write the minimal diff scope (zero cleanup, zero opportunistic refactoring) and exact rollback trigger/command **before** writing fix code.
- **QA Re-Entry (`NOT ASSESSED != PASS`)**: Assess blast radius via callers/grep (`smoke-check` vs. targeted regression vs. full QA). Under emergency pressure, unrun tests MUST be logged as `NOT ASSESSED` with explicit risk sign-off — never marked `PASS`.
- **Mandatory Dual-Branch Backport**: Verify the hotfix commit lands on **BOTH** `main` and active `release/*` branches (`git branch --contains`), eliminating next-release regressions.
- **Escalation & Review SLA**: Escalate any hotfix exceeding **`4 hours`**; require a post-incident review within **`48 hours`**. For Day-One Patches, verify the base release passed its release gate first and log deferred bugs in an explicit **Deferred to Next Release** table.

---

## 2. Step-by-Step Workflow

- **Inputs**: `architecture.md`, `nfr-slo-matrix.md` (RPO/RTO), `threat-model.md`, alert policies, live release tags.
- **Outputs**: Versioned `docs/runbooks/*.md` (from `templates/operational-runbook.md`), DR drill receipt, rotation log, backport verification.
- **Owners**: Primary SRE / Backend On-Call (execution) and Tech Lead (hotfix approval & backport verification).
- **Primary Tools**: `psql`, `pg_restore`, `curl`, `openssl`, `git`, `vercel` / platform CLI, `sentry`.

1. **Author Executable Runbooks per Alert Class (Owner: SRE + Backend Lead)**:
   - Create one focused runbook per paging alert class using `templates/operational-runbook.md`.
   - Include exact alert trigger, user blast radius, and read-only pre-flight diagnostic commands (with expected healthy vs. degraded outputs and denominator-first checks).
   - Provide numbered copy-paste mitigation steps, post-action verification gates, and an inverse rollback procedure.

2. **Execute Quarterly DR Backup & Restore Drill with RPO/RTO Proof (Owner: SRE)**:
   - Never equate *"backup cron exited 0"* with Disaster Recovery.
   - Provision an **isolated scratch database**, record `T_start`, restore the latest snapshot plus WAL logs (`pg_restore` / PITR), and record `T_restore_end`.
   - Prove `T_restore_end - T_start <= RTO` and `T_restore_start - T_last_wal_tx <= RPO`.
   - Run automated schema integrity, foreign-key, row-count, and checksum queries plus a read smoke test against the scratch instance, log the verdict, and destroy the scratch database cleanly.

3. **Run Zero-Downtime Secret & TLS Certificate Rotation (Owner: Platform / Security)**:
   - Rotate signing secrets (JWT, HMAC drain secrets, API keys) strictly via a **dual-active overlap window**:
     - Generate `KEY_V2` and configure verifiers to accept `[KEY_V1, KEY_V2]`.
     - Switch signers to `KEY_V2` and monitor auth `401` and webhook signature failures for `>= 1x` max token TTL.
     - Revoke `KEY_V1` only after zero `KEY_V1` verifications remain.
   - Automate TLS expiry alerts at **`30d`**, **`14d`**, and **`7d`** before expiration and test ACME renewal in staging.

4. **Execute Capacity Protection & Non-Critical Load Shedding (Owner: On-Call Ops)**:
   - Inspect DB connection pool saturation (`PgBouncer` active/waiting clients), queue lag, and `p95` latency before scaling stateless replicas (which can amplify thundering-herd DB connections).
   - **Shed non-critical load first** via runtime feature-flag kill switches: disable heavy CSV exports, AI assistants, expensive analytics, and non-essential webhooks.
   - Tighten rate-limit tiers and pause low-priority background workers until core checkout and auth journeys stabilize.

5. **Isolate Downstream Failures & Execute Bounded Idempotent DLQ Replay (Owner: Backend On-Call)**:
   - Trip the circuit breaker or serve bounded stale cache/async fallback so request threads do not exhaust timeouts.
   - Inspect dead-letter queue (DLQ) payloads and isolate deterministic poison-pill schema errors from transient outages.
   - Replay repaired records strictly in **bounded batches** (`--batch-size 50 --dry-run` first) enforcing **idempotency keys** so retries never double-charge or duplicate state transitions.

6. **Execute Emergency Hotfix or Day-One Patch Protocol (Owner: Tech Lead + On-Call)**:
   - Confirm base release passed its release gate (premise check for Day-One Patches).
   - Cut branch strictly from the live release tag (`git checkout -b hotfix/<slug> <live-tag>`), write the rollback trigger and inverse command before coding, and apply ONLY the minimum fix (zero refactoring).
   - Run targeted QA verification (logging `NOT ASSESSED` honestly for unrun suites), deploy tag `vX.Y.(Z+1)`, verify live `/healthz` and error deltas, and verify backport commits exist on **BOTH** `main` and active `release/*`.

7. **Runbook Condensation & Stale-Procedure Pruning Pass (Owner: SRE)**:
   - During quarterly GameDays and pre-ship **3C**, test every runbook against a fresh engineer with no prior context.
   - Delete narrative background paragraphs, dead dashboard links, and retired hostnames; consolidate duplicate steps and archive runbooks for decommissioned services.

---

## 3. Reusable Artifact & Template

Instantiate [Operational Runbook Template](../templates/operational-runbook.md) for every critical service failure mode and emergency patch path.

| Template Section | Required Fields | Validation & Completeness Rule |
|---|---|---|
| **Header Metadata** | `runbook_id`, `title`, `service`, `linked_alerts`, `severity_scope`, `owner`, `rto_target`, `rpo_target`, `last_drill_utc`, `drill_verdict` | `last_drill_utc <= 90d` for `PASS`; verdict obeys `FAIL > CONCERNS > NOT ASSESSED > PASS` |
| **1. Trigger & Blast Radius** | `alert_expression`, `user_symptom`, `hard_escalation_boundary` | Explicit `15m` / `4h` escalation boundary and user impact stated |
| **2. Pre-Flight Diagnostics** | `readonly_cli_commands`, `healthy_baseline`, `degraded_signal` | Zero side effects; includes denominator-first check and `NOT ASSESSED — NO DATA` rule |
| **3. Executable Mitigation** | `stabilization_cmds`, `recovery_scenario` (PITR / Rotation / DLQ / Hotfix), `backport_check` | Copy-pasteable commands with blast-radius warnings and `main` + `release/*` check |
| **4. Post-Action Gate** | `verification_cmds`, `pass_thresholds`, `verdict_recorded` | Quantitative `p95`, `5xx`, RPO/RTO, and checksum pass rules |
| **5. Rollback Procedure** | `rollback_trigger`, `exact_inverse_commands` | Must be filled and reviewed **before** executing mitigation or hotfix code |

---

## 4. Verification Checklist

- [ ] Every paging burn-rate or infrastructure alert links directly to a copy-pasteable operational runbook.
- [ ] Database disaster recovery verified via isolated scratch restore proving actual RPO and RTO budgets within target.
- [ ] Secret and TLS certificate rotation procedures enforce dual-key overlap windows with zero session or webhook breakage.
- [ ] Load-shedding kill-switch flags disable non-critical expensive endpoints before connection pools or downstream databases saturate.
- [ ] Dead-letter queue replay commands enforce bounded batch sizes and idempotency keys to prevent duplicate side effects.
- [ ] Emergency hotfixes branch strictly from live release tags, document rollback prior to coding, and backport to main and release branches.
- [ ] Quarterly runbook Condensation Pass deleted stale environment URLs, narrative fluff, and retired service procedures.

---

## 5. Hard Quality Gate

Validate hotfix ancestry/backport integrity, TLS expiry headroom, and runbook drill freshness with executable checks:

```bash
# 1. Verify hotfix descends from live release tag and is backported to main (and release/* if active)
LIVE_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$LIVE_TAG" ]; then
  git merge-base --is-ancestor "${LIVE_TAG}" HEAD && echo "Hotfix ancestry PASS (${LIVE_TAG})"
  if git branch -a --contains HEAD | grep -qE '(^|[[:space:]/])main$' \
    && { [ -z "$(git branch -a --list 'release/*' '*/release/*')" ] \
         || [ -n "$(git branch -a --contains HEAD --list 'release/*' '*/release/*')" ]; }; then
    echo "Backport PASS (main + active release/*)"
  else
    echo "Backport FAIL (missing main or active release/*)"; false
  fi
else
  echo "NOT ASSESSED — NO DATA: zero release tags in repository"
fi

# 2. Verify TLS certificate expiry (> 14 days / 1209600s headroom required)
CERT_PEM=$([ -n "${PROD_HOST:-}" ] && openssl s_client -connect "${PROD_HOST}:443" -servername "${PROD_HOST}" </dev/null 2>/dev/null || true)
EXPIRY_DATE=$(printf '%s\n' "$CERT_PEM" | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2 || true)
if [ -z "$EXPIRY_DATE" ]; then
  echo "NOT ASSESSED — NO DATA: TLS probe failed for ${PROD_HOST:-unset}"
elif printf '%s\n' "$CERT_PEM" | openssl x509 -noout -checkend 1209600 >/dev/null 2>&1; then
  echo "TLS cert PASS: notAfter=${EXPIRY_DATE} (> 14d headroom)"
else
  echo "TLS cert FAIL: notAfter=${EXPIRY_DATE} (< 14d headroom)"; false
fi
```

- **PASS**: Every critical failure mode (DR PITR restore, secret/TLS rotation, load-shedding, DLQ replay, hotfix/day-one-patch) has an executable runbook verified within `<= 90 days`, DR restore drill proved `RTO/RPO` targets on a scratch target, TLS expiry exceeds `14 days`, and any hotfix is branched from a live tag and backported to `main` + `release/*`.
- **CONCERNS**: Non-critical Tier-3 runbook drill overdue (`91–120d`) or minor documentation cleanup pending with scheduled GameDay date (`<= 14d`), while Tier-1 DR, rotation, and rollback runbooks pass.
- **NOT ASSESSED**: DR drill never executed, TLS host unreachable, or no release tags exist — MUST emit `NOT ASSESSED — NO DATA`; never infer DR readiness from backup cron exit codes.
- **FAIL**: Backup-only DR without scratch restore proof, single-step destructive secret replacement causing live outages, hotfix branched from `main` head or missing backport to `main`/`release/*`, missing rollback plan before coding, or `NOT ASSESSED` QA checks treated as `PASS`.

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Schrodinger's Backup (Backup Without Restore Drill)** | Snapshots silently omit schemas, WAL archives, or permissions until an actual outage occurs | Zero scratch-restore logs; DR "verified" by cron exit `0` | Execute **quarterly scratch DB PITR restore** measuring actual `RTO`, `RPO`, and row checksums |
| **Hotfix Branched from `main` or Unbackported** | Ships unreleased broken work from `main` or causes the exact SEV1 bug to return on the next release | `git merge-base` skips release tag, or `main` lacks hotfix SHA | Branch strictly from **live release tag**; verify `git branch --contains` on `main` + `release/*` |
| **Single-Step Destructive Secret Rotation** | Overwriting live JWT/HMAC keys immediately invalidates active sessions and drops valid webhooks | Auth `401` spike or drain rejection immediately post-rotate | Use **dual-active key overlap** (`[old, new]`) for `>= 1` max token TTL before revoking old key |
| **Prose-Heavy Tribal Runbooks** | Long paragraphs without exact commands or expected outputs fail under 03:00 UTC fatigue | Responder must Slack a senior engineer to know which CLI flags to run | Write terse numbered commands, expected healthy/degraded outputs, and pre-written rollback |
| **Unbounded / Non-Idempotent DLQ Replay** | Replaying 50,000 failed messages in one loop re-triggers the outage or double-charges customers | Replay script lacks `--batch-size` and idempotency key checks | Dry-run poison-pill inspection + bounded `--batch-size 50` replay with idempotency keys |
| **Custom Multi-Cloud DR Bot Overengineering (Anti-Overengineering)** | Adds fragile failover state machines that cause worse split-brain outages than manual PITR | Bespoke Terraform/ChatOps failover scripts for `< 99.99%` SLA | Managed cloud PITR + `<= 40`-LOC verified restore script + platform rollback (`Option A`) |
