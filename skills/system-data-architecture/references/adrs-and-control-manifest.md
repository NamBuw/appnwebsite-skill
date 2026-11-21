# Architecture Decision Records & Control Manifest

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

Architectural decisions drift rapidly when buried inside chat threads or sprawling design prose. Sparse Architecture Decision Records (`ADRs`) capture *why* irreversible trade-offs were chosen, an independent traceability review verifies that every requirement is covered without cross-ADR conflicts or cycles, and a flat `control-manifest.md` distills *what* engineers must and must never do into a scannable rule sheet before coding begins.

---

## 1. Decision Framework

### 1.1 The 3-Criteria Sparse ADR Gate (Anti-Overengineering Filter)

Following MIT-licensed `mattpocock/skills/domain-modeling` and Radical Simplicity ("Least Code, Highest Craft"), skip ADRs for reversible local choices. Author an ADR only when **all three** criteria hold:

1. **Hard to Reverse**: Changing later costs `> 1–2` engineering days, a live migration, or an external contract break.
2. **Surprising Without Context**: Future engineers would question why this constraint beat the obvious default.
3. **Real Trade-Off**: Viable alternatives competed across latency, cost, consistency, security, or ops complexity.

Evaluate **Option A (Simplest High-Craft Baseline)** inside `## Alternatives Considered` before accepting higher complexity.

### 1.2 ADR Status Lifecycle & Acceptance Authority

```text
[Proposed] --(Explicit Sign-Off + All Upstream ADRs Accepted)--> [Accepted]
    |                                                                |
    +--(Rejected)---------------------------------------------> [Deprecated]
                                                                     ^
[Accepted] --(Replaced by newer ADR-NNNN; NEVER revive old ADR)------+
```

- Authoring initializes `Status: Proposed`.
- `Status: Accepted` is the only state unlocking Phase 3A and feature coding.
- Never accept an ADR while any `Depends On` ID is `Proposed`, missing, or `UNKNOWN`.
- Never revive `Deprecated` or `Superseded` ADRs by edit; issue a new `ADR-NNNN` citing the predecessor.

### 1.3 Architecture Traceability & Verdict Precedence

When auditing requirements coverage across ADRs and `docs/architecture/architecture.md`, apply the strict 4-state verdict hierarchy **`FAIL > CONCERNS > NOT ASSESSED > PASS`**:

| Verdict | Exact Trigger Condition | Downstream Action |
|---|---|---|
| **`FAIL`** | Any Foundation/Core requirement is `Gap`, any cross-ADR conflict exists, or a dependency cycle exists in `Depends On` | **Hard Stop** — block Phase 3A; resolve gap/conflict/cycle first |
| **`CONCERNS`** | Non-critical feature requirement is `Partial`, or a requirement is covered only by a `Proposed` (unaccepted) ADR | **Conditional Hold** — accept pending ADRs or log mitigation before feature work |
| **`NOT ASSESSED`** | Missing `docs/product/prd.md`, missing `docs/architecture/architecture.md`, unreadable ADR, or unverified runtime/platform constraint | **Honest Incomplete** — never emit `PASS` when scope was not examined |
| **`PASS`** | `100%` of in-scope requirements map to `Covered (Accepted)`, `0` cross-ADR conflicts, `0` DAG cycles, all platform checks verified | **Unlock** — generate/refresh `docs/architecture/control-manifest.md` and unlock Phase 3B |

### 1.4 Six Cross-ADR Conflict Classes & Layer Default Rule

Check every accepted and proposed ADR pair against six explicit conflict classes:
1. **Data Ownership Conflict**: Two ADRs claim write authority over the same entity or table.
2. **Integration Contract Conflict**: Incompatible payload format, auth mechanism, or sync/async protocol across caller and callee ADRs.
3. **Performance / Latency Budget Conflict**: Combined subsystem budgets exceed the end-to-end `NFR` ceiling (e.g., `3` sequential `100 ms` steps violating a `200 ms` p95 SLO).
4. **Dependency Cycle**: `ADR-A` depends on `ADR-B` while `ADR-B` (transitively) depends on `ADR-A`.
5. **Architecture Pattern Conflict**: Incompatible stances on state authority or eventing (e.g., sync REST vs. async event-only reads for one user flow).
6. **State Authority Conflict**: Competing sources of truth (cache vs. DB vs. client state) without a single owner.

- **Layer Default Rule**: Unlayered ADRs default strictly to **`Layer: Foundation`** (blocking priority) so critical persistence or security assumptions never slip past review.
- **Immutability Rule**: Once superseded, an ADR stays permanently `Superseded by ADR-NNNN` for historical auditability.
- **Registry Check**: Always verify new proposals against existing `State Ownership` and `Forbidden Patterns` before writing.

### 1.5 Separation of Concerns: ADRs vs. Control Manifest

ADRs are historical *rationale* documents explaining context, alternatives, and trade-offs (`300–600` words each). Engineers implementing features should not re-read twenty narrative ADRs on every ticket. Instead, `control-manifest.md` is a **flat, non-prose programmer rule sheet** extracted exclusively from `Accepted` ADRs and pinned runtime configs, stamped with `Manifest Version` (`YYYY-MM-DD`). Any feature PR or story checks `Manifest Version` against the latest `Accepted` ADR date to detect rule drift immediately.

---

## 2. Step-by-Step Workflow

Apply **Token Economy** strictly: never read every ADR body in full during initial triage. Read only the header metadata and the 2-sentence `## Summary` first (`40 KB` Read Guard), establishing total denominator counts (`N_reqs`, `N_adrs`) up front.

1. **Scan Registry & Assign Sequential ADR ID**
   - **Inputs**: `docs/architecture/adr/adr-*.md`, `docs/architecture/architecture.md`, `docs/product/prd.md`, `docs/product/nfr-slo-matrix.md`.
   - **Owner**: System Architect.
   - **Action**:
     - List existing ADRs and extract `Status`, `Layer`, `Depends On`, and `## Summary` for each.
     - Apply the **3-Criteria Sparse ADR Gate** to candidate decisions and reject trivial choices before creating files.
     - Assign the next sequential 4-digit ID (`ADR-0001`, `ADR-0002`).
   - **Output**: Confirmed ADR candidate list and existing stance inventory (`State Ownership`, `Interface Contracts`, `Budgets`, `Forbidden Patterns`).

2. **Check Upstream Dependencies & Stance Conflicts Before Drafting**
   - **Inputs**: Existing ADR summaries and stance inventory.
   - **Owner**: System Architect.
   - **Action**:
     - Verify the proposed decision does not silently contradict an accepted `State Ownership` or `Budget` stance.
     - Populate `Depends On` explicitly; write `UNKNOWN` for unresolved dependencies (never default `UNKNOWN` to `"None"`).
   - **Output**: Conflict-checked dependency list (`None | ADR-NNNN | UNKNOWN`).

3. **Draft Sparse ADR with Machine-Scannable Rules**
   - **Inputs**: Decision context, verified NFRs, and runtime compatibility constraints.
   - **Owner**: Decision Author.
   - **Action**:
     - Populate `templates/adr.md` with `Status: Proposed`, a crisp 2-sentence `## Summary`, and the 3-Criteria verification.
     - Contrast Option A (Simplest Baseline) against alternatives, include an ASCII mechanism diagram, and write `### Implementation Guidelines` strictly as enforceable `"must"` and `"must never"` directives.
     - Record performance budgets and a falsifiable validation command.
   - **Output**: `docs/architecture/adr/adr-NNNN-<slug>.md` in `Proposed` state.

4. **Execute Independent Traceability, Conflict & DAG Review**
   - **Inputs**: Complete PRD/NFR denominator (`N_reqs`) and all ADRs (`N_adrs`).
   - **Owner**: Independent Reviewer (separate pass from author).
   - **Action**:
     - Map every requirement to `Covered (Accepted)`, `Covered (Proposed)` (caps verdict at `CONCERNS`), `Partial`, `Gap`, or `Not assessed`.
     - Run pairwise checks across all 6 Cross-ADR Conflict Classes.
     - Run deterministic topological sort on `Depends On` edges, flagging `CYCLE:`, `BLOCKED_BY_CYCLE:`, `NO_DEPS_SECTION:`, and `UNFILLED_DEPS:`.
     - Execute a **3-State Platform Sync Check** (`Found` / `None Found` / `NOT ASSESSED`) verifying stack version constraints against pinned lockfiles.
   - **Output**: Traceability matrix and review verdict (`PASS | CONCERNS | NOT ASSESSED | FAIL`).

5. **Run Explicit Acceptance Gate & Extract Control Manifest**
   - **Inputs**: Reviewed `Proposed` ADRs with `0` cycles and `0` blocking conflicts.
   - **Owner**: Technical Director / Lead Architect.
   - **Action**:
     - Transition approved ADRs from `Proposed` to `Accepted` with updated `Last Verified` date.
     - Distinguish malformed states (`0` ADRs vs. `0` Accepted ADRs vs. missing `Status` header).
     - Generate `control-manifest.md` exclusively from `Accepted` ADRs across four channels: `Decision` -> `Must-Do`, `Alternatives Considered` -> `Never-Do` + reason, `Performance Implications` -> `Budgets`, and `Platform Compatibility` -> `Pinned/Deprecated APIs` scoped strictly to the active stack.
   - **Output**: Accepted ADRs and updated `docs/architecture/control-manifest.md` stamped with `Manifest Version`.

6. **Condensation & Drift Audit Pass**
   - **Inputs**: Draft `docs/architecture/control-manifest.md` and `Accepted` ADRs.
   - **Owner**: Lead Engineer.
   - **Action**:
     - Delete every speculative, generic, or duplicated paragraph inside `docs/architecture/control-manifest.md`.
     - Confirm every rule fits in a compact table row citing `[ADR-NNNN]`, verify `Last Updated == Manifest Version`, and confirm zero `Proposed` ADRs block Phase 3A unlock.
   - **Output**: Compact, high-signal `docs/architecture/control-manifest.md` ready for Phase 3B implementation.

---

## 3. Reusable Artifact & Template

This module owns two paired templates inside `skills/system-data-architecture/templates/`:
- [templates/adr.md](../templates/adr.md) -> `docs/architecture/adr/adr-NNNN-<slug>.md` — Sparse decision record with `Summary`, 3-criteria check, Option A comparison, and machine-extractable `Implementation Guidelines`.
- [templates/control-manifest.md](../templates/control-manifest.md) -> `docs/architecture/control-manifest.md` — Flat programmer rule sheet enforcing layer dependency direction, `Must-Do` / `Never-Do` tables, source-of-truth paths, and runtime ceilings.

### 3.1 Field-by-Field Contract

| Artifact | Mandatory Contract Fields | Drift & Integrity Invariant |
|---|---|---|
| **ADR (`docs/architecture/adr/adr-NNNN-*.md`)** | `Status`, `Date`, `Last Verified`, `Layer`, `Depends On`, `Requirements Addressed`, `Summary` (2 sentences), `Implementation Guidelines`, `Validation Criteria` | `Status: Accepted` invalid if any `Depends On` is `Proposed` or `UNKNOWN` |
| **Control Manifest (`docs/architecture/control-manifest.md`)** | `Manifest Version`, `Last Updated`, `ADRs Covered`, `ADRs Excluded & Status`, Layer Import Matrix, Layer `Must-Do`/`Never-Do` Tables, Shared Contract Paths, Runtime Ceilings | Every rule row cites `[ADR-NNNN]`; zero narrative `Context` prose copied from ADRs |

### 3.2 Four-Channel Manifest Extraction Rule

When compiling `control-manifest.md` from `Accepted` ADRs, copy only four machine-actionable channels and drop all narrative background:
1. **`Decision` & `Implementation Guidelines`** -> Layer `Must-Do` directives with explicit `[ADR-NNNN]` citation.
2. **`Alternatives Considered`** -> Layer `Never-Do` bans plus one-clause failure reason.
3. **`Performance Implications`** -> Quantitative latency, memory, pool, and payload ceilings.
4. **`Runtime Compatibility`** -> Active-stack deprecated/pinned API constraints (omit entries unrelated to the repo's stack).

### 3.3 Traceability Matrix Status Codes

```text
Covered (Accepted)  -> Full green coverage; unlocks Phase 3A
Covered (Proposed)  -> Unaccepted ADR; caps review verdict at CONCERNS
Partial             -> Sub-requirements remain; requires follow-up slice or ADR
Gap                 -> Unaddressed PRD/NFR item; triggers FAIL on Foundation/Core
Not assessed        -> Missing input or unverified constraint; forces NOT ASSESSED
```

---

## 4. Verification Checklist

- [ ] Every ADR satisfies all three sparse-ADR criteria before creation.
  - Confirmed hard to reverse, surprising without context, and a real trade-off.
- [ ] Every ADR includes a 2-sentence `Summary` and explicit metadata headers.
  - `Status`, `Layer`, `Depends On`, and `Requirements Addressed` are populated.
- [ ] All Foundation and Core ADRs reached `Status: Accepted` before Phase 3A.
  - Zero `Proposed` ADRs block foundational implementation work.
- [ ] Dependency graph across all `Depends On` edges is strictly acyclic.
  - Topological sort finds zero cycles and zero `UNKNOWN` links.
- [ ] Independent traceability review checked `100%` of PRD/NFR items honestly.
  - Unverified scope reports `NOT ASSESSED` rather than masking as `PASS`.
- [ ] Pairwise check confirmed zero cross-ADR conflicts across all six classes.
  - Data ownership, contracts, budgets, patterns, cycles, and state authority verified.
- [ ] `control-manifest.md` extracts rules solely from `Accepted` ADRs.
  - Excluded `Proposed` and `Deprecated` records are listed explicitly.
- [ ] `control-manifest.md` stamps current `Manifest Version` without narrative bloat.
  - Every rule row cites `[ADR-NNNN]` and deletes generic filler.

---

## 5. Hard Quality Gate

Gate decision follows **`FAIL > CONCERNS > NOT ASSESSED > PASS`**:

- **PASS**: `0` Foundation/Core requirement gaps, `0` cross-ADR conflicts, `0` dependency cycles, all Foundation ADRs `Accepted`, `control-manifest.md` `Manifest Version` current, and the suite gate + DAG check commands exit `0`.
- **CONCERNS**: Non-critical Feature requirements rely on `Proposed` ADRs or have minor partial coverage while all Foundation ADRs are `Accepted` and acyclic.
- **NOT ASSESSED**: Requirements baseline, `docs/architecture/architecture.md`, or runtime compatibility checks were missing or unread — never emit `PASS` on unexamined scope.
- **FAIL**: Any Foundation requirement unaddressed, any `Accepted` ADR depending on a `Proposed` or `UNKNOWN` ADR, any cycle in `Depends On`, any unresolved cross-ADR conflict, or a stale/empty `docs/architecture/control-manifest.md` while Phase 3B implementation proceeds.
- **Drift Rule**: Any newly accepted ADR must immediately trigger a `docs/architecture/control-manifest.md` version bump before feature tickets resume.

Run standalone ADR/manifest verification (and suite-level gate checks when running inside the full `appnwebsite-skill` suite):

```bash
# Standalone project-level verification (no parent-suite scripts required):
python3 -c "import pathlib, re, sys; adrs=sorted(pathlib.Path('docs/architecture/adr').glob('adr-*.md')); cm=pathlib.Path('docs/architecture/control-manifest.md').is_file(); print('ADRs:', len(adrs), 'ControlManifest:', cm); [print(p.name, re.findall(r'(?m)^- \*\*(?:Status|Depends On)\*\*:.*', p.read_text())) for p in adrs]; bad=[p.name for p in adrs if not re.search(r'(?im)^- \*\*Status\*\*:\s*`?Accepted`?', p.read_text())]; sys.exit(1 if not adrs or not cm or bad else 0)"

# When running inside the full appnwebsite-skill suite:
python3 scripts/check_spiral_gates.py --stage foundation --strict --json
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **ADR Spam (Paperwork Bloat)** | ADRs for local helpers or formatting drown real constraints in noise | `> 10` MVP ADRs on naming or linters | Apply 3-Criteria Sparse Gate; use linter configs |
| **Vacuous Dependency Pass** | Defaulting unverified `Depends On` to `"None"` hides ordering bugs | `Depends On: None` despite relying on auth/DB ADRs | Mark unresolved links `UNKNOWN`; block acceptance |
| **`Proposed` Treated as `Covered`** | Coding against unaccepted ADRs triggers rework upon rejection | Manifest cites an ADR still marked `Proposed` | Cap review at `CONCERNS`; block manifest extraction |
| **Silent `NOT ASSESSED` as `PASS`** | Missing baselines masked as `PASS` create false Phase 3A confidence | Review emits `PASS` with `0` mapped requirements | Emit `NOT ASSESSED` whenever inputs are absent |
| **Bloated Essay Control Manifest** | Copying narrative `Context` into `control-manifest.md` burns tokens | Manifest exceeds `150` lines of ADR prose | Extract only `Must-Do`, `Never-Do`, `Budgets`, `Pinned APIs` |
| **Reviving Deprecated ADRs** | Editing superseded records back to `Accepted` destroys audit history | Git diff alters old ADR status instead of adding new | Leave old ADRs immutable; author new `ADR-NNNN` |

- **Review Discipline**: Always separate ADR authoring from traceability review so blind spots surface before Phase 3B coding starts.
- **Manifest Freshness**: Re-run manifest extraction immediately after any ADR status change.
