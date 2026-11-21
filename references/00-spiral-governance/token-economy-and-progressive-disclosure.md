# Token Economy & Progressive Disclosure ("Maximum Signal, Minimum Tokens")

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow-the-8-runtime-protocols) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This module defines the operational runtime architecture minimizing **tokens-per-verified-task** across skill discovery, progressive module loading, structural reads, deterministic checks, subagent isolation, KV-cache stability, and Spiral-boundary compaction—without sacrificing rigor.

---

## 1. Decision Framework

### 1.1 Core Doctrine: Tokens-Per-Task & the "Smart Zone"

> *"Optimize total end-to-end tokens to verified completion (discovery + tool schemas + arguments + replies + retries), never isolated payload bytes. Keep active context inside the model's high-reasoning smart zone (`<= 150k` tokens; `< 2,000` focused task lines; `> 5,000` lines = flooding)."*

Three structural principles maximize signal per token:
1. **KV-Cache Prefix Stability**: Keep static instructions (`tools -> system -> templates -> history -> dynamic`) deterministic and append-only; NEVER inject live timestamps, UUIDs, or random counters into reusable skill prefixes.
2. **Order for Recency**: Place stable constraints first and live failing errors, active diff lines, and immediate next step last to avoid lost-in-the-middle degradation.
3. **Never Trust Ephemeral Todo State Across Compaction**: Always persist canonical state to disk (`<!-- CHECKPOINT -->`) before `/compact` or `/clear`.

### 1.2 Authoring & Runtime Progressive Disclosure Budgets

| Tier | Artifact / Mechanism | Quantitative Budget Gate | Loading & Authoring Rule |
|---|---|---|---|
| **L1 — Metadata** | Frontmatter `name` + `description` | `<= 500` chars target (`<= 1,024` hard cap, `<= 150` tokens) | Trigger-only third-person SDO keywords; **zero workflow summary inside `description`** |
| **L2 — Router (`SKILL.md`)** | Parent + active `<= 2` Child `SKILL.md`s | `<= 250` lines ideal (`<= 500` warn, `> 800` error) | Routes by Spiral stage, Execution Mode, & Surface; 1-level-deep links ONLY; zero `@` imports |
| **L3 — CLI Projection** | `python3 scripts/query_skill.py` | `100–600` tokens per query | Run `--headings`, `--extract`, `--pillar`, or BM25+MMR search BEFORE reading files |
| **L4 — Range Read** | `references/**/*.md` sections | `<= 1` active module (`2–4k` tokens) | Files `> 250` lines include a Top TOC; use `grep` + `StartLine..EndLine` (`40 KB` Read Guard) |

### 1.3 Read vs. Deterministic Script vs. Subagent Matrix

| Task Shape | Optimal Token-Saving Action | Forbidden Token-Burning Habit |
|---|---|---|
| Lookup checklist, gate, anti-pattern, surface route, or template | `python3 scripts/query_skill.py "<query>" -n 3` or `--extract <path> "<Heading>"` | Reading 4–6 full markdown files to orient |
| Verify links, frontmatter, R2 pillars, token budget, or gate invariants | Run `validate_skill.py`, `query_skill.py --audit-budget`, `check_spiral_gates.py` | Asking the LLM to count headings, check JSON, or trace ADR cycles by eye |
| Inspect `1–2` known files (`< 350` lines / `< 40 KB`) | Batched parallel `read_file` in one turn | Spawning a subagent for 1–2 small files |
| Explore sprawling codebase (`> 5k` tokens or `> 4` files) | Dispatch fresh-context isolated subagent returning `path:START-END reason` | Dumping 25 raw files into parent orchestrator context |
| Inspect large file (`> 40 KB` or `> 400` lines) or noisy test log | Run `--headings <path>` / `grep -n` / AST symbol lookup -> narrow `StartLine..EndLine` | Whole-file reads or printing 2,000-line test logs (`pytest -q --tb=short`) |
| Execute `>= 3` identical small edits across sibling files | Batch into parallel tool calls or a single structured brief | Serial 1-file-per-turn loops replaying full context N times |

### 1.4 Phase-Boundary Context Decision Tree

| Session State Signal | Recommended Action | Why |
|---|---|---|
| Context `< 50%`, same Spiral quadrant, active files in view | **Continue** | KV cache stays warm with zero handoff overhead |
| Moving to an unrelated ticket or finished Spiral | **`/clear` after disk `<!-- CHECKPOINT -->`** | Prevents cross-task pollution and prefix bloat |
| Approaching `60–70%` context (or `160k` on `200k` window) at Spiral boundary | **`/compact` after disk `<!-- CHECKPOINT -->`** | Preserves exact paths/ADRs while clearing old tool turns |
| Same bug failed `>= 2` fix attempts | **Freeze + `/clear` + re-read clean source** | Stops sunk-cost hallucination loops |
| `>= 3` independent subsystems or `> 5k`-token unknown exploration | **Fresh-context Subagent (`<= 2` active skills)** | Isolates noisy reads outside parent smart zone |

### 1.5 Simplest High-Craft & Anti-Overengineering Alignment

Token efficiency and **Radical Simplicity ("Least Code, Highest Craft")** reinforce each other: fewer files, native primitives, and zero speculative wrappers mean smaller reads, fewer tool calls, and lower context pressure. Before expanding abstractions or spawning subagents, apply the **Simplest High-Craft Self-Interrogation**:
- **Code & Architecture**: *"Is there a simpler native approach (stdlib, SQL, HTML/CSS) delivering equal or higher quality with fewer files and dependencies?"* (Reject YAGNI layers before generating boilerplate.)
- **Orchestration & Tokens**: *"Can `query_skill.py` or a single-pass Direct edit solve this cleanly without spawning `/teamwork` subagents or bulk-reading references?"*

---

## 2. Step-by-Step Workflow (The 8 Runtime Protocols)

### P1 — Query CLI First
Before opening any `references/**/*.md` or `templates/*.md`, project the exact slice via [query_skill.py](../../scripts/query_skill.py):
- `python3 scripts/query_skill.py --stage 3a --surface web-app --summary`
- `python3 scripts/query_skill.py "deletion pass" --mmr 0.7 -n 3 --json`
- `python3 scripts/query_skill.py --headings references/00-spiral-governance/spiral-lifecycle.md`
- `python3 scripts/query_skill.py --extract references/00-spiral-governance/spiral-lifecycle.md "5. Hard Quality Gate"`

### P2 — Structural & Grep-First Reads (40 KB Read Guard)
Never bulk-read files exceeding `40 KB` (`~10k` tokens). First extract the fence-aware heading map (`--headings`) or symbol locations (`grep -n`, AST/LSP symbol tools where available), then read exact `StartLine..EndLine` windows. Keep focused per-task context `< 2,000` lines.

### P3 — Parallel Lane Matrix & Fresh-Context Subagents
Batch independent read/check calls into one turn. Isolate exploration requiring `> 5k` tokens into **fresh-context** subagents returning only `path:START-END reason` citations. Partition parallel execution ONLY when `>= 3` independent subtasks exist or context pressure exceeds `60%`, assigning strictly disjoint write paths.

### P4 — Search-First & Surgical Coding (Rule of 500)
Search existing repo modules, stdlib, and vetted libraries (`Adopt -> Extend -> Compose -> Build`) before writing custom utilities. Enforce the Spiral's **Complexity Budget** and execute a **Deletion/Condensation Pass** before Phase 3C sign-off (*"if 50 clean lines solve it, never write 200"*; delete unused exports and redundant wrappers so future reads stay lean). For mechanical refactors exceeding `500` lines, prefer AST/codemod scripts over manual multi-turn edits.

### P5 — Tool Output & Observation Masking
Offload verbose outputs `> 2,000` chars to scratch files and retain a `<= 200`-token summary + path pointer. Run quiet/failure-only test commands (`pytest -q --tb=short`, `| tail -n 40`). Mask resolved stale tool outputs older than 3 turns (`[Obs:id elided; key result: ...]`)—**NEVER** elide active stack traces or raw file slices needed for upcoming edits.

### P6 — Incremental Section Writing
For long artifacts (PRDs, architecture specs, multi-module code), write the heading skeleton to disk first, then draft and flush one section at a time (`~3–5k` peak context vs. `~30–50k` monolithic generation).

### P7 — Calibrated Terse Intermediate Reporting
In intermediate coordination notes and status updates, lead with the answer, keep sentences concise (`<= 20` words), and drop filler ceremony. Keep code, file paths, negations, security warnings, user-facing documentation, PR descriptions, and commit messages **100% clear, complete prose**.

### P8 — Spiral-Boundary Compaction & Anchored Checkpoints
Compact or clear context **only at clean Spiral boundaries** (`Q1->Q2`, `Q2->3A`, `3A->3B`, `3C->Q4`) or between unrelated tickets — never mid-edit. Before compacting:
1. Overwrite the disk `<!-- CHECKPOINT -->` (`<= 25` lines) preserving: **Intent, Exact Files/Symbols Modified, Locked ADRs, Verification Pass/Fail, Next Action**.
2. Validate resume readiness with the **4-Probe Check**: *(1) Recall* (exact constraints/ADRs), *(2) Artifact* (exact paths/symbols), *(3) Continuation* (single next step), *(4) Decision* (why alternatives were rejected).
3. Trigger `/compact` or `/clear` cleanly and reload ONLY Parent `SKILL.md` plus the `<= 2` active Child Skills for the incoming Spiral quadrant.

---

## 3. Reusable Artifact & Template

### Anchored Disk Checkpoint (`<= 25` Lines, Overwrite-In-Place)

Embedded inside [Spiral Charter](../../templates/spiral-charter.md) (`<!-- CHECKPOINT -->` ... `<!-- /CHECKPOINT -->`):

```markdown
<!-- CHECKPOINT -->
- **Active Spiral**: SP-001 | **Tier**: standard | **Mode**: greenfield
- **Current Quadrant**: 3A | **Phase 3A Lock**: LOCKED
- **Intent**: Multi-tenant auth + Postgres schema locked before Slice 1 UI
- **Locked Decisions**: ADR-0001 (Modular Monolith + Postgres), SIR-001 (Option A PASS)
- **Verification**: check_spiral_gates --stage q2-risk PASS; skeleton smoke test pending
- **Next Action**: Run `python3 scripts/check_spiral_gates.py --stage foundation --strict`
- **Files Modified**: docs/architecture/architecture.md, docs/architecture/data-model.md
<!-- /CHECKPOINT -->
```

### Token Budget Audit Contract (`query_skill.py --audit-budget`)
Checks deterministically across Parent + active Child Skills:
1. **L1 Metadata**: `SKILL.md` frontmatter `description <= 1,024` chars and estimated trigger cost `<= 150` tokens.
2. **L2 Router Size**: `SKILL.md` body lines (`<= 500` pass, `501–800` warn, `> 800` error) and zero `@path` eager imports.
3. **L3 Link Depth & TOC**: Links from `SKILL.md` stay 1 level deep into `references/` or `skills/<name>/`; any reference file `> 250` lines includes a Top Table of Contents (`## Contents` / `> **Contents**:`).
4. **Estimated Token Totals**: Reports `L1_trigger_tokens`, `L2_router_tokens`, and `L3_deferred_tokens` per skill without failing on planned M2–EXP child stubs.

### Concrete Token-Saving Command Recipes (P1–P8 in Practice)

```bash
# 1. Discover exact child skill & pillar without reading 10 files (~150 tokens)
python3 scripts/query_skill.py --stage 3a --surface web-app --summary

# 2. BM25 + MMR search across all modules with bounded excerpts (~300 tokens)
python3 scripts/query_skill.py "system first foundation gate" --mmr 0.7 -n 3

# 3. Inspect headings + line ranges of a reference before partial read (~120 tokens)
python3 scripts/query_skill.py --headings references/00-spiral-governance/spiral-lifecycle.md

# 4. Extract ONE specific section cleanly (~250 tokens)
python3 scripts/query_skill.py --extract references/00-spiral-governance/spiral-lifecycle.md "5. Hard Quality Gate"

# 5. Audit progressive-disclosure budgets across Parent + active Children
python3 scripts/query_skill.py --audit-budget --json
```

### Quiet / Low-Noise Test & Tool Flags (P5 Reference)
| Tool | Noisy Default (Avoid) | Quiet / Failure-Only Flag (Use) |
|---|---|---|
| `pytest` | `pytest -vv` (prints full tracebacks & passes) | `pytest -q --tb=short` |
| `vitest` / `jest` | `npm test` with full ANSI spinner | `npx vitest run --reporter=dot` |
| `git diff` | Unbounded `git diff` across lockfiles | `git diff --stat` then scoped `git diff -- <path>` |
| `grep` / search | Unbounded recursive grep into `node_modules` | Scoped `grep -rn` excluding build/vendor dirs |

### Anchored Compaction 4-Probe Verification Template
Before executing `/clear` or `/compact`, verify your disk `<!-- CHECKPOINT -->` answers all 4 probes without re-reading chat history:
1. **Recall Probe**: Are the active Spiral ID, Rigor Tier, and key ADRs/constraints stated explicitly?
2. **Artifact Probe**: Are exact modified file paths and symbol names listed?
3. **Continuation Probe**: Is the single next executable command or edit unambiguous?
4. **Decision Probe**: Are rejected alternatives noted so post-compaction turns do not re-propose them?

### Subagent Isolation & Token Accounting Checklist
Before spawning a subagent (`Agent` / `Teamwork` worker), verify positive net token ROI (`rea-analysis-optimization` rule):
- **Spawn Subagent When**: Exploration spans `> 4` unknown files or `> 5k` tokens of noisy output, OR `>= 3` genuinely parallel subsystems have disjoint write surfaces.
- **Keep In Parent When**: Target is `1–2` known files (`< 350` lines each), or deterministic script (`validate_skill.py`, `query_skill.py`, `check_spiral_gates.py`) answers in `< 200` tokens.
- **Fresh-Context Mandate**: Force clean fresh context on exploratory subagents (avoid inheriting 100k tokens of parent history); require concise `path:START-END reason` citations or disk handoffs back.

### Calibrated Terse Output Rules (P7 Boundaries)
| Context Channel | Style Target | Preserved Verbatim (Never Abbreviate) |
|---|---|---|
| Intermediate status / agent-to-agent updates | Answer-first, `<= 20` words/sentence, zero filler greetings | Exact file paths, symbol names, CLI commands, error codes, `NOT`/`MUST NOT` negations |
| Persisted docs (`README`, `SKILL.md`, `references/`, PRs, ADRs) | Full, crisp, high-density English technical prose | Complete schemas, security warnings, acceptance criteria, git commit messages |

---

## 4. Verification Checklist

- [ ] Parent `SKILL.md` stays `<= 250` lines (`<= 450` hard router cap), with trigger-only `description <= 1,024` chars.
- [ ] Zero `@path` eager-import directives and zero `AGENTS.md`/`GEMINI.md` pollution anywhere in repo.
- [ ] Reference modules `> 250` lines include a compact Top TOC; links from `SKILL.md` stay 1 level deep.
- [ ] `scripts/query_skill.py --audit-budget`, `--headings`, `--extract`, and `--mmr` search execute cleanly in Python 3 stdlib.
- [ ] Large reads (`> 40 KB`) guarded by heading/symbol lookup + narrow `StartLine..EndLine` slices; test runners use quiet/short flags.
- [ ] Disk `<!-- CHECKPOINT -->` (`<= 25` lines) written prior to compaction and passes the 4-Probe Check.

---

## 5. Hard Quality Gate

- **Commands**:
  - `python3 scripts/validate_skill.py . --strict --json`
  - `python3 scripts/query_skill.py --audit-budget --json`
- **PASS Criteria**:
  - Parent `SKILL.md` within budget (`<= 250` lines ideal / `< 500` lines), `description <= 1,024` chars without workflow spoilers.
  - Zero `@` eager imports, zero broken relative links, 1-level link depth from `SKILL.md`, Top TOC present on references `> 250` lines.
  - `query_skill.py` BM25+MMR / `--headings` / `--extract` / `--audit-budget` execute cleanly in Python 3 stdlib (`exit 0`).
- **FAIL Criteria**:
  - `SKILL.md > 800` lines, workflow steps leaked inside `description`, or `@` force-loads present.
  - Unbounded bulk-reads of `references/` or `> 2` Child Skills loaded concurrently.
  - Relying solely on ephemeral todo memory across `/compact` without disk `<!-- CHECKPOINT -->`.

### Concrete Token-Budget Diagnostic Remediation
- If `--audit-budget` flags `SKILL.md > 500 lines`: move deep procedures or tables out to `references/` and replace with a 3-line pointer + `query_skill.py` command.
- If `--audit-budget` flags missing Top TOC on a `> 250`-line reference: add a 1-line `> **Contents**: ...` anchor strip under the `# Title`.
- If `--audit-budget` flags L1 `description > 150 est. tokens`: trim redundant adjectives while preserving exact domain trigger keywords.

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Upfront Bulk-Reading** | Burns 40k–100k tokens loading irrelevant domains before scoping | Agent reads `> 3` full reference docs before identifying Spiral stage | Route via `SKILL.md` -> `query_skill.py --headings/--extract` -> `<= 2` active skills |
| **Workflow-Spoiler `description`** | Summarizing Q1–Q4 inside YAML `description` causes agents to skip `SKILL.md` | Frontmatter `description` lists workflow steps | Keep `description` purely third-person SDO triggers (`<= 1,024` chars) |
| **`@path` Eager Context Bombs** | Force-loads linked docs upfront regardless of relevance | `@references/...` syntax inside `SKILL.md` or children | Standard Markdown links + explicit `query_skill.py` commands |
| **Mid-Implementation Compaction** | Loses half-edited symbol context and causes broken retries or re-reads | `/compact` triggered mid-edit or without disk checkpoint | Write `<= 25`-line `<!-- CHECKPOINT -->` at Spiral boundaries; verify via 4-Probe Check |
| **Unmeasured Micro-JSON Tweaks** | Shorter keys that trigger extra tool retries increase total tokens-per-task | Extra discovery/retry round-trips after shrinking payloads | Measure total end-to-end task tokens; use deterministic `--summary` & `--extract` |
| **Noisy Log / Whole-File Dumps** | Floods past `150k` smart zone with 2,000-line raw test/grep outputs | Unfiltered test runs or unbounded `read_file` on `> 40 KB` files | Quiet flags (`-q --tb=short`), `--headings`, range reads, and scratch offload |
| **Volatile Prefix Timestamps** | Changing timestamps/UUIDs inside system/skill headers breaks KV-cache hits | Dynamic `now()` tokens embedded in reusable templates/prompts | Keep static prefixes 100% deterministic; put dynamic dates only in disk records |
