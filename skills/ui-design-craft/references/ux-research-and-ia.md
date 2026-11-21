# UX Research & Information Architecture (IA)

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

---

## 1. Decision Framework

Information Architecture (IA) and UX research determine whether users complete high-value tasks on the first visit or abandon a visually polished interface because labels, navigation depth, and mental models conflict with their workflow. Before designing components or visual tokens, select the **Research Rigor Tier** and **IA Topology** proportional to product uncertainty and navigation complexity.

### Research Rigor Tier Selector

| Tier | When to Select | Minimum Evidence Sample | Core Methods | Target Decision Latency |
|---|---|---|---|---|
| **Minimal** | Known workflow, internal tool, or low-risk marketing refresh (`<= 5` pages) | `3–5` target user sessions + `3` competitor teardowns | Batched intake, JTBD synthesis, heuristic baseline (`0–4` severity) | `0.5–1 day` |
| **Standard** | New SaaS workspace, multi-role web/mobile app, or conversion funnel redesign | `5–8` JTBD interviews + `n >= 15` card sort / tree test | Open/closed card sort, tree testing (`>= 80%` success), interactive flow walkthrough | `2–3 days` |
| **Full** | High-stakes regulated domain (fintech, clinical, enterprise platform) or novel IA | `8–12` contextual inquiries + `n >= 30` card sort + moderated usability (`n >= 5/cohort`) | Longitudinal diary/field observation, first-click testing, SEQ + SUS benchmarking | `5–7 days` |

### IA Topology Decision Matrix

| Topology | Max Top-Level (L1) Items | Max Clicks to Core Task | Best-Fit Product Archetype | Avoid When |
|---|---|---|---|---|
| **Flat Hub** | `3–5` items | `1–2` clicks | Focused single-product landing page, utility app, micro-SaaS | Catalog exceeds `25` distinct entity types |
| **Hierarchical L1/L2** | `5–7` L1 items (`<= 2` levels) | `2–3` clicks | B2B SaaS workspaces, developer portals, documentation hubs | Users jump across orthogonal facets |
| **Faceted Search & Filter** | `3–5` global + inline facet bar | `1–2` clicks | E-commerce, directories, log explorers, analytics catalogs | Item count `< 15` (facets add dead weight) |
| **Linear Task Wizard** | `1` focused stepper (`<= 5` steps) | `1` linear flow | Checkout, onboarding, tax/grant submission, identity setup | Users compare non-linear items freely |
| **Command-First (`Cmd+K`)** | `3–5` persistent anchors + palette | `1` shortcut | Power-user IDEs, issue trackers, telemetry consoles | First-time or low-frequency consumer audiences |

### Token Economy & Simplest High-Craft Option (Anti-Overengineering Check)

- **Token Economy Rule:** Query `python3 skills/ui-design-craft/scripts/core_search.py "<domain>" --domain ux` and `--domain product` for targeted guidelines before opening entire reference catalogs. Never duplicate PRD prose inside the design brief; link the existing requirement IDs.
- **Simplest High-Craft Option:** Before commissioning multi-week research studies, custom analytics instrumentation, or deep 4-level mega-menus, ask:
  - *"Can a single flat navigation bar (`<= 5` links), a clickable HTML flow prototype, and 5 task-based user observations resolve the structural uncertainty with equal or higher clarity?"*
  - *"Which secondary tabs, nested routes, or multi-step wizard screens can be deleted outright without reducing task completion?"*
  - *"Are we inventing hierarchical taxonomy for hypothetical future modules instead of optimizing the 3 workflows active today?"*
  In most greenfield and redesign engagements, deleting ambiguous top-level categories produces a larger conversion and usability gain than adding onboarding tours over a broken IA.

---

## 2. Step-by-Step Workflow

1. **Batched Intake & JTBD Synthesis**
   - **Input:** `spiral-charter.md`, `prd.md`, existing product analytics, churn interviews, or support tickets.
   - **Output:** Completed Sections 1–2 of `design-brief.md` (Site-Kind classification, Primary Conversion Action, Functional/Emotional/Social Jobs, Forces of Progress).
   - **Owner:** Product Designer / UX Researcher.
   - **Tool / Script:** `python3 scripts/design_search.py "<product>" --domain product --json` to pull domain-specific pattern and dashboard expectations.
   - **Execution:** Batch all stakeholder questions into one structured intake instead of multi-round chat drift:
     - Lock the single Primary Conversion Action (`<= 6` words, verb + measurable outcome).
     - Map all four **Forces of Progress**: Push (concrete pain triggering search), Pull (desired future state), Anxiety (fear of migration, downtime, or lock-in), and Habit (inertia of spreadsheets, email, or legacy CLIs).
     - Document the top 3 buyer/operator objections and pair each with verifiable proof (benchmark, live sandbox, security posture, or pricing transparency).

2. **Behavioral Personas & Assistive Constraints**
   - **Input:** JTBD interview notes, customer support logs, target device/network telemetry.
   - **Output:** Behavioral persona matrix in `design-brief.md` Section 3.
   - **Owner:** UX Researcher.
   - **Tool / Script:** `python3 scripts/core_search.py "accessibility navigation mobile" --domain ux --json`.
   - **Execution:** Define cohorts strictly by operational reality rather than fictional demographics:
     - **Task Frequency & Pressure:** Daily power operator vs. weekly approver vs. once-a-year setup admin.
     - **Device & Network Baseline:** `390px` mid-tier mobile on `3G/4G` vs. `1440px` dual-monitor desktop.
     - **Assistive Constraints:** Keyboard-only `Tab`/`Shift+Tab` traversal, screen-reader landmarks (`<main>`, `<nav>`, `<aside>`), high-contrast light/dark needs, and vestibular motion sensitivity.
     - Ban demographic vanity fluff (hobbies, fictional stock headshots, irrelevant bio filler).

3. **Card Sorting, Labeling & Tree Testing**
   - **Input:** Inventory of all domain objects, actions, and content routes (`20–60` cards).
   - **Output:** Validated L1/L2 taxonomy, controlled vocabulary glossary, and quantitative findability metrics.
   - **Owner:** Information Architect.
   - **Tool / Script:** Standard spreadsheet or tree-test runner; Jaccard similarity clustering for open sorts (`n >= 15` for `standard`/`full` tiers).
   - **Execution:** Run an open card sort to uncover user mental groupings (never mirror internal org charts or database table names into navigation labels).
     - Convert findings into plain, consistent labels (`Billing` not `Monetization Operations`; `Team Access` not `RBAC Entities`).
     - Compute pairwise co-occurrence (`Jaccard = |A ∩ B| / |A ∪ B|`) to collapse synonyms and prune weak categories (`< 0.35` agreement).
     - Validate via blind **Tree Testing** (`>= 80%` direct-success rate, `< 20%` backtrack rate) before drawing visual frames.
     - Measure first-click accuracy (`>= 85%` on primary navigation items) on low-fidelity wireframes.
     - Document any split-label ambiguity in a concise controlled-vocabulary glossary inside `design-brief.md`.

4. **Sitemap, Critical User Flows & Edge-State Mapping**
   - **Input:** Validated taxonomy and `prd.md` functional stories.
   - **Output:** Sitemap tree (`<= 7` L1 items) and end-to-end flow specs in `design-brief.md` Sections 4–5.
   - **Owner:** UX Architect / Frontend Lead.
   - **Tool / Script:** `python3 scripts/core_search.py "<landing or app>" --domain landing --json`.
   - **Execution:** Enforce a strict navigation budget (`<= 7` L1 destinations, `<= 3` clicks from landing/home to every primary task). For every critical flow, explicitly specify five states:
     - **Happy Path:** Shortest verifiable sequence from entry to committed outcome.
     - **Empty State:** Actionable first-run invitation with starter action or sample import.
     - **Error & Recovery State:** Field-level recovery preserving every entered character.
     - **Permission-Denied State:** Plain explanation of missing role/plan and exact escalation path.
     - **Offline / Degraded State:** Clear stale-data indicator and queued or retryable action.

5. **Heuristic Baseline & Think-Aloud Usability Verification**
   - **Input:** Clickable low-fidelity HTML/Figma prototype or existing staging build.
   - **Output:** Scored Nielsen 10-Heuristic audit (`0–4` severity) and task completion report.
   - **Owner:** QA / UX Evaluator.
   - **Tool / Script:** Moderated 5-user think-aloud protocol (`>= 85%` unassisted task completion, Single Ease Question `SEQ >= 5.5 / 7`).
   - **Execution:** Score every core screen against Nielsen's 10 heuristics:
     - System status visibility, real-world mental-model match, user control & undo freedom, internal consistency, error prevention before submission.
     - Recognition over recall, keyboard/power-user shortcuts, aesthetic restraint, plain-English error recovery, and contextual help.
     - Remediate every Severity `3` (major) and `4` (catastrophic) defect before entering visual token polishing.

6. **Complexity Budget & Deletion / Condensation Pass**
   - **Input:** Draft sitemap, flow matrix, and wizard steps.
   - **Output:** Pruned IA documented in `design-brief.md` Section 6 (`Simplicity Pruning Log`).
   - **Owner:** Design Lead & Engineering Lead.
   - **Execution:** Audit every route, tab, and wizard step:
     - Merge single-field or ceremonial confirmation screens into inline controls.
     - Delete orphan routes with `< 2%` task necessity and collapse duplicate entry points (e.g., identical settings in both top menu and sidebar).
     - Replace multi-page intro/overview wrappers with direct workspace or value-first entry.
     - Verify every remaining navigation item maps to a documented JTBD outcome in `design-brief.md`.

---

## 3. Reusable Artifact & Template

Instantiate [../templates/design-brief.md](../templates/design-brief.md) during Spiral Q1/Q2 (and prior to locking `design-master.md` in Phase 3A). Every field below is mandatory for `standard` and `full` tiers (`minimal` permits compact rows with explicit rationale):

| Field / Section | Type | Constraint / Validation Rule | Downstream Consumer |
|---|---|---|---|
| `site_kind` | Enum | One of `software \| gaming \| tech \| product \| service \| place` | `anti-ai-slop-and-ux-copy.md`, `design-master.md` |
| `rigor_tier` | Enum | `minimal \| standard \| full` matching project risk | Spiral Q2 Gate |
| `primary_conversion_action` | String | Verb + concrete outcome (`<= 6` words; zero `Submit`/`Learn more`) | Hero & CTA hierarchy |
| `jtbd_statement` | Structured | `When <situation>, I want to <action>, so I can <outcome>` | Copywriting & flow priority |
| `forces_of_progress` | 4-part Map | Push, Pull, Anxiety, Habit populated from user evidence | Objection handling & onboarding |
| `personas_matrix` | Table | Task frequency + viewport + assistive needs (zero demographic fluff) | Accessibility & responsive grid |
| `ia_sitemap_tree` | Hierarchy | `<= 7` L1 routes, `<= 3` clicks to core task, zero orphan pages | Navigation & router implementation |
| `critical_user_flows` | Matrix | Happy + Empty + Error + Permission + Offline states per core flow | `ui-design-craft` 13-state spec & QA E2E |
| `simplicity_pruning_log` | Log | Explicit list of deleted routes, merged steps, and native substitutions | Phase 3A Simplicity Gate |

---

## 4. Verification Checklist

- [ ] Site-Kind taxonomy (`software`, `gaming`, `tech`, `product`, `service`, or `place`) and Research Rigor Tier (`minimal`, `standard`, `full`) are recorded in `design-brief.md`.
- [ ] JTBD statement captures Functional, Emotional, and Social jobs alongside all four Forces of Progress (Push, Pull, Anxiety, Habit).
- [ ] Personas specify task frequency, device/network constraints, and assistive requirements without demographic filler.
- [ ] Top-level navigation obeys the `<= 7` L1 items budget (`<= 5` for Flat Hub) and reaches every primary task in `<= 3` clicks.
- [ ] Navigation labels reflect user mental models verified via card sorting / tree testing (`>= 80%` direct success on `standard`/`full` tiers) rather than internal org charts or database tables.
- [ ] Every critical user flow defines Happy, Empty, Error/Recovery, Permission-Denied, and Offline/Degraded states.
- [ ] Nielsen's 10 heuristics audit logs zero unresolved Severity `3` or `4` defects on core tasks.
- [ ] Simplicity Pruning Log documents deleted orphan routes, merged wizard steps, and native HTML/CSS choices before Phase 3A sign-off.
- [ ] Keyboard-only tab traversal (`Tab`, `Shift+Tab`, `Enter`, `Escape`) completes primary flows without mouse dependency or focus traps.
- [ ] Primary landing or workspace route establishes clear first-click hierarchy (`>= 85%` accuracy on `standard`/`full` tier tests).

### Nielsen 10-Heuristic Quick Reference & Severity Scale

| Severity | Meaning | Release Action |
|---|---|---|
| `0` | Not a usability issue | No action required |
| `1` | Cosmetic defect only | Fix only if adjacent code is already open |
| `2` | Minor friction with easy workaround | Schedule in regular polish queue |
| `3` | Major blocker delaying task completion | Fix before Phase 3C / Release Gate |
| `4` | Catastrophic failure or data-loss risk | Immediate block; resolve before continuing |

Key checks per screen:
- **Status Visibility:** Immediate visual confirmation within `<= 100ms` of every user click or submission.
- **Error Prevention:** Confirm destructive actions with typed or explicit intent rather than accidental single taps.
- **User Control & Freedom:** Every modal, drawer, and multi-step flow offers an unambiguous `Cancel`, `Back`, or `Undo` exit.
- **Recognition Over Recall:** Keep active filters, unit labels, and validation rules visible adjacent to inputs.

---

## 5. Hard Quality Gate

| Verdict | Criteria |
|---|---|
| **PASS** | `design-brief.md` exists with all required fields populated, L1 nav `<= 7` items, zero Severity `3–4` heuristic defects, `>= 80%` tree-test direct success (or documented `minimal`-tier rationale), all 5 edge states mapped per critical flow, and Simplicity Pruning Log complete. |
| **CONCERNS** | Minor Severity `1–2` label refinements pending or `minimal`-tier tree test deferred to first Usability Sprint with explicit owner and date. |
| **NOT ASSESSED** | Existing brownfield project where UX research was explicitly waived via signed Spiral Charter exception. |
| **FAIL** | Missing `design-brief.md`, L1 navigation `> 7` items without documented faceted search rationale, unresolved Severity `3–4` heuristic blockers, missing Empty/Error/Recovery flows, or Conway's-Law org-chart navigation. |

Executable gate check command:

```bash
python3 skills/ui-design-craft/scripts/core_search.py "navigation accessibility empty state" --domain ux --json
test -s design-brief.md && grep -E "^\|\s*\*\*Site-Kind Taxonomy\*\*" design-brief.md
```

Quantitative benchmark summary:
- Tree-test direct success: `>= 80%` across core L1/L2 tasks (`< 20%` backtrack rate).
- First-click accuracy: `>= 85%` on primary navigation landmarks.
- Unassisted moderated usability completion: `>= 85%` with `SEQ >= 5.5 / 7`.

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Conway's-Law Org-Chart IA** | Mirrors internal team or database schema instead of user goals; forces users to guess which department owns a feature | Nav items named after internal services, DB models, or org divisions | Group by user task and validated card-sort clusters (`>= 80%` tree-test success) |
| **Demographic Vanity Personas** | Fictional hobbies, ages, and stock photos do not inform edge states, keyboard flows, or error recovery | Persona cards with bio paragraphs but zero assistive or device constraints | Behavioral cohort matrix tied to task frequency, tech context, and a11y needs |
| **4-Level Mega-Menu Bloat** | Triggers Hick's Law paralysis, breaks mobile navigation, and hides core workflows under hover-dependent trees | `> 7` L1 items or `> 2` nested dropdown levels on desktop | Prune to `<= 7` L1 routes, surface `Cmd+K` or faceted search for deep catalogs |
| **Happy-Path-Only Flow Specs** | Leaves engineers guessing empty, offline, and error states, producing blank screens or raw stack traces in production | Flow diagrams lacking Empty, Error, Permission, and Offline branches | Specify all 5 flow states per critical workflow before Phase 3B implementation |
| **Survey-Instead-of-Observe Research** | Asking users *"Would you use feature X?"* collects polite speculation rather than real behavioral friction | Feature roadmap justified solely by Likert preference polls | Observe `5–8` real task attempts or run blind tree/first-click tests |
| **Ceremonial Multi-Step Wizard Overengineering** | Splits 3 simple inputs across 5 full-page steps with state stores and animated transitions when one single-page `<form>` works better | Multi-route wizard for `< 6` total inputs without conditional branching | Condense into a single semantic HTML `<form>` with native validation and clear fieldsets |
