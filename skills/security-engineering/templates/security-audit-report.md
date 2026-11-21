# Security Audit & Verification Report — <project-or-release>

- **Audit ID**: `SAR-<NNN>`
- **Target Ref / Commit**: `<git-sha>`
- **Audit Mode**: `<Static SAST + Baseline | Diff Review | Loopback DAST + IDOR | Full 3-Lens Audit>`
- **Overall Verdict**: `<PASS | CONCERNS | NOT ASSESSED | FAIL>`
- **Generated (UTC)**: `<YYYY-MM-DDTHH:MM:SSZ>`

---

## 1. Executive Summary & Coverage Disclosure

| Severity | Confirmed (`Open`) | Confirmed (`Fixed`) | `Needs Validation` (No Severity) | `Rejected / False Positive` |
|---|---|---|---|---|
| **Critical** | `<0>` | `<0>` | N/A | N/A |
| **High** | `<0>` | `<0>` | N/A | N/A |
| **Medium** | `<0>` | `<0>` | N/A | N/A |
| **Low** | `<0>` | `<0>` | N/A | N/A |
| **Total** | `<0>` | `<0>` | `<0>` | `<0>` |

- **Tools Executed (Vendor-Neutral Primary Path)**:
  - `check_security_baseline.py`: `<exit code, files scanned, findings count>`
  - `semgrep` / `bandit` / `codeql`: `<commands run and exit status>`
  - `osv-scanner` / `trivy` / `gitleaks`: `<commands run and exit status>`
  - `owasp-zap` / `nuclei` / Loopback IDOR suite: `<target 127.0.0.1 URL or NOT PERFORMED>`
- **Explicit Coverage Disclosure & Skipped Areas**:
  - **Scanned Scope**: `<src/, api/, web/, .github/workflows/>`
  - **Skipped / Unscanned Components**: `<e.g., native binary C++ addon, external IdP tenant configuration — explain why>`
  - **Secret Redaction Guarantee**: Raw credential values are redacted to `***REDACTED***`; only `file:line` references appear below.

---

## 2. Confirmed Vulnerabilities (`CS-<CLASS>-<NNN>`)

*(Include ONLY findings backed by a complete 7-element Assessment Tuple: `source -> control -> sink -> reachable path -> boundary -> counterevidence -> proof gaps` and bounded source/local proof.)*

### `CS-<CLASS>-001`: <Concise Vulnerability Title>

- **CWE / Class**: `<CWE-NNN / e.g. SQL Injection | BOLA/IDOR | XSS | SSRF>`
- **Severity**: `<Critical | High | Medium | Low>`
- **Confidence**: `<High | Medium>`
- **Status**: `<Fixed | Open | Accepted Risk>`
- **Location**: `<path/to/file.ext:line>`
- **Assessment Tuple**:
  - **Source**: `<untrusted actor + input vector>`
  - **Control Gap**: `<missing or bypassed check at boundary>`
  - **Sink / Impact**: `<exact dangerous operation + concrete compromise>`
  - **Counterevidence Checked**: `<upstream sanitization or middleware checked>`
- **Smallest Effective Fix (Last Trusted Decision Point)**: `<exact symbol/boundary patch applied or recommended>`
- **Regression Test Added**: `<path/to/test_file.py::test_name>`

---

## 3. Needs Validation Leads (Unresolved Infra / Runtime Blockers — No Severity Assigned)

*(Never assign speculative severity to leads blocked by unobserved deployment, WAF, IdP, or proxy behavior.)*

| Lead ID | Location (`file:line`) | Candidate Path Hypothesis | Exact Unobserved Blocker | Non-Destructive `validation_plan` (`local` / `deployment`) |
|---|---|---|---|---|
| `NV-001` | `<src/proxy.ts:24>` | `<Forwarded header trust>` | `<Upstream ALB header-stripping config not in repo>` | `<Local curl to 127.0.0.1 or read ALB listener rule>` |

---

## 4. PoC Verification & Patch Verification Triad Receipts

*(Every fix MUST pass both an exploit trace / regression test and the 3-claim Patch Verification Triad.)*

| Finding ID | Attack Class | Exploit Trace / Loopback Test (`127.0.0.1` Dummy Principals) | PoC Outcome (`Fix verified \| Fix incomplete`) | Patch Triad (`targeted / no_new_vuln / behaviour_unchanged`) | Fresh Post-Fix Command & Exit Code |
|---|---|---|---|---|---|
| `CS-<CLASS>-001` | `<SQLi \| XSS \| Path \| SSRF \| IDOR>` | `<payload rejected 403/400; TenantA cannot read TenantB>` | `<Fix verified>` | `<CONFIDENT / CONFIDENT / CONFIDENT>` | `pytest -q tests/sec_test.py -> exit 0` |

---

## 5. Suppressed, Rejected Findings & Security Waivers

| ID / Fingerprint | Disposition (`Rejected \| False Positive \| Suppressed \| Accepted Risk`) | Location (`file:line`) | Counterevidence / Compensating Control | Waiver Expiry (`SW-NNN` or `N/A`) |
|---|---|---|---|---|
| `<FP-001>` | `<Rejected>` | `<path:line>` | `<Parameterized driver / central router Depends() blocks reachability>` | `N/A` |
