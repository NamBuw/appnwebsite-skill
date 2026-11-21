# Anti-Overengineering & Radical Simplicity Self-Interrogation Gate ("Least Code, Highest Craft")

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This module enforces the **"Least Code, Highest Craft" (`ít nhất mà tốt nhất`)** protocol across every architecture decision, database schema, backend service, API contract, UI surface, CSS rule, test suite, and deployment pipeline. Simplicity here is **never** cutting quality, security, or UX—it is achieving **equal or HIGHER reliability, craft, speed, and maintainability** using the fewest moving parts, layers, dependencies, and lines of code.

---

## 1. Decision Framework

### 1.1 The 4 Mandatory Socratic Self-Interrogation Questions

Before proposing or implementing **any** new architecture, feature, module, external dependency, abstraction layer, state store, or UI mechanism, the agent MUST answer all four questions explicitly with concrete evidence:

1. **Q1 — Simpler Equal-or-Higher-Quality Alternative**:
   *"For this feature or requirement, is there a simpler approach that delivers equal or HIGHER quality, UX, reliability, and maintainability?"*
   - *Rule*: You are forbidden from presenting a complex architecture first. You MUST construct **Option A (Simplest High-Craft Option)** first and attempt to disprove it against verified constraints.
2. **Q2 — Layer Deletion & Native Platform Primitives**:
   *"What layers, third-party dependencies, wrappers, state stores, or moving parts can be deleted or replaced with native platform, language, database, or browser primitives?"*
   - *Rule*: Never add a library, microservice, wrapper class, or client state manager when SQL/PostgreSQL, HTTP semantics, language stdlib, or semantic HTML + modern CSS already provide the capability natively.
3. **Q3 — Real Verified Constraint vs. Hypothetical Scale (YAGNI)**:
   *"Are we solving a real, verified constraint right now (backed by PRD/NFR/telemetry), or inventing complexity for hypothetical future scale?"*
   - *Rule*: Every non-minimal moving part must cite a concrete constraint locator (`NFR-03`, benchmark latency, compliance rule) and pass an ablation test (*"what measurable requirement fails if we delete this?"*).
4. **Q4 — Maximum Density & Craft (`ít nhất mà tốt nhất`)**:
   *"How do we make the code and technical architecture as concise, dense, readable, and minimal as possible while maximizing craft?"*
   - *Rule*: Optimize for low cognitive load, flat call paths, zero single-use indirection, cohesive vertical modules, and strict Complexity Budgets.

### 1.2 Complexity Budget & Native-Primitive Substitution Matrix

| Proposed Addition | Earned Evidence Required to Justify | Default Simplest High-Craft Option |
|---|---|---|
| **Separate Service / Queue / Cache / Microservice** | Proven throughput/latency/isolation failure in measured benchmark or compliance boundary (`NFR` citation) | Modular Monolith + single ACID PostgreSQL (`SKIP LOCKED` job table, materialized/indexed views, CTEs) |
| **New NPM / PyPI / Crate External Dependency** | Replaces `>= 150` LOC of subtle or security-critical logic (crypto, auth, parser, PDF) AND passes supply-chain audit | Language/runtime stdlib (`fetch`, `crypto`, `URL`, `Intl.*`, Python `json`/`sqlite3`/`urllib`) or `<= 50`-LOC tested helper |
| **New Interface / Wrapper / Factory / Repository** | **Rule of Three**: `>= 3` concrete, actively diverging implementations or external test-port boundary TODAY | Direct typed module function; inline 1–2 call sites until genuine divergence occurs |
| **Client Global State Library / Effect Chain** | Proven multi-tab/offline/optimistic graph synchronization beyond server state + URL | URL `searchParams` + Server Components/actions + native HTML `<form>`/`FormData` + lightweight query cache |
| **Custom JS/Div UI Widget** | Native HTML/CSS primitive measurably lacks required keyboard/a11y/positioning behavior | `<dialog>`, `<details>`/`<summary>`, `popover`, `<datalist>`, CSS Grid/Subgrid, `:has()`, `clamp()`, `@container` |
| **ORM / GraphQL / BFF Layer** | Multi-client schema federation or complex multi-backend aggregation verified in PRD | Typed SQL query builder / parameterized SQL + clean REST/OpenAPI + RFC 9457 errors |

### 1.3 Simplest High-Craft Option First (Worked Cross-Domain Examples)

- **Backend Background Jobs (`Standard` Tier SaaS)**:
  - *Over-Engineered*: RabbitMQ + Celery/BullMQ + Redis cluster + 3 worker containers + dead-letter dashboard for 500 emails/day.
  - *Simplest High-Craft Option*: Single `jobs` table in existing Postgres with `FOR UPDATE SKIP LOCKED`, exponential backoff `run_at`, idempotency key, and 60 lines of typed worker loop inside existing runtime. *Result*: 0 new infra stores, transactional enqueueing with business writes, higher reliability.
- **UI Interactive Modal & Responsive Typography**:
  - *Over-Engineered*: `react-modal` + `focus-trap-react` + portal context + 4 media-query JS resize listeners + 3-layer `ModalWrapper -> ModalContainer -> ModalBase`.
  - *Simplest High-Craft Option*: Native HTML `<dialog>` (`showModal()` handles Escape, backdrop, Top Layer, and focus return natively) + CSS `clamp()` fluid type scale + `:has()` state styling. *Result*: ~180 LOC deleted, better accessibility, 0 dependencies.
- **Design System & Token Layer**:
  - *Over-Engineered*: Custom CSS-in-JS runtime theme provider + 400 bespoke prop overrides + 12 variant dimensions per button.
  - *Simplest High-Craft Option*: Static W3C DTCG `tokens.json` compiled once to CSS custom properties + semantic HTML elements + 3–4 bounded variants (`primary | secondary | ghost | danger`). *Result*: 0 runtime style overhead, clean Figma parity.

---

## 2. Step-by-Step Workflow

### Stage A — Pre-Design Socratic Interrogation (`Q1 / Q2` Before Phase 3A)
1. Open [Simplicity Interrogation Record template](../../templates/simplicity-interrogation-record.md) (`Pass Stage: PRE-DESIGN`).
2. Write non-trivial, concrete answers to **Q1–Q4** for the Spiral's architecture, data model, dependencies, and UI surfaces.
3. Fill **Section 2 (Simplest High-Craft Option)** first; reject any Option B that lacks a verified constraint citation.
4. Populate **Section 3 (Rejected Complexity Ledger)** recording every deleted layer/dependency and its native replacement.
5. Set the Spiral's hard **Complexity Budget** (`Max New External Deps`, `Max New Layers`, `Target Max Files/LOC`, `Bundle/Latency Ceiling`).

### Stage B — Pre-Implementation Plan Proportion Check (Before Phase 3B Coding)
1. Audit planned files and `Consumes`/`Produces` interfaces against the Complexity Budget.
2. Delete speculative abstractions before writing a single line:
   - Collapse `IFooService -> FooServiceImpl -> FooRepo -> FooRepoImpl` chains into direct module functions unless an external port/mock boundary or `>= 3` variants exist.
   - Remove speculative `strategy`, `plugin`, or `future_provider` config switches with only 1 concrete branch.
3. Verify every remaining external package against the `>= 150` LOC / security-critical threshold and supply-chain check.

### Stage C — Mandatory Pre-Ship Deletion & Condensation Pass (Phase 3C)
Before claiming any vertical slice or PR complete, perform a dedicated **Deletion & Condensation Pass**:
1. **Dead & Speculative Code Sweep**: Delete unused exports, unreachable branches, orphaned types, commented-out code, and unused feature flags.
2. **Layer Collapse**: Inline single-caller pass-through helpers (`< 20` LOC wrappers that merely rename args), redundant DTO mappers where DB/domain/wire shapes match cleanly, and redundant hooks.
3. **Dependency Trim**: Inspect `package.json` / `pyproject.toml` / `Cargo.toml` diffs — remove any package replaceable cleanly by native primitives.
4. **UI/CSS Simplification**: Replace `useEffect` state syncing with derived values, replace JS media/toggle state with CSS Grid/`:has()`/`<details>`/`<dialog>`, flatten wrapper `<div>` soup.
5. **Post-Deletion Verification (Iron Law)**: Re-run the full build, linter, typechecker, and test suite **after** the deletion pass (`verification-before-completion`). Record exact `Files Deleted`, `Deps Removed`, and `Net LOC Reduced` in Section 4 of `simplicity-interrogation-record.md` (`Pass Stage: PRE-SHIP-CONDENSATION` or `BOTH`).

### Stage D — Ablation Test for Any Added Complexity
Whenever an engineer proposes Option B (extra layer, cache, queue, or package), apply the **3-Question Ablation Test** before approving:
1. **Baseline Benchmark**: What exact metric (`p95`, bundle KB, error rate, dev hours) failed on Option A? (Unmeasured intuition is rejected.)
2. **Removal Impact**: If we delete this new component right now, which specific requirement (`FR-xx` / `NFR-xx`) breaks?
3. **30-Day Reversibility**: Can this added dependency/layer be deleted in `< 1` day if traffic or requirements stay simple? If not, require an Accepted ADR with explicit exit criteria.

#### Domain-by-Domain Deletion Triggers (Where Bloat Hides)
| Domain | Primary Bloat Signal | Surgical Condensation Action |
|---|---|---|
| **Backend / Services** | `Controller -> Service -> Manager -> Repository -> DAO` with 1:1 passthroughs | Collapse into `Route Handler -> Domain Module -> Typed Query`; keep ports only at external I/O boundaries |
| **Database & Caching** | Premature Redis cache in front of `< 10k`-row Postgres table | Drop Redis; add composite/partial Postgres index + `EXPLAIN ANALYZE` check |
| **API & Contracts** | 14-field generic envelope + custom pagination/error framework | Use flat JSON + standard HTTP status + RFC 9457 `ProblemDetails` |
| **Frontend / CSS** | 8 wrapper `div`s, JS resize listeners, `useEffect` derived-state sync | Use semantic HTML (`<dialog>`, `<details>`), CSS Grid/`clamp()`/`:has()`, pure derived expressions |
| **Tests & Tooling** | Testing third-party library internals or mocking every internal helper | Test real behavior at boundaries (black-box EP/BVA + integration tests against real test DB) |
| **Observability / Config** | Multi-tier plugin/DI framework for 2 static config keys | Typed env schema validation at startup (`<= 25` LOC) + direct OpenTelemetry SDK hooks |

### Stage E — Concrete Before/After Condensation Examples ("Ít Nhất Mà Tốt Nhất")

#### Example 1: Backend Auth & Repository Collapse (`-140 LOC`, `0` Regressions)
- *Bloated (4 files, 185 LOC)*: `IUserRepository.ts` -> `PostgresUserRepository.ts` -> `UserMapper.ts` -> `UserService.ts` (all 1:1 pass-throughs returning raw DB columns renamed into DTOs).
- *Condensed (`1` file, `45` LOC)*: `users.ts` exporting `findUserById(db, id)` and `createUser(db, input)` with typed SQL returning the exact API/domain projection directly. Behavior, SQL safety, and test coverage stay 100% identical while eliminating 3 indirection layers.

#### Example 2: Frontend Modal & Filter State Collapse (`-210 LOC`, `-2 deps`, Better A11y)
- *Bloated*: `modal-portal-lib` + `zustand` filter store + 3 `useEffect` hooks syncing query params with local component state + custom `keydown` Escape listener.
- *Condensed*: Native `<dialog ref={dialogRef}>` (`showModal()` handles Top Layer, backdrop, focus return, and `Escape` natively) + URL `searchParams` as the single source of truth for filters. Zero external state/modal dependencies, shareable URLs out of the box, full WCAG keyboard compliance.

#### Example 3: Pre-Ship Dependency Audit Checklist (Run Before Phase 3C Sign-Off)
1. List every package added in `package.json` / `pyproject.toml` / `Cargo.toml` during the current Spiral.
2. For each package, answer: *"Can standard library or native browser/SQL primitives implement the exact subset we use in `<= 50` clean lines?"*
3. If YES -> replace with the native implementation, run unit/integration tests, and uninstall the package.
4. If NO -> verify package passes `skills/security-engineering` supply-chain audit (`osv-scanner` / `npm audit` / `pip-audit`) and record justification in Section 3 of `simplicity-interrogation-record.md`.

### Pre-Ship Condensation Receipt Format
Record exact before/after counts inside `simplicity-interrogation-record.md` so reviewers can verify deletion occurred rather than trusting vague claims:
- `Files Deleted`: integer count + paths removed
- `Deps Removed`: package names removed from manifest/lockfile
- `Net LOC Reduced`: `git diff --stat` net negative or bounded delta
- `Post-Deletion Test Command`: exact command + exit code `0` run **after** final deletion edit

### Cross-Discipline Simplicity Checkpoints (Architecture, API, UI, QA, Infra)
Before approving any slice in Q1–Q4, verify each discipline applied the simplest high-craft primitive:
- **Data & Queries**: Did we check if a SQL CTE, partial index, or JSONB column eliminates a second datastore or cache?
- **APIs & Validation**: Did we share one typed schema (e.g., Zod/OpenAPI/Pydantic) instead of duplicating hand-written validators across client, controller, and service?
- **UI & Styling**: Did we replace custom JS focus/accordion/popover logic with `<dialog>`, `<details>`, `popover`, CSS `:has()`, and fluid `clamp()` before reaching for UI helper libraries?
- **State & Fetching**: Did we keep filter/pagination state in URL `searchParams` and server state in one cache layer instead of mirroring API payloads in a global store?
- **Testing**: Did we test real contract behavior and boundary partitions directly rather than writing brittle mocks that assert private helper call counts?
- **Infra & CI**: Did we start with 1 deployable unit + managed Postgres + 1 clean CI check workflow rather than Kubernetes/Helm/Terraform multi-cluster boilerplate for a single-team MVP?

### Exception Approval Protocol (When Complexity Is Genuinely Earned)
When Option A demonstrably fails a verified constraint (`NFR-xx`), complexity is permitted **only** if all four conditions hold:
1. **Measured Failure**: Exact reproducible metric from Option A benchmark or compliance audit (e.g., *"Single-region Postgres p95 read exceeded 400ms at 5k RPS during realistic load test"*).
2. **Narrowest Addition**: Add only the smallest structural correction (e.g., read replica or indexed view before distributed cache).
3. **ADR & Reversibility Plan**: Record an Accepted ADR noting migration path and deletion trigger if load assumptions change.
4. **Complexity Budget Updated**: Update `Max New External Deps` and `Max New Layers` explicitly in `spiral-charter.md`.

---

## 3. Reusable Artifact & Template

- **Canonical Template**: [Simplicity Interrogation Record](../../templates/simplicity-interrogation-record.md)
- **Required Fields Enforced by `check_spiral_gates.py`**:
  - Header metadata: `Record ID`, `Spiral ID`, `Target Scope`, `Pass Stage` (`PRE-DESIGN | PRE-SHIP-CONDENSATION | BOTH`), `Verdict` (`PASS | CONCERNS | NOT ASSESSED | FAIL`), `Evaluated (UTC)`.
  - Section 1: Explicit non-placeholder answers (`>= 20` chars, not echoing the prompt) to all 4 Socratic questions (`Q1`–`Q4`).
  - Section 2: `Option A — Simplest High-Craft Baseline` surfaced first + comparative Trade-off Matrix (`Moving Parts | External Deps | Failure Modes | Craft Impact`).
  - Section 3: Rejected Complexity & Native-Primitive Substitutions Ledger (`Rejected Item | Category | Native Replacement | Deps/LOC Saved`).
  - Section 4: Declared Complexity Budget (`Max New Deps | Max New Layers | Target Files/LOC | Bundle/Latency Ceiling`) + checked Pre-Ship Deletion/Condensation Checklist (`[x]`) + numeric Condensation Metrics (`Files Deleted | Deps Removed | Net LOC Reduced | Craft Regressions: 0`) when `Pass Stage` is `PRE-SHIP-CONDENSATION` or `BOTH`.

### Example Filled `SIR-001` Excerpt (Passing Gate)
```markdown
- **Q1 Response**: Server-rendered form + single Postgres `leads` table replaces headless CMS + client state store + Zapier webhook relay, cutting latency from 420ms to 35ms with 0 extra failure modes.
- **Q2 Substitutions**: Replaced `zod-to-openapi` + `axios` + `framer-motion` accordion with TypeScript strict types + native `fetch` + HTML `<details>` + CSS transition (`-3 deps`, `-240 LOC`, `-48KB gz`).
- **Q3 Constraint**: Verified `NFR-02` requires `< 100KB` total JS and `1,000` submissions/day; no distributed queue or Redis needed.
- **Q4 Condensation**: Collapsed 4 helper files into 1 cohesive `leads.ts` module (`95 LOC` total, 100% covered by 6 boundary tests).
```

---

## 4. Verification Checklist

- [ ] All 4 Socratic Simplicity Questions (`Q1`–`Q4`) answered with concrete, system-specific evidence (zero generic boilerplate).
- [ ] **Option A (Simplest High-Craft)** evaluated first; every deviation cites a measured constraint (`NFR`/benchmark/compliance) and failed simpler baseline.
- [ ] Zero single-implementation interfaces (`IFoo`/`FooImpl`), zero pass-through mappers, and zero speculative config flags.
- [ ] Every external dependency justifies itself against a `<= 150`-LOC native/stdlib alternative and passes security vetting.
- [ ] UI uses native HTML/CSS primitives (`<dialog>`, `<details>`, `<form>`, Grid, `:has()`, `clamp()`) wherever sufficient.
- [ ] Complexity Budget respected (`New Deps`, `New Layers`, `Bundle/Latency Ceiling`).
- [ ] Pre-Ship Deletion/Condensation Pass executed, metrics logged, and full build + test suite re-run cleanly **after** deletions.

---

## 5. Hard Quality Gate

- **Command**: `python3 scripts/check_spiral_gates.py --project-dir <repo> --stage simplicity --strict --json`
- **PASS Criteria**: Valid `simplicity-interrogation-record.md` with substantive answers to `Q1`–`Q4`, Option A surfaced first, Complexity Budget within limits (or measured exception recorded), and Deletion Pass checkboxes `[x]` completed with post-deletion tests passing.
- **NOT ASSESSED Criteria**: Record missing, or any Socratic answer / metrics field still contains `[...]` placeholders or copies the question text verbatim.
- **FAIL Criteria**:
  - Gratuitous external dependency added for logic trivial in language stdlib or native HTML/CSS/SQL.
  - Premature microservice, cache, or message broker introduced without measured bottleneck evidence.
  - Pre-Ship Deletion Pass skipped (`[ ]` unchecked when `Pass Stage` is `PRE-SHIP-CONDENSATION` or `BOTH`) or tests not re-run after deletions.
- **Concrete Remediation Triggers**:
  - If `Deps Removed == 0` after a complex slice, manually audit `package.json`/`pyproject.toml` diff for single-use helpers.
  - If `SIR` echoes the prompt verbatim instead of naming real files/primitives, `check_spiral_gates.py` emits `NOT ASSESSED` and blocks merge.

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Resume-Driven / Premature Microservices** | Adds network hops, partial failures, distributed tracing, and deploy overhead before scale exists | Separate services/Kafka/Redis added for low-QPS CRUD | Modular Monolith + Postgres (`SKIP LOCKED`, views, clean internal ports) |
| **Enterprise Boilerplate Cascade (`IFoo -> FooImpl -> FooRepo`)** | Triples file count and indirection for 1 concrete behavior; slows review and debugging | 1:1 interfaces with single implementations and pass-through methods | Direct typed module functions; extract interface only at real port or 3rd variant |
| **Micro-Dependency Sprawl** | Bloats client bundle, fragments types, and widens supply-chain attack surface | Packages installed for class-merging, date formatting, simple modals, or 10-line utils | `Intl.*`, native `crypto`/`URL`, `<dialog>`, CSS `:has()`, or small tested helper |
| **Client State-Store Mirroring** | Duplicates server cache in Redux/Zustand with manual sync bugs and boilerplate reducers | Global client store holding API responses and transient modal/form flags | URL `searchParams`, native `<form>`, server state cache, local component state |
| **Over-Engineered Custom UI Widgets** | Breaks keyboard nav, screen readers, and focus trapping while burning hundreds of LOC | Custom `div` accordions/modals/dropdowns reimplementing browser behavior poorly | Native `<dialog>`, `<details>`, `popover`, `<select>`, CSS Grid + `clamp()` |
| **Skip-Deletion Ship Rush** | Leaves AI-generated scaffolding, dead helpers, and unused imports accumulating across Spirals | Net LOC grows monotonically; `PRE-SHIP-CONDENSATION` unchecked | Mandatory Stage C Deletion/Condensation Pass + post-deletion test run |
| **Premature Plugin / Rule Engines** | Invents JSON DSLs or runtime hook registries for 2 static business rules | Custom AST/rule interpreter with 1 consumer | Plain typed `if/else` or lookup table; extract only at `>= 3` dynamic external rules |

---

## Related Governance Modules
- [Spiral Lifecycle](spiral-lifecycle.md)
- [System-First Foundation Gate](system-first-foundation-gate.md)
- [Token Economy & Progressive Disclosure](token-economy-and-progressive-disclosure.md)
- [Orchestration Protocol](../orchestration-protocol.md)
- [Simplicity Record Template](../../templates/simplicity-interrogation-record.md)
