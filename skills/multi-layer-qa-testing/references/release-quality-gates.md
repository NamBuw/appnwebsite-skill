# Release Quality Gates, Verification Loops & Evidence Audits

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

Release quality gating converts fragmented build, test, evaluation, security, and operational checks into an unforgeable, deterministic `GO / CONDITIONAL / HOLD / NO-GO` decision. It prevents premature completion claims, stale evidence reuse, vacuous zero-assertion suites, and unrecoverable one-way deployments.

---

## 1. Decision Framework

### 1.1 Four-State Gate Verdict & Precedence Rules

Evaluate gate dimensions in strict precedence order (**first match wins**):
`FAIL (NO-GO)` **>** `CONCERNS (CONDITIONAL)` **>** `NOT ASSESSED (HOLD — MISSING EVIDENCE)` **>** `PASS (GO)`

| Gate Verdict | Go/No-Go Decision | Exact Trigger Conditions | Allowed Next Action |
|---|---|---|---|
| **FAIL** | **NO-GO** | Any build/type/lint failure, `> 0` test failures, `> 0` open `P0`, `> 0` open `P1` (`standard/full`), Critical/Serious security or a11y issue, or `> 0` vacuous `0`-assertion critical tests | **Block release**; remediate root cause and re-run full verification |
| **NOT ASSESSED** | **HOLD** | Any required check unrun, `N == 0` tests executed, truncated soak, missing manual SR check, or content-hash receipt marked `CHANGED`/`GONE`/`UNRESOLVED` | **Block release**; execute missing checks (never coerce to `PASS`) |
| **CONCERNS** | **CONDITIONAL** | Zero `FAIL`/`NOT ASSESSED` conditions, plus bounded `P2/P3` issues or `1–2` assertion thin tests covered by explicit owner + deadline waiver (`minimal/standard` only) | **Ship with logged waiver** (forbidden in `full` rigor for `P2`) |
| **PASS** | **GO** | `100%` 6-phase verification loop fresh pass, `pass^3 = 100%` critical regression, content hashes `UNCHANGED`, `0` blockers for rigor tier, and rollback triggers locked | **Cleared for target deployment** |

### 1.2 Rigor Tier Matrix (`minimal` vs. `standard` vs. `full`) & Blocker Ceilings

| Dimension | `minimal` (Prototype / Low-Risk) | `standard` (Production SaaS / Default) | `full` (Payments / Auth / PII / Regulated) |
|---|---|---|---|
| **Defect Blockers** | `0` open `P0` | `0` open `P0` and `P1` (`P2` needs waiver + deadline) | `0` open `P0`, `P1`, and `P2` |
| **Test & Coverage Bar** | Clean build + Smoke `PASS` (`<= 5m`) + visual screenshots retained | All `minimal` + `100%` PR/integration + `>= 80%` core branch coverage | All `standard` + full regression (`100%` `BUG-NNN`) + MC/DC + mutation core |
| **Reliability (`pass@k` / `pass^k`)** | `1x` fresh clean pass | `pass^3 = 100%` on critical regression paths | `pass^3 = 100%` regression + `pass@3 >= 90%` AI/probabilistic capability |
| **Quarantined Flake Ceiling** | `<= 2%` non-critical | `<= 2%` non-critical (`0%` on Auth/PII/Payments/P0) | `0%` unquarantined; `<= 1%` non-critical with active fix SLA |
| **Security & A11y** | Secret scan clean | Vendor-neutral SAST/secrets/SCA + `axe-core` clean | Full STRIDE/DAST/BOLA + fail-closed `axe-core` + `pa11y` + manual SR/zoom |
| **Rollback & Telemetry** | Revert SHA documented | Rollback-trigger pairing (metric + command + safe migration) | Automated canary abort triggers + verified rollback drill |

### 1.3 Simplest High-Craft Release Gate Strategy & Anti-Overengineering

Do not build multi-team release committees, manual sign-off spreadsheets, or bespoke governance portals when deterministic scripts can verify the same invariants in under ten minutes:
- **Simplest High-Craft Option**: Run one deterministic 6-phase CLI verification script in CI, hash modified artifacts with `sha256sum`, parse JUnit XML for `failures == 0 && tests > 0`, and populate one concise `release-gate-signoff.md`.
- **Anti-Overengineering Self-Question**: *"Is every gate check backed by an automated exit code or verifiable content hash rather than manual copy-paste status theater?"*

---

## 2. Step-by-Step Workflow

1. **Execute the 6-Phase Pre-Release Verification Loop (`verification-loop`)**
   - **Inputs**: Candidate release branch / commit SHA.
   - **Owner**: Release / Feature Engineer.
   - **Tool / Script**: Stack build, typechecker, linter, test runner, security scanner, `git diff`.
   - **Output**: Fresh sequential receipts in strict stop-on-fail order:
     1. **Build**: Compile/bundle (`npm run build` / `python -m build`) — fail immediately on error.
     2. **Typecheck**: `tsc --noEmit` / `pyright` — zero type errors.
     3. **Lint**: `ruff check` / `eslint` — zero lint violations.
     4. **Tests & Coverage**: Run unit, integration, black-box, and E2E suites (`-q --tb=short`), enforcing `tests > 0` and coverage floor.
     5. **Security Baseline**: Secrets (`gitleaks`), SAST (`semgrep`/`bandit`), dependencies (`osv-scanner`/`npm audit`).
     6. **Diff Review**: `git diff --stat main...HEAD` — verify zero leftover debug logs, zero unrequested scope drift, and clean error handling.

2. **Evaluate Capability (`pass@k`) and Regression (`pass^k`) Evals (`eval-harness`)**
   - **Inputs**: Eval dataset (defined pre-implementation in Eval-Driven Development), grader scripts.
   - **Owner**: QA / AI / Feature Engineer.
   - **Tool / Script**: Code-based deterministic graders (primary), Model-based `1–5` rubric graders (only where rules are semantic), Human graders (security/UX craft).
   - **Output**: Distinct reliability metrics (`eval-harness`):
     - **`pass@k`** (*at least 1 success in `k` independent attempts*, e.g., `pass@3 >= 90%`): measures capability discovery on non-deterministic or AI-assisted workflows.
     - **`pass^k`** (*all `k` consecutive trials succeed*, e.g., `pass^3 = 100%`): **mandatory** for deterministic regression, payments, auth, and migration paths so intermittent `1-in-5` flakes never slip past a lucky retry.

3. **Audit Test Evidence Quality & Content-Hash Freshness (`test-evidence-review` + `review-receipts.sh`)**
   - **Inputs**: Test files, screenshots, QA artifacts, recorded SHA-256 receipts.
   - **Owner**: Independent QA Reviewer.
   - **Tool / Script**: Assertion density scanner + `sha256sum` / `git hash-object` receipt checker.
   - **Output**: Two non-negotiable quality audits:
     - **Assertion Density Audit**: Scan every test function. `3+` meaningful assertions = **ADEQUATE**; `1–2` assertions = **ADVISORY** (thin — verify edge cases); **`0` assertions (vacuous pass) = BLOCKING (`FAIL`)**. Verify formula and acceptance-criteria traceability.
     - **Content-Hash Staleness Check**: Never trust filesystem `mtime` (which lies across git checkouts, restores, and CI caches) or `git diff` alone (which misses uncommitted edits). Record `sha256sum` byte hashes of source, schema, and test files when QA evidence is captured. Re-hash at gate sign-off: any `CHANGED`, `GONE`, or `UNRESOLVED` glob marks evidence `POTENTIALLY STALE` and forces `NOT ASSESSED` until re-executed.

   | Content-Hash Receipt Status | Meaning at Gate Evaluation | Required Gate Action |
   |---|---|---|
   | `UNCHANGED` | Current byte hash equals hash recorded during test execution | Evidence remains valid for sign-off |
   | `CHANGED` | File was edited after QA run (even if uncommitted or `mtime` untouched) | Mark `POTENTIALLY STALE` (`NOT ASSESSED`); re-run affected tests |
   | `GONE` / `UNRESOLVED` | Tracked file deleted, renamed, or glob matched zero files | Disqualify stale waiver; verify replacement path and re-run |

4. **Separate Local Verification from Target Environment Acceptance**
   - **Inputs**: CI/local receipts vs staging/canary health checks.
   - **Owner**: Release Manager / SRE.
   - **Tool / Script**: Smoke probe against staging/canary URL + deployment log.
   - **Output**: Two distinct sign-off sections (`verification-loop`): **Local Verification (`READY | NOT READY`)** and **Target Environment Acceptance (`VERIFIED | FAILED | NOT PERFORMED | NOT APPLICABLE` + next permitted step)**. Passing on `localhost` or CI containers NEVER signs off staging or production readiness.

5. **Lock Rollback-Trigger Pairing Before Deployment (`hotfix` / `release-checklist`)**
   - **Inputs**: Production deployment manifest, database migrations, feature flags, SLO alerts.
   - **Owner**: SRE / Release Owner.
   - **Tool / Script**: Expand-and-contract migration audit + canary alert rules.
   - **Output**: Every change row paired with: (a) **Automated Abort Trigger** (numeric metric + window, e.g., `HTTP 5xx > 1.0% for 3m` OR `p95 > 2x baseline for 5m`), (b) **Exact Rollback Action** (feature flag kill-switch, traffic shift, `git revert`/redeploy command), and (c) **Backward-Compatibility Proof** (previous app version still runs cleanly against new DB schema).

6. **Run Pre-Release Condensation & Final Post-Cleanup Verification**
   - **Inputs**: Candidate release branch after all fixes and cleanup.
   - **Owner**: Release Owner.
   - **Tool / Script**: Full 6-phase command re-run.
   - **Output**: Zero temporary debug files, zero undocumented `.skip` tests, zero stale SHA-256 receipts, and **one final passing execution observed after the last edit** (`Iron Law: verification-before-completion`).

---

## 3. Reusable Artifact & Template

Instantiate [Release Gate Sign-Off Template](../templates/release-gate-signoff.md) for every release candidate or high-risk PR in Spiral `3C` and `Q4`.

| Field / Section | Required Content | Verification Rule |
|---|---|---|
| `Header & Overall Verdict` | `Release ID`, `Commit SHA`, `Rigor Tier`, `Verdict` | Must obey `FAIL > CONCERNS > NOT ASSESSED > PASS` |
| `1. 6-Phase Verification Loop` | Build, Typecheck, Lint, Tests, Security, Diff commands + outputs | Stop-on-fail; unrun phase = `NOT ASSESSED` |
| `2. Eval & Assertion Audit` | `pass@k`, `pass^k`, `0`-assertion count, `1–2` thin count | `0`-assertion critical test = `FAIL` |
| `3. Content-Hash Freshness` | Path + capture SHA-256 + sign-off SHA-256 + status | Any `CHANGED` / `GONE` blocks `GO` until re-run |
| `4. Defect, Flake & NFR Bar` | `P0–P3` counts, coverage w/ denominator, quarantine %, a11y, SLO | Meets rigor-tier ceiling (`minimal / standard / full`) |
| `5. Target Env Acceptance` | Separate Local vs Staging vs Prod Canary rows | `LOCAL VERIFIED` never marks `PROD VERIFIED` |
| `6. Rollback-Trigger Pairing` | Change -> Numeric Abort Trigger -> Rollback Command -> Schema safe? | Mandatory for every release and schema migration |
| `7. Waivers & Approver` | Only `CONCERNS` (`P2/P3`) w/ owner & expiration; UTC sign-off | `FAIL` and `NOT ASSESSED` are strictly non-waivable |

---

## 4. Verification Checklist

- [ ] Six-phase pre-release verification loop executed freshly after the final code edit.
- [ ] Critical regression and auth suites satisfy consecutive pass-caret-k stability bar.
- [ ] Assertion density audit confirms zero vacuous zero-assertion tests exist in critical suites.
- [ ] Byte-level SHA-256 content hashes match across source, contracts, and test evidence.
- [ ] Defect counts, coverage denominators, and quarantine rates meet active rigor thresholds.
- [ ] Local CI verification recorded separately from staging and production acceptance.
- [ ] Every deployment change pairs a measurable abort trigger with a backward-safe rollback command.

---

## 5. Hard Quality Gate

Release promotion is governed by strict binary precedence (`FAIL > CONCERNS > NOT ASSESSED > PASS`):

- **PASS (`GO`)**: All 6 verification phases pass freshly after the final edit; `pass^3 = 100%` on critical regression paths; `0` vacuous `0`-assertion tests; `100%` content-hash receipts `UNCHANGED`; `0` open blockers for the declared rigor tier (`P0` always `0`, `P1` `0` for `standard/full`, `P2` `0` for `full`); Target Environment acceptance explicitly recorded; Rollback-Trigger Pairing verified backward-safe.
- **CONCERNS (`CONDITIONAL`)**: Zero `FAIL` or `NOT ASSESSED` conditions, with bounded `P2/P3` findings carrying explicit owner and expiration waivers in `minimal` or `standard` tiers only.
- **NOT ASSESSED (`HOLD`)**: Any required verification phase skipped, `0` tests executed in JUnit XML, or any content-hash receipt marked `CHANGED`, `GONE`, or `UNRESOLVED`.
- **FAIL (`NO-GO`)**: Any build/type/lint/test/security failure, `0`-assertion critical test, unwaived `P0/P1` defect, or missing rollback command on a schema or code deployment.

```bash
# Verify content-hash receipt freshness, zero-failure non-empty JUnit XML, and clean git diff state
sha256sum -c test-results/evidence-receipts.sha256
python3 -c '
import xml.etree.ElementTree as ET
root = ET.parse("test-results/junit.xml").getroot()
suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
tests = sum(int(s.attrib.get("tests", 0)) for s in suites)
fails = sum(int(s.attrib.get("failures", 0)) + int(s.attrib.get("errors", 0)) for s in suites)
assert tests > 0 and fails == 0, f"Gate FAIL: tests={tests}, failures={fails}"
print(f"Gate PASS: {tests} tests verified with 0 failures")
'
git status --short
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Rubber-Stamp Existence Gate** | Counts `test_*.py` files without detecting empty or `0`-assertion vacuous tests | Gate checks only `pytest` exit code `0` without `tests > 0` or assertion audit | Enforce `tests > 0` guard and block any `0`-assertion critical test |
| **Trusting `mtime` / Stale Evidence** | File timestamps reset on clone/rebase while code changed after QA ran | Screenshots or QA reports dated prior to latest `src/` commit SHA | Hash source + test bytes via `sha256sum`; fail on `CHANGED`/`GONE` |
| **Conflating Local Pass with Prod Acceptance** | Staging/prod env vars, migrations, and IAM rules fail despite green `localhost` tests | Sign-off marks `Ready for Prod` with zero staging/canary smoke evidence | Separate Local Verification from Target Environment Acceptance table |
| **One-Way Deploy Without Rollback Trigger** | Leaves on-call guessing when to revert during an outage or breaks old code on DB revert | Release ticket has blank rollback section or destructive `DROP COLUMN` | Require numeric abort trigger + exact revert command + expand-and-contract safety |
| **Coercing `NOT ASSESSED` into `PASS`** | Treats unrun security, soak, or manual SR audits as "advisory passed" | Report says `PASS` while listing `Security: skipped (not configured)` | Enforce strict precedence `FAIL > CONCERNS > NOT ASSESSED > PASS` |
| **Manual Governance Theater** | Multi-hour spreadsheet approval meetings substitute for deterministic CI verification (Anti-Overengineering) | Sign-off checklist manually copied by hand without CLI receipts | Automate the 6-phase CLI loop + SHA-256 receipts into one concise sign-off |
