---
name: meta-plan-goal-teamwork
description: Meta-execution orchestrator for Plan-First Execution (/plan), Goal-Completion Evidence Loops (/goal), and Portable Multi-Agent Teamwork (/teamwork). Strictly gated by Radical Simplicity to avoid over-orchestrating trivial edits.
license: MIT
metadata:
  suite: appnwebsite-skill
  version: "1.0.0"
  spiral_stages: "Q1,Q2,3A,3B,3C,Q4"
  estimated_tokens: 2100
---

# Meta-Plan, Goal-Completion & Multi-Agent Teamwork

> **Progressive Disclosure Rule**: Read ONLY the single reference module and template matching your active execution mode (`/plan`, `/goal`, or `/teamwork`). Never bulk-load all three modules into context at once.

---

## Step 0 — Radical Simplicity Triage Gate (Anti-Over-Orchestration)

Before invoking any planning document, goal ledger, or multi-agent swarm, classify the task complexity first. Default to **Direct** execution whenever simple inline engineering delivers equal or higher quality.

| Mode | Activation Threshold | Required Action | Negative-Trigger Exit Rule |
|---|---|---|---|
| **Direct (Default)** | `XS/S` task (`<= 2` files, `1` subsystem, `< 100` LOC, zero DB/API/auth boundary changes) | **EXIT this skill immediately.** Apply Simplicity Q1/Q2 + TDD + fresh command verification directly. | Forbidden to generate plan docs, goal ledgers, or subagents for trivial edits. |
| **`/plan` (Plan-First)** | `M/L` multi-file slice (`3–8` files), greenfield feature, or cross-layer architectural change | Load [Plan-First Execution](references/plan-first-execution.md) + [Execution Plan Template](templates/execution-plan.md). | If `> 8` files or `>= 2` independent subsystems, split into separate subsystem plans first. |
| **`/goal` (Evidence Loop)** | Ambiguous intent, numeric threshold (`p95`, coverage, bundle KB), eval target, or pre-ship audit | Load [Goal-Completion Evidence Loop](references/goal-completion-evidence-loop.md) + [Goal Contract Template](templates/goal-contract.md). | Skip formal Goal Contract ceremony for single-step binary fixes; keep Iron Law fresh check. |
| **`/teamwork` (Parallel)** | `>= 3` genuinely disjoint write surfaces, parallel audit fan-out, or independent author/verifier lanes | Load [Multi-Agent Teamwork Orchestration](references/multi-agent-teamwork-orchestration.md) + [Teamwork Dispatch & Ledger Template](templates/teamwork-dispatch-and-ledger.md). | Forbidden when edits touch `<= 2` files or share tight coupled state; use Inline Plan instead. |

---

## Standalone Child Pre-Flight Fallback

When invoked standalone without the root suite orchestrator, complete these three checks before mutating application code:

1. **System-First Lock (Phase 3A Invariant)**: Confirm architecture boundaries, data schema, and API/token contracts exist on disk—or author a concise 1-page contract before Task 1 begins.
2. **Simplicity Self-Interrogation (Q1/Q2)**: Verify whether a zero-new-dependency native primitive (`std` library, SQL, semantic HTML, modern CSS) solves the task with equal or higher craft.
3. **Fresh Verification Iron Law**: Never claim completion, passing tests, or parity without running the exact verification command **after** the final edit and reading its full exit status.

---

## Module & Template Dispatch Index

| Execution Mode | Reference Module (Read On Demand) | Reusable Template | Runtime Output Artifact | Est. Tokens |
|---|---|---|---|---:|
| **`/plan`** | [Plan-First Execution](references/plan-first-execution.md) | [Execution Plan Template](templates/execution-plan.md) | `execution-plan.md` | ~1,900 |
| **`/goal`** | [Goal-Completion Evidence Loop](references/goal-completion-evidence-loop.md) | [Goal Contract Template](templates/goal-contract.md) | `goal-evidence-ledger.md` | ~1,900 |
| **`/teamwork`** | [Multi-Agent Teamwork Orchestration](references/multi-agent-teamwork-orchestration.md) | [Teamwork Dispatch & Ledger Template](templates/teamwork-dispatch-and-ledger.md) | `teamwork-handoff.md` | ~2,100 |

---

## Cross-Runtime Portability Matrix

Execute `/plan`, `/goal`, and `/teamwork` identically across any host harness by mapping abstract capabilities to native runtime primitives (or falling back cleanly to single-agent inline execution):

| Abstract Capability | Antigravity | Claude Code | Codex CLI | Cursor / Single-Agent Fallback |
|---|---|---|---|---|
| **Plan Mode Survey** | Read-only search/read + disk plan | Read-only survey + plan file | Read-only workspace inspection | Read-only survey + `execution-plan.md` |
| **Goal & Evidence Gate** | Fresh command receipts + ledger | Hook/CLI verify + evidence table | Goal tracker + fresh CLI run | Fresh shell run + `goal-evidence-ledger.md` |
| **Parallel Worker Dispatch** | Subagent / Swarm / Workflow API | `Agent` tool / parallel subagents | Parallel subagent sessions | Sequential inline execution (`executing-plans`) |
| **Write Isolation** | Disjoint worktrees or branch lanes | Git worktrees per parallel worker | Isolated sandbox / worktree | Single working tree, strict vertical slices |
| **Coordination & Handoff** | Dedicated state folder + `handoff.md` | Disk progress ledger + diff files | Shared ledger + structured summary | Disk `progress.md` + `teamwork-handoff.md` |
| **Event Wait & Stall Guard** | Event-driven wakeup / monitor tick | Subagent completion callback | Async wait + timeout escalation | Synchronous step-by-step execution |

---

## Token-Economy & Execution Flow

```text
Task Request
  |
  +--> [Step 0 Triage] --(XS/S <= 2 files, 0 boundary risk)--> Direct Exit (Simplicity Q1/Q2 + TDD + Fresh Check)
  |
  +--> [/plan] --------(3-8 files / greenfield / multi-layer) --> execution-plan.md (READY)
  |                                                               |
  |                                     +-------------------------+-------------------------+
  |                                     v                                                   v
  |                              Inline Execution                                    /teamwork (>= 3 disjoint)
  |                                     |                                                   |
  +--> [/goal] <------------------------+---------------------------------------------------+
         |
         +--> 6-Phase Loop + Staleness Check + Deletion Pass -> goal-evidence-ledger.md (COMPLETE)
```

- **Zero Bulk-Loading**: Load at most one mode reference and its template per phase; release finished plan/dispatch context at Spiral boundaries.
- **Path-Pointer Handoffs**: Pass exact file paths, line ranges, and `BASE..HEAD` diff scopes to subagents instead of pasting multi-kilobyte histories.
- **Deterministic Checks First**: Run CLI compilers, linters, and test runners for proof before spending tokens on prose or model review.

---

## Mode Escalation, Return Statuses & Stop Conditions

- **Escalate `/plan` -> `/teamwork`**: Only when a verified `execution-plan.md` yields `> 5` tasks or `>= 3` disjoint vertical slices with zero shared file ownership.
- **Pair `/plan` -> `/goal`**: Close every multi-task `/plan` or `/teamwork` run with `/goal`'s 6-phase verification loop, staleness receipt check, and Pre-Ship Deletion/Condensation Pass before declaring completion.

| Worker / Gate Status | Required Coordinator / Agent Action |
|---|---|
| **`DONE` / `READY` / `COMPLETE`** | Proceed only after reading fresh post-edit verification receipts (`exit 0`). |
| **`DONE_WITH_CONCERNS`** | Inspect caveats first; promote blockers to fix loop or record minor notes explicitly. |
| **`NEEDS_CONTEXT` / `NOT ASSESSED`** | Supply missing contract or run unobserved check; never default unobserved items to pass. |
| **`BLOCKED` / Hard Stop** | Halt immediately and ask the user on destructive ops, security overrides, external pushes/deploys, or broken plans. |
