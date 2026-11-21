# Sample Child Domain Module

This standalone child domain reference validates isolated child-skill link containment and complete six-pillar R2 compliance inside a hierarchical multi-skill package.
Every section keeps links self-contained inside the child skill directory so the child skill works identically standalone or under Parent Orchestrator routing.

## 1. Decision Framework

Evaluate the **Simplest High-Craft Option** first before introducing external frameworks or multi-layer abstractions.
Use the quantitative thresholds below to decide when simple native constructs suffice versus when structured escalation is warranted.
Reject speculative abstractions that lack a verified production bottleneck.

| Option | Quantitative Trigger | Simplest High-Craft Choice | Escalation Threshold |
|---|---|---|---|
| Direct Function Module | `<= 300` lines, `<= 3` callers | Pure stdlib module with typed dataclass contracts | `> 3` independent persistence backends |
| Relational Table + Constraint | `<= 100k` rows/day, ACID required | Single PostgreSQL schema with CHECK constraints | Sustained write rate `> 5,000` inserts/sec |
| Static Generated Asset | `< 10` state transitions | Server-rendered HTML with progressive enhancement | Real-time collaborative state `< 100 ms` RTT |
| Native CSS Layout | `<= 12` page sections | CSS Grid and Flexbox with custom properties | Complex 2D physics or WebGL canvas |

### Socratic Anti-Overengineering Gate

Before approving any implementation plan, record written answers to all four prompts:
1. Does a simpler approach deliver equal or higher quality, reliability, and maintainability?
2. Which dependencies, config layers, or intermediate wrapper classes can be deleted immediately?
3. Is every proposed component solving a verified current requirement rather than hypothetical scale?
4. Can this design be expressed in at least 25% fewer files and clearer data contracts?

### Quantitative Engineering Boundaries

- Target API response budget: `p95 <= 250 ms` under nominal load.
- Target cold-start budget: `<= 500 ms` for serverless or CLI tooling.
- Maximum transitive runtime dependencies per child component: `<= 3` justified packages.
- Maximum function body length after condensation: `<= 40` executable lines.
- Maximum nested conditional depth inside request handlers: `<= 3` levels.
- Maximum database round-trips per synchronous user action: `<= 3` queries.
- Minimum input validation coverage on public boundary schemas: `100%` explicit schema checks.
- Maximum permitted unindexed sequential scans on tables exceeding 10,000 rows: `0` queries.
- Maximum permitted hardcoded credentials or tokens in source files: `0` occurrences.
- Maximum allowed cross-child relative path escapes in Markdown links: `0` escapes.
- Minimum required boundary test cases per validator input type: `3` distinct edge values.
- Maximum allowed external CSS frameworks when native grid suffices: `0` frameworks.
- Minimum accessible touch target size on interactive controls: `44x44 px`.
- Minimum keyboard focus indicator contrast ratio: `3.0:1` against adjacent surface.
- Maximum animation duration for micro-interactions: `<= 250 ms` with reduced-motion fallback.
- Maximum allowed placeholder text or `Lorem ipsum` snippets: `0` snippets.
- Minimum required fields in child handoff record: `3` structured metadata fields.
- Maximum token budget for child skill entry router: `<= 2,500` tokens.
- Maximum allowed circular alias references in design tokens: `0` cycles.
- Minimum required verification items per checklist: `5` concrete falsifiable checks.
- Maximum allowed unhandled exceptions on malformed CLI inputs: `0` tracebacks.
- Minimum required documentation language consistency: `100%` English prose.
- Maximum permitted unused exports or dead helper functions after Deletion Pass: `0` items.
- Minimum required explicit error exit codes for gate failures: non-zero status code.
- Minimum required documentation of rejected complex alternatives: `1` written rationale.
- Maximum permitted speculative feature flags without active experiment owner: `0` flags.
- Minimum required idempotency guarantees on mutating webhook handlers: `100%` deduplicated.
- Maximum permitted inline style overrides bypassing semantic tokens: `0` overrides.
- Minimum required schema migration rollback safety: zero-downtime expand-and-contract.
- Maximum permitted unverified assumptions carried into release gate: `0` assumptions.
- Minimum required audit trail entries per Spiral cycle transition: `1` immutable record.
- Maximum permitted blocking synchronous calls in healthcheck probes: `0` calls.
- Minimum required static syntax verification pass rate: `100%` across all scripts.
- Maximum permitted third-party Python package imports in stdlib validators: `0` imports.
- Minimum required explicit error diagnostics when invalid JSON or YAML frontmatter is parsed: clear message with file path.
- Maximum allowed unlinked orphan template files inside child skill templates directory: `0` files.
- Minimum required integration coverage for boundary and error-path behaviors: `100%` of documented exit codes.
- Maximum permitted relative link climbs escaping child skill root boundary: `0` climbs.
- Minimum required execution speed for standalone child validator checks: `<= 2.0 s` local run.

## 2. Step-by-Step Workflow

Follow these sequential stages with explicit inputs, owners, outputs, and deletion-pass verification.
Do not start downstream implementation before upstream gate artifacts are marked `PASS`.

1. **Step 1 — Ingest Charter and Constraints (Owner: Child Skill Lead)**
   - **Inputs**: Approved Spiral Charter (`<= 2` pages) and system boundary list.
   - **Action**: Validate requirement clarity, measurable SLO targets (`p95 <= 250 ms`), and explicit scope exclusions.
   - **Action Detail**: Record edge-case invariants and invalid input handling rules upfront.
   - **Output**: Bounded task specification ready for design.

2. **Step 2 — Draft Simplest High-Craft Solution (Owner: Domain Engineer)**
   - **Inputs**: Task specification and native platform capability matrix.
   - **Action**: Design the minimal contract using standard language and database primitives before evaluating any external package.
   - **Action Detail**: Document why alternative heavy frameworks were rejected in favor of native primitives.
   - **Output**: Minimal design proposal with external dependency count `<= 1`.

3. **Step 3 — Validate Contract Against Standalone Boundaries (Owner: Domain Engineer)**
   - **Inputs**: Minimal design proposal and child template schema.
   - **Action**: Verify all schema fields, error codes, and file paths are self-contained inside the child domain boundary.
   - **Action Detail**: Confirm zero circular dependencies or undocumented implicit state assumptions.
   - **Output**: Verified standalone interface specification.

4. **Step 4 — Execute Complexity Budget & Deletion/Condensation Pass (Owner: Peer Reviewer)**
   - **Inputs**: Draft module, code diff, and template artifact.
   - **Action**: Delete redundant indirection, inline single-use abstractions, and compress verbose branching into flat guard clauses.
   - **Action Detail**: Remove unused configuration flags, speculative feature switches, and duplicate validation helpers.
   - **Output**: Condensed deliverable ready for standalone validation.

## 3. Reusable Artifact & Template

Instantiate [Child Artifact Template](../templates/child-template.md) for every deliverable generated by this child skill.
Keep all references self-contained within the child skill directory so standalone installation never breaks relative paths.

| Field | Format | Constraint | Example |
|---|---|---|---|
| `artifact_id` | Kebab-case slug | Matches `^[a-z0-9-]+$` | `"child-spec-01"` |
| `simplest_design` | Prose `>= 25` chars | Names native primitive chosen first | `"Direct SQL query with explicit typed row mapping"` |
| `verification_status` | `PASS` or `FAIL` | Must equal `PASS` before handoff | `"PASS"` |

Field completeness requirements:
- `artifact_id` must be unique within the current Spiral cycle output directory.
- `simplest_design` must explicitly compare the chosen primitive against the rejected complex option.
- `verification_status` may transition to `PASS` only after executing the local verification command below.

## 4. Verification Checklist

- [ ] Standalone child skill links resolve exclusively inside the child skill directory without external relative climbs.
- [ ] Simplest High-Craft Option was evaluated and recorded prior to selecting any complex architecture.
- [ ] Complexity Budget and Deletion Pass removed redundant wrappers, speculative hooks, and dead code paths.
- [ ] All template fields conform to documented schema types and quantitative bounds.
- [ ] Automated standalone checks execute cleanly with zero third-party runtime dependencies.
- [ ] Error paths and boundary inputs have deterministic failure behavior without unhandled exceptions.

## 5. Hard Quality Gate

Child skill deliverables pass only when all deterministic checks succeed without warnings or stub content.
Any single failed criterion blocks handoff to downstream child skills.

- **PASS Criteria**:
  1. All six R2 pillars exist in order with concrete thresholds and zero placeholder text.
  2. Standalone link verification passes (`0` broken or escaping relative links).
  3. Deletion/Condensation Pass notes confirm zero redundant wrapper layers.
  4. Run local validation check exiting `0`:
     ```bash
     python3 -m py_compile ../../scripts/sample_check.py
     ```
- **FAIL Criteria**:
  1. Any relative link escapes the child skill directory or targets a missing file.
  2. Missing Simplicity Interrogation or Deletion Pass evidence.
  3. Non-zero validation exit status or presence of stub markers.

## 6. Anti-Patterns

Reject every child-domain anti-pattern below prior to marking `verification_status` as `PASS`.

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| Cross-Child Relative Coupling | Breaks standalone child-skill installation when links climb into sibling skill folders | Markdown links containing `../../other-child/` | Keep child references self-contained and coordinate across children only through Parent `registry.json` |
| Over-Engineered Wrapper Layers | Multiplies token consumption and cognitive load without improving correctness | Pass-through interfaces wrapping single native API calls | Call native language or database primitives directly with explicit boundary validation |
| Unbounded Boilerplate Checklist | Creates false confidence with vague items that cannot be falsified | Checklist items under 4 words or lacking observable pass/fail bounds | Write concrete, testable verification assertions with measurable thresholds |
| Premature Client State Stores | Adds hydration bugs and bundle weight when URL params or server state suffice | Importing global state managers for `< 3` local UI flags | Use native HTML forms, URL search parameters, and local component state first |
| Hardcoded Secret Literals | Leaks credentials into version control and breaks environment rotation | API keys or tokens embedded directly in source modules | Read runtime secrets from environment variables or secret managers only |
| Unchecked External Inputs | Exposes SQL injection, XSS, and runtime crashes on boundary inputs | Direct string interpolation in SQL or unvalidated user HTML | Use parameterized queries, strict schema validation, and safe JSX escaping |
