# Sample Governance Module

This module establishes a complete six-pillar domain reference for automated structural verification.
Every section enforces concrete engineering rigor, radical simplicity, and falsifiable gate criteria.
Agents must consult only the active quadrant section rather than preloading unrelated modules.

## 1. Decision Framework

Before introducing any architectural layer, third-party package, or runtime service, teams must evaluate the **Simplest High-Craft Option** first.
Apply the Anti-Overengineering Self-Interrogation Protocol prior to every technical design decision.
Never adopt distributed infrastructure or custom abstractions until measured traffic, latency, or compliance constraints prove native primitives insufficient.
Quantify load, storage volume, and team velocity before escalating out of Tier A.

| Complexity Tier | Trigger Threshold (Quantitative) | Simplest High-Craft Option | Escalation Condition |
|---|---|---|---|
| Tier A: Single-Process Monolith | `<= 5,000 req/min`, `<= 50 GB` data, `<= 10` engineers | Modular monolith with PostgreSQL and standard SQL transactions | Sustained p95 latency `> 250 ms` after indexing |
| Tier B: Background Worker Split | Jobs `> 500 ms` synchronous budget or retry-sensitive webhooks | Single database-backed job table with idempotency key | Queue depth `> 10,000` pending jobs for `> 15 min` |
| Tier C: Dedicated Cache / Read Replica | Read/write ratio `> 20:1` and primary CPU `> 75%` sustained | In-process bounded LRU cache or single read replica | Cache miss storm threatens p99 `< 400 ms` SLO |
| Tier D: Service Extraction | Independent regulatory boundary or `> 3x` scaling divergence | Isolated worker deployment sharing versioned schema contract | Verified cross-team deployment lock-step `> 2` sprints |

### Mandatory Socratic Simplicity Interrogation

Answer all four interrogation prompts in writing prior to selecting Tier B, C, or D:
1. Can an existing language, browser, or database primitive deliver equal or higher reliability and user experience?
2. Which wrapper layers, indirection interfaces, or dependencies can be deleted immediately without reducing correctness?
3. Is this requirement driven by a verified current user constraint or hypothetical future scale (YAGNI)?
4. How can the implementation achieve maximum clarity and craft with at least 30% fewer lines of code?

### Threshold Evaluation Rules

- Latency budget for interactive requests: `p95 <= 200 ms`, `p99 <= 450 ms`.
- Availability error budget for production services: `>= 99.9%` monthly uptime (`<= 43.2 min` downtime).
- Dependency budget per feature slice: `<= 2` newly introduced external packages unless justified by security or compliance.
- Cyclomatic complexity ceiling per function: `<= 10`, maximum nesting depth `<= 3`.
- Database query latency budget: `<= 25 ms` median, `<= 80 ms` p95 per transaction.
- Cold-start CLI execution budget: `<= 150 ms` for Python standard library validators.
- Maximum function body length: `<= 40` lines excluding docstrings and type signatures.
- Maximum file size per domain module: `<= 600` lines unless split into cohesive submodules.
- Maximum active child skills loaded simultaneously: `<= 2` per Spiral quadrant.
- Maximum external runtime network calls in offline validators: `0` calls.
- Minimum unit and boundary test coverage on gate scripts: `100%` branch coverage on error paths.
- Minimum contrast ratio for normal text: `4.5:1` WCAG AA, `7.0:1` WCAG AAA.
- Minimum contrast ratio for large text and UI components: `3.0:1` WCAG AA.
- Maximum bundle size per client route initial payload: `<= 120 KB` gzipped.
- Maximum time-to-interactive budget on mid-tier mobile hardware: `<= 2.5 s`.
- Minimum required retention for architecture decision logs: entire repository lifetime.
- Minimum required verification items per module checklist: `5` falsifiable assertions.
- Maximum allowed stub or placeholder markers in shipped artifacts: `0` occurrences.
- Minimum peer review sign-off count for security-boundary changes: `1` independent reviewer.
- Maximum permitted circular dependencies across registry graph: `0` cycles.
- Maximum permitted unparameterized SQL interpolations: `0` occurrences.
- Minimum required regression scenarios for every P0/P1 defect fix: `1` automated test.

## 2. Step-by-Step Workflow

Execute this deterministic sequence in order before approving any Spiral Quadrant 3 implementation task.
Each step declares explicit inputs, responsible roles, tool commands, and verifiable outputs.
Never skip Phase 3A foundation verification or the Deletion Pass.

1. **Step 1 — Capture Measurable Cycle Objectives & Constraints (Owner: Product & Tech Lead)**
   - **Inputs**: Stakeholder problem statement, latency budget (`p95 <= 200 ms`), error budget (`<= 0.1%`).
   - **Action**: Quantify functional scope, non-functional SLOs, and hard boundary limits in the cycle charter.
   - **Action Detail**: Document explicit non-goals so feature creep cannot enter mid-cycle.
   - **Output**: Signed cycle charter with explicit rejection criteria for out-of-scope features.

2. **Step 2 — Run Simplest High-Craft Interrogation (Owner: Architect)**
   - **Inputs**: Cycle charter and proposed technical approach.
   - **Action**: Answer all four Socratic simplicity questions in writing and evaluate the Simplest High-Craft Option first.
   - **Action Detail**: Compare native SQL/stdlib primitives against every proposed package or middleware layer.
   - **Output**: Completed Simplicity Interrogation Record approving the minimal architecture.

3. **Step 3 — Enforce System-First Foundation Gate (Owner: Systems Engineer)**
   - **Inputs**: Approved Simplicity Interrogation Record and domain entities.
   - **Action**: Author Architecture Decision Records, boundary contracts, data schema, and core repository skeleton before feature coding.
   - **Action Detail**: Verify all contracts live in versioned files and pass static checks.
   - **Output**: Frozen foundation artifacts verified by `python3 scripts/sample_check.py --check`.

4. **Step 4 — Execute Complexity Budget & Deletion/Condensation Pass (Owner: Reviewer & Author)**
   - **Inputs**: Draft implementation diff and dependency manifest.
   - **Action**: Audit every newly added file, helper, and package to eliminate dead branches and redundant wrappers.
   - **Action Detail**: Collapse single-use abstractions into direct functions and remove unused configuration flags.
   - **Output**: Condensed diff meeting complexity ceiling (`<= 3` nesting levels, `<= 40` lines per function).

5. **Step 5 — Verify Against Quantitative Gate & Record Decision (Owner: QA & Release Lead)**
   - **Inputs**: Condensed diff, test execution logs, and checklist evidence.
   - **Action**: Run automated checks, confirm zero unverified assumptions, and record the binary PASS or FAIL gate verdict.
   - **Action Detail**: Archive gate evidence with exact command output and timestamp.
   - **Output**: Immutable gate record authorizing transition to the next Spiral cycle.

## 3. Reusable Artifact & Template

All Spiral cycle decisions and simplicity audits must be persisted using the structured contract defined in [Sample Template](../../templates/sample-template.md).
Every field below is mandatory for automated gate validation.
Keep records concise, scannable, and under 120 lines per cycle.

| Field Name | Format / Constraint | Validation Rule | Example Value |
|---|---|---|---|
| `spiral_cycle` | Positive integer `>= 1` | Must increment monotonically per cycle | `1` |
| `objective` | Non-empty string `20..240` chars | Must state measurable user or system outcome | `"Deliver checkout flow with p95 < 200 ms"` |
| `simplest_option` | Non-empty string `>= 30` chars | Must describe native/minimal baseline evaluated first | `"Single PostgreSQL transaction without Redis"` |
| `deletion_pass_notes` | Non-empty string `>= 20` chars | Must list deleted layers, wrappers, or dependencies | `"Removed custom repository wrapper class"` |
| `gate_verdict` | Literal `PASS` or `FAIL` | Only `PASS` permits Quadrant 3 coding entry | `"PASS"` |

Additional field-level rules:
- `objective` must reference at least one quantitative latency, reliability, or adoption metric.
- `simplest_option` cannot be blank or repeat the escalated architecture description verbatim.
- `deletion_pass_notes` must name at least one removed layer, dependency, or redundant branch or justify `0` deletions.
- `gate_verdict` must never be set to `PASS` while any verification checklist item remains unchecked.

## 4. Verification Checklist

- [ ] Quantified cycle objectives, latency SLOs, and hard failure bounds are documented before any implementation starts.
- [ ] All four Socratic anti-overengineering interrogation questions are answered with concrete technical evidence.
- [ ] The Simplest High-Craft Option was evaluated first and chosen unless quantitative evidence justified escalation.
- [ ] System foundation contracts, data models, and Architecture Decision Records exist prior to feature coding or UI authoring.
- [ ] Complexity Budget and Deletion/Condensation Pass removed speculative abstractions, unused wrappers, and redundant dependencies.
- [ ] Automated helper validation runs cleanly from the command line without external runtime daemons or hidden network state.
- [ ] Template links resolve to real files on disk and contain zero placeholder or stub markers.

## 5. Hard Quality Gate

Transition from planning to implementation is strictly blocked unless every binary condition below holds true.
Never bypass a failing gate by commenting out checks or lowering thresholds mid-cycle.

- **PASS Criteria**:
  1. All required fields in the reusable template artifact are populated without stub markers or empty sections.
  2. Quantitative thresholds (latency, complexity budget, and dependency justification) have explicit numeric targets.
  3. Deletion/Condensation Pass confirms zero gratuitous abstraction layers remain in the diff.
  4. Automated verification command exits with status code `0`:
     ```bash
     python3 scripts/sample_check.py --check
     ```
- **FAIL Criteria**:
  1. Missing Simplicity Interrogation answers or absent Simplest High-Craft Option comparison.
  2. Feature code or UI authoring started before System-First Foundation artifacts passed review.
  3. Unjustified third-party library added when native platform primitives satisfy the requirement.
  4. Non-zero exit code from `python3 scripts/sample_check.py --check` or any broken relative artifact link.

## 6. Anti-Patterns

Reject every anti-pattern below during peer review and Deletion/Condensation Pass audits.

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| Premature Microservices & Event Bus Bloat | Introduces network latency, distributed failure modes, and deployment overhead before product-market or scale need exists | Multiple services, message brokers, or CQRS pipelines for `< 5,000 req/min` workload | Start with a modular monolith backed by ACID database transactions and clean module boundaries |
| Speculative Abstraction & Wrapperitis | Obscures control flow, inflates token cost, and triples code volume with pass-through interfaces that have one implementation | Single-implementation `IUserRepositoryFactory` classes or three-layer pass-through wrappers | Write direct, cohesive functions using native language types until a second genuine implementation appears |
| Dependency-First Engineering | Pulls heavy third-party packages for trivial formatting, state, or UI tasks, increasing bundle size and supply-chain risk | Adding external packages for `< 30` lines of native CSS, HTML, or standard-library logic | Use native platform, browser CSS, and Python/TypeScript standard library primitives first |
| Gate-Bypassed Vibe Coding | Writes feature screens and endpoints before core contracts and data boundaries exist, forcing expensive rewrites | UI components or controllers merged with no ADR, no schema contract, and no simplicity review | Enforce Phase 3A System-First Foundation Gate and Simplicity Interrogation before coding begins |
| Context Bulk-Loading | Exhausts LLM token budgets with irrelevant modules and increases instruction-following drift | Loading `> 3` unrelated domain modules simultaneously | Query the active stage index first and load only the single target reference module |
| Speculative Configuration Sprawl | Buries default behavior under dozens of untested environment toggles and feature flags | More than `5` optional config flags for a single-tenant service | Hardcode clean opinionated defaults until a concrete deployment requires variation |
