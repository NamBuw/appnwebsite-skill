# Release, Promotion & Documentation Sign-Off Checklist (`REL-<VERSION>`)

- **Release Version / Tag**: [vX.Y.Z]
- **Git Commit SHA**: [40-char-sha]
- **Immutable Artifact Digest / Build ID**: [sha256:digest-or-vercel-deployment-id]
- **Deployment Strategy**: [Rolling | Blue-Green | Canary / Rolling Release | Feature-Flag Progressive]
- **Target Environment**: [preview | staging | production]
- **Release Owner**: [Engineer / Release Lead]
- **Last Verified (UTC)**: [YYYY-MM-DDTHH:MM:SSZ]
- **Release Verdict**: [NOT ASSESSED | FAIL | CONCERNS | PASS] *(Precedence: `FAIL > CONCERNS > NOT ASSESSED > PASS`)*

---

## 1. Pre-Flight Quality, Security & Migration Gates

| Gate Item | Required Evidence / Command | Denominator & Result (`scanned N, hits M`) | Status (`PASS \| CONCERNS \| NOT ASSESSED \| FAIL`) |
|---|---|---|---|
| **CI Pipeline & Test Suite** | `gh pr checks` / `circleci config validate` + full test run | [All required checks green; 0 deterministic failures] | [PASS / FAIL] |
| **Single-Build Immutable Artifact** | Build once (`--standalone` / OCI digest); promote without rebuild | [Artifact digest matches tested staging build] | [PASS / FAIL] |
| **SBOM, Provenance & Supply Chain** | `trivy fs --scanners vuln,secret` + `cosign verify` + SBOM | [0 Critical/High CVEs; 0 leaked secrets] | [PASS / FAIL] |
| **Expand-Only DB Migration Safety** | Verify zero `DROP`/`RENAME`/destructive alters coupled to deploy | [Expand migration applied; backward compatible with N-1] | [PASS / FAIL] |
| **QA & Security Verdict Inputs** | `release-qa-verdict.md` + `security-audit-report.md` reviewed | [0 unresolved P0/P1 defects; explicit sign-off] | [PASS / FAIL] |
| **Feature-Flag Kill Switch Ready** | PostHog / flag targeting audited read-first before prod toggle | [Kill switch tested; `< 5s` disable latency] | [PASS / NOT ASSESSED] |

---

## 2. Progressive Rollout Schedule & Automated Halt Thresholds

| Stage | Traffic / Cohort % | Hold Duration | Max 5xx Error Rate | Max p95 Latency | Burn-Rate Halt Guard | Stage Verdict |
|---|---|---|---|---|---|---|
| **Preview / Staging** | `0%` prod (protected URL) | `>= 5m` smoke | `0.0%` on smoke | `<= baseline * 1.2` | `vercel curl` `/healthz` `200` | [PASS / FAIL] |
| **Canary Stage 1** | `5%–10%` | `5–10 min` | `<= 1.0%` (`< 2x` base) | `<= baseline * 1.5` | `ALR-01` / `ALR-02` clear | [PASS / FAIL] |
| **Canary Stage 2** | `50%` | `10–15 min` | `<= 0.5%` (`< 1.5x` base) | `<= baseline * 1.3` | Zero new unresolved Sentry P0/P1 | [PASS / FAIL] |
| **Full Promotion** | `100%` | `48h–72h` watch | `<= SLO-01` target | `<= SLO-02` target | Error budget burn `< 2%` | [PASS / FAIL] |

---

## 3. Post-Deploy Verification Receipts (60s–15m Window)

- **Health & Binding Probe (`0.0.0.0:$PORT`)**: `[curl -sS -o /dev/null -w "%{http_code}" https://<prod-host>/healthz -> 200]`
- **Error Log Scan (`--since 1h`)**: `[vercel logs <url> --level error --since 1h --json -> scanned N events, 0 critical regressions]`
- **Error Tracker Delta (`Sentry / PostHog`)**: `[sentry issue list --query "is:unresolved release:<sha>" -> 0 new P0/P1 issues]`
- **Protected Preview / CWV Smoke**: `[LCP < 2.5s, INP < 200ms, CLS < 0.1 verified on production telemetry]`
- **Human Approval Receipt (Production Tag/Promote)**: `[Approved by: <Name> at <YYYY-MM-DDTHH:MM:SSZ>]`

---

## 4. Rollback Plan & Post-Release Cleanup

- **Exact Instant Rollback Command**: `[vercel rollback <previous-prod-url> | flag-off <flag-key> | git revert <merge-sha>]`
- **Automated Rollback Triggers**: `5xx > 2x baseline or > 1% for 3–5m` OR `p95 > 1.5x baseline for 5m` OR `>= 2 consecutive /healthz failures` OR `14.4x / 6.0x burn-rate page`.
- **Data Rollback / Forward-Fix Note**: [Confirm N-1 code runs safely against expanded DB schema; contract migration scheduled only after bake window.]
- **Pipeline & Flag Cleanup Deadline**: [Remove retired feature flags and unused CI caches/workspaces by `<YYYY-MM-DD>`.]

---

## 5. CI/CD Complexity & Deletion Audit

- **Unused Cache / Workspace Sweep**: [Verified 0 write-only `{{ epoch }}`/SHA cache keys and 0 unused `persist_to_workspace` jobs.]
- **Tag Filter & Concurrency Check**: [Verified deploy job AND upstream `requires` jobs share matching tag filters; stale PR runs auto-cancel.]

---

## 6. Changelog, User Release Notes, and Docs Freshness Sign-Off

| Documentation & Changelog Artifact | Verification Rule | Denominator / Provenance Output | Status |
|---|---|---|---|
| **Bounded Git Provenance Scan** | `git log --oneline <last-tag>..HEAD` (or `-n 100` initial) | [Scanned N commits: X user-facing, Y internal, Z unclear->internal] | [PASS / NOT ASSESSED] |
| **Internal `CHANGELOG.md` (Keep-a-Changelog)** | SemVer `Added \| Changed \| Deprecated \| Removed \| Fixed \| Security` + breaking migration flags | [Commit range `<last-tag>..vX.Y.Z` recorded; metrics attached] | [PASS / FAIL] |
| **User-Facing Release Notes** | Plain-language benefit/symptom-fixed; zero internal file paths, refactors, CI commits, or developer names; transparent Known Issues | [100% internal commits excluded; before/after metrics verified] | [PASS / FAIL] |
| **Diataxis & OpenAPI Schema Parity** | API/schema changes regenerated OpenAPI + updated `docs/` in same PR; `last_verified` updated (`<= 90d`) | [Scanned N docs files, 0 broken relative links, 0 stale contracts] | [PASS / FAIL] |
| **Fresh-Context Reader Test & Bloat Sweep** | 5–8 realistic reader questions tested with zero prior context; duplicated/generic prose deleted (`>= 3` iteration check) | [All reader questions passed; condensation delta recorded] | [PASS / CONCERNS] |

---

## References
- Release Engineering: [CI/CD Pipelines & Release Engineering](../references/cicd-and-release-engineering.md)
- Documentation & Changelogs: [Documentation, Onboarding & Changelogs](../references/documentation-and-changelogs.md)
- Companion Templates: [SLO & Alerting Spec](slo-alerting-spec.md) | [Operational Runbook](operational-runbook.md) | [Postmortem Report](postmortem-report.md)
- Skill Router: [SKILL.md](../SKILL.md)
