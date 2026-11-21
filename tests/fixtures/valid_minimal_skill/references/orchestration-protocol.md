# Orchestration Protocol

Defines deterministic parent-to-child skill routing, Phase 3A foundation blocking rules, execution mode selection, and progressive disclosure handoffs.
Parent orchestrators load only the minimal child skill subset required for the active Spiral quadrant.

## 1. Decision Framework

Route to the single active child skill matching the current Spiral quadrant and task trigger.
Evaluate the **Simplest High-Craft Option** (`Direct` mode first) before escalating to `/plan`, `/goal`, or multi-agent `/teamwork` orchestration.
Prevent over-orchestration by matching execution complexity strictly to verified task coupling and risk.

| Routing / Execution Mode | Quantitative Trigger | Simplest High-Craft Choice | Escalation Condition |
|---|---|---|---|
| `Direct` Single-Step | `1` file or `<= 30` min task, low risk | Execute directly with `1` active child module | Cross-domain schema or security impact |
| `/plan` Mode | `2..5` tightly coupled modules, `1` engineer | Short ordered plan before editing, `0` subagents | Multi-track parallel work `> 3` independent domains |
| `/goal` Evidence Loop | Measurable target SLO or regression fix | Iterative verify-until-PASS loop on exact test command | Ambiguous requirements needing discovery |
| `/teamwork` Multi-Agent | `>= 3` disjoint domains, high verification risk | Parallel specialists gated by `registry.json` DAG | Task solvable by `1` agent in `< 20` tool calls |

### Anti-Over-Orchestration Interrogation

1. Can a single agent finish this cleanly in `Direct` mode without spawning subagents?
2. Which coordination layers or intermediate handoff documents can be deleted?
3. Are `depends_on` edges in `registry.json` acyclic and strictly justified by artifact dependencies?
4. Does the selected routing keep loaded context within the `<= 4,000` token per-stage budget?

### Deterministic Routing & Token Budget Rules

- Maximum child skills loaded per Spiral Q1 discovery pass: `1` (`product-discovery-and-specs`).
- Maximum child skills loaded per Spiral Q2 risk/architecture pass: `2` (`system-data-architecture`, `security-engineering`).
- Maximum concurrent child dispatches after Phase 3A clearance: `3` disjoint domains.
- Maximum allowed `SKILL.md` line count for Parent Orchestrator: `<= 280` lines.
- Maximum allowed `SKILL.md` byte size for Parent Orchestrator: `<= 18,432` bytes.
- Maximum allowed `SKILL.md` line count per Child Skill: `<= 280` lines.
- Maximum allowed `SKILL.md` byte size per Child Skill: `<= 18,432` bytes.
- Maximum allowed `depends_on` cycle count across `registry.json`: `0` cycles.
- Minimum required fields per child skill entry in `registry.json`: `id`, `path`, `spiral_stages`, `triggers`, `depends_on`, `inputs`, `outputs`, `estimated_tokens`.
- Minimum required execution modes documented in Parent router: `4` modes (`/plan`, `/goal`, `/teamwork`, `Direct`).
- Maximum allowed bulk copy-paste blocks duplicated between `SKILL.md` and `references/`: `0` blocks.
- Minimum required standalone link containment inside every `skills/<child>/`: `100%` self-contained.
- Maximum allowed broken relative Markdown links across entire suite: `0` broken links.
- Minimum required Phase 3A Foundation artifacts before Q3 coding dispatch: architecture, data model, boundaries, contracts, ADR, skeleton.
- Maximum allowed unverified gate bypasses during Q3 feature execution: `0` bypasses.
- Minimum required Socratic simplicity answers before complex multi-service adoption: `4` written answers.
- Maximum allowed third-party Python dependencies in suite validator scripts: `0` external packages.
- Minimum required CLI `--help` exit code compliance across all scripts: exit `0`.
- Minimum required English prose consistency across all Markdown artifacts: `100%` English.
- Maximum allowed stub or placeholder markers outside code fences: `0` occurrences.
- Minimum required R2 six-pillar coverage across every reference module: `100%` of modules.
- Maximum allowed length variance below suite median word count: `>= 0.35x` median words.
- Minimum required word count floor per domain reference module: `>= 800` words.
- Minimum required non-empty line count floor per domain reference module: `>= 120` lines.
- Minimum required checklist items per Pillar 4 verification list: `5` falsifiable items.
- Minimum required anti-patterns per Pillar 6 failure catalog: `3` structured entries.
- Maximum allowed `AGENTS.md` or `GEMINI.md` files inside repository: `0` files.
- Maximum allowed symlinks inside repository: `0` symlinks.
- Minimum required author/committer identity match across all git commits: `100%` exact match.
- Maximum allowed IDE daemon hard-exit failures in offline security checks: `0` failures.
- Minimum required contrast ratio verification coverage on generated design systems: `100%` WCAG AA.
- Maximum allowed banned default fonts (`Inter`, `Roboto`, `Arial`, `Open Sans`, `Helvetica`) in default recommendations: `0` recommendations.
- Maximum allowed banned default icon sets (`Lucide`, `Feather`, `Heroicons`, `Material Icons`, `Material Symbols`) in default recommendations: `0` sets.
- Minimum required Deletion/Condensation Pass audit executions per Spiral cycle: `1` recorded pass.
- Minimum required black-box testing techniques documented in QA skill: `8` distinct techniques.
- Maximum allowed dangling or circular references in W3C DTCG token schemas: `0` errors.
- Minimum required script syntax verification across `.py`, `.sh`, and `.js` files: `100%` valid syntax.
- Maximum allowed unlinked orphan templates inside `templates/`: `0` orphans.
- Minimum required source coverage cross-check parity against classified local skills: `100%` Relevant skills mapped.
- Maximum allowed stale handoff context carried past Spiral cycle boundaries: `0` stale blocks.
- Minimum required structured error reporting on invalid CLI paths or traversal attempts: non-zero exit without traceback.
- Maximum allowed token-budget overrun per stage without explicit escalation note: `0` overruns.
- Minimum required standalone executability for every child skill directory: `100%` self-contained.
- Minimum required parity between `registry.json` skill entries and `skills/*/` directories: exact `1:1` match.
- Maximum allowed unreviewed security vulnerabilities (`P0`/`P1`) at release gate: `0` findings.
- Minimum required rollback and runbook readiness before production cutover: `100%` verified.
- Minimum required blameless postmortem action tracking for SEV-1/SEV-2 incidents: `100%` documented.
- Maximum allowed speculative wrapper abstractions retained after Deletion Pass: `0` wrappers.
- Minimum required deterministic CLI query coverage across active reference pillars: `100%` searchable.

## 2. Step-by-Step Workflow

Execute this routing sequence at every Spiral quadrant boundary to maintain token discipline and foundation integrity.

1. **Step 1 — Inspect Registry and Spiral Stage (Owner: Parent Orchestrator)**
   - **Inputs**: `registry.json`, active Spiral quadrant (`Q1..Q4`), and user objective.
   - **Action**: Match triggers and verify upstream `depends_on` artifacts exist on disk.
   - **Action Detail**: Select the smallest set of child skills required for the active quadrant.
   - **Output**: Selected child skill ID(s) within the active token budget.

2. **Step 2 — Enforce Phase 3A & Simplicity Gate (Owner: Gatekeeper)**
   - **Inputs**: Spiral Charter, Simplicity Interrogation Record, and Foundation artifacts.
   - **Action**: Block Quadrant 3 coding or UI child skills until Phase 3A architecture and Deletion Pass constraints are satisfied.
   - **Action Detail**: Reject requests that jump directly to UI styling or endpoints without core contracts.
   - **Output**: Gate clearance token for downstream child execution.

3. **Step 3 — Dispatch Child Skill(s) via Minimal-Token Contracts (Owner: Parent Orchestrator)**
   - **Inputs**: Gate clearance token and child skill `SKILL.md` path.
   - **Action**: Pass only the required input artifact paths and expected output contract to the child skill workflow.
   - **Action Detail**: Prohibit bulk-reading unrelated child skill directories.
   - **Output**: Draft child skill artifacts ready for verification.

4. **Step 4 — Execute Deletion/Condensation & Handoff Check (Owner: Parent Orchestrator)**
   - **Inputs**: Child skill outputs and `registry.json` output schema.
   - **Action**: Verify each child deliverable meets output contracts, removes redundant wrappers, and avoids duplicated boilerplate.
   - **Action Detail**: Confirm all output links and automated validator checks succeed cleanly.
   - **Output**: Verified handoff artifact for the next Spiral quadrant.

## 3. Reusable Artifact & Template

Record every orchestration handoff using [Sample Template](../templates/sample-template.md) to enforce minimal context transfer.
Keep handoff records focused strictly on artifact paths, gate verdicts, and deleted complexity.

| Field | Type | Constraint | Example |
|---|---|---|---|
| `spiral_cycle` | `integer` | `>= 1` | `1` |
| `objective` | `string` | `20..240` chars | `"Route Q2 architecture to system-data-architecture"` |
| `simplest_option` | `string` | `>= 30` chars | `"Single child invocation before parallel fan-out"` |
| `deletion_pass_notes` | `string` | `>= 20` chars | `"Excluded redundant context files"` |
| `gate_verdict` | `PASS` or `FAIL` | Binary gate status | `"PASS"` |

## 4. Verification Checklist

- [ ] Target child skill exists in `registry.json` with valid triggers and non-cyclic `depends_on` edges.
- [ ] Only the active child skill and required reference modules are loaded into context.
- [ ] Phase 3A Foundation Gate passed before any Q3 coding or UI child skill was dispatched.
- [ ] Execution mode matches task complexity without over-orchestrating simple single-agent work.
- [ ] Simplicity Interrogation Record confirms the Simplest High-Craft Option was prioritized.
- [ ] Deletion/Condensation Pass verified output artifacts contain zero speculative bloat.

## 5. Hard Quality Gate

Orchestration transitions pass only when structural parity, DAG integrity, and automated checks all succeed.

- **PASS Criteria**:
  1. `registry.json` matches `skills/*/` 1:1 with zero dependency cycles and valid token budgets.
  2. Active handoff passes `python3 scripts/sample_check.py --check` with exit code `0`.
  3. Zero bulk-loading of unrelated child skills occurred during routing.
- **FAIL Criteria**:
  1. Bulk-loading all child skills simultaneously without active stage justification.
  2. Circular `depends_on` edges or missing output contract fields in `registry.json`.
  3. Over-orchestrating a trivial `Direct` task with multi-agent coordination overhead.

## 6. Anti-Patterns

Reject the coordination and routing failures below during every Spiral boundary review.

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| Bulk-Loading All Child Skills | Exhausts context window and degrades reasoning precision | Reading `> 3` child `SKILL.md` files before routing | Query `registry.json` and load only the active stage child skill |
| Skipping Phase 3A Gate | Causes expensive UI and API rework when domain boundaries shift | Dispatching coding or UI skills with no ADR or schema | Require Phase 3A Foundation Gate PASS before Q3 dispatch |
| Cyclic Skill Dependencies | Deadlocks deterministic orchestration ordering | `A -> B -> A` inside `registry.json` `depends_on` | Enforce strict DAG ordering across Spiral quadrants |
| Multi-Agent Over-Orchestration | Wastes tokens and latency on trivial single-file edits | Triggering `/teamwork` for `< 30` line single-module fixes | Default to `Direct` or `/plan` mode when coupling is low |
| Implicit Handoff State | Causes silent contract drift across sequential child skill invocations | Passing prose summaries instead of typed artifact paths | Pass explicit file paths matching `registry.json` inputs and outputs |
| Unbounded Parallel Fan-Out | Triggers merge conflicts and duplicated boilerplate across shared files | Dispatching `> 3` child skills editing overlapping paths | Serialize dependent edits and isolate disjoint outputs |
