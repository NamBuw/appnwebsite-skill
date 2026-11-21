# CI/CD Pipelines, Artifact Provenance & Release Engineering

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

Release engineering guarantees that every artifact promoted to production is:
1. **Built once** and cryptographically verifiable (`SBOM` + keyless OIDC provenance).
2. **Backward-compatible** with live database state via expand-before-deploy migrations.
3. **Progressively exposed** and **instantly reversible** within seconds or minutes.

This module governs CI/CD skeletons in Spiral **3A**, release-gate condensation in **3C**, and progressive production promotion in **Q4**.

---

## 1. Decision Framework

### 1.1 Simplest High-Craft CI/CD Option & Anti-Overengineering Gate

Apply **Least Code, Highest Craft** before authoring multi-stage GitOps or custom deployment controllers:

- **Option A (Default Simplest High-Craft)**:
  - Single clean CI/CD workflow (GitHub Actions or CircleCI) running fast parallel lint/typecheck/unit checks.
  - **Build once** (`--standalone` prebuilt bundle or immutable OCI digest) + run SAST/SCA/SBOM scan.
  - Auto-deploy protected preview/staging + run smoke verification.
  - Promote to production via a single human approval gate (`Blue-Green` `promote` or `Canary` `10% -> 50% -> 100%`).
  - Zero custom deployment bots, zero multi-repo GitOps sync loops, zero environment-specific rebuilds.
- **Earned Evidence Required for Option B (Multi-Cluster GitOps / Service Mesh Canary)**:
  - Only adopt ArgoCD/Flux, Istio weighted meshes, or multi-stage Jenkins pipelines when verified `NFR` constraints fail on Option A:
    - Multi-cluster Kubernetes fleets serving `>= 5` independent production services.
    - Air-gapped compliance targets requiring pull-based cluster reconciliation.

### 1.2 Deployment Strategy Selection Matrix

| Strategy | Traffic Control Mechanism | Blast Radius | Rollback Latency | DB Schema Requirement | Best Fit |
|---|---|---|---|---|---|
| **Rolling** | Platform sequentially replaces old instances (`0–100%`) | Medium (`1` batch at a time) | `1–5 min` (re-roll prior image) | Strictly backward-compatible `expand` before rollout | Standard stateless APIs & worker containers |
| **Blue-Green** | Deploy idle target (`vercel --prod --skip-domain`), smoke via `vercel curl`, flip router (`vercel promote`) | Zero until switch; instant `100%` swap | **`< 10s`** (`vercel rollback` / alias flip) | Dual-active compatibility between `N-1` and `N` | Web apps, Next.js/SSR services, low-downtime cutovers |
| **Canary / Rolling Release** | Weighted traffic stages (`vercel rr configure --stage=10,5m --stage=50,10m --stage=100,0`) or ingress weights | Low (`5%–10%` cohort first) | **`< 30s`** (shift weight back to `0%`) | Expand-only forward compatibility | High-traffic APIs, payment/checkout flows |
| **Feature-Flag Progressive** | Decouple **deploy** from **release** via runtime flags (`internal -> 5% -> 25% -> 100%` in PostHog/flags) | Minimal (user/cohort scoped) | **`< 5s`** (kill switch without redeploy) | Flag-guarded dual read/write paths | High-risk UX launches, A/B experiments, kill switches |

### 1.3 Automated Rollback & CI Cache Quantitative Thresholds

- **Mandatory Automated Rollback Triggers**:
  - Server `5xx` error rate exceeds **`2x` baseline** or **`> 1.0%`** sustained for `3–5 min`.
  - Route `p95` latency exceeds **`1.5x` baseline** sustained for `5 min`.
  - Synthetic `/healthz` (`0.0.0.0:$PORT`) or critical-path E2E smoke probe fails **`>= 2` consecutive checks**.
  - Multi-window burn-rate alert (`14.4x` `5m/1h` or `6.0x` `30m/6h`) fires within `30 min` post-release.
- **CircleCI / GHA Cache ROI & Persistence Rules**:
  - Target cache ROI of **`10–20x`** restored bytes over saved bytes.
  - Key caches on lockfile checksum plus manual version prefix (`v1-npm-{{ checksum "package-lock.json" }}`), NEVER `{{ epoch }}` or commit SHA (write-only waste).
  - Cache package-manager download stores (`~/.npm`, `~/.cache/pip`) rather than `node_modules` when running `npm ci`.
  - Enforce the 3-way persistence boundary: **Cache** = cross-run dependency speedup; **Workspace** = narrow in-workflow artifact handoff (`build -> deploy`, never concurrent jobs writing the same path); **Artifact** = post-run audit inspection (SBOM, JUnit XML, coverage).

---

## 2. Step-by-Step Workflow

- **Inputs**: `architecture.md`, `migration-plan.md`, `release-qa-verdict.md`, `security-audit-report.md`.
- **Outputs**: Signed CI/CD workflow YAML, immutable artifact digest + SBOM, `release-checklist.md`.
- **Owners**: Release Engineer / CI Owner (pipeline & promotion) and Tech Lead (approval & DB safety).
- **Primary Tools**: `gh`, `circleci`, `vercel`, `render`, `trivy`, `syft`, `cosign`, `git`.

1. **Enforce CI Hygiene, Pinning, Caching & Test Splitting (Owner: CI Owner)**:
   - Pin third-party GitHub Actions to full 40-char commit SHAs and CircleCI orbs to immutable semantic versions.
   - Enable auto-cancellation of redundant branch runs on new pushes.
   - Output JUnit XML with explicit `file` and `classname` attributes (`store_test_results`).
   - Enable `circleci tests run --split-by=timings` only after baseline timing data exists, creating output directories beforehand so `0`-test nodes never crash `store_test_results`.

2. **Build Once & Generate Signed Provenance + SBOM (Owner: CI Owner)**:
   - Compile a single immutable artifact in CI: container image pushed by `@sha256:...` digest, or split Vercel build (`vercel pull --yes --environment=production` -> `vercel build --prod --standalone` -> upload `.vercel/output`).
   - Always pass `--standalone` when transferring `.vercel/output` across CI jobs; omitting it breaks prebuilt deploys.
   - Generate an SPDX/CycloneDX SBOM (`trivy` / `syft`) and sign the artifact via keyless OIDC (`cosign sign` + SLSA provenance).
   - Authenticate to cloud providers via short-lived **OIDC federation** rather than long-lived static keys.

3. **Run Security, Supply-Chain & Secrets Gates Without Token Leaks (Owner: Security / CI)**:
   - Block promotion if `release-qa-verdict.md` or `security-audit-report.md` reports unresolved `P0/P1` issues.
   - Run `trivy fs --scanners vuln,secret` to block Critical/High CVEs or leaked credentials.
   - Pass provider tokens (`VERCEL_TOKEN`, `CLOUDFLARE_API_TOKEN`, `SENTRY_AUTH_TOKEN`, `RENDER_API_KEY`) strictly via environment variables or restricted CI contexts — NEVER via CLI `--token` flags that leak in `ps` process listings.
   - Exclude `.env*`, `.git`, and `node_modules` from direct PaaS upload bundles.

4. **Execute Expand-and-Contract DB Migrations Safely (Owner: Backend + Tech Lead)**:
   - **Expand (Pre-Deploy)**: Run additive migrations (`ADD COLUMN ... NULL`, new tables, backfill jobs) **before** deploying new application code so `N-1` instances continue serving traffic cleanly.
   - **Deploy & Bake**: Roll out code reading/writing both shapes; verify idempotent backfill completion.
   - **Contract (Later Release Only)**: Drop obsolete columns or constraints only after `100%` of old instances drain and the `48h–72h` bake window passes with zero rollback risk.

5. **Deploy Protected Preview / Staging & Probe Binding (Owner: Release Engineer)**:
   - Default all branch/PR pushes to preview/staging deployments (`--prod` is explicit-only).
   - Verify protected Vercel preview endpoints using `vercel curl /healthz --deployment "$PREVIEW_URL"` — NEVER disable Vercel Deployment Protection.
   - On container PaaS targets (Render/Fly/Cloud Run), run the 4-step post-deploy check: instance status `live`, server binds `0.0.0.0:$PORT`, `/healthz` returns `HTTP 200`, and container logs show `0` startup crashes.
   - Validate IaC manifests (`render blueprints validate`) with secrets marked `sync: false`.

6. **Promote Production via Approval Gate & Progressive Delivery (Owner: Tech Lead + SRE)**:
   - Require an explicit human `type: approval` or environment protection gate directly before production promotion, bound to a restricted production context.
   - **CircleCI Tag-Filter Trap**: Declare matching `filters: tags:` on **BOTH** the production deploy job AND every upstream `requires:` job in the workflow DAG, or CircleCI skips the entire tag pipeline.
   - Execute Blue-Green (`vercel --prod --skip-domain` -> `vercel curl` -> `vercel promote`), Rolling Release (`vercel rr start` -> `vercel rr status`), or PostHog feature-flag rollout (always read-first audit targeting rules and confirm explicitly before toggling production flags or ending experiments).

7. **Observe Post-Deploy Window, Triage Failures & Drill Rollback (Owner: SRE)**:
   - Hold a `60s–15m` active observation window after cutover (`vercel logs`, `vercel metrics`, Sentry new-issue delta).
   - If thresholds in Section 1.3 breach, execute instant rollback (`vercel rollback`, flag kill switch, or `vercel rr abort`) immediately.
   - Use `vercel bisect --good <url> --bad <url> --run ./smoke.sh` offline/in staging to pinpoint regression commits.
   - Classify every CI failure strictly as **Transient** (network timeout, registry 503, runner OOM) vs. **Deterministic** (test assertion, lint, type error, lockfile drift) before retrying — never mask deterministic bugs with blanket retries.

8. **Pipeline Complexity Budget & Deletion/Condensation Pass (Owner: CI Owner)**:
   - Audit `.github/workflows/` or `.circleci/config.yml` quarterly and before Q4 sign-off.
   - Delete unused `save_cache` / `restore_cache` / `persist_to_workspace` steps, redundant branch-vs-PR triggers, and expired feature flags post-100% rollout.
   - Re-validate CI config (`circleci config validate` / `gh pr checks`) after deletions.

---

## 3. Reusable Artifact & Template

Use [Release Checklist Template](../templates/release-checklist.md) Sections `1–5` for every staging/production release (`Section 6` covers Documentation & Changelog sign-off).

| Template Section | Required Fields | Validation & Completeness Rule |
|---|---|---|
| **Header & Verdict** | `version_tag`, `commit_sha`, `artifact_digest`, `strategy`, `target_env`, `owner`, `verified_utc`, `verdict` | Artifact digest MUST match tested staging build; verdict uses `FAIL > CONCERNS > NOT ASSESSED > PASS` |
| **1. Pre-Flight Gates** | `ci_status`, `single_build_digest`, `sbom_signature`, `expand_only_migration`, `qa_security_inputs`, `kill_switch` | Every row records concrete denominator/result and explicit `PASS \| CONCERNS \| NOT ASSESSED \| FAIL` |
| **2. Rollout Schedule** | `stage_pct`, `hold_duration`, `max_5xx`, `max_p95`, `burn_rate_guard`, `stage_verdict` | Progressive stages hold `5–15m` each with numeric halt criteria |
| **3. Post-Deploy Receipts** | `health_200`, `error_log_scan`, `sentry_posthog_delta`, `cwv_smoke`, `human_approval_utc` | Records actual CLI/probe outputs from the `60s–15m` observation window |
| **4. Rollback & Cleanup** | `instant_rollback_cmd`, `auto_triggers`, `data_forward_fix_note`, `flag_cleanup_deadline` | Exact copy-paste rollback command tested; data forward-fix note confirms `N-1` compatibility |
| **5. CI Condensation** | `unused_cache_workspace_sweep`, `tag_filter_and_concurrency_check` | Confirms `0` write-only caches and matching upstream tag filters |

---

## 4. Verification Checklist

- [ ] CI builds a single immutable artifact once (`--standalone` or OCI `@sha256`) and promotes without rebuilding per environment.
- [ ] Cloud authentication uses short-lived OIDC tokens and environment variables with zero CLI `--token` flags.
- [ ] SBOM generated and artifact signature verified alongside zero unresolved Critical/High vulnerabilities or leaked secrets.
- [ ] Database migrations execute additive expand steps before deployment and defer destructive column drops to a later release.
- [ ] Protected preview environments are verified via `vercel curl` without disabling deployment protection.
- [ ] Tag-triggered production jobs declare matching tag filters on every upstream `requires` job in the workflow graph.
- [ ] Automated rollback thresholds (`5xx > 2x`, `p95 > 1.5x`, `14.4x` burn rate) and exact instant rollback command are verified before cutover.
- [ ] CI failures are classified as transient versus deterministic before retrying, and unused caches/flags are removed in Condensation Pass.

---

## 5. Hard Quality Gate

Run pipeline validation, provenance checks, and prebuilt promotion probes before production cutover:

```bash
# 1. Inspect PR checks (with fallback if fields drift) & validate CI config
gh pr checks --json name,state,bucket,link,workflow || gh pr checks
circleci config validate 2>/dev/null || echo "No CircleCI config present"

# 2. Supply-chain & secret preflight gate
trivy fs --scanners vuln,secret --severity CRITICAL,HIGH --exit-code 1 .

# 3. Prebuilt standalone build -> protected preview probe -> Blue-Green promote (uses VERCEL_TOKEN env)
vercel pull --yes --environment=production
vercel build --prod --standalone
DEPLOY_URL=$(vercel deploy --prebuilt --prod --skip-domain)
vercel curl /healthz --deployment "${DEPLOY_URL}" -- --fail -sS
vercel promote "${DEPLOY_URL}" --yes

# 4. Post-deploy 60s–1h error log verification
vercel logs "${DEPLOY_URL}" --level error --since 1h --json | head -n 40
```

- **PASS**: Single immutable artifact built once with clean `trivy` + signature verification, expand-only DB compatibility confirmed, protected preview health check returns `200`, human approval recorded before prod cutover, instant rollback command verified, and `60s–1h` post-deploy logs show `0` critical regressions.
- **CONCERNS**: Non-blocking staging flake or deferred stale-flag cleanup logged with named owner and deadline (`<= 7d`), while prod artifact provenance, rollback, and smoke probes pass cleanly.
- **NOT ASSESSED**: Pipeline checks, `trivy`, or post-deploy log probes could not run (missing `VERCEL_TOKEN`/sandbox isolation) — MUST record `NOT ASSESSED` rather than marking release ready.
- **FAIL**: Environment-specific rebuilds bypassing tested SHA, destructive `DROP`/`RENAME` coupled to rollout, `--token` secret exposure in CLI flags, missing upstream tag filters breaking tag releases, disabled preview protection, or `5xx`/`p95` regression post-deploy without rollback.

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Rebuild-Per-Environment (`build-staging` != `build-prod`)** | Invalidates QA/security testing via dependency drift or build-flag differences | Multiple `docker build` / `vercel build` jobs per commit | Build once (`--standalone` / `@sha256` digest); promote same artifact across envs |
| **Destructive Migration Coupled to Rollout** | Rolling instances on `N-1` crash on missing columns and rollback becomes impossible | `DROP COLUMN` or `RENAME` in same PR as reader removal | Two-release **Expand-and-Contract** (`add nullable -> deploy -> backfill -> drop later`) |
| **Blanket Retries Masking Deterministic Failures** | Burns CI minutes and hides flaky tests or race conditions until production | `retry: 3` on test jobs without transient-error filter | Classify transient vs. deterministic; fix flaky root causes; rerun failed splits only |
| **Write-Only Cache Keys (`{{ epoch }}` / Commit SHA)** | Never hits cache, slows every build, and inflates CI storage spend | Cache hit rate `< 20%` or cache size equals restored size | Use lockfile checksum + prefix (`v1-npm-{{ checksum "package-lock.json" }}`) targeting `10–20x` ROI |
| **Tag-Triggered Deploy Missing Upstream Tag Filters** | CircleCI silently skips the entire tag pipeline because upstream jobs lack tag filters | Release tag pushed but `deploy-prod` workflow never runs | Add identical `filters: tags:` rules to BOTH deploy job and every upstream `requires` job |
| **Premature Multi-Cluster GitOps / Mesh Overengineering (Anti-Overengineering)** | Adds weeks of Helm/ArgoCD/Istio maintenance for a single-app team | Custom operators/service meshes serving `< 3` services | Single GHA/CircleCI workflow + platform Blue-Green/Rolling + PostHog flags (`Option A`) |
