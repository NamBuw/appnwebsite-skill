# Plan-First Execution (`/plan`)

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

Plan-First Execution turns verified product specs and Phase 3A contracts into small, vertically sliced, test-first steps before mutating code.
It prevents mid-flight architectural drift while strictly blocking planning ceremony on trivial edits.

---

## 1. Decision Framework

### 1.1 Execution Mode & Plan Granularity Matrix

Choose the lightest planning mode that preserves safety and clarity:

| Scope & Risk Profile | Quantitative Threshold | Selected Path | Required Ceremony |
|---|---|---|---|
| **Trivial / Single-Slice** | `<= 2` files, `1` subsystem, `< 100` LOC, zero DB/API/auth change | **Direct (Skip `/plan`)** | Answer Simplicity Q1/Q2; run TDD + fresh check directly. |
| **Cohesive Multi-File Slice** | `3–8` files, `<= 5` tasks, sequential deps or shared context | **`/plan` + Inline Execution** | Survey -> `execution-plan.md` -> inline TDD + 1 fresh review. |
| **Large Multi-Slice Feature** | `> 5` tasks OR `>= 3` genuinely disjoint vertical slices | **`/plan` + `/teamwork`** | Survey -> `execution-plan.md` -> partition ownership & dispatch. |
| **Multi-Subsystem Scope** | `> 8` files OR `>= 2` independent subsystems | **Split Sub-Plans First** | Author one `execution-plan.md` per subsystem; never merge DAGs. |

### 1.2 Vertical Slicing & Task Sizing Thresholds

Every task must cut vertically through the stack so it ends in a runnable, tested increment:

| Size | File Count | Effort Window | Required Action |
|---|---|---|---|
| **`XS`** | `1` file | `5–15` min | Keep as one self-contained TDD task. |
| **`S`** | `1–2` files | `15–30` min | Standard vertical slice (implementation + co-located test). |
| **`M`** | `3–5` files | `30–60` min | Maximum single-task size; verify tight cohesion first. |
| **`L`** | `5–8` files | `> 60` min | **Mandatory split** into `2–3` smaller `S`/`M` tasks. |
| **`XL`** | `8+` files | Multi-hour | **Forbidden** in one task; split into sub-plans or slices. |

- **Compound Title Rule**: Any task title joining two behaviors with `"and"` must be split into two tasks.
- **Subsystem Independence Rule**: Separate unrelated domains with distinct storage or deploy cycles into separate plan files.

### 1.3 Simplest High-Craft & Anti-Overengineering Self-Interrogation

Before locking any task into `execution-plan.md`, verify Radical Simplicity:

1. **Plan Proportion Rule**:
   - Never write a plan longer than the code it describes.
   - Record only non-obvious decisions, exact signatures, and edge invariants an implementer cannot derive from codebase conventions.
2. **YAGNI & Rule of Three**:
   - Delete planned factory wrappers, single-use interfaces, or speculative switches unless `>= 3` concrete variants or an external port boundary exist today.
3. **Phase 3A Foundation Lock**:
   - Confirm schema migrations, domain types, API contracts, and UI tokens are settled before Task 1 writes code.

### 1.4 Worked Triage Examples (`Direct` vs. `/plan` vs. `/teamwork`)

- **Example A (`Direct`, Skip `/plan`)**: Fix a timezone offset bug in `formatInvoiceDate.ts` (`1` file, `12` LOC, `1` unit test). Exiting `/plan` saves ~2,000 planning tokens with equal test rigor.
- **Example B (`/plan` + Inline)**: Add signed webhook verification + retry table (`4` files, `3` sequential tasks). Sequential `progress.md` execution avoids worktree overhead.
- **Example C (`/plan` + `/teamwork`)**: Build billing webhooks, admin analytics, and email alerts (`11` files, `3` disjoint directories). Split or dispatch parallel lanes after `READY`.

---

## 2. Step-by-Step Workflow

1. **Read-Only Survey & Incomplete-Plan Guard**
   - **Owner**: Planner (Lead Agent).
   - **Inputs**: User request, PRD/spec, Phase 3A contracts, existing repository.
   - **Outputs**: Verified codebase inventory and collision check.
   - **Tools**: Read-only search (`rg`/`grep`), file reader, directory listing.
   - **Actions**:
     - Inspect existing modules, test conventions, and shared helpers without editing source files.
     - Scan `tasks/plan.md`, `.agents/teamwork/`, and `.superpowers/sdd/` for active incomplete plans with unchecked boxes.
     - Never overwrite an active unfinished plan silently; resume, archive explicitly, or isolate into a fresh run folder.

2. **Bottom-Up Dependency Graph & Vertical Slice Partition**
   - **Owner**: Planner.
   - **Inputs**: Survey notes, `data-model.md`, API specification.
   - **Outputs**: Bottom-up DAG, compact ASCII flow diagram, ordered vertical slices.
   - **Tools**: Read-only architecture inspection.
   - **Actions**:
     - Order dependencies strictly bottom-up:
       - `Schema & Migrations` -> `Shared Contracts & Types` -> `Domain Services & Endpoints` -> `UI Surfaces` -> `E2E Verification`.
     - Include a compact ASCII data-flow or state diagram for non-trivial flows, retries, or state machines.
     - Slice vertically so Task 1 delivers a minimal working end-to-end thread before later tasks layer edge cases.

3. **Lock `Global Constraints`, `Review Focus`, and Task Contracts**
   - **Owner**: Planner.
   - **Inputs**: Spec thresholds, security/UI rules, slice list.
   - **Outputs**: Complete draft `execution-plan.md`.
   - **Tools**: Template instantiation (`execution-plan.md` schema).
   - **Actions**:
     - Copy numeric constraints (latency budgets, coverage floors, font/icon bans, HTTP status codes) verbatim into `Global Constraints`.
     - Enumerate the **top 5 uncovered edge or failure classes** in `Review Focus`:
       - Malformed inputs, boundary limits, idempotency races, authorization boundaries, and downstream timeouts.
       - Attach each failure class to an owning task and named pinning test.
     - Specify per task: `Files (Create / Modify / Test)`, `Interfaces (Consumes / Produces)`, and 5 RED->GREEN steps with exact `Expected:` output.

4. **Plan Readiness & Self-Review Gate (`Story/Plan Readiness`)**
   - **Owner**: Planner (or independent Reviewer on `L` plans).
   - **Inputs**: Draft `execution-plan.md`, referenced spec and asset paths.
   - **Outputs**: Readiness verdict (`BLOCKED > NEEDS WORK > NOT ASSESSED > READY`) and alignment prompt.
   - **Tools**: Read-only path checks and 5-point self-review.
   - **Actions**:
     - Run the 5-point self-review across the full draft:
       - **Spec Coverage**: Every requirement maps to at least one task.
       - **Step Unambiguity**: Zero steps lack exact paths, symbols, or commands.
       - **Signature Parity**: Cross-task `Consumes` and `Produces` match verbatim.
       - **Review Focus Pinning**: All 5 failure modes have named pinning tests.
       - **Proportion & Simplicity**: Zero speculative wrappers or bloated code dumps.
     - Grade readiness across six groups (Design, Architecture, Scope, Open Questions, Assets, DoD) using strict precedence (`BLOCKED > NEEDS WORK > NOT ASSESSED > READY`; zero-scope drafts resolve to `NOT ASSESSED`).
     - Present the `READY` plan and execution mode (`Inline` vs `/teamwork`) for alignment before mutating code.

5. **Inline Ledgered Execution & Pre-Ship Deletion/Condensation Pass**
   - **Owner**: Implementer (when `Execution Approach = Inline`).
   - **Inputs**: Approved `execution-plan.md`, disk `progress.md`.
   - **Outputs**: Tested implementation, logged rulings, condensed final diff.
   - **Tools**: Test runner, compiler/linter, `git diff`.
   - **Actions**:
     - Run a **Pre-Flight Cross-Task Interface Conflict Scan** before Task 1 to catch signature or file collisions.
     - Execute tasks continuously (`task-start` -> `task-done` in `progress.md`) without noisy check-ins.
     - Log any codebase-forced adaptation immediately as `Ruling: <decision> — <rationale> — <cost if wrong>`.
     - Halt **only** on the four hard stops:
       1. Destructive or irreversible operations (data loss, schema drops).
       2. Security-sensitive boundary changes or permission overrides.
       3. External shared side effects (`git push`, deploy, package publish).
       4. A broken plan where continuing requires guessing.
     - Run a mandatory **Pre-Ship Deletion & Condensation Pass**:
       - Delete dead helpers, inline single-caller pass-through wrappers, and trim unused dependencies.
       - Re-run the full build and test suite **after** deletions (`exit 0`).
     - Close with one fresh-context whole-branch review grading findings by real user-facing effect and fixing valid defects in at most one RED->GREEN wave.

---

## 3. Reusable Artifact & Template

Instantiate [Execution Plan Template](../templates/execution-plan.md) to author the runtime artifact `execution-plan.md` (paired with `progress.md` during inline execution).

### 3.1 Execution Plan Section & Field Contract

| Section / Field | Type & Cardinality | Contract & Validation Rule |
|---|---|---|
| `Metadata Header` | Table (`8` required keys) | Locks `Plan ID`, `Feature / Scope`, `Spec Path`, `Phase 3A Gate Ref`, `Simplicity Record Ref`, `Execution Approach`, `Status`. |
| `1. Architecture & Data Flow` | Summary + ASCII diagram | 1-sentence goal, 2–3 sentence simplest high-craft summary, bottom-up DAG, fenced ASCII diagram. |
| `2. Global Constraints` | Bulleted verbatim rules | Exact numeric limits, API schemas, security bounds, and UI policies copied verbatim. |
| `3. Review Focus` | Numbered list (`<= 5` items) | Five uncovered edge/failure classes pinned to owning task and named test. |
| `4. Vertical-Sliced Tasks` | Ordered task blocks (`Task 1..N`) | `Size` (`XS\|S\|M`), `Dependencies`, `Files`, `Interfaces`, `Acceptance Criteria`, 5 RED->GREEN steps. |
| `5. Pre-Flight Conflict & Readiness` | Matrix (`>= 2` rows) | Cross-task signature parity check and readiness verdict (`READY\|NEEDS WORK\|BLOCKED\|NOT ASSESSED`). |
| `6. Re-Plan, Condensation & Rulings` | Triggers + metrics + log | `Re-plan if:` triggers, Deletion Pass metrics (`Files Deleted`, `Deps Removed`, `Net LOC Reduced`), `Ruling:` log. |

### 3.2 Execution Plan Required Field Keys (`execution-plan.md`)

- `Plan ID`: Unique plan identifier linking back to the active Spiral cycle.
- `Execution Approach`: `Inline` (single-context sequential) or `Teamwork` (disjoint parallel).
- `Files`: Explicit `Create`, `Modify`, and `Test` lists per task (`<= 5` files total).
- `Consumes` / `Produces`: Typed symbols, endpoints, or tables exchanged across tasks.
- `Expected`: Concrete CLI exit code and output string required at RED and GREEN checkpoints.
- `Re-plan if`: Invalidation triggers forcing pause and structural re-design.

### 3.3 Worked Plan Ruling & Condensation Receipt

```markdown
- Task 2: Ruling: Reuse existing `db.tx()` helper instead of adding a new unit-of-work wrapper — preserves transactional guarantees across 2 queries — reversible in 15 min if cross-DB support is later added.
- Pre-Ship Condensation: Files Deleted: 1 (`legacy_mapper.py`) | Deps Removed: none | Net LOC: -68 | Post-Deletion Test: `pytest -q` -> exit 0 (42 passed)
```

---

## 4. Verification Checklist

- [ ] Read-only codebase survey completed and Phase 3A contracts verified before drafting tasks.
- [ ] Existing active plan files inspected so no incomplete session plan is silently overwritten.
- [ ] Every task cuts vertically, stays at or below 5 files (`L`/`XL` split), and avoids compound `"and"` titles.
- [ ] Every task specifies exact `Files`, matching `Consumes`/`Produces` interfaces, and RED->GREEN commands with expected output.
- [ ] `Review Focus` enumerates up to 5 concrete edge or failure modes pinned to explicit tests.
- [ ] Plan contains zero unresolved marker tokens, zero speculative abstractions, and obeys the Plan Proportion Rule.
- [ ] Pre-ship Deletion/Condensation Pass executed and full build plus test suite re-run cleanly after final edits.

---

## 5. Hard Quality Gate

### 5.1 Plan Gate Verdict Rules

- **`PASS`**:
  - Readiness verdict is `READY` with Phase 3A contracts cited and zero unresolved markers.
  - Every task is `<= M` (`<= 5` files), cuts vertically, and declares matching `Consumes`/`Produces` plus RED->GREEN commands.
  - Adaptations are logged as `Ruling:` entries, Deletion/Condensation Pass ran, and post-deletion tests exit `0`.
- **`CONCERNS`**:
  - Minor non-blocking wording or test-naming notes exist; core contracts, constraints, and suite pass cleanly.
- **`NOT ASSESSED`**:
  - `execution-plan.md` has zero tasks, missing `Spec Path`, or unreadable referenced artifacts.
- **`FAIL`**:
  - Source files mutated before `READY` alignment, incomplete active plan overwritten, horizontal mega-tasks (`> 5` files) unsplit, silent deviations, or skipped Deletion Pass.

### 5.2 Plan Gate Remediation Triggers

- **Task > 5 files**: Split along vertical capability seams before starting implementation.
- **Unledgered signature change**: Record `Ruling:` in `progress.md` and run cross-task conflict scan again.

### 5.3 Plan Gate Verification Commands

```bash
# 1. Confirm workspace scope and inspect changed files
git status --porcelain

# 2. Verify zero unresolved stub markers outside fenced code blocks in execution-plan.md
python3 -c '
import re
from pathlib import Path
p = Path("execution-plan.md")
text = re.sub(r"```.*?```", "", p.read_text(encoding="utf-8"), flags=re.DOTALL)
hits = re.findall(r"\b(?:TODO|TBD|FIXME)\b|\[placeholder\]", text, re.I)
assert not hits, f"Unresolved markers in execution-plan.md: {hits}"
print("execution-plan.md marker check PASS")
'

# 3. Run full project build and test suite after the Deletion/Condensation Pass
pytest -q --tb=short
```

---

## 6. Anti-Patterns

Reject these planning failure modes during pre-execution review and inline adaptation:

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Over-Planning Trivial Edits** | Burns tokens authoring multi-page plans for a 10-line fix | Plan file created for `<= 2` file edit with zero boundary risk | Exit via Step 0 `Direct` gate and execute inline with TDD + fresh check. |
| **Horizontal Layer Mega-Tasks** | Delays integration proof until Task N; hides signature mismatches | Task 1 writes all schemas, Task 2 all APIs, Task 3 all UI | Slice vertically so every task ends in a testable increment. |
| **Silent Plan Overwrite** | Destroys progress ledgers and rulings from an active session | Overwriting `plan.md` or `progress.md` with unchecked items | Inspect disk first; resume, archive, or isolate into a new run folder. |
| **Transcript Plan (Bloat > Code)** | Turns planning into speculative code generation, freezing brittle guesses | Plan embeds 200-line full implementations instead of interfaces | Lock `Consumes`/`Produces` contracts, constraints, and pinning tests concisely. |
| **Speculative Abstraction Inside Plan** | Violates YAGNI by inventing unused factories/adapters before Task 1 | Plan adds `IFooService`/`FooImpl` wrappers for 1 concrete caller | Apply Rule of Three and direct module functions until divergence exists. |
| **Vague Step & Silent Ruling Drift** | Lets implementers invent incompatible signatures without audit trail | Steps read *"update handlers as needed"* or diverge silently | Name exact paths/symbols per step and log every change as a `Ruling:`. |
