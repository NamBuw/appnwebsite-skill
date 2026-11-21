# Documentation, Onboarding & Changelogs

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

Technical documentation and release notes fail in two opposite directions: stale walls of prose that drift from code within weeks, or leaking internal refactors and developer commit messages to end users. This module enforces:
- **Diataxis** 4-quadrant boundary discipline.
- **Single Source of Truth** OpenAPI/schema generation and **15-minute** contributor onboarding.
- **`doc-coauthoring`** fresh-context reader testing and **provenance-filtered** dual-audience changelogs across Spiral **3C** and **Q4**.

---

## 1. Decision Framework

### 1.1 Simplest High-Craft Docs Option & Anti-Overengineering Gate

Apply **Least Code, Highest Craft** before spinning up external doc infrastructure:

- **Option A (Default Simplest High-Craft)**:
  - Co-located Markdown under `docs/` + root `README.md` (`<= 15` min setup) + root `CHANGELOG.md` (Keep-a-Changelog).
  - Auto-generated `openapi.yaml` rendered via lightweight static HTML/Swagger or GitHub Markdown.
  - Deterministic `<= 60`-LOC git-tag changelog helper (`git log --oneline <last-tag>..HEAD`).
  - Zero separate CMS databases, zero multi-build Docusaurus/Algolia clusters, zero manual payload copy-pasting.
- **Earned Evidence Required for Option B (Dedicated Doc Portal / Multi-Locale CMS)**:
  - Only deploy Docusaurus, Mintlify, Fern, or external localization doc pipelines when a verified `NFR` proves Option A fails:
    - Shipping **`>= 3` public SDK languages** or **`>= 50` public API endpoints**.
    - Multi-locale public developer documentation with versioned API trees.

### 1.2 Diataxis 4-Quadrant Documentation Selection Matrix

Never mix incompatible reader intents in a single document. Route every doc artifact strictly to one Diataxis quadrant:

| Quadrant | Reader State & Need | Tone & Structure | Canonical Repo Location | Strict Boundary Rule |
|---|---|---|---|---|
| **Tutorial** | New contributor learning by doing | Guided, reproducible `<= 15m` happy path | `README.md` / `docs/onboarding.md` | Zero architecture debates or exhaustive flag tables |
| **How-To Guide** | Practitioner solving a specific task | Imperative numbered steps + exact CLI | `docs/guides/` / `docs/runbooks/` | Assume baseline knowledge; link to Reference for schemas |
| **Reference** | Engineer/integrator checking facts | Dry, exact, generated from code/OpenAPI | `docs/contracts/` / `docs/api/` | Zero hand-written JSON payloads; generated from single source |
| **Explanation** | Architect understanding *why* | Context, trade-offs, C4 diagrams, ADRs | `docs/architecture/` / `docs/adr/` | Never bury urgent CLI commands inside conceptual essays |

### 1.3 Documentation & Changelog Scope by Rigor Tier and Audience

| Rigor Tier | Architecture & API Docs | Onboarding (`onboard` Standard) | Internal Technical Changelog | User-Facing Release Notes | Freshness & Drift Ceiling |
|---|---|---|---|---|---|
| **`minimal`** | `README.md` + C4 summary + generated OpenAPI/routes | Verified `<= 15m` setup + test command + 3 starter tasks | SemVer + Keep-a-Changelog from bounded `git log` | Concise plain-language highlights + symptom fixes | `0` broken relative links; `last_verified <= 90d` |
| **`standard`** | `architecture.md` + ADR index + RFC 9457 OpenAPI + auth/rate limits | Role-scoped read priority + standards + common pitfalls | Commit SHAs, breaking migration flags, metrics, missing-ref audit | Strict **Provenance Filter**, before/after tuning metrics, Known Issues + workarounds | API PRs MUST regenerate docs in same PR (`<= 7d` drift max) |
| **`full`** | Multi-surface C4 + versioned OpenAPI/SDK reference + DPIA/compliance map | Multi-role onboarding tracks + automated devcontainer/smoke script | Signed release manifest + CVE/SBOM delta + rollback notes | Multi-channel release notes (web/mobile/API) + deprecation timelines | Automated CI link, OpenAPI diff, and staleness gates block merge |

### 1.4 Quantitative Thresholds & Provenance Rules

- **Contributor Onboarding Ceiling**: Clean setup to first passing test MUST execute in **`<= 15 minutes`**.
- **Doc Drift & Staleness Window**: **`<= 7 days`** max lag after API/schema changes (same-PR regeneration for `standard`/`full`); `last_verified` triggers a stale warning at **`> 90 days`**.
- **Git Provenance Filter Rule**:
  - Bound commit inspection explicitly (`<last-tag>..HEAD`, or `-n 100` for initial release — never unbounded `git log`).
  - Classify every commit into `User/Product Impact`, `Internal/Maintenance/CI/Docs`, or `Unclear`, and **treat `Unclear` strictly as `Internal`**.
  - Exclude 100% of internal file paths, refactors, CI tweaks, and developer names from user-facing release notes.
- **Denominator-First Zero-Hit Rule**: Every doc lint or staleness scan MUST report `scanned [N] files, [M] hits`; if `N == 0` or upstream source docs are missing, emit `NOT ASSESSED — NO DATA` rather than guessing paths.

---

## 2. Step-by-Step Workflow

- **Inputs**: `architecture.md`, `openapi.yaml` (or typed schemas), `README.md`, `git` tag history, `release-qa-verdict.md`.
- **Outputs**: Diataxis docs (`docs/`), updated `CHANGELOG.md`, user-facing release notes, and [Release Checklist (Section 6)](../templates/release-checklist.md#6-changelog-user-release-notes-and-docs-freshness-sign-off).
- **Owners**: Tech Lead / Authoring Engineer (docs & OpenAPI parity) and Release Owner (changelog & reader verification).
- **Primary Tools**: `git`, `gh`, OpenAPI generator, Python/Markdown link & freshness check.

1. **Gather Context & Verify `FOUND` vs. `ABSENT` Inputs (Owner: Tech Lead)**:
   - Apply **`doc-coauthoring` Stage 1**: define target Diataxis quadrant, reader persona, and desired reader action before drafting.
   - Audit which canonical upstream artifacts exist on disk (`architecture.md`, `data-model.md`, `openapi.yaml`, `README.md`).
   - Follow the `onboard` insufficient-input gate: mark missing inputs explicitly as `NOT ASSESSED — NO DATA` rather than fabricating directory trees, ports, or CLI flags.

2. **Author Architecture, Generated API Reference & 15-Minute Onboarding (Owner: Tech Lead)**:
   - *Architecture Explanation*:
     - Link C4 context/container boundaries, trust zones, and the Accepted ADR index.
     - Add descriptive alt-text captions for every architecture diagram.
   - *API Reference (Single Source of Truth)*:
     - Generate `openapi.yaml` / JSON Schema directly from typed routes or validators.
     - Include auth schemes, pagination cursors, idempotency headers, rate limits, and RFC 9457 `ProblemDetails` errors directly from schema definitions so docs never drift.
   - *Role-Scoped Onboarding (`onboard` pattern)*:
     - Structure onboarding as: Project Summary -> Role Scope -> Key Directories & Read Priority -> Engineering Standards -> Current State & Dependencies -> Common Pitfalls -> Verified `<= 15m` Setup/Test Commands -> First 3 Tasks.
     - Execute every onboarding command in a clean shell to prove reproducibility before merging.

3. **Generate Dual-Audience Changelogs via Bounded Provenance Filter (Owner: Release Owner)**:
   - Extract commits strictly within release range: `git log --oneline "$(git describe --tags --abbrev=0)..HEAD"` (falling back to `-n 100` only if zero tags exist).
   - Audit **every commit** through the **Provenance Filter** (`User/Product Impact` vs. `Internal/Maintenance` vs. `Unclear` -> `Internal`).
   - *Internal Technical `CHANGELOG.md`*:
     - Group under Keep-a-Changelog sections (`Added | Changed | Deprecated | Removed | Fixed | Security`) with SemVer (`MAJOR.MINOR.PATCH`).
     - Include commit SHAs, breaking-change migration steps, performance metrics, and an audit line flagging commits missing task/issue references.
   - *User-Facing Release Notes*:
     - Rewrite ONLY verified `User/Product Impact` items in plain language describing the **user benefit or symptom fixed** (e.g., *"Fixed checkout failure on expired promo codes"* rather than *"Refactored DiscountValidator null guard"*).
     - Include concrete before/after numbers for tuned behavior plus **Known Issues & Workarounds**, and strip 100% of internal refactors, file paths, and developer names.

4. **Run Fresh-Context Reader Testing (`doc-coauthoring` Stage 3) (Owner: Release Owner + Fresh Reviewer)**:
   - Draft the highest-unknown technical sections first and write executive summaries last.
   - Generate `5–8` realistic discovery and execution questions a brand-new engineer or API consumer would ask (e.g., *"How do I rotate a webhook secret locally?"*, *"Which HTTP status codes trigger retry backoff?"*).
   - Hand ONLY the drafted document — with zero prior conversation context — to a fresh reviewer or isolated subagent to answer those questions.
   - Patch every hidden assumption, missing prerequisite, broken cross-reference, or undefined acronym surfaced.

5. **Enforce Docs-as-Code CI & Run the 3-Iteration Bloat-Sweep / Condensation Pass (Owner: Tech Lead)**:
   - Wire CI guards checking: (a) API/schema PR diffs force updated `openapi.yaml` / `docs/` in the same PR, (b) zero broken relative links or heading anchors, (c) `last_verified` metadata present and `<= 90 days` old, and (d) denominator-first non-stub checks (`scanned N files, M hits`).
   - Execute the **`doc-coauthoring` Condensation & Bloat-Sweep Pass**: after 3 consecutive refinement iterations with minimal structural change, delete duplicated setup prose between `README.md` and `docs/`, replace hand-maintained CLI flag tables with `--help` output references, strip generic intros, and verify every remaining paragraph earns its context tokens.

---

## 3. Reusable Artifact & Template

Record documentation freshness, Keep-a-Changelog provenance, and user release-note sign-off inside **Section 6** of [Release Checklist Template](../templates/release-checklist.md#6-changelog-user-release-notes-and-docs-freshness-sign-off) so release promotion and documentation parity share a single auditable gate.

| Artifact / Field | Required Schema Elements | Verification & Completeness Rule |
|---|---|---|
| **Doc Metadata Header** | `doc_id`, `diataxis_type`, `owner`, `last_verified`, `source_of_truth` | Every `docs/*.md` file carries `last_verified: YYYY-MM-DD` (`<= 90d`) and exact upstream source path |
| **Bounded Provenance Scan** | `commit_range`, `total_scanned`, `user_facing_count`, `internal_count`, `unclear_treated_internal` | Bounded `<last-tag>..HEAD` or `-n 100`; zero `Unclear` commits leaked to user notes |
| **Internal `CHANGELOG.md`** | `version`, `date_utc`, `Added/Changed/Deprecated/Removed/Fixed/Security`, `breaking_migration`, `unlinked_commits` | SemVer aligned with git tag; breaking changes carry explicit expand/migrate instructions |
| **User Release Notes** | `highlights`, `new_capabilities`, `improvements_with_before_after`, `symptom_fixes`, `known_issues_workarounds` | Zero internal paths, refactors, CI commits, or developer names; plain symptom language |
| **Docs & Reader Sign-Off** | `openapi_parity`, `broken_links_count`, `reader_test_questions_passed`, `bloat_sweep_delta` | Fresh-context Reader Testing `5–8` questions passed; 3-iteration Bloat Sweep completed |

---

## 4. Verification Checklist

- [ ] Every document maps cleanly to a single Diataxis quadrant without mixing tutorials, how-tos, specs, and ADRs.
- [ ] API reference documentation is generated or validated directly against canonical OpenAPI or typed schemas in CI.
- [ ] Contributor onboarding instructions execute end-to-end in a clean environment within 15 minutes or mark missing inputs `NOT ASSESSED`.
- [ ] Changelog uses SemVer, Keep-a-Changelog headings, and an explicit bounded commit range since the previous release tag.
- [ ] Provenance filter excludes all internal maintenance commits, file paths, stack internals, and author names from user release notes.
- [ ] Fresh-context Reader Testing validated 5 to 8 realistic reader tasks with zero unresolved ambiguities or missing prerequisites.
- [ ] Bloat-Sweep Condensation Pass deleted duplicated prose across README and docs, and all relative links and `last_verified` dates pass CI.

---

## 5. Hard Quality Gate

Execute bounded provenance extraction, denominator-first freshness audits, and link checks before finalizing any release:

```bash
# 1. Bounded changelog provenance scan (never unbounded git log)
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$LAST_TAG" ]; then
  git log --oneline "${LAST_TAG}..HEAD"
else
  git log --oneline -n 100
fi

# 2. Denominator-first docs freshness & staleness check
DOC_COUNT=$(find docs -type f -name "*.md" 2>/dev/null | wc -l)
if [ "$DOC_COUNT" -eq 0 ]; then
  echo "NOT ASSESSED — NO DATA: docs/ contains 0 markdown files"
else
  MISSING_META=$(grep -rL --include="*.md" "last_verified" docs/ 2>/dev/null | wc -l)
  echo "Docs freshness scan: scanned ${DOC_COUNT} files, ${MISSING_META} missing last_verified"
fi
```

- **PASS**: Required Diataxis surfaces exist with `last_verified <= 90d`, OpenAPI/schema diff parity is green in CI, clean onboarding completes `<= 15m`, bounded provenance filter separates internal `CHANGELOG.md` from clean user release notes, fresh-context Reader Testing passes `5–8` queries, and Bloat Sweep deleted redundant prose.
- **CONCERNS**: Minor wording improvement or non-API `last_verified` refresh older than `90d` logged with named owner (`<= 7d`), while API parity, provenance filter, and onboarding paths pass.
- **NOT ASSESSED**: `docs/` contains `0` files, git tags/history are unavailable, or onboarding was not executed on a clean shell — MUST emit `NOT ASSESSED — NO DATA`, never `PASS`.
- **FAIL**: API/schema PR merged without regenerating OpenAPI/docs, user-facing release notes expose internal file paths/refactors/developer names, onboarding steps fail clean reproduction, broken relative links exist, or missing upstream architecture inputs were fabricated instead of marked `NOT ASSESSED`.

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Maintenance-Commit Leak in User Notes** | Exposes internal refactoring, CI tweaks, or developer names as fake customer features and breaks trust | User notes list `chore:`, file paths, or `refactored FooHelper` | Run **Provenance Filter**; classify `Unclear` as Internal; publish plain-language symptom fixes |
| **Hand-Written Drifting API Docs** | Manual JSON request/response examples diverge from backend validators within weeks | API tests pass while copy-pasted docs return `400`/`422` | Generate OpenAPI/reference docs directly from typed schemas and enforce diff parity in CI |
| **Diataxis Soup in Monolithic `README.md`** | Mixes 15-minute setup, conceptual ADRs, and 200 env vars into one unreadable scroll | `README.md > 500` lines mixing tutorials, specs, and history | Split strictly into Tutorial (`README`), How-To (`docs/guides`), Reference (`docs/contracts`), Explanation (`docs/adr`) |
| **Doc-Portal Over-Engineering (Anti-Overengineering)** | Wastes sprint cycles maintaining Docusaurus/Algolia/CMS pipelines for a single small service | Custom doc-site build pipeline outnumbering product endpoints | Keep co-located `docs/` + `CHANGELOG.md` + generated OpenAPI (`Option A`) until `>= 50` endpoints or `>= 3` SDKs |
| **Fabricating Missing Context (`NOT ASSESSED` Suppression)** | Guessing undocumented ports, env vars, or build scripts produces broken onboarding that wastes hours | Docs cite paths or scripts not present in repository | Follow `onboard` gate: mark missing artifacts `NOT ASSESSED — NO DATA` and surface exact gap |
| **Zero-Context Skipping & Unbounded `git log`** | Skips fresh-reader verification and dumps 2,000 ancient commits into release notes | Ambiguous setup steps and unframed `git log` dumps | Run `5–8` fresh-context Reader Tests, bound `git log <last-tag>..HEAD`, and execute 3-pass Bloat Sweep |
