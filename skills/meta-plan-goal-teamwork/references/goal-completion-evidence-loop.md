# Goal-Completion & Evidence-Audit Loop (`/goal`)

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

The Goal-Completion & Evidence-Audit Loop enforces a non-negotiable engineering rule: **no completion claim without fresh, post-edit verification evidence**.
It converts vague intent into quantitative contracts, runs a 6-phase verification loop, checks receipt staleness, and separates local passes from target-environment acceptance.

---

## 1. Decision Framework

### 1.1 Activation Threshold (`Direct` Iron Law vs. Full `/goal` Contract)

Use the full Goal Contract only when ambiguity, multi-constraint auditing, or iterative optimization earns it:

| Task Type | Activation Decision | Required Rigor |
|---|---|---|
| **Deterministic 1-Step Edit** (`<= 2` files, obvious pass/fail) | **Skip Goal Contract Ceremony** (`Direct`) | Apply the **Iron Law** only: run the check fresh after final edit and read exit `0`. |
| **Ambiguous / Open-Ended Intent** (*"make checkout faster"*, *"harden auth"*) | **Activate `/goal` Contract** | Rewrite intent into a 5-axis quantitative contract before editing code. |
| **Quantitative Optimization / Eval** (`p95`, coverage %, bundle KB, AI `pass@k`) | **Activate `/goal` + Eval Matrix** | Pre-register baseline + target thresholds (`pass@k` / `pass^k`) before tuning. |
| **Pre-Ship Multi-Constraint Closure** (closing `/plan` or `/teamwork`) | **Activate `/goal` Audit** | Run 6-phase loop, staleness receipt check, and AC traceability ledger. |

### 1.2 The 5-Axis Goal Quality Bar & Strict Verdict Precedence

Every formalized Goal Contract must answer all five axes unambiguously:

1. **Concrete Outcome**: Observable artifact or system state (never pure activity like *"investigate"* or *"improve"*).
2. **Verification Command / Method**: Exact CLI script, test suite, benchmark, or browser audit proving the state.
3. **Quantitative or Binary Threshold**: Exact pass bar (for example, `p95 < 250ms` across `3` runs, `0` WCAG contrast errors, `100%` AC coverage).
4. **In / Out Scope Bounds**: Explicit file paths and capabilities included versus excluded to prevent scope creep.
5. **Stop & Ask Trigger**: Concrete condition where automation halts and requests a user ruling.

Verdicts follow strict precedence from worst to best so missing or unobserved evidence never masquerades as success:

`BLOCKED > NOT ASSESSED > COMPLETE WITH NOTES > COMPLETE`

- **Target-Environment Separation**: Report **Local Verification** separately from **Target-Environment Acceptance** (`VERIFIED | FAILED | NOT PERFORMED | NOT APPLICABLE`). A green local suite never proves staging or production readiness.
- **Unobserved Rule**: Any criterion lacking an executed check or retained output resolves to `NOT ASSESSED`, never pass.

### 1.3 Simplest High-Craft & Anti-Overengineering Check

- Reject decorative metrics, custom LLM judge pipelines, or brittle visual harnesses when one deterministic CLI command + exit code `0` proves correctness cleanly.
- Follow the grader hierarchy: **Code Grader > Model Grader > Human Grader**.
- Keep `goal-evidence-ledger.md` compact—record exact commands, exit codes, and deltas instead of pasting megabytes of raw logs.

### 1.4 Worked Goal Quantifications (`Activity` vs. `5-Axis Contract`)

| Raw Intent (Rejected) | 5-Axis Quantified Replacement | Verification Grader |
|---|---|---|
| *"Make checkout faster"* | Reduce `/api/checkout` `p95` latency `< 220ms` at `50 RPS` in `src/checkout/` | `k6` load script + exit `0` |
| *"Audit and fix UI"* | Zero `check_anti_slop.py` errors and `>= 4.5:1` contrast across `src/ui/` | CLI validators + Playwright screenshot |
| *"Stabilize flaky test"* | `pass^5 = 100%` consecutive passes on `tests/test_billing.py` without mocks | `pytest --count=5` fresh run |

---

## 2. Step-by-Step Workflow

1. **Quantify & Bound the Goal (`Define` Gate)**
   - **Owner**: Lead Agent.
   - **Inputs**: User request, codebase state, active goal ledgers.
   - **Outputs**: Populated Section 1 (`5-Axis Quantitative Goal Contract`) of `goal-evidence-ledger.md`.
   - **Tools**: Read-only codebase inspection, active goal dedupe check.
   - **Actions**:
     - Reject pure activity goals (*"look into slow queries"*, *"clean up CSS"*).
     - Rewrite into a measurable end state naming exact files, metric thresholds, scope bounds, and stop triggers.
     - Check existing disk ledgers first so duplicate goal contracts are never created for one deliverable.
     - Ask at most one concise clarifying question only if an unknown threshold changes the solution.

2. **Pre-Register Evals & QA-Level Evidence Matrix**
   - **Owner**: Lead Agent / QA Lead.
   - **Inputs**: Quantitative contract, `qa.level` (`minimal | standard | full`), acceptance criteria (`AC-1..N`).
   - **Outputs**: Eval Matrix (`Capability` vs `Regression`) and expected evidence list.
   - **Tools**: Test harness config, benchmark scripts.
   - **Actions**:
     - Lock **Capability Evals** (`pass@3 >= 90%` for new workflows) before editing code.
     - Lock **Regression Evals** (`pass^3 = 100%` consecutive passes proving zero regressions) before editing code.
     - Match required evidence depth to `qa.level`:
       - `minimal`: Targeted unit checks and clean diff audit.
       - `standard`: Full unit + integration suites and type/lint checks.
       - `full`: End-to-end runtime verification plus retained post-edit UI screenshots.

3. **Execute Implementation & Pre-Evidence Condensation Pass**
   - **Owner**: Implementer.
   - **Inputs**: Goal Contract, codebase, `execution-plan.md` (if paired with `/plan`).
   - **Outputs**: Condensed, clean implementation ready for final verification.
   - **Tools**: Language runtime, formatter, `git diff --stat`.
   - **Actions**:
     - Implement the minimal high-craft change needed to satisfy contract thresholds.
     - Run a **Deletion & Condensation Pass** before capturing final evidence:
       - Remove temporary debug instrumentation and collapse redundant helper wrappers.
       - Strip unused imports or packages replaceable by native primitives.
     - Never capture final receipts before your final edit—post-receipt cleanup invalidates proof.

4. **Run the 6-Phase Verification Loop & Staleness Receipt Check**
   - **Owner**: Verifier / Lead Agent.
   - **Inputs**: Final unedited workspace state after Step 3.
   - **Outputs**: Timestamped 6-phase receipts and freshness confirmation.
   - **Tools**: Build tool, typechecker, linter, test runner, security scanner, `git status`.
   - **Actions**:
     - Execute the Iron Law sequence strictly in order:
       - `IDENTIFY` -> `RUN` (fresh in current turn) -> `READ` (full output + exit code) -> `VERIFY` -> `CLAIM`.
     - Run all six verification phases sequentially:
       1. **Build**: Compile production bundle or package cleanly.
       2. **Types**: Run strict typechecker (`tsc --noEmit`, `mypy`, `pyright`).
       3. **Lint**: Run project linter with zero warnings in changed files.
       4. **Tests & Coverage**: Execute unit, integration, and regression suites; record exact counts.
       5. **Security & Debug-Log Scan**: Scan for secrets, vulnerabilities, and leftover `console.log`/`print` lines.
       6. **Diff & Scope Audit**: Run `git status --porcelain` and `git diff --stat` against `In Scope`.
     - Run the **Staleness Receipt Check**: confirm every test log, benchmark, and screenshot is newer than the final source edit; re-capture any `STALE` artifact immediately.

5. **Build AC Traceability Table & Issue Strict Verdict**
   - **Owner**: Lead Agent / Independent Reviewer.
   - **Inputs**: Fresh 6-phase receipts, `AC-1..N`, environment status.
   - **Outputs**: Completed `goal-evidence-ledger.md` and final verdict.
   - **Tools**: Traceability matrix and `git` state checks.
   - **Actions**:
     - Map every criterion (`AC-1..N`) to an exact `file::test` symbol or retained screenshot (`COVERED | UNTESTED | DEFERRED`).
     - Classify discrepancies explicitly as `BLOCKING`, `ADVISORY`, or `OUT OF SCOPE`.
     - Report `Target Acceptance` separately (`VERIFIED | FAILED | NOT PERFORMED | NOT APPLICABLE`).
     - Issue `COMPLETE` only at `100%` coverage with fresh receipts and `0` blocking deviations; otherwise downgrade per `BLOCKED > NOT ASSESSED > COMPLETE WITH NOTES`.

---

## 3. Reusable Artifact & Template

Instantiate [Goal Contract Template](../templates/goal-contract.md) to produce the runtime artifact `goal-evidence-ledger.md`.

### 3.1 Goal Ledger Section & Field Contract

| Section / Field | Type & Cardinality | Contract & Validation Rule |
|---|---|---|
| `Metadata Header` | Table (`6` required keys) | Declares `Goal ID`, `Target Artifact / System`, `QA Level`, `Target Environment`, `Final Verdict`, runtime path. |
| `1. 5-Axis Goal Contract` | `6`-row table | Locks `Concrete Outcome`, `Verification Command`, `Quantitative Threshold`, `In Scope`, `Out of Scope`, `Stop & Ask`. |
| `2. Eval Matrix` | Table (`>= 1` row if iterative) | Tracks `Capability`/`Regression`, `Code/Model/Human` grader, `pass@k`/`pass^k` target, measured result. |
| `3. 6-Phase Receipts` | `6`-row command log | Exact CLI command, exit code, UTC timestamp, measured summary for Build, Types, Lint, Tests, Security, Diff. |
| `4. AC Traceability & Staleness` | Matrix + freshness line | Maps every `AC-ID` to `file::test` or screenshot with `Post-Edit Fresh?` and `COVERED/UNTESTED/DEFERRED`. |
| `5. Deviations & Sign-Off` | Structured verdict block | Separates `BLOCKING`/`ADVISORY`/`OUT OF SCOPE` items, `Target Acceptance`, and final verdict justification. |

### 3.2 Goal Ledger Required Field Keys (`goal-evidence-ledger.md`)

- `Goal ID`: Unique goal identifier linked to the active Spiral cycle.
- `QA Level`: `minimal` (targeted checks), `standard` (unit + integration), or `full` (E2E + visual).
- `Post-Edit Fresh?`: `YES | STALE` indicator comparing receipt timestamp against final source edit.
- `Target Acceptance`: Independent `VERIFIED | FAILED | NOT PERFORMED | NOT APPLICABLE` status.
- `Final Verdict`: Strictly ordered outcome (`BLOCKED > NOT ASSESSED > COMPLETE WITH NOTES > COMPLETE`).

### 3.3 Worked Staleness & Traceability Receipt

```markdown
- AC-1 (Checkout p95 < 220ms): `k6 run perf/checkout.js` -> p95=184ms, exit 0 | Captured: 14:12:05Z | Last Edit: 14:10:02Z | Fresh: YES | Status: COVERED
- Target Acceptance: NOT PERFORMED (staging deploy pending) | Local Verification: COMPLETE
```

---

## 4. Verification Checklist

- [ ] Goal statement specifies an observable outcome, executable check, and numeric threshold without activity phrasing.
- [ ] In-scope and out-of-scope paths are explicitly bounded before any files are modified.
- [ ] Deletion and condensation cleanup completed prior to capturing final verification receipts.
- [ ] All applicable phases of the 6-phase verification loop executed fresh in the current turn with full exit codes read.
- [ ] Staleness receipt check confirms every test output and screenshot is newer than the final code edit.
- [ ] Every acceptance criterion maps to a named test or retained artifact in the AC traceability table.
- [ ] Local CI verification and target-environment acceptance are reported as separate status fields.

---

## 5. Hard Quality Gate

### 5.1 Goal Gate Verdict Rules

- **`PASS` (`COMPLETE`)**:
  - Every in-scope AC is `COVERED` with zero `UNTESTED` items.
  - All applicable 6-phase checks executed fresh post-final-edit with exit `0` and `Post-Edit Fresh? = YES`.
  - `0` blocking deviations, clean `git status --porcelain` scope, and `Target Acceptance` explicitly classified.
- **`COMPLETE WITH NOTES`**:
  - Core ACs `COVERED` and verified fresh; only non-blocking `ADVISORY` or `OUT OF SCOPE` notes remain, explicitly disclosed.
- **`NOT ASSESSED`**:
  - Any AC lacks a mapped check, an evidence file is missing, or a required target check was unobserved.
- **`FAIL` / `BLOCKED`**:
  - Any build, type, lint, test, or security failure; any `STALE` screenshot/receipt captured before the final edit; or hedge claims substituted for fresh execution.

### 5.2 Goal Gate Remediation Triggers

- **Stale Receipt Detected**: Re-run the exact command or UI screenshot capture after the final edit and overwrite the stale timestamp.
- **Scope Drift Detected**: Revert unrequested out-of-scope edits or obtain explicit user ruling before closing.

### 5.3 Goal Gate Verification Commands

```bash
# 1. Confirm scope drift and record latest source timestamp vs current UTC time
git status --porcelain
git diff --stat
date -u +"%Y-%m-%dT%H:%M:%SZ"

# 2. Run project verification suite fresh (example: Python compile + pytest suite)
python3 -m compileall -q .
pytest -q --tb=short

# 3. Verify zero leftover debug markers or secrets in modified diff lines
git diff --unified=0 | grep -E "^\+.*(console\.log|debugger|pdb\.set_trace|AKIA[0-9A-Z]{16})" && exit 1 || echo "Clean diff scan PASS"
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Activity-Only Goal** | Allows endless investigation or cleanup with zero stopping criterion | Goal reads *"improve performance"* or *"debug auth"* without numbers | Define concrete artifact, CLI command, and numeric threshold. |
| **Confidence-Over-Evidence** | Turns unverified assumptions into production regressions | Reports say *"should pass now"*, *"probably fixed"*, or *"trivial"* | Run exact command fresh, read full output, cite exit code `0`. |
| **Stale Pre-Edit Receipt** | Final refactor or formatting pass silently breaks earlier proof | Receipt timestamp or screenshot mtime precedes final `git` edit | Re-run verification and re-capture screenshots after final edit. |
| **Code-Reading Substitute** | Static inspection misses runtime wiring, imports, and env bugs | Claiming *"verified by reading function X"* without test output | Execute real tests; mark unobserved checks `NOT ASSESSED`. |
| **Local-Means-Production** | Local mocks hide env vars, migrations, CORS, and network failures | Declaring *"production ready"* solely from localhost unit tests | Separate `Local Verification` from `Target Acceptance` explicitly. |
| **Eval Harness Overengineering** | Wastes hours building LLM-judge pipelines for binary assertions | Spins up model-graded evals where `pytest` + exit `0` suffices | Prefer deterministic Code Graders; reserve model graders for open prose. |
