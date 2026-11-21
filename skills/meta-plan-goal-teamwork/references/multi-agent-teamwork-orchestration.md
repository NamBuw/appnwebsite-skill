# Multi-Agent Teamwork Orchestration (`/teamwork`)

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

Multi-Agent Teamwork Orchestration coordinates parallel implementation and independent verification across genuinely disjoint workstreams while preserving strict file isolation, cold-start clarity, bounded fix loops, and portable execution across any AI agent runtime.

---

## 1. Decision Framework

### 1.1 Swarm Necessity & Topology Selector (Anti-Over-Orchestration Gate)

Coordination overhead grows faster than worker count. Never invoke `/teamwork` when one agent finishes faster inline:

| Workload Shape | Quantitative Threshold | Selected Topology | Hard Guardrail |
|---|---|---|---|
| **Single-Slice / Coupled** | `<= 2` files OR tightly coupled sequential edits OR single-file refactor | **FORBIDDEN: Use `Direct` or Inline `/plan`** | Spawning workers for `<= 2` files wastes tokens and adds merge friction. |
| **Fan-Out / Task Review** | `2` independent investigation angles OR `1` author + `1` verifier per task | **Pipeline / Task Subagents** | Workers return structured diffs/reports; coordinator merges sequentially. |
| **Multi-Stream Feature** | `>= 3` genuinely disjoint write surfaces (`0` overlapping files) | **Coordinator-Worker Swarm** | `1` independent verifier per `2–4` authors; coordinator writes zero feature code. |
| **High-Fan-Out Multi-Domain** | `> 8` workers OR `>= 2` concurrent subsystems | **Scoped Channel Swarm** | Partition updates into domain channels so the main feed stays uncluttered. |

### 1.2 Model Tiering & Workspace Isolation Matrix

Optimize total elapsed wall-clock turns rather than chasing fragile low-tier token savings (`turn count beats token price`):

| Role / Complexity | Model Tier | Workspace Isolation Mode | Write Permission Rule |
|---|---|---|---|
| **Mechanical Single-File Transcription** | **Low / Fast** | Isolated `worktree` / `branch` / `share` | Exact single-file `owns` path only. |
| **Multi-File Feature Author / Debugger** | **Standard** | Isolated `worktree` / `branch` / `share` | Strictly disjoint `owns` paths; `0` overlap across parallel authors. |
| **Task Spec & Quality Verifier** | **Standard** | Shared read-only (`inherit`) | Read-only source/tests; writes verification report only. |
| **Coordinator / Architect / Final Reviewer** | **Top** | Coordinator ledger only; Reviewer `inherit` | Coordinator edits ledgers only mid-swarm; escalates rounds `4–5` to Top. |

### 1.3 Harness-Agnostic Portable Capability Adapter

Write every plan and handoff in portable concepts mapped cleanly to the active host runtime:

| Abstract Primitive | Antigravity | Claude Code | Codex CLI | Cursor / Inline Fallback |
|---|---|---|---|---|
| **Coordinator Role** | Parent orchestrator + state dir | Lead session + `progress.md` | Lead session + plan ledger | Single agent switching roles |
| **Worker Dispatch** | Subagent / Swarm / Workflow API | `Agent` tool / parallel agents | Parallel subagent sessions | Sequential vertical slices |
| **Write Isolation** | `share` / `branch` / disjoint paths | Git `worktree` per author | Isolated sandbox / worktree | Single tree, 1 slice at a time |
| **Handoff Bus** | `handoff.md` + `progress.md` | Disk reports + `BASE..HEAD` | Disk ledger + typed summary | Runtime `teamwork-handoff.md` |
| **Wait & Stall Guard** | Event-driven wait / monitor | Subagent completion callback | Async wait + escalation | Synchronous execution |

### 1.4 Simplest High-Craft Teamwork Check (Anti-Overengineering & YAGNI)

Before creating worker briefs, answer the Simplicity gate:

- **Least Code & Coordination**: Can one agent finish the change inline in fewer total turns and zero merge risk? If yes, exit `/teamwork` immediately (`Direct` or Inline `/plan`).
- **YAGNI Topology**: Never add monitor, narrator, or multi-channel layers unless `> 8` workers or `>= 2` parallel subsystems run concurrently.

### 1.5 Worker Status Routing & Fix-Loop Escalation Matrix

| Worker Return Status | Coordinator Action | Fix-Loop / Escalation Rule |
|---|---|---|
| **`DONE`** | Dispatch `BASE..HEAD` diff + handoff to Verifier | Never merge without independent verification receipt. |
| **`DONE_WITH_CONCERNS`** | Inspect concerns before verification/merge | Promote blocking issues to fix loop; log minors in `Deferred minors`. |
| **`NEEDS_CONTEXT`** | Supply missing spec path or contract ruling | Do not count missing-input clarification against fix-round cap. |
| **`BLOCKED`** | Narrow task scope, split files, or escalate `+1` tier | At round `5` breaker, adjudicate explicitly (`parked` or `Ruling:`). |

---

## 2. Step-by-Step Workflow

1. **Partition Disjoint Ownership & Initialize Disk Ledger**
   - **Owner**: Coordinator.
   - **Inputs**: `READY` `execution-plan.md`, Phase 3A contracts, baseline `MERGE_BASE` SHA.
   - **Outputs**: Initialized `teamwork-handoff.md` and `progress.md` with disjoint `owns` matrix.
   - **Tools**: `git rev-parse HEAD`, pre-flight conflict scan, ledger template.
   - **Actions**:
     - Lock coordinator discipline: **coordinator never edits feature code mid-swarm** so worker branches never collide.
     - Partition tasks into strictly disjoint `owns` paths; serialize overlapping files or extract shared contracts into Task 0 first.
     - Record `MERGE_BASE` SHA and publish the ownership matrix before spawning workers.

2. **Author Self-Contained Cold-Start Briefs (Zero-Paste Rule)**
   - **Owner**: Coordinator.
   - **Inputs**: `execution-plan.md` task contracts, ownership matrix.
   - **Outputs**: One concise 6-part brief per worker.
   - **Tools**: File-path pointers and reference IDs (`#N` / `#task-N`).
   - **Actions**:
     - Treat every spawned worker as cold-start with zero prior conversation context.
     - Include exactly six fields in each brief:
       - **Project Context**: 1-sentence system purpose and active milestone.
       - **Ownership & Boundaries**: Exact `owns` write paths and `must_not_touch` exclusions.
       - **Canonical Path Pointers**: File paths to specs and task sections (never paste 40KB inline).
       - **No-Subagents Rule**: Ban recursive subagents and duplicate task reviewers inside workers.
       - **Verification Command**: Exact CLI command worker runs fresh before reporting.
       - **Done Contract**: Return status (`DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED`) plus 5-component `handoff.md`.

3. **Dispatch Parallel Lanes, Wait Event-Driven & Triage Stalls**
   - **Owner**: Coordinator.
   - **Inputs**: Verified cold-start briefs.
   - **Outputs**: Completed worker handoffs and active stall recoveries.
   - **Tools**: Parallel dispatch, event-driven completion wait.
   - **Actions**:
     - Launch independent lanes in one parallel turn rather than trickling sequentially.
     - Wait event-driven for completions—never burn turns in busy-polling loops.
     - Triage stalls (live workers idle while deliverables remain unfinished) across five causes:
       - **Unaddressed Output**: Completed report awaiting coordinator review or merge.
       - **Unread Queue**: Worker missed coordinator ruling or dispatch update.
       - **Unanswered Escalation**: Worker returned `NEEDS_CONTEXT` or `BLOCKED`.
       - **Dependency Deadlock**: Two lanes implicitly wait on each other's output.
       - **Quota Exhaustion**: Switch the affected role's model tier instead of killing worker state.

4. **Independent Verification (`1 Verifier : 2–4 Authors`) & Bounded Fix-Loop Breaker**
   - **Owner**: Independent Verifier + Coordinator.
   - **Inputs**: Worker `handoff.md`, exact diff (`git diff BASE..HEAD`—never `HEAD~1`), cold-start brief.
   - **Outputs**: Binary verifier verdict (`PASS | FAIL | NEEDS_CONTEXT`) and fix-loop log.
   - **Tools**: `git diff`, test runner, independent inspection.
   - **Actions**:
     - Assign `1` independent verifier per `2–4` authors inside read-only (`inherit`) workspaces.
     - Supply unbiased diffs and briefs without pre-judging instructions.
     - Enforce the **5-round fix-loop breaker** per task:
       - **Rounds 1–3**: Resume original author with exact verifier line-number findings.
       - **Rounds 4–5**: Replace with a fresh author escalated `+1` tier plus prior failure summary.
       - **Breaker at Round 5**: Halt automated retries; coordinator records `parked` or structural `Ruling:`.

5. **Land Workspaces, Run Deletion Pass & Final Whole-Branch Review**
   - **Owner**: Coordinator + Fresh Top-Tier Reviewer.
   - **Inputs**: Verified isolated worker branches/worktrees.
   - **Outputs**: Integrated branch, condensed diff, `Rulings I made` register, clean scratch tree.
   - **Tools**: `git merge` / `cherry-pick`, full test suite, linter, `git worktree prune`.
   - **Actions**:
     - Integrate verified slices bottom-up onto the integration branch.
     - Run a coordinator-led **Post-Merge Deletion & Condensation Pass**:
       - Delete duplicate helpers authored in parallel, strip dead scaffolding, and run the **entire** test suite (`exit 0`).
     - Dispatch **one** fresh top-tier whole-branch review across `MERGE_BASE..HEAD` with at most **one** consolidated fixer wave.
     - Publish exhaustive `Rulings I made` and `Deferred minors` in `teamwork-handoff.md` and prune temporary worktrees.

---

## 3. Reusable Artifact & Template

Instantiate [Teamwork Dispatch & Ledger Template](../templates/teamwork-dispatch-and-ledger.md) to author the runtime coordination artifacts `teamwork-handoff.md` and `progress.md`.

### 3.1 Teamwork Ledger Section & Field Contract

| Section / Field | Type & Cardinality | Contract & Validation Rule |
|---|---|---|
| `Metadata Header` | Table (`6` required keys) | Locks `Run ID`, `Plan Ref`, `Runtime Adapter`, `Coordinator`, `Merge Base SHA`, runtime paths. |
| `1. Simplicity Justification` | Rationale + budget (`3` fields) | Proves `>= 3` disjoint lanes or verifier need; sets `Max Workers`, `Max Fix Rounds: 5`, Deletion flag. |
| `2. Ownership & Isolation Matrix` | Table (`1` row per worker) | `Worker Name`, `Role`, `Model Tier`, `Workspace Mode`, disjoint `owns`, `must_not_touch`, `Status`. |
| `3. Cold-Start Brief Contract` | `6`-field block | Context, ownership bounds, path-only inputs, `no-subagents`, verification CLI, `Done` contract. |
| `4. Workstream & Fix-Loop Log` | Table + stall log | `Task`, `Worker`, `BASE..HEAD`, `Verifier Verdict`, `Fix Round (0..5)`, `Outcome (complete\|parked\|ruled)`. |
| `5. Rulings, Minors & Post-Merge` | Registers + suite receipt | Exhaustive `Rulings I made`, `Deferred minors`, Deletion metrics, and full-suite `exit 0`. |

### 3.2 Teamwork Ledger Required Field Keys (`teamwork-handoff.md`)

- `Merge Base SHA`: Git commit recorded prior to dispatch so verifier diffs cover every worker commit.
- `owns` / `must_not_touch`: Disjoint write boundaries verified to have zero path overlap across parallel authors.
- `Fix Round`: Bounded `0..5` counter triggering `+1` tier escalation at round `4` and coordinator breaker at round `5`.
- `Rulings I made`: Exhaustive disclosure of every ambiguity resolution, parked item, and breaker ruling.

### 3.3 Worked Cold-Start Worker Brief

```markdown
- Context: Implement webhook HMAC verification for Spiral M2 billing slice.
- Owns: `src/webhooks/verify.ts`, `tests/webhooks/verify.test.ts` | Must Not Touch: `src/billing/*`, `registry.json`
- Inputs: `execution-plan.md#task-2`, `contracts/webhooks.md` | Rule: No nested subagents.
- Verify: `npm test -- verify.test.ts` | Done: Emit `DONE` + 5-component `handoff.md`.
```

---

## 4. Verification Checklist

- [ ] Task complexity genuinely earns `/teamwork` (`>= 3` disjoint surfaces or independent review) over `Direct` or Inline `/plan`.
- [ ] Every parallel author holds strictly disjoint `owns` write paths inside an isolated workspace (`worktree`/`branch`/`share`).
- [ ] Coordinator refrained from editing application or feature files mid-swarm.
- [ ] Every worker brief is cold-start self-contained using path references rather than giant inline history pastes.
- [ ] One independent verifier per `2–4` authors reviewed `BASE..HEAD` diffs without coordinator pre-judging.
- [ ] Every task fix loop stayed within the 5-round breaker with explicit `Ruling:` adjudication at escalation limits.
- [ ] Post-merge Deletion/Condensation Pass, single whole-branch review, and full-suite integration tests passed after final merge.

---

## 5. Hard Quality Gate

### 5.1 Teamwork Gate Verdict Rules

- **`PASS`**:
  - Zero write-path collisions across parallel authors and zero mid-swarm feature edits by coordinator.
  - Every merged task has a 5-component report and fresh `BASE..HEAD` verification; fix-loop rounds `<= 5` with rulings disclosed.
  - Post-merge Deletion Pass and full repository test suite exit `0`; scratch worktrees pruned cleanly.
- **`CONCERNS`**:
  - Core deliverables verified `PASS`; minor non-load-bearing items remain `parked` in `Deferred minors` with owner disclosed.
- **`FAIL`**:
  - Overlapping `owns` paths, coordinator editing feature code mid-swarm, recursive worker reviewers, unverified `"success"` claims, or `> 5` retry rounds un-adjudicated.

### 5.2 Teamwork Gate Remediation Triggers

- **Write Collision Found**: Halt conflicting lane immediately, reset overlapping file, and re-partition ownership.
- **Round 5 Breaker Hit**: Freeze retries and emit a coordinator `Ruling:` simplifying or splitting the failing slice.

### 5.3 Teamwork Gate Verification Commands

```bash
# 1. Inspect integrated diff from recorded MERGE_BASE and confirm clean workspace
git status --porcelain
git diff --stat <MERGE_BASE>..HEAD

# 2. Verify zero forbidden coordination artifacts or symlinks leaked into repository tree
find . -maxdepth 4 \( -name "AGENTS.md" -o -name "GEMINI.md" -o -type l \)

# 3. Execute full repository test suite after Post-Merge Deletion/Condensation Pass
pytest -q --tb=short
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Swarm-on-a-Typo (Over-Orchestration)** | Coordination, brief writing, and merge overhead dwarf a 15-line change | Spawning subagents for `<= 2` files or tightly coupled edits | Reject `/teamwork` at Step 0; execute `Direct` or Inline `/plan`. |
| **Shared-File Collision** | Parallel workers overwrite each other's changes and break merges | Two rows in Ownership Matrix list the same file or directory | Partition strictly disjoint `owns` paths or serialize shared contracts first. |
| **40KB Context-Paste Dispatch** | Bloats every worker's initial context window and induces instruction drift | Worker brief embeds raw chat transcripts or full multi-file dumps | Send a 6-field cold-start brief referencing exact file paths and `#task-N`. |
| **Busy-Polling / Unbounded Fix Loop** | Burns token budget endlessly on deadlocked workers or failing patches | Repeated status polling loops or `> 5` retry cycles on one failing task | Use event-driven waits, stall triage, tier escalation at round 4, and round-5 breaker. |
| **Worker-Spawned Duplicate Reviewer** | Multiplies recursive token burn and produces conflicting review rulings | Implementer worker invokes its own subagent reviewer inside a task | Enforce `no-subagents` in cold-start briefs; let coordinator dispatch verifiers. |
| **Coordinator Pre-Judging / Silent Rulings** | Masks real defects and hides architectural assumptions from final audit | Prompt tells verifier *"ignore X"* or coordinator edits code mid-swarm silently | Keep verifiers unbiased on `BASE..HEAD` diffs and disclose all `Rulings I made`. |
