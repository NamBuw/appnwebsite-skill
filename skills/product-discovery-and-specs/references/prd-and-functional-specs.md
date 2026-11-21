# PRDs, Functional Specifications, and Domain Glossaries

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

A Product Requirements Document (PRD) succeeds only when an engineer or QA lead can
build and test every behavior without inventing silent assumptions. When PRDs omit
explicit non-goals, bury implicit edge behaviors, or overload domain nouns like
`"account"` or `"user"`, downstream teams either guess inconsistently or gold-plate
speculative configurability.

This module defines how to author crisp, falsifiable functional specs (`FR-NNN`),
explicit scope boundaries (`NG-NNN`), a clean implementation-free `GLOSSARY.md`, and
an ambiguity-free Readiness Gate.

---

## 1. Decision Framework

### 1.1 PRD Depth Scaling by Rigor Tier

Match specification ceremony to project blast radius without ever relaxing
testability or explicit non-goals:

| Rigor Tier | Spec Scope | Glossary & Edge Matrix | Ambiguity & Sign-Off Bar |
|---|---|---|---|
| `minimal` | 1-page `prd.md`: Pitch, **Option A** Wedge, `P0` `FR-NNN` table, `>= 3` `NG-NNN` | Inline `3–6` canonical terms; `P0` empty + invalid-input rows | `0` open `P0` blockers; self-verified readiness check |
| `standard` | Full `prd.md`: Brief, `FR-NNN` (`P0/P1`) + implicit rules, `NG-NNN`, Edge catalog | Dedicated `docs/product/GLOSSARY.md` (`0` tech details); 5-vector edge table | Ambiguity ledger (`Clarifications`, `Missing Info`, `Conflicts`) at `0` `OPEN` |
| `full` | Multi-actor `FR-NNN` matrix, compliance rules, cross-system contracts | Cross-checked `GLOSSARY.md` audited vs. repo; exhaustive recovery states | Independent Builder Check + quality review score `>= 7/10` |

### 1.2 Priority & Testability Classification Matrix

Every functional requirement (`FR-NNN`) MUST carry one priority tier and pass the
**Binary Testability Rule** (rejecting untestable adjectives like `"fast"`,
`"intuitive"`, `"clean"`, or `"seamless"` unless bound to numeric metrics or
observable actions):

| Priority | Inclusion Rule | Treatment in Spiral 1 | Testability Requirement |
|---|---|---|---|
| `P0` (Critical) | Required for Option A Wedge, data integrity, auth/PII, or compliance | **Must ship**; blocks Spiral exit | Exact trigger, observable state transition, error contract, `NFR` link |
| `P1` (High) | High leverage inside Option A workflow; clear pain reduction | Ships unless capacity cuts cleanly to `SP-02` | Observable `When ... must ...` behavior + boundary rule |
| `P2` (Medium) | Convenience feature, secondary export, or preference toggle | **Default Cut to `NG-NNN`** unless `< 2h` and 0 deps | Retained only if explicitly justified against Simplicity Q1–Q3 |
| `P3` (Out of Scope) | Speculative customization or unvalidated edge tooling | Logged in `NG-NNN` Non-Goals table | Simplicity/YAGNI rationale + target future Spiral (`SP-<N+1>`) |

### 1.3 Implicit Requirement Expansion Rule

Human briefs describe the happy path and leave defensive behavior unstated. Expand
mechanical implicit behaviors for every `P0` /`P1` capability while keeping feature
surface minimal:

- **File Uploads**: Specifying `"upload CSV up to 25 MB"` implicitly requires
  rejecting `> 25 MB` (`413` / inline guidance), rejecting invalid MIME/magic bytes,
  displaying progress above `1 MB`, and supporting safe cancellation without orphan
  partial writes.
- **Search & Filter Lists**: Specifying `"search invoices"` implicitly requires
  defining empty-query defaults, zero-match empty states with reset actions, maximum
  page size, and deterministic default sort order.
- **Destructive Actions**: Specifying `"delete workspace"` implicitly requires
  naming the target object in confirmation, enforcing owner authorization, and
  defining post-delete redirect state.

### 1.4 Radical Simplicity & Scope-Condensation Gate

Overengineering enters codebases first as unchecked PRD wishlists. Before freezing
`docs/product/prd.md`, enforce three **Least Code, Highest Craft** rules:

- **Simplicity Q1 (Configuration Elimination)**: Delete `"admin settings screens"`
  for parameters with a single sensible default covering `>= 90%` of users; keep
  constants in code until genuine divergence occurs.
- **Simplicity Q2 (Zero Duplicate Prose)**: Never duplicate database schemas, REST
  routes, or UI step-by-step instructions inside `prd.md`. Reference canonical
  `GLOSSARY.md` terms and assign stable `FR-NNN` IDs.
- **Simplicity Q3 (Explicit Edge Exclusion)**: When complex edge cases (e.g.,
  offline merge conflicts, multi-currency FX) are excluded from Spiral 1, log them
  explicitly in `NG-NNN` so developers do not build defensive scaffolding for
  unsupported scenarios.

---

## 2. Step-by-Step Workflow

1. **Extract Core Domain Terms & Lock `GLOSSARY.md`**
   - *Inputs*: Discovery Brief, brownfield codebase.
   - *Output*: `docs/product/GLOSSARY.md`.
   - *Owner*: PM / Domain Modeler | *Tool*: [prd-spec.md](../templates/prd-spec.md).
   - Create `docs/product/GLOSSARY.md` lazily as soon as the first core domain
     boundary settles.
   - Audit overloaded nouns (`"account"`, `"user"`, `"project"`) and separate
     distinct responsibilities:
     - separate billing `Customer` from authenticated `Member` and isolation
       boundary `Workspace`;
     - challenge synonyms across sections so one canonical noun maps to one concept.
   - In brownfield projects, cross-check terms against existing models and document
     deliberate renames.
   - **Strict Isolation Rule**: Keep `GLOSSARY.md` completely free of implementation
     details — zero SQL column types, ORM classes, API routes, or UI components.

2. **Author Numbered Functional Requirements (`FR-NNN`) with Implicit Criteria**
   - *Inputs*: Settled Wedge, `GLOSSARY.md`.
   - *Output*: Section 3 of `docs/product/prd.md`.
   - *Owner*: Product Lead | *Tool*: Incremental disk write.
   - Phrase every `FR-NNN` atomically using canonical glossary nouns:
     `When [trigger/actor], the system must [observable behavior] within [constraint].`
   - Assign `P0–P3` priority and record concrete implicit behaviors (size caps,
     progress feedback, cancellation, auth checks) alongside each row.
   - Cross-reference each `FR-NNN` to its corresponding `UC-NNN` and governing
     `NFR-NNN`.

3. **Document Explicit Non-Goals & Scope Cuts (`NG-NNN`)**
   - *Inputs*: OST deferred items, `P2/P3` cuts.
   - *Output*: Section 4 of `docs/product/prd.md`.
   - *Owner*: Product Lead | *Tool*: Wedge Ablation check.
   - Record at least `3` concrete `NG-NNN` entries covering:
     - deferred product features lacking `P0` demand;
     - explicitly unsupported operational flows;
     - intentionally unhandled edge cases deferred out of Spiral 1.
   - Cite the exact Simplicity/YAGNI rationale and target Spiral (`SP-02`, `SP-03`,
     or `Deferred`).

4. **Build the Edge-Case & Domain Error Semantics Catalog**
   - *Inputs*: `FR-NNN` table.
   - *Output*: Section 5 of `docs/product/prd.md`.
   - *Owner*: PM + QA Lead | *Tool*: 5-vector stress matrix.
   - Map every `P0` and `P1` requirement across five failure vectors:
     - **Empty / Zero State**: clean zero-data presentation plus primary action;
     - **Size / Length Boundary**: exact max bytes, characters, or rows rejected
       deterministically;
     - **Concurrent / Duplicate Submission**: idempotent handling preventing
       duplicate charges or records;
     - **Authorization / Ownership Denial**: explicit access rejection without
       leaking tenant existence;
     - **Downstream Dependency Failure**: atomic rollback and user-visible retry
       path.
   - Forbid exposing raw stack traces, SQL errors, or internal identifiers in
     user-facing error semantics.

5. **Run Ambiguity Triage, Condensation Pass & Builder Check**
   - *Inputs*: Draft `prd.md` + `GLOSSARY.md`.
   - *Output*: Locked `READY` PRD.
   - *Owner*: Independent Reviewer | *Tool*: Ambiguity ledger.
   - Classify open questions in Section 6 across three buckets:
     - **Clarifications Needed**: exact ambiguous phrase, question, impact, and
       Option A default;
     - **Missing Information**: exact missing policy and which downstream story ID
       it blocks;
     - **Conflicting Requirements**: exact pair (for example `FR-002` vs `FR-007`)
       and precedence decision.
   - **Condensation Pass**: Write sections incrementally to disk (Token Economy),
     merge overlapping `FR` rows, strip `P2` config toggles, and delete narrative
     duplicating Section 1 or `GLOSSARY.md`.
   - Complete an **Independent Builder Check** reading the spec cold; set
     `Status: LOCKED` and `Verdict: READY` only when
     `Blocking Open Items Count = 0`.

### Worked Example: Converting Vague Prose into a Testable `FR`

- **Vague Draft**: *"Users can easily upload invoice files and the system handles
  large files gracefully."*
- **Testable `FR-001` (`P0`)**: *"When an authenticated `Member` uploads a `.csv`
  file `<= 25 MB` to a `Workspace`, the system must parse rows atomically and return
  a match summary within `NFR-002` latency (`p95 <= 250ms` for metadata, async job
  above `1 MB`)."*
- **Implicit Behaviors Locked**: Reject `> 25 MB` (`413`), reject non-CSV magic
  bytes (`415`), show progress bar above `1 MB`, expose cancel button rolling back
  partial state.

---

## 3. Reusable Artifact & Template

Functional specs populate Sections 2–6 of [prd-spec.md](../templates/prd-spec.md)
(`docs/product/prd.md`) alongside `docs/product/GLOSSARY.md`. Follow these
token-economy and traceability conventions:
- Write `docs/product/GLOSSARY.md` once lazily and reference terms rather than
  redefining nouns inside every `FR-NNN`.
- Assign contiguous `FR-001..FR-NNN` and `NG-001..NG-NNN` IDs so `use-cases.md` and
  `architecture.md` link by ID without restating requirements.
- Maintain Section 6 (`Ambiguity & Clarification Ledger`) strictly until
  `Blocking Open Items Count = 0`.

| Section / Field | Cardinality | Contract & Validation Rule |
|---|---|---|
| `Metadata Header` | `1` table | `Product Name`, `Spiral ID`, `Rigor Tier`, `Status (DRAFT|REVIEW|LOCKED)`, `Owner`, UTC timestamp |
| `Domain Glossary Ref` | `>= 1` link + table | Links `docs/product/GLOSSARY.md`; `Canonical Term`, `Definition`, `Forbidden Aliases` (zero tech terms) |
| `Functional Requirements` | `>= 1` `FR-NNN` rows | `FR-ID`, `Priority (P0-P3)`, `Actor`, `Observable Requirement`, `Implicit Behaviors`, `Linked UC/NFR` |
| `Explicit Non-Goals` | `>= 3` `NG-NNN` rows | `NG-ID`, `Excluded Feature/Edge Case`, `Simplicity/YAGNI Rationale`, `Target Spiral` |
| `Edge & Error Catalog` | `>= 3` `EDGE-NNN` rows | `Scenario ID`, `Linked FR`, `Trigger/Boundary`, `Expected System State`, `User-Visible Recovery` |
| `Ambiguity Ledger` | `1` table + verdict | Tracks `Clarification`, `Missing Info`, and `Conflict`; `Blocking Open Items Count` equals `0` for `READY` |

---

## 4. Verification Checklist

- [ ] `docs/product/GLOSSARY.md` defines canonical domain terms, bans conflicting aliases, and omits all database, framework, or UI details.
- [ ] Every `FR-NNN` row declares `P0–P3` priority, canonical glossary terms, implicit mechanical behaviors, and testable outcomes.
- [ ] Zero subjective adjectives (`fast`, `easy`, `intuitive`, `scalable`, `user-friendly`) appear as standalone acceptance criteria without numeric bounds.
- [ ] At least three concrete `NG-NNN` Non-Goals explicitly exclude deferred features, unsupported flows, and deferred edge cases.
- [ ] Every `P0` flow covers empty state, bounds, duplicate submission, permission denial, and partial failure with recovery guidance.
- [ ] Condensation Pass deleted speculative `P2` configuration flags and duplicated prose across sections.
- [ ] Ambiguity Ledger reports `0` open blockers and passes an independent cold-reader Builder Check (`READY`).

---

## 5. Hard Quality Gate

PRD authoring advances to Architecture / Use Cases **ONLY** with `PASS` under
`FAIL > CONCERNS > NOT ASSESSED > PASS`:

- **PASS**: `docs/product/prd.md` and `docs/product/GLOSSARY.md` exist on disk with
  zero stub markers (`TODO`, `TBD`, `FIXME`, `[placeholder]`):
  - `FR-\d+` requirements and `>= 3` `NG-\d+` non-goals are populated;
  - `GLOSSARY.md` contains canonical domain definitions with zero technical leakage;
  - Edge/Error matrix covers all `P0` failure vectors;
  - Ambiguity Ledger has `0` open blockers and `Verdict: READY`.
- **CONCERNS**: Minor non-blocking `P1` clarification noted with an explicit Option
  A fallback and owner before Phase 3B.
- **NOT ASSESSED**: `GLOSSARY.md` missing on `standard` /`full` tier, or Builder
  Check verdict remains unset.
- **FAIL**: Zero `NG-NNN` non-goals, implementation details inside `GLOSSARY.md`,
  vague untestable `FR` prose, silent omission of error/empty states, or open
  `Missing Information` blocking `P0` scope.

```bash
python3 - <<'PY'
from pathlib import Path
import re, sys

prd = Path("docs/product/prd.md")
glossary = Path("docs/product/GLOSSARY.md")
if not prd.is_file():
    print("FAIL: missing docs/product/prd.md"); sys.exit(1)
if not glossary.is_file():
    print("FAIL: missing docs/product/GLOSSARY.md"); sys.exit(1)
text = prd.read_text(encoding="utf-8")
frs = set(re.findall(r"\bFR-\d{3}\b", text))
ngs = set(re.findall(r"\bNG-\d{3}\b", text))
vague = re.findall(r"\b(?:user-friendly|intuitive|seamless|fast|scalable)\b", text, re.I)
for pat in (r"\bTODO\b", r"\bTBD\b", r"\bFIXME\b", r"\[placeholder\]", r"\bLorem ipsum\b"):
    if re.search(pat, text):
        print(f"FAIL: stub marker {pat!r} found"); sys.exit(1)
verdict_ready = re.search(
    r"(?im)^\s*(?:-\s*\*\*|###?\s*)?.*verdict\*{0,2}\s*:\s*`?(?-i:READY)`?\b(?!\s*/)",
    text,
)
if len(frs) < 1 or len(ngs) < 3 or not verdict_ready or "Edge" not in text:
    print(f"FAIL: incomplete PRD (FR={len(frs)}, NG={len(ngs)}, ready={bool(verdict_ready)})"); sys.exit(1)
if vague:
    print(f"CONCERNS: untethered adjectives {sorted(set(vague))}")
print(f"PASS: PRD gate passed ({len(frs)} FRs, {len(ngs)} NGs).")
PY
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Subjective Requirement Adjectives** | Engineers and QA cannot write deterministic assertions for `"intuitive"` or `"fast"` | `FR` states `"system should be fast / easy / seamless"` with no units | Use observable state changes plus numeric `NFR` thresholds (`p95 <= 250ms`) |
| **Missing Non-Goals (`NG-NNN`)** | Unbounded scope invites silent feature creep and defensive overengineering mid-build | Section 4 is empty or relies on vague disclaimers | Log `>= 3` excluded features, flows, and edge cases with target Spiral IDs |
| **Implementation Bleed in `GLOSSARY.md`** | Couples domain vocabulary to transient database tables or frontend libraries | Glossary mentions `"users_table"`, `"JWT"`, `"Redis"`, or `"Redux"` | Define purely business concepts, ownership boundaries, and forbidden aliases |
| **Happy-Path-Only PRD** | Forces developers to invent silent behavior for duplicates, timeouts, and empty states | Zero coverage of empty state, `4xx/5xx` recovery, or idempotency | Map every `P0` flow through the 5-vector Edge & Error Semantics table |
| **Gold-Plated `P2` Config Flags** | Multiplies database columns, UI controls, and test permutations unnecessarily | `FR` adds `"admin toggles for X, Y, Z"` without validated user demand | Delete speculative settings; use one clean default until real divergence occurs |
| **Silent Term Overloading** | `"Account"` means billing customer in one rule and login user in another | Multiple `FR` rows swap `User`, `Member`, and `Account` inconsistently | Lock canonical terms in `GLOSSARY.md` and ban conflicting aliases |
