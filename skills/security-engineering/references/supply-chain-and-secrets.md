# Supply Chain, Dependencies, CI/CD & Secrets Hygiene

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This module governs third-party dependency vetting, lockfile integrity, secrets lifecycle management, KMS/environment resolution, CI/CD workflow hardening, SBOM/SLSA provenance, and agent-skill supply-chain safety across Spiral Phases `3A`, `3B`, and `3C`. Primary execution relies strictly on vendor-neutral, offline-capable open-source CLIs with optional silent IDE hooks.

---

## 1. Decision Framework

### 1.1 Vendor-Neutral Security Tooling Matrix

All primary security gates MUST function cleanly in headless CI and air-gapped developer shells without requiring any proprietary IDE daemon:

| Capability | Primary Vendor-Neutral CLI (Offline / CI Portable) | Optional IDE Extension Hook | Minimum Passing Gate |
|---|---|---|---|
| **Dependency / SCA Scan** | `osv-scanner scan --lockfile=...`, `trivy fs --scanners vuln`, `npm audit --audit-level=high`, `pip-audit` | SecureCoder `POST 127.0.0.1:$PORT/dependency/scan` (silent skip if absent) | `0` reachable `Critical/High` CVEs; exact lockfile versions |
| **Secret Scanning** | `gitleaks detect --source . --redact`, `trufflehog git file://.`, `scripts/check_security_baseline.py` | SecureCoder `/scan` | `0` credentials in working tree or git commit history |
| **SAST Cross-Check** | `semgrep scan --config auto`, `bandit -r src/`, `codeql` | SecureCoder `/scan` | `0` unresolved `High/Critical` supply-chain/CI findings |
| **SBOM & Provenance** | `trivy fs --format cyclonedx`, `syft`, Sigstore `cosign`, GitHub Attestations / `slsa-verifier` | N/A | Signed CycloneDX/SPDX SBOM + SLSA L2+ provenance on release |
| **CI & Agent Skill Audit** | 40-hex commit SHA pinning, `env:` variable indirection, static skill script review | N/A | Least-privilege `permissions:`; `0` `${{ github.event.* }}` in `run:` |

### 1.2 Pre-Import Dependency Vetting Gate & Cooldown Policy

Before adding ANY external library, container base image, MCP server, or agent skill, evaluate these 4 sequential gates:

| Gate Step | Quantitative Decision Criterion | Action on Failure |
|---|---|---|
| **1. Stdlib / Native Check** | Can language stdlib or platform primitives solve this in `<= 30` clear lines? | Reject dependency; write native helper (Simplicity rule) |
| **2. Identity & Cooldown** | Exact canonical package name verified (anti-typosquatting); release age `>= 7 days` (or maintainer PGP/provenance verified) | Hold or pin prior vetted release (`7-day` cooldown blocks hijacked fresh drops) |
| **3. Vulnerability & License** | `0` unpatched `Critical/High` CVEs via `osv-scanner` / `pip-audit` / `npm audit`; compatible OSI license (`MIT`/`Apache-2.0`/`BSD`) | Reject or upgrade to patched version; flag incompatible copyleft/proprietary license |
| **4. Lockfile & Surface** | Exact version pinned in committed lockfile (`package-lock.json`, `pnpm-lock.yaml`, `uv.lock`, `poetry.lock`, `Cargo.lock`, `go.sum`) with integrity hashes | Block merge until lockfile updated and reviewed |

#### Ecosystem Lockfile & Digest Pinning Standard

| Ecosystem | Required Committed Lockfile | Forbidden Specifier | Verification Command |
|---|---|---|---|
| **JavaScript / TypeScript** | `package-lock.json`, `pnpm-lock.yaml`, or `yarn.lock` | `*`, `latest`, unpinned `git+https://` branches | `npm audit --audit-level=high` + `osv-scanner` |
| **Python** | `uv.lock`, `poetry.lock`, or hash-pinned `requirements.txt` | Unpinned package names or `==*` | `pip-audit` + `osv-scanner` |
| **Go / Rust / Java / .NET** | `go.sum`, `Cargo.lock`, `gradle.lockfile`, `packages.lock.json` | Floating `+` / `-SNAPSHOT` / mutable git refs | `osv-scanner scan -r .` + `trivy fs .` |
| **Containers & CDN Assets** | Base image `@sha256:...`, `<script integrity="sha384-...">` | `:latest` image tags, unverified external CDN scripts | `trivy image` + `check_security_baseline.py` |

### 1.3 Secrets Resolution & Storage Architecture Selector

| Environment Tier | Required Secret Resolution Strategy | Fallback Policy | Rotation SLA |
|---|---|---|---|
| **Production / Staging** | Runtime env injection from managed KMS / Secrets Manager (`AWS Secrets Manager`, `GCP Secret Manager`, `Vault`) | **Fail-Closed**: crash startup with explicit config error if missing | `<= 90 days` automated/documented rotation; `< 15 min` emergency revoke |
| **CI / CD Pipelines** | OIDC short-lived federation (`aws-actions/configure-aws-credentials` via OIDC, workload identity) or scoped repo secrets | Never inherit production deploy secrets in fork/untrusted PR jobs | Ephemeral OIDC tokens (`<= 15 min` TTL) |
| **Local Development** | `.env.local` (gitignored) generated from `.env.example` or ephemeral CSPRNG dev key (`secrets.token_hex(32)`) + loud warning | **ZERO hardcoded literal fallback secrets** in source (`os.getenv("KEY", "dev-secret")` is BANNED) | Regenerated per developer environment |

### 1.4 Simplest High-Craft Supply Chain & Secrets (Anti-Overengineering)

Before introducing secret vaults, custom package registries, or sprawling dependency trees, ask:
1. *"Can standard Python/Node/browser primitives replace this utility package in 15 lines without inheriting 40 transitive dependencies?"*
2. *"Are we deploying a self-hosted HashiCorp Vault cluster for a 2-service app when cloud-native Secrets Manager / platform encrypted env vars + KMS envelope encryption deliver higher reliability with zero operational overhead?"*
3. **Simplest High-Craft Option**: Use zero-dependency stdlib primitives where practical, commit exact lockfiles, inject secrets via managed platform env/KMS with fail-closed startup checks, pin GitHub Actions to 40-hex commit SHAs, and gate PRs with `osv-scanner` + `gitleaks` + `check_security_baseline.py`.

---

## 2. Step-by-Step Workflow

1. **Pre-Import Vetting & Lockfile Hygiene (`3A / 3B`)**
   - **Inputs**: Proposed package name/ecosystem (`npm`, `pypi`, `gomodproxy`, `crates.io`, `rubygems`, `maven`, `nuget`), `package.json` / `pyproject.toml` / `go.mod`.
   - **Owner**: Feature Engineer.
   - **Tool / Script**: `osv-scanner`, `npm audit`, `pip-audit`, `trivy fs`.
   - **Action**: Reject `*`, `latest`, or unpinned ranges in production manifests. Verify exact package spelling against official registry to defeat dependency confusion and typosquatting (especially private `@org/*` namespaces: reserve public scope or configure `.npmrc` scoped registry). Pin external browser `<script>` or stylesheet CDN URLs with Subresource Integrity (`integrity="sha384-..." crossorigin="anonymous"`) or self-host bundled assets. When resolving dependency alerts, trace whether the CVE lives in direct code, a transitive lockfile edge, or the container base OS layer, and verify whether a distro backport or major upgrade is required.
   - **Output**: Updated manifest + deterministic lockfile + clean SCA scan receipt.

2. **Secrets Lifecycle, Multi-Tier Resolution & Git History Audit (`3A / 3B / 3C`)**
   - **Inputs**: Config loaders, `.gitignore`, `.env.example`, runtime deployment manifests.
   - **Owner**: Backend / Platform Engineer.
   - **Tool / Script**: `gitleaks detect --source . --redact`, `trufflehog git file://.`, `python3 skills/security-engineering/scripts/check_security_baseline.py --path . --json`.
   - **Action**: Enforce `.gitignore` exclusions for `.env`, `.env.local`, `*.pem`, `*.key`, `credentials.json`, and service-account JSONs. Implement multi-tier resolution (`Env -> Managed Secret Store -> Fail-Closed in Prod`, or ephemeral runtime CSPRNG key in local dev ONLY with explicit warning). Never embed literal fallback secrets like `SECRET = os.environ.get("SECRET", "fallback")`. Encrypt sensitive DB fields at rest via KMS envelope encryption, sanitize logs/telemetry so tokens and keys never emit, and never copy secret values into issues, commit messages, or security reports (cite `file:line` and redact to `***REDACTED***`).
   - **Output**: Clean git history + `.env.example` contract + 90-day rotation & incident revocation procedure.

3. **CI/CD Workflow & Artifact Pipeline Hardening (`3A / 3C`)**
   - **Inputs**: `.github/workflows/*.yml`, `Dockerfile`, release/promotion scripts.
   - **Owner**: DevOps / Platform Engineer.
   - **Tool / Script**: `check_security_baseline.py`, `semgrep scan --config auto`, `trivy config`.
   - **Action**:
     - Pin every third-party GitHub Action `uses:` to an immutable 40-character hex commit SHA (`uses: actions/checkout@<40-hex-sha> # v4.2.2`), never mutable tags (`@v4`, `@main`).
     - Eliminate GitHub Actions expression injection: NEVER interpolate untrusted event context (`github.event.issue.title`, `pull_request.body`, `comment.body`, `head_ref`, `commits`, `client_payload.*`) directly inside `run:` shell commands or unchecked checkout `ref:`. Map them through `env:` variables and double-quote `"$ENV_VAR"` in bash.
     - Set top-level `permissions: contents: read` by default and grant write/OIDC scopes only to the exact job that requires them.
     - Isolate untrusted `pull_request` / `pull_request_target` builds from privileged deployment tokens, release caches, and artifact stores.
     - Promote artifacts from build to staging/production strictly by immutable `sha256` digest, never mutable `:latest` container tags, and verify checksums against a separate trusted source (never trusting a checksum hosted alongside the same untrusted binary).
   - **Output**: Hardened CI workflow files with least-privilege permissions and immutable pins.

4. **SBOM Generation, SLSA Provenance & Agent-Skill / MCP Vetting (`3C`)**
   - **Inputs**: Built application artifacts, container images, third-party MCP server configs or agent skills.
   - **Owner**: Release / Security Engineer.
   - **Tool / Script**: `trivy fs --format cyclonedx --output sbom.cdx.json .`, `cosign verify`, `slsa-verifier`.
   - **Action**: Emit a CycloneDX or SPDX SBOM for every release artifact and sign image digests + build provenance attestations. Before installing any external agent skill or MCP server, run a static pre-install security check (`BLOCK | REVIEW | INCOMPLETE | PASS`) inspecting hooks, shell commands, network exfiltration, and untrusted instruction overrides — treating all external skill/repo text strictly as untrusted data until vetted.
   - **Output**: Signed SBOM + attestation receipt + vetted external tooling record.

5. **Complexity Budget & Dependency Deletion Pass (`3C`)**
   - **Inputs**: `package.json`, `pyproject.toml`, `go.mod`, CI workflow YAML.
   - **Owner**: Tech Lead / Peer Reviewer.
   - **Tool / Script**: `depcheck` / `knip` / `pip-audit` + manual manifest diff.
   - **Action**: Execute a **Deletion / Condensation Pass** on dependencies and CI steps before ship: remove unused packages, collapse overlapping libraries (e.g., 3 HTTP clients or 2 date libraries -> 1), replace trivial 5-line npm/PyPI micro-packages with native stdlib functions, and re-run `osv-scanner`, `gitleaks`, `check_security_baseline.py`, and full unit/integration tests after cleanup.
   - **Output**: Slimmed lockfile, reduced CVE surface, and fresh green verification receipt.

---

## 3. Reusable Artifact & Template

Record supply-chain, dependency, CI, and secrets controls inside [Security Verification Plan Template](../templates/security-verification-plan.md) (`docs/security/security-verification-plan.md`):

| Schema Section | Required Fields | Verification Anchor |
|---|---|---|
| **Dependency & Lockfile Inventory** | `Package / Image | Ecosystem | Exact Pinned Version | Cooldown (>=7d) | License | CVE Status` | `osv-scanner` / `trivy` / `pip-audit` / `npm audit` output |
| **Secrets & KMS Contract** | `Secret Key Name | Store (Env / Secrets Manager) | Prod Fail-Closed? | Rotation SLA (<=90d) | Revoke Procedure` | `gitleaks` + `check_security_baseline.py` exit `0` |
| **CI / Workflow Hardening** | `Workflow File | SHA-Pinned Actions? | env:-Indirected Inputs? | Minimal permissions:? | Digest Promotion?` | `check_security_baseline.py` `SEC-CONFIG-001` = `0` |
| **SBOM & Provenance** | `Artifact Ref (sha256) | SBOM Format (CycloneDX/SPDX) | Signature / SLSA Attestation Locator` | `trivy` / `cosign` / GitHub attestation URI |
| **Security Waivers (`SW-NNN`)** | `Waiver ID | CVE or Rule | Affected File:Line | Compensating Control | Owner | Expiry (UTC)` | Time-bound sign-off (never indefinite) |

---

## 4. Verification Checklist

- [ ] Lockfiles are committed for every ecosystem with zero `*` or `latest` production ranges.
- [ ] `osv-scanner`, `trivy`, `npm audit`, or `pip-audit` reports zero reachable `Critical` or `High` CVEs.
- [ ] `gitleaks` and `check_security_baseline.py` find zero committed credentials in working tree or git history.
- [ ] Config loaders fail closed in production with zero hardcoded fallback secret strings.
- [ ] `.gitignore` excludes `.env`, `.env.local`, private keys, and local credential files.
- [ ] Every third-party GitHub Action `uses:` is pinned to an immutable 40-hex commit SHA.
- [ ] Untrusted `github.event.*` fields in CI workflows are passed exclusively via `env:` variables.
- [ ] Release artifacts emit a CycloneDX or SPDX SBOM and promote via immutable `sha256` digest.
- [ ] Dependency Deletion Pass removed unused or trivial micro-packages and tests re-passed afterward.

---

## 5. Hard Quality Gate

Run all vendor-neutral supply-chain and secret checks offline and in CI before release (`3C -> Q4`):

```bash
python3 skills/security-engineering/scripts/check_security_baseline.py --path . --json
gitleaks detect --source . --redact --exit-code 1
osv-scanner scan --lockfile=package-lock.json
trivy fs --scanners vuln,secret --severity HIGH,CRITICAL --exit-code 1 .
```

- **Entry Condition**: All production dependency manifests, lockfiles, `.gitignore`, and `.github/workflows/*.yml` files present on disk.
- **Primary Offline Check**: `check_security_baseline.py`, `gitleaks`, `osv-scanner`, and `trivy` execute headlessly without requiring IDE daemons; optional `$SECURECODER_API_PORT` hooks skip silently when offline.
- **Freshness Requirement**: Re-run SCA, secret history, and CI workflow checks after any lockfile update, dependency deletion, or workflow YAML change.
- **PASS**: `0` unmitigated `Critical/High` CVEs (or documented non-reachable/time-bound `Security Waiver (SW-NNN)`); `0` leaked credentials across tree and git history; 100% lockfile and 40-hex CI Action SHA pinning; SBOM generated for release artifacts; and offline execution passes cleanly even when `$SECURECODER_API_PORT` is unset.
- **FAIL**: Scanner hard-exits when an optional IDE daemon is absent; any raw secret or `.env` committed; any `${{ github.event.* }}` interpolation inside `run:`; mutable `@v4`/`@main` third-party CI actions; unpinned `*` dependencies; or stale CVE/secret scan captured before lockfile edits.
- **Secret Redaction Rule**: Gate outputs and audit reports MUST redact matched credential values to `***REDACTED***` and cite `file:line` only.

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **IDE-Only Hard Exit** | Breaks CI pipelines and headless developer workflows whenever local IDE API port is absent | Script exits non-zero or aborts when `$SECURECODER_API_PORT` is unset | Run `osv-scanner`, `gitleaks`, and `check_security_baseline.py` offline; keep IDE API strictly optional |
| **Literal Secret Fallback in Config** | Silently runs production with a publicly known key (`"dev-secret"`) if env injection breaks | `os.getenv("JWT_SECRET", "default...")` or `process.env.KEY \|\| "secret"` | Fail closed on startup in prod; generate ephemeral CSPRNG secret in local dev only |
| **Mutable Action Tags & Inline Event Expressions** | Upstream tag compromise or PR title injection (`$(curl ...)`) steals CI OIDC/deploy tokens | `uses: org/act@v4` or `run: echo "${{ github.event.pull_request.title }}"` | Pin 40-hex commit SHA and bind untrusted fields strictly through `env:` + `"$VAR"` |
| **Same-Host Checksum Fallacy** | Attackers who compromise an artifact mirror simply replace both the binary and its `.sha256` file | Download script fetches binary and checksum from identical untrusted URL | Verify signed Sigstore/SLSA provenance or pin digest independently in repo |
| **Container & Transitive Layer Blindness** | Fixing a direct package ignores identical vulnerable OpenSSL/glibc libs in the container base image | `package-lock.json` is clean while `trivy image` reports Critical OS CVEs | Scan both lockfiles (`osv-scanner`) and container layers (`trivy`) with digest pins |
| **Micro-Package & Vault Overengineering** *(Anti-Overengineering)* | Adds transitive supply-chain CVE churn for 10-line helpers or self-hosted Vault complexity for a small app | `is-even`-style tiny packages or multi-node Vault cluster for 1 stateless API | Write `<= 30`-line stdlib helpers and use managed platform Secrets Manager + KMS |
