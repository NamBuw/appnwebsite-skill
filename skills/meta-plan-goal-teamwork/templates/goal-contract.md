# Goal Contract & Evidence Ledger Schema (`goal-evidence-ledger.md`)

> Instantiate this template to produce the runtime artifact `goal-evidence-ledger.md` when `/goal` is active for ambiguous intents, quantitative optimization targets, eval harnesses, or formal acceptance audits.

## Metadata Header

| Field | Value |
|---|---|
| **Goal ID** | `<GOAL-001>` |
| **Target Artifact / System** | `<exact repository, service, route, or UI surface>` |
| **QA Level** | `<minimal \| standard \| full>` |
| **Target Environment** | `<local \| staging \| production>` |
| **Final Verdict** | `<BLOCKED \| NOT ASSESSED \| COMPLETE WITH NOTES \| COMPLETE>` |
| **Target Runtime Artifact** | `goal-evidence-ledger.md` |

---

## 1. 5-Axis Quantitative Goal Contract

| Axis | Contract Specification |
|---|---|
| **Concrete Outcome** | `<observable target state — never pure activity phrasing>` |
| **Verification Command / Method** | `<exact executable CLI command, benchmark script, or browser audit>` |
| **Quantitative or Binary Threshold** | `<exact numeric ceiling/floor, e.g., p95 < 250ms, 0 errors, >= 90% coverage>` |
| **In Scope** | `<exact files, endpoints, routes, or behaviors included>` |
| **Out of Scope** | `<explicit exclusions to prevent scope creep>` |
| **Stop & Ask Trigger** | `<exact condition under which execution halts and requests user ruling>` |

---

## 2. Capability & Regression Eval Matrix (When Iterative / EDD)

| Eval ID | Type | Grader | Target Metric | Measured Result | Status |
|---|---|---|---|---|---|
| `<EVAL-01>` | `<Capability \| Regression>` | `<Code \| Model \| Human>` | `<e.g., pass@3 >= 0.90 \| pass^3 = 1.00>` | `<actual pass rate & sample count>` | `<PASS \| FAIL \| NOT ASSESSED>` |
| `<EVAL-02>` | `<Capability \| Regression>` | `<Code \| Model \| Human>` | `<exact threshold>` | `<actual measurement>` | `<PASS \| FAIL \| NOT ASSESSED>` |

---

## 3. 6-Phase Verification Loop Receipts

Run all applicable phases **after** the final code edit (including any Deletion/Condensation Pass) and record verbatim command outputs:

| Phase | Exact Command Executed | Exit Code | Fresh Timestamp (UTC) | Measured Summary |
|---|---|---:|---|---|
| **1. Build** | `<build command>` | `<0>` | `<YYYY-MM-DDTHH:MM:SSZ>` | `<clean build output>` |
| **2. Types** | `<typecheck command>` | `<0>` | `<YYYY-MM-DDTHH:MM:SSZ>` | `<0 type errors>` |
| **3. Lint** | `<lint command>` | `<0>` | `<YYYY-MM-DDTHH:MM:SSZ>` | `<0 lint violations>` |
| **4. Tests & Coverage** | `<test suite + coverage command>` | `<0>` | `<YYYY-MM-DDTHH:MM:SSZ>` | `<N passed, 0 failed, coverage %>` |
| **5. Security & Log Scan** | `<secret/vuln/debug-log scan command>` | `<0>` | `<YYYY-MM-DDTHH:MM:SSZ>` | `<0 secrets, 0 debug statements>` |
| **6. Diff & Scope Audit** | `git status --porcelain && git diff --stat` | `<0>` | `<YYYY-MM-DDTHH:MM:SSZ>` | `<all touched paths within In Scope>` |

---

## 4. AC-to-Evidence Traceability & Staleness Check

| AC ID | Requirement Summary | Evidence (`file::test` or Retained Artifact Path) | Post-Edit Fresh? | Coverage Status |
|---|---|---|---|---|
| `<AC-1>` | `<requirement description>` | `<tests/test_x.py::test_case_name>` | `<YES \| STALE>` | `<COVERED \| UNTESTED \| DEFERRED>` |
| `<AC-2>` | `<requirement description>` | `<artifacts/screenshot.png or test::case>` | `<YES \| STALE>` | `<COVERED \| UNTESTED \| DEFERRED>` |

- **Staleness Receipt Check**: Last source edit timestamp `<YYYY-MM-DDTHH:MM:SSZ>` <= earliest retained verification receipt `<YYYY-MM-DDTHH:MM:SSZ>` (`<PASS \| RE-CAPTURE REQUIRED>`).

---

## 5. Deviations, Target Acceptance & Final Sign-Off

- **Deviations**:
  - `BLOCKING`: `<none or exact failure blocking completion>`
  - `ADVISORY`: `<none or non-load-bearing minor note>`
  - `OUT OF SCOPE`: `<none or deferred follow-up item>`
- **Target-Environment Acceptance** (never conflate local pass with staging/production pass):
  - Status: `<VERIFIED \| FAILED \| NOT PERFORMED \| NOT APPLICABLE>`
  - Notes: `<exact environment verified or why not performed>`
- **Sign-Off Verdict**: `<BLOCKED \| NOT ASSESSED \| COMPLETE WITH NOTES \| COMPLETE>` — `<1-sentence evidence-backed justification>`
