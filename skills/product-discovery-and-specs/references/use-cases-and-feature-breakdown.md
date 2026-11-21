# Structured Use Cases, Vertical Epics, and Feature Breakdown

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

Even a crisp PRD stalls when decomposed into horizontal technical layers
(`"build all database tables first, all APIs second, all UI screens last"`) or
bloated into 50 micro-tickets for two-hour scaffolding chores.

True product velocity comes from vertical slicing. Structured use cases (`UC-NNN`)
capture complete actor-system interactions including alternate and failure recovery
paths, while dependency-ordered epics (`EP-NNN`) and typed stories (`ST-NNN`)
deliver thin, end-to-end testable value gated by **PR-EPIC Realism** and
**QL-STORY-READY Testability** checks.

---

## 1. Decision Framework

### 1.1 Vertical Slice vs. Horizontal Layer Slicing

Every epic and story MUST trace a thin vertical cut through the stack
(`Schema/State -> Domain Logic -> API Boundary -> UI/Feedback -> Automated Test`) so
each completed slice produces verifiable user or contract value.

- **Horizontal Breakdown (Rejected)**:
  `[EP-1 All DB Tables] -> [EP-2 All API Routes] -> [EP-3 All UI Pages]` leaves zero
  runnable behavior until the end of the Spiral and hides contract mismatches.
- **Vertical Breakdown (Mandatory)**:
  `[ST-001 Sign-In Slice: User row + Auth logic + POST /login + Form + Integration Test]`
  ships runnable, testable value from day one.

### 1.2 Rigor-Tier Breakdown & Story Granularity Matrix

Scale epic ceremony, story granularity, and producer/QA gates directly to the active
Spiral rigor tier:

| Rigor Tier | Epic Structure | Story Granularity | Acceptance Criteria Format | Mandatory Readiness Gates |
|---|---|---|---|---|
| `minimal` | `1` MVP build-order list (`<= 3` thin slices); skip formal epic ceremony | `coarse` (`5–10` ACs per story; `1` story per MVP feature) | Concise `Given / When / Then` bullets per slice | Self-verified testability + explicit `Out of Scope` |
| `standard` | Dependency-ordered `EP-NNN` (`Foundation -> Core -> Feature -> Presentation`), max `3` epics | `balanced` (`2–4` ACs per story; `0.5–2` days / single session) | `Given / When / Then / Edge Cases` or `Setup / Verify / Pass` | **PR-EPIC Realism** + **QL-STORY-READY** (`>= 1` pass) |
| `full` | Multi-epic dependency DAG + strict `Accepted` ADR coverage tracking | `balanced` or `fine` (`1` AC per story for high-risk logic/security) | Full boundary/concurrency ACs + `Consumes / Produces` | **PR-EPIC** + **QL-STORY-READY**; `Proposed` ADR forces `Blocked` |

### 1.3 Story Type & Required Verification Evidence Matrix

Classify every story by its highest-risk dimension when multiple layers change
together (`Logic > Integration > Config/Data > Visual/Feel > UI`):

| Story Type | Primary Risk Profile | Required Proof Path (`tests/` or Verification) |
|---|---|---|
| `Logic` | Domain state transitions, financial math, validation, auth rules | Deterministic unit tests covering boundaries and edge invariants |
| `Integration` | Database persistence, HTTP/webhook contracts, external boundaries | Integration tests against real local DB / contract mocks (`2xx/4xx/5xx`) |
| `Config/Data` | Migrations, seeds, env validation, token/build pipeline | Idempotent up/down migration check + schema/lint smoke test |
| `UI` | Form wiring, keyboard navigation, loading/empty/error states | Component/Playwright interaction test (`Setup / Verify / Pass condition`) |
| `Visual/Feel` | Layout geometry, responsive breakpoints, motion, design-token parity | Multi-viewport visual inspection + zero layout shift (`CLS`) check |

### 1.4 Radical Simplicity ("Least Code, Highest Craft") Breakdown Rules

Apply strict **Complexity Budgeting & Task Right-Sizing** before committing stories
to a backlog:

- **Simplicity Q1 (Spiral 1 Cap)**: Cap Spiral 1 at `<= 3` thin epics. If a
  breakdown exceeds 3 epics or 12 stories for an MVP, cut lower-priority features
  back to `NG-NNN` instead of shrinking stories into fragments.
- **Simplicity Q2 (Micro-Story Deletion)**: Fold `< 2`-hour boilerplate chores
  (creating a directory, adding one env variable, installing one package) directly
  into the first vertical story that consumes them. Never create standalone
  `"Setup X"` ticket bloat.
- **Simplicity Q3 (Upper Size Ceiling)**: Split any story estimated `> 2–3` days or
  containing `>= 2` independent failure boundaries into two cohesive vertical slices
  (`ST-001a`, `ST-001b`).
- **Hollow-Line Ban**: Explicitly forbid placeholder acceptance criteria such as
  `"handle edge cases"`, `"appropriate validation"`, or `"works as expected"`.

---

## 2. Step-by-Step Workflow

1. **Author Structured Use Cases (`UC-NNN`)**
   - *Inputs*: `docs/product/prd.md`, `docs/product/GLOSSARY.md`.
   - *Output*: `docs/product/use-cases.md`.
   - *Owner*: Product / Systems Analyst | *Tool*:
     [use-case-spec.md](../templates/use-case-spec.md).
   - For every `P0` and `P1` requirement (`FR-NNN`), draft one structured `UC-NNN`
     detailing:
     - `Primary & Secondary Actors` and observable `Preconditions`;
     - exact `Trigger` and numbered `Main Success Flow`;
     - `Alternative Flows (A1..An)` and `Exception/Failure Flows (E1..En)` with
       rollback state;
     - verifiable `Postconditions`.
   - Cross-reference `FR-NNN` and `NFR-NNN` IDs instead of repeating PRD prose
     (Token Economy: single source of truth).
   - Inspect every Main Flow step for invalid input, duplicate submit, permission
     denial, and timeout triggers.

2. **Group into Dependency-Ordered Vertical Epics (`EP-NNN`)**
   - *Inputs*: `use-cases.md`, `architecture.md` / ADRs once Phase 3A begins.
   - *Output*: Part B of `docs/product/feature-breakdown.md`.
   - *Owner*: Tech Lead / PM | *Tool*: Dependency layering.
   - Order epics strictly by dependency layer:
     - `Foundation` (auth/workspace boundary and walking skeleton);
     - `Core` (primary domain engine);
     - `Feature` (secondary user workflows);
     - `Presentation` (visual polish and marketing surfaces).
   - Trace each `EP-NNN` to `FR-NNN` and `UC-NNN` IDs and link governing
     Architecture Decision Records (`ADR-NNNN`).
   - Enforce **Strict ADR Traceability**: only `Accepted` ADRs satisfy governance;
     any epic depending on a `Proposed` or missing ADR remains untraced and marks
     downstream stories `Blocked`.

3. **Run the `PR-EPIC` Realism & Scope-Cut Gate**
   - *Inputs*: `EP-NNN` table, team capacity/timeline.
   - *Output*: `PR-EPIC Verdict`.
   - *Owner*: Producer / Tech Lead | *Tool*: Realism audit.
   - Judge whether epic count and estimates fit realistically inside the Spiral
     window, returning `REALISTIC | CONCERNS | UNREALISTIC | NOT ASSESSED`.
   - **No Silent Defaults Rule**: When capacity or timeline baseline is missing,
     emit `NOT ASSESSED` — NEVER default silently to `REALISTIC`.
   - If `UNREALISTIC`, execute an immediate **Scope-Cut Pass** moving `P1/P2`
     features into `SP-<N+1>` rather than shrinking QA or Phase 3A foundation time.

4. **Slice Epics into Typed Vertical Stories (`ST-NNN`)**
   - *Inputs*: `EP-NNN`, `use-cases.md`.
   - *Output*: Part C of `docs/product/feature-breakdown.md`.
   - *Owner*: Engineering Lead | *Tool*: Incremental disk write.
   - Decompose each `REALISTIC` epic into `S` (`0.5–1d`) or `M` (`1–2d`) vertical
     stories, assigning the highest-risk `Story Type`.
   - Declare exact `Consumes` (upstream tables, schemas, endpoints) and `Produces`
     (persisted state, payloads, UI states) interfaces so parallel workers never
     collide.
   - Specify explicit `Out of Scope` bullets per story naming neighboring stories
     (`"Bulk CSV export handled in ST-006"`) and `Dependencies` (`Blocked By` /
     `Unlocks`).
   - Author falsifiable ACs using `Given / When / Then / Edge Cases` for `Logic`
     /`Integration` stories and `Setup / Verify / Pass condition` for `UI`
     /`Visual/Feel` stories.

5. **Execute `QL-STORY-READY` Testability Gate & Story Condensation Pass**
   - *Inputs*: Draft `feature-breakdown.md`.
   - *Output*: Locked `Ready`/`Blocked` story backlog.
   - *Owner*: QA Lead | *Tool*: Testability audit.
   - Review every story's ACs BEFORE implementation starts, returning
     `ADEQUATE | GAPS | INADEQUATE | NOT ASSESSED`.
   - Rewrite any vague AC into concrete input/boundary assertions, and mark any
     story touching an unsettled decision or `Proposed` ADR as `Status: Blocked`
     citing the exact blocker.
   - **Condensation Pass**: Delete duplicate scaffolding tickets, fold `< 2h`
     micro-tasks into consumer slices, strip redundant PRD text, and write
     `docs/product/use-cases.md` and `docs/product/feature-breakdown.md` cleanly to
     disk.

### Worked Example: Collapsing Micro-Stories into One Clean Vertical Slice

- **Bloated Breakdown (5 tickets)**: `ST-1 Create uploads folder`,
  `ST-2 Add CSV parser lib`, `ST-3 Build POST /import endpoint`,
  `ST-4 Add upload button`, `ST-5 Write upload test`.
- **Condensed Vertical Slice (1 `M` story)**: `ST-001 Invoice CSV Import Slice`
  (`Integration`, `1.5d`) delivering validated `POST /import` + atomic DB insert +
  upload dropzone + integration test (`<= 25 MB` pass + `> 25 MB` `413` error).

---

## 3. Reusable Artifact & Template

Use cases (`docs/product/use-cases.md`) and vertical feature breakdowns
(`docs/product/feature-breakdown.md`) share the unified schema in
[use-case-spec.md](../templates/use-case-spec.md). Follow these authoring
discipline rules:
- Write `Part A` to `docs/product/use-cases.md` and `Parts B–C` to
  `docs/product/feature-breakdown.md` incrementally.
- Link `FR-NNN` and `UC-NNN` IDs directly rather than repeating functional
  requirement tables.
- Record explicit `Consumes` and `Produces` interfaces on every `Ready` story so
  Phase 3B lanes parallelize safely.

| Component / Field | Location | Mandatory Contract |
|---|---|---|
| `Header & Gate Verdicts` | Top Table | `Scope`, `Spiral ID`, `Rigor Tier`, `Story Granularity`, `PR-EPIC Verdict`, `QL-STORY-READY Verdict` |
| `Use Case Record (UC-NNN)` | Part A | `Linked FR/NFR`, `Actors`, `Preconditions`, `Trigger`, `Main Flow`, `Alternative Flows`, `Exception Flows`, `Postconditions` |
| `Vertical Epic Table (EP-NNN)` | Part B | `Epic ID`, `Layer`, `Vertical Scope`, `Linked FR/UC`, `Governing ADR & Status`, `Effort`, `PR-EPIC Verdict` |
| `Story Card (ST-NNN)` | Part C | `Epic`, `Type`, `Estimate (S|M)`, `Status (Ready|Blocked)`, `Dependencies`, `Consumes/Produces`, `Out of Scope`, `Test Evidence`, `ACs` |

---

## 4. Verification Checklist

- [ ] Every `P0` and `P1` requirement (`FR-NNN`) traces to at least one `UC-NNN` use case and one `ST-NNN` story.
- [ ] Every `UC-NNN` defines `Preconditions`, `Trigger`, numbered `Main Success Flow`, `Alternative Flows`, `Exception Flows`, and `Postconditions`.
- [ ] All epics slice vertically (`Foundation -> Core -> Feature -> Presentation`) instead of grouping pure DB or pure UI layers separately.
- [ ] Every story stays within `<= 2` days (`S` or `M`), folds `< 2h` scaffolding into its owning slice, and declares explicit `Out of Scope` boundaries.
- [ ] Every `Logic` and `Integration` story uses deterministic `Given / When / Then` acceptance criteria free of hollow phrases.
- [ ] `PR-EPIC` and `QL-STORY-READY` verdicts reflect real evidence (`NOT ASSESSED` if missing capacity/ACs; `Blocked` if governing ADRs remain `Proposed`).

---

## 5. Hard Quality Gate

Breakdown exits Q1/Q2 into Phase 3A/3B **ONLY** when binary conditions evaluate to
`PASS` (`FAIL > CONCERNS > NOT ASSESSED > PASS`):

- **PASS**: `docs/product/use-cases.md` and `docs/product/feature-breakdown.md`
  exist with zero stub tokens (`TODO`, `TBD`, `FIXME`, `[placeholder]`):
  - every `UC-NNN` defines `Preconditions`, `Exception`, and `Postconditions`;
  - epics slice vertically in dependency order (`<= 3` epics in Spiral 1);
  - every `Ready` story declares testable ACs, `Out of Scope`, `Consumes`
    /`Produces`, and `ADEQUATE` testability;
  - governing ADRs for `Ready` stories are `Accepted`.
- **CONCERNS**: `P1` stories carry minor estimate variance (`S` vs `M`) while all
  `P0` slices pass `QL-STORY-READY`.
- **NOT ASSESSED**: Capacity/timeline missing (`PR-EPIC: NOT ASSESSED`) or story ACs
  awaiting QA review (`QL-STORY-READY: NOT ASSESSED`).
- **FAIL**: Horizontal layer epics, use cases missing `Exception` flows, stories
  `> 3` days or `< 2h` micro-tickets, `Ready` status on `Proposed` ADRs, or hollow
  ACs.

```bash
python3 - <<'PY'
from pathlib import Path
import re, sys

uc = Path("docs/product/use-cases.md")
fb = Path("docs/product/feature-breakdown.md")
for p in (uc, fb):
    if not p.is_file():
        print(f"FAIL: missing {p}"); sys.exit(1)
    txt = p.read_text(encoding="utf-8")
    for pat in (r"\bTODO\b", r"\bTBD\b", r"\bFIXME\b", r"\[placeholder\]", r"\bLorem ipsum\b"):
        if re.search(pat, txt):
            print(f"FAIL: {p} contains stub marker {pat!r}"); sys.exit(1)

uc_txt = uc.read_text(encoding="utf-8")
fb_txt = fb.read_text(encoding="utf-8")
for req in ("Preconditions", "Exception", "Postconditions"):
    if req not in uc_txt:
        print(f"FAIL: {uc} missing {req}"); sys.exit(1)
for req in ("Out of Scope", "Consumes", "Produces"):
    if req not in fb_txt:
        print(f"FAIL: {fb} missing {req}"); sys.exit(1)
if not (("Given" in fb_txt and "When" in fb_txt and "Then" in fb_txt) or ("Setup" in fb_txt and "Verify" in fb_txt)):
    print("FAIL: feature-breakdown.md missing testable ACs"); sys.exit(1)
print("PASS: Use Cases & Vertical Feature Breakdown gate satisfied.")
PY
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Horizontal Layer Epics** | Produces zero integrated value for weeks and hides schema-to-UI bugs until late Spiral | Epics titled `"Database Setup"`, `"Backend APIs"`, `"Frontend Pages"` | Slice vertically end-to-end (`Schema -> Logic -> API -> UI -> Test`) |
| **Happy-Path Use Cases** | Leaves rollback, permission errors, and partial failures undefined until outages hit | `UC-NNN` has only a Main Flow with zero `A1` or `E1` paths | Add concrete `Alternative` and `Exception` flows with recovery postconditions |
| **Untestable Acceptance Criteria** | Allows defective code to pass review because no falsifiable assertion exists | ACs state `"handles edge cases"` or `"appropriate validation"` | Write `Given / When / Then` with exact inputs, status codes, and state checks |
| **Micro-Story Scaffolding Bloat** | Burns planning tokens and adds dependency noise for 30-minute chores | Backlog includes `"Create repo folder"` or `"Add logger config"` | Fold `< 2h` setup directly into the first vertical story that consumes it |
| **Premature `Ready` on `Proposed` ADRs** | Sends engineers building on unapproved architecture choices likely to change | Story marked `Ready` while linked `ADR-NNNN` still reads `Proposed` | Mark story `Status: Blocked` citing the unresolved ADR until `Accepted` |
| **Missing `Out of Scope` Per Story** | Parallel workers implement overlapping features or gold-plate sibling work | Story cards omit an explicit `Out of Scope` boundary | Name excluded sibling behaviors or `NG-NNN` items on every `ST-NNN` |
