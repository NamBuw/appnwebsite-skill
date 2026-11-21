# Security Verification Plan — <feature-or-release-name>

- **Plan ID**: `SVP-<NNN>`
- **Spiral ID**: `SP-<NNN>`
- **Linked Threat Model**: `TM-<NNN>`
- **Target Scope**: `<files, services, or PR diff>`
- **Owner**: `<engineer-or-security-owner>`
- **Updated (UTC)**: `<YYYY-MM-DDTHH:MM:SSZ>`

---

## 1. Target Scope & Simplicity Check

- **Risk Elevation Triggers Present**: `<AuthN/AuthZ | PII | Multi-Tenant | Payments | File Uploads | LLM Tools | None>`
- **Simplest High-Craft Control Choice**: `<Native framework escaping, parameterized SQL/ORM, Postgres RLS, __Host- BFF cookies, KMS env injection — zero custom crypto/sanitizers>`
- **Deleted / Simplified Redundant Controls**: `<e.g., Removed duplicate regex validator in controller; enforced single Zod schema + DB RLS>`

---

## 2. AuthN / AuthZ / Input / Session Control Matrix

| Control ID | Domain | Target File & Symbol | Enforced Security Invariant (Last Trusted Decision Point) | Verification Test / Check | Status |
|---|---|---|---|---|---|
| `CTL-01` | AuthN & Session | `<src/auth/session.ts:createSession>` | Opaque CSPRNG token in `__Host-` `HttpOnly` `SameSite=Lax` cookie; zero `localStorage` tokens | `<test_session_cookie_flags>` | `<PASS \| FAIL \| NOT ASSESSED>` |
| `CTL-02` | AuthZ / Tenant | `<src/dal/orders.py:get_order>` | Authenticated principal + `tenant_id` / owner predicate + Postgres RLS enforced | `<test_cross_tenant_idor_403>` | `<PASS \| FAIL \| NOT ASSESSED>` |
| `CTL-03` | Input & SQLi/XSS | `<src/api/users.py:update_bio>` | Strict schema (`extra='forbid'` / Zod), parameterized `%s` SQL, JSX auto-escape / `DOMPurify` | `<test_sqli_xss_rejected>` | `<PASS \| FAIL \| NOT ASSESSED>` |
| `CTL-04` | SSRF / Uploads | `<src/files/upload.ts:handleUpload>` | Magic-byte + extension allowlist, `<= 10MB` cap, UUID name outside webroot, `https:` SSRF blocklist | `<test_upload_ssrf_blocked>` | `<PASS \| FAIL \| NOT ASSESSED>` |

---

## 3. Supply-Chain, Lockfile & Secrets / KMS Gate

| Check Area | Target Artifact / Store | Pinning / Encryption / Rotation Standard | CLI Verification Evidence | Status |
|---|---|---|---|---|
| **Lockfile & CVEs** | `<package-lock.json / poetry.lock>` | Exact pinned versions; `0` reachable `Critical/High` CVEs; `>= 7d` cooldown on new deps | `osv-scanner` / `trivy` / `npm audit` / `pip-audit` | `<PASS \| FAIL \| NOT ASSESSED>` |
| **Secrets & KMS** | `<Env + AWS/GCP Secrets Manager>` | Multi-tier `Env -> KMS -> Fail-Closed Prod`; zero literal fallback strings; `90d` rotation SLA | `gitleaks detect --source . --redact` | `<PASS \| FAIL \| NOT ASSESSED>` |
| **CI Workflows** | `<.github/workflows/*.yml>` | 40-hex commit SHA `uses:`; untrusted `github.event.*` passed via `env:` only; minimal `permissions:` | `check_security_baseline.py` | `<PASS \| FAIL \| NOT ASSESSED>` |
| **SBOM & Provenance** | `<dist/sbom.cdx.json>` | Signed CycloneDX/SPDX SBOM; promotion by immutable `sha256` digest | `trivy fs --format cyclonedx` / attestation | `<PASS \| FAIL \| NOT ASSESSED>` |

---

## 4. Automated CLI & Regression Commands

Run offline / in CI after the final edit (`verification-before-completion`):

```bash
python3 skills/security-engineering/scripts/check_security_baseline.py --path . --json
semgrep scan --config auto --error .
bandit -r src/ -ll
osv-scanner scan --lockfile=package-lock.json
gitleaks detect --source . --redact --exit-code 1
```

---

## 5. Security Waivers (`SW-NNN`)

*(Never leave bare unresolved security debt. Any temporary exception MUST carry an owner, compensating control, and expiry date.)*

| Waiver ID | Control / Rule | Affected File:Line | Compensating Control | Approver & Owner | Expiry (UTC) |
|---|---|---|---|---|---|
| `SW-001` | `<rule-or-cve-id>` | `<path:line>` | `<network ACL / feature flag / WAF rule>` | `<@owner / @sec-lead>` | `<YYYY-MM-DD>` |

---

## 6. Sign-Off Criteria (`PASS` / `FAIL`)

- **Gate Verdict**: `<PASS | FAIL | NOT ASSESSED>`
- **PASS Criteria**: `0` `High/Critical` findings from `check_security_baseline.py`, `semgrep`, `bandit`, `osv-scanner`, and `gitleaks`; all AuthN/AuthZ/IDOR regression tests pass freshly; zero unapproved waivers.
- **FAIL Criteria**: Any unmitigated injection/XSS/SSRF/auth-bypass/secret leak, missing lockfile, mutable CI action ref without SHA, or stale check captured before final edit.
