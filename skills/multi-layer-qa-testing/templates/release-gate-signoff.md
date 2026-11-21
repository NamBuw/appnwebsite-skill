# Release Gate Sign-Off — `<release-or-pr-id>`

> **Release / PR ID**: `<REL-2026-11-21>` | **Spiral ID**: `<SP-001>` | **Target Commit SHA**: `<40-char-git-sha>`
> **Rigor Tier**: `<minimal | standard | full>` | **Evaluated (UTC)**: `<YYYY-MM-DDTHH:MM:SSZ>`
> **Overall Verdict**: `<GO (PASS) | CONDITIONAL (CONCERNS) | HOLD (NOT ASSESSED) | NO-GO (FAIL)>`

---

## 1. 6-Phase Pre-Release Verification Loop (`verification-loop`)

> Strict stop-on-fail order: Phase 1 Build failures halt downstream phases. Unrun phases MUST record `NOT ASSESSED` (never omit or coerce to pass).

| Phase | Verification Step | Command Executed | Fresh Output Summary (Pass / Fail / Count) | Status (`PASS | FAIL | NOT ASSESSED`) |
|---|---|---|---|---|
| **1. Build** | Compile / bundle production artifacts | `<npm run build / python -m build>` | `<exit 0, 0 errors>` | `<PASS>` |
| **2. Typecheck** | Static type verification | `<npx tsc --noEmit / pyright>` | `<0 type errors>` | `<PASS>` |
| **3. Lint** | Formatter & static lint rules | `<npm run lint / ruff check .>` | `<0 errors, 0 warnings>` | `<PASS>` |
| **4. Tests & Coverage** | Unit + integration + black-box + E2E | `<pytest -q --tb=short --cov=src --cov-branch>` | `<142 passed, 0 failed, 86.4% branch>` | `<PASS>` |
| **5. Security Baseline** | Secrets, SAST & dependency scan | `<semgrep + gitleaks + osv-scanner>` | `<0 high/critical findings>` | `<PASS>` |
| **6. Diff Review** | Scope & regression sanity check | `<git diff --stat main...HEAD>` | `<12 files, 0 debug logs, 0 scope drift>` | `<PASS>` |

---

## 2. Eval & Reliability Metrics + Assertion Quality Audit

- **Capability Evals (`pass@k`)**: `<e.g., pass@3 = 96% (>= 90% target) | N/A (deterministic app)>`
- **Regression Stability (`pass^k`)**: `<e.g., pass^3 = 100% across 3 consecutive full runs>`
- **Assertion Quality Audit**:
  - Zero-assertion vacuous tests (`BLOCKING` if `> 0`): `<0>`
  - Thin `1–2` assertion tests (`ADVISORY`): `<count + review note>`
  - Evidence Verdict: `<ADEQUATE | INCOMPLETE | MISSING | NOT ASSESSED | WAIVED>`

---

## 3. Content-Hash Evidence Freshness Audit

> Verify byte-level SHA-256 hashes (never `mtime`) between evidence capture and release sign-off. Any `CHANGED`, `GONE`, or `UNRESOLVED` entry marks evidence `POTENTIALLY STALE` and blocks `GO`.

| Artifact / Source Path | SHA-256 at Evidence Capture | Current SHA-256 at Sign-Off | Freshness (`UNCHANGED | CHANGED | GONE`) |
|---|---|---|---|
| `<src/billing/checkout.ts>` | `<sha256-at-test-run>` | `<sha256-at-signoff>` | `<UNCHANGED>` |
| `<openapi.yaml>` | `<sha256-at-test-run>` | `<sha256-at-signoff>` | `<UNCHANGED>` |
| `<tests/e2e/checkout.spec.ts>` | `<sha256-at-test-run>` | `<sha256-at-signoff>` | `<UNCHANGED>` |

---

## 4. Defect, Coverage, Flake & Non-Functional Thresholds

| Gate Dimension | Required Threshold (`standard / full`) | Measured Value (with Denominator) | Status |
|---|---|---|---|
| **Open `P0` (Critical) Defects** | `0` (all tiers) | `<0 open>` | `<PASS>` |
| **Open `P1` (High) Defects** | `0` (`standard / full`) | `<0 open>` | `<PASS>` |
| **Open `P2` (Medium) Defects** | `0` (`full`) / Waived w/ deadline (`standard`) | `<0 open>` | `<PASS>` |
| **Quarantined Non-Critical Flake Rate** | `<= 2%` (and `0%` on Auth/Pay/P0) | `<0 / 142 (0.0%)>` | `<PASS>` |
| **Dual-Engine A11y (`axe-core` + `pa11y`)** | `0` Critical/Serious (both engines exited clean) | `<0 critical, 0 serious>` | `<PASS>` |
| **Performance / Soak SLO** | `<p95 <= 250ms, err < 0.5%, soak delta <= 20%>` | `<p95=142ms, err=0.02%, delta=+2.1%>` | `<PASS>` |

---

## 5. Target Environment Acceptance (Strictly Separate from Local Verification)

> Local green checks NEVER imply deployed staging/production acceptance. Record each target environment independently.

| Target Environment | Status (`VERIFIED | FAILED | NOT PERFORMED | NOT APPLICABLE`) | Evidence Locator / Smoke URL | Next Permitted Step |
|---|---|---|---|
| **Local / CI Ephemeral** | `<VERIFIED>` | `<CI run #482 + local receipts>` | `<Promote to Staging>` |
| **Staging** | `<VERIFIED | NOT PERFORMED>` | `<staging-smoke-log.json>` | `<Promote to Prod Canary | Run staging smoke first>` |
| **Production Canary** | `<NOT PERFORMED | VERIFIED>` | `<canary-dashboard-url>` | `<Ramp 5% -> 25% -> 100%>` |

---

## 6. Rollback-Trigger Pairing Matrix

> Every deployment or schema migration MUST pair a measurable automated abort trigger with an exact rollback command and backward-compatibility check.

| Release / Migration Change | Automated Abort Trigger (Metric & Window) | Exact Rollback Action / Command | Backward-Safe Verified? | Owner |
|---|---|---|---|---|
| `<Deploy v1.4.0 API + flag>` | `<HTTP 5xx > 1.0% for 3 min OR p95 > 500ms for 5 min>` | `<gh workflow run rollback.yml -f sha=<prev_sha>; flag off>` | `<Yes — expand-and-contract>` | `<@sre-oncall>` |

---

## 7. Conditional Waivers (`CONCERNS` Only) & Final Sign-Off

> `FAIL` and `NOT ASSESSED` are non-waivable. Only `P2/P3` `CONCERNS` in `minimal`/`standard` tiers may carry an explicit time-bound waiver.

- **Active Waivers**: `<None | Waiver ID, justification, owner, expiration date>`
- **Precedence Check (`FAIL > CONCERNS > NOT ASSESSED > PASS`)**: `<GO (PASS) | CONDITIONAL (CONCERNS) | HOLD (NOT ASSESSED) | NO-GO (FAIL)>`
- **Approver & Timestamp (UTC)**: `<qa-and-release-owner, YYYY-MM-DDTHH:MM:SSZ>`
