# Operational Runbook (`RB-<NNN>`)

- **Runbook ID**: [RB-001]
- **Title**: [Short Actionable Incident / Procedure Title]
- **Service / Component**: [service-name]
- **Linked Alert(s) / SLO(s)**: [ALR-01 / SLO-01]
- **Severity Scope**: [SEV1 | SEV2 | SEV3 | SEV4]
- **Owner Role**: [Primary SRE / Backend On-Call]
- **RTO Target**: [e.g., <= 15 minutes]
- **RPO Target**: [e.g., <= 5 minutes]
- **Last Verified Drill (UTC)**: [YYYY-MM-DDTHH:MM:SSZ]
- **Drill Verdict**: [NOT ASSESSED | PASS | CONCERNS | FAIL] *(Precedence: `FAIL > CONCERNS > NOT ASSESSED > PASS`)*

---

## 1. Trigger Conditions & Blast Radius

- **Exact Alert / Symptom Trigger**: [e.g., Burn rate `>= 14.4x` over `5m/1h` on `SLO-01` OR TLS cert `< 14d` expiry OR DB connection pool `> 90%` saturated]
- **User-Visible Impact**: [Describe exact customer symptom — e.g., checkout requests returning HTTP 503 or stale feed]
- **Hard Escalation Boundary**: [Declare `SEV1` and page secondary on-call if unmitigated after `15 minutes` or hotfix exceeds `4 hours`]

---

## 2. Pre-Flight Read-Only Diagnostics (Zero Side Effects)

Run read-only probes first; always record denominator (`scanned N, hits M`) or mark `NOT ASSESSED — NO DATA`:

```bash
# 1. Health & live deployment SHA check
curl -sS -w "\nHTTP:%{http_code} TIME:%{time_total}s\n" "https://${PROD_HOST}/healthz"

# 2. Recent deploys & error spikes (last 1h)
sentry issue list --query "is:unresolved environment:production" --period 24h --limit 20 --json --fields shortId,title,priority,level,status
```

- **Expected Healthy Baseline**: [HTTP `200`, `p95 < 300ms`, `0` new P0/P1 issues in `last 1h`]
- **Degraded Signal Confirmed**: [Specify threshold confirming this runbook applies]

---

## 3. Step-by-Step Executable Mitigation & Recovery

### 3A. Immediate Stabilization (Execute First — Stop User Bleeding)

1. **Check Recent Deploy / Flag Delta**: Inspect last `6h` deployments and feature-flag changes before deep debugging.
2. **Rollback or Kill-Switch Command**:
   ```bash
   # Roll back production alias or disable offending feature flag
   vercel rollback "${PREVIOUS_GOOD_DEPLOYMENT_URL}"
   ```
   - *Blast-Radius Warning*: [Confirm rollback does not hit incompatible destructive DB changes — expand-only schema required.]
3. **Emergency Load Shedding (If Traffic / Pool Saturated)**:
   ```bash
   # Disable non-critical heavy endpoints (exports / AI / analytics) via runtime flag before DB scales
   curl -sS -X POST "https://${ADMIN_HOST}/internal/flags/shed-noncritical" -H "Authorization: Bearer ${OPS_TOKEN}"
   ```

### 3B. Core Scenario Recovery (Choose Applicable Playbook)

- **Scenario 1 — DB PITR Backup Restore (Scratch Target Verification)**:
  ```bash
  # Restore latest snapshot/WAL into isolated scratch DB, verify schema + checksum, never overwrite live blindly
  pg_restore --clean --if-exists --no-owner --dbname="${SCRATCH_DB_URL}" "${BACKUP_ARTIFACT}"
  psql "${SCRATCH_DB_URL}" -c "SELECT count(*) AS users_count, max(created_at) AS latest_write FROM users;"
  ```
- **Scenario 2 — Zero-Downtime Dual-Key Secret / TLS Rotation**:
  1. Generate new key (`KEY_V2`) and configure verifiers to accept `[KEY_V1, KEY_V2]`.
  2. Switch signer to `KEY_V2`; monitor auth `401` rate for `>= 1` max token TTL.
  3. Revoke `KEY_V1` only after `0` `KEY_V1` verifications remain.
- **Scenario 3 — Bounded Idempotent Dead-Letter Queue (DLQ) Replay**:
  ```bash
  # Replay poisoned queue messages in bounded batches using idempotency keys
  python3 scripts/replay_dlq.py --batch-size 50 --require-idempotency-key --dry-run
  ```
- **Scenario 4 — Emergency Hotfix / Day-One Patch (`< 4h` Timebox)**:
  ```bash
  # Branch strictly from live release tag — NEVER from main head
  LIVE_TAG=$(git describe --tags --abbrev=0)
  git checkout -b "hotfix/${HOTFIX_SLUG}" "${LIVE_TAG}"
  ```

### 3C. Mandatory Hotfix Backport Verification

```bash
# Confirm hotfix commit exists on BOTH main and active release/* branch
if git branch -a --contains HEAD | grep -qE '(^|[[:space:]/])main$' \
  && { [ -z "$(git branch -a --list 'release/*' '*/release/*')" ] \
       || [ -n "$(git branch -a --contains HEAD --list 'release/*' '*/release/*')" ]; }; then
  echo "Backport PASS (main + active release/*)"
else
  echo "Backport FAIL (missing main or active release/*)"; false
fi
```

---

## 4. Post-Action Verification Gate

```bash
# Confirm error rate and p95 return to healthy envelope
curl -sS -o /dev/null -w "%{http_code}\n" "https://${PROD_HOST}/healthz"
vercel logs "${PROD_URL}" --level error --since 15m --json
```

- **PASS Criteria**: `HTTP 200` sustained `>= 15m`, `5xx < 0.1%`, `p95 <= SLO-02`, RPO/RTO measured within budget, and hotfix backported to `main` + `release/*`.
- **Verdict Recorded**: `[NOT ASSESSED | PASS | CONCERNS | FAIL]`

---

## 5. Mandatory Rollback Procedure (If Mitigation Worsens State)

- **Rollback Trigger**: [Error rate climbs `> 2x` baseline within `3m` of mitigation OR scratch/canary verification fails.]
- **Exact Inverse Command**: `[Restore prior config/secret/deployment URL and re-enable previous stable routing]`

---

## 6. Escalation & Internal References

- **Primary On-Call**: [Role / Rotation] | **Secondary / IC Escalation**: [Role / Rotation]
- **Reference Module**: [Operational Runbooks, DR Drills & Emergency Patching](../references/operational-runbooks.md)
- **Incident Capture**: [Postmortem Report Template](postmortem-report.md) | **SLO Spec**: [SLO & Alerting Spec](slo-alerting-spec.md)
- **Skill Router**: [SKILL.md](../SKILL.md)
