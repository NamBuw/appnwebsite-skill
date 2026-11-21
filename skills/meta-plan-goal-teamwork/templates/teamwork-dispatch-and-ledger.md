# Teamwork Dispatch & Ledger Schema (`teamwork-handoff.md` & `progress.md`)

> Instantiate this template to produce the runtime artifacts `teamwork-handoff.md` and `progress.md` when `/teamwork` is justified by `>= 3` genuinely disjoint write surfaces or independent author/verifier lanes.

## Metadata Header

| Field | Value |
|---|---|
| **Run ID** | `<RUN-001>` |
| **Plan Ref** | `<path/to/execution-plan.md>` |
| **Runtime Adapter** | `<Antigravity \| Claude Code \| Codex \| Cursor/Inline>` |
| **Coordinator** | `<coordinator identifier — never edits feature code mid-swarm>` |
| **Merge Base SHA** | `<git rev-parse HEAD before parallel dispatch>` |
| **Target Runtime Artifacts** | `teamwork-handoff.md`, `progress.md` |

---

## 1. Simplicity & Topology Justification

- **Why `/teamwork` Is Earned**: `<exact list of >= 3 disjoint domains or independent author/verifier needs proving single-agent inline is slower/riskier>`
- **Topology**: `<Fan-Out Subagents \| Pipeline \| Coordinator-Worker Swarm>` (`1` independent verifier per `2–4` authors)
- **Complexity Budget**: `Max Workers: <N>`, `Max Fix Rounds per Task: 5`, `Post-Merge Deletion Pass Required: YES`

---

## 2. Worker Ownership & Isolation Matrix

| Worker Name | Role | Model Tier | Workspace Mode | Exclusive `owns` Paths | `must_not_touch` Paths | Status |
|---|---|---|---|---|---|---|
| `<worker_1>` | `<author>` | `<Low \| Standard \| Top>` | `<worktree \| branch \| share>` | `<exact disjoint paths>` | `<all other worker paths + registry>` | `<PENDING \| ACTIVE \| DONE \| BLOCKED>` |
| `<worker_2>` | `<author>` | `<Standard>` | `<worktree \| branch \| share>` | `<exact disjoint paths>` | `<all other worker paths + registry>` | `<PENDING \| ACTIVE \| DONE \| BLOCKED>` |
| `<verifier_1>` | `<verifier>` | `<Standard \| Top>` | `<inherit (read-only)>` | `<handoff/verification report only>` | `<all source & test files>` | `<PENDING \| ACTIVE \| DONE>` |

---

## 3. Cold-Start Worker Brief Contract (Zero-Paste Rule)

Every dispatched worker starts cold and MUST receive this self-contained 6-part brief (referencing file paths or `#seq` IDs rather than pasting long history):

1. **Project Context (1 sentence)**: `<system purpose, stack, and active Spiral milestone>`
2. **Ownership & Boundaries**: `owns: [<exact paths>]`; `must_not_touch: [<explicit exclusions>]`
3. **Canonical Inputs (Paths Only)**: `<path/to/execution-plan.md#task-N>`, `<path/to/contract.md>`
4. **Isolation & Subagent Rule**: `Do not spawn nested subagents or duplicate task reviewers.`
5. **Verification Command**: `<exact CLI command worker must execute fresh before claiming done>`
6. **Done Contract & Report Path**: `Emit status (DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED) and write 5-component handoff (Observation, Logic Chain, Caveats, Conclusion, Verification Method) to <exact handoff path>.`

---

## 4. Workstream Ledger & Bounded Fix-Loop Log

| Workstream / Task | Assigned Worker | Diff Package (`BASE..HEAD`) | Verifier Verdict | Fix Round (`0–5`) | Outcome |
|---|---|---|---|---:|---|
| `<Task 1>` | `<worker_1>` | `<abc123..def456>` | `<PASS \| FAIL \| NEEDS_CONTEXT>` | `<0>` | `<complete \| parked \| ruled>` |
| `<Task 2>` | `<worker_2>` | `<abc123..ghi789>` | `<PASS \| FAIL \| NEEDS_CONTEXT>` | `<1>` | `<complete \| parked \| ruled>` |

- **Stall & Quota Recovery Log**: `<none or exact root cause (unaddressed output / unread queue / dependency deadlock / quota model switch) + resolution>`

---

## 5. Exhaustive `Rulings I Made`, `Deferred Minors` & Post-Merge Verification

### 5.1 Rulings Register (Every Ambiguity, Conflict, or Breaker Adjudication)
1. `<Ruling ID>: Decision: <chosen option> — Rationale: <why> — Cost if wrong: <reversibility/impact>`

### 5.2 Deferred Minors Register
- `<Minor ID>: <file:line or description> — Reason deferred (non-load-bearing) — Follow-up owner/milestone>`

### 5.3 Post-Merge Deletion Pass, Whole-Branch Review & Full Suite Receipt
- **Pre-Ship Deletion Pass**: `Files Deleted: <N>`, `Deps Removed: <N>`, `Net LOC Reduced: <delta>`
- **Whole-Branch Final Review**: `Reviewer Tier: Top`, `Fix Wave Count: <= 1`, `Verdict: <PASS | CONCERNS>`
- **Full-Suite Post-Merge Verification**: `<exact full-repo test/validation command> -> exit 0 (<timestamp UTC>)`
- **Workspace Cleanup**: `<temporary worktrees/branches pruned cleanly>`
