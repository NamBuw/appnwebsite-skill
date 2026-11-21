# Product Discovery, Frontier Grilling, and Jobs-to-be-Done (JTBD)

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

Product failures rarely begin with broken syntax. They begin when a team builds an
elaborate solution for an unverified problem, mistakes a noisy feature wishlist for
genuine demand, or interrogates stakeholders in unfocused, sprawling loops.

This module establishes a disciplined, token-efficient Spiral Q1 discovery workflow
uniting narrowest-wedge framing, frontier decision-tree grilling, Jobs-to-be-Done
(JTBD), Opportunity Solution Trees (OST), and Radical Simplicity
(`"Least Code, Highest Craft"`) before any architecture or UI work begins.

---

## 1. Decision Framework

### 1.1 Discovery Mode Calibration by Rigor Tier

Select the lightest discovery posture that resolves uncertainty without inventing
premature bureaucracy. Scale inquiry depth strictly to risk, irreversibility, and
evidence gaps:

| Rigor Tier | Discovery Mode | Trigger Signals | Interview Cap | Mandatory Outputs | Exit Bar |
|---|---|---|---|---|---|
| `minimal` | **Narrowest-Wedge Fast Track** | Single-surface MVP, landing page, or `<= 1`-week build | `1` focused round (`<= 5` frontier questions) | Pitch, `1` persona, `1` JTBD, **Option A** wedge, `>= 3` Non-Goals, binary goal | Pain + metric + Option A locked |
| `standard` | **Structured JTBD + Frontier Grill** | Multi-feature SaaS, web/mobile app, or brownfield pivot | `2–3` rounds (`<= 7` questions/round) | Observed vs. inferred log, `<= 2` personas, `<= 3` JTBDs, ranked OST, 3 approaches | Frontier empty; top pain evidenced |
| `full` | **Evidence-Backed OST Matrix** | Auth/PII/Payments, multi-tenant platform, or `>= 2` teams | `3–5` bounded rounds + telemetry scan | Triangulated evidence, segment contrast, risk-adjusted OST, binary validator | Zero unvalidated `High`-risk gaps |

**Mandatory Security Elevation**: Any slice touching authentication, personally
identifiable information (PII), or financial transactions automatically elevates
from `minimal` to `standard` (or `full` for multi-tenant compliance).

### 1.2 Six-Question Forcing Matrix (Pre-Spec Framing)

Before drafting requirements, test product intent with six forcing questions:

1. **Concrete Pain Example**: Capture the exact last incident — tool opened, failure
   point, and workaround cost in minutes or revenue. Reject `"users might want"`
   guesses.
2. **Workaround Cost & Urgency**: Quantify `90`-day inaction damage; low urgency
   signals a vitamin rather than a viable wedge.
3. **Core Capability vs. Surface**: Separate durable job utility from transient UI
   chrome.
4. **Premise Challenge (`<= 4`)**: Test hidden assumptions (mandatory signup before
   value, real-time sync where 5-minute batch suffices).
5. **Three Approaches — Option A First**: Compare three distinct framings (manual
   bridge, thin workflow wedge, full platform), surfacing **Option A (Narrowest
   Wedge)** first.
6. **Binary Goal Validator**: Lock one falsifiable target
   (`metric + threshold + check`) and reject activity slogans
   (`"improve onboarding"`).

### 1.3 Frontier Decision-Tree Grilling Rules

Model open product decisions as a dependency tree and interview strictly along the
**unblocked frontier**:

```text
Root Decision: Who is the primary active/paying actor?
├── Settled -> Frontier moves to: What is the single core workflow (JTBD-01)?
│   ├── Settled -> Frontier moves to: Which edge inputs belong in Spiral 1 vs Non-Goals?
│   └── Open -> Defer export formats, notifications, and billing tier questions.
└── Open -> Ask ONLY the root question plus a recommended Option A default.
```

- **Frontier Rule**: Never ask downstream questions invalidated by an open
  prerequisite.
- **Tool-First Fact Resolution**: Inspect existing repositories via read-only search
  before asking about frameworks, schemas, or routes.
- **Confirmable Defaults**: Pair each frontier question with a recommended **Option
  A** default so `"yes"` locks the simpler choice.
- **Single-Question Minimal Override**: When one metric or bound is missing on
  `minimal` tier, ask `1` targeted question and proceed.

### 1.4 Opportunity Ranking & Radical Simplicity Wedge Gate

Separate **observed evidence** from **inferred hypotheses** before ranking problems:

- **Observed Evidence**: Direct user quotes, telemetry counts, support tickets, or
  codebase friction.
- **Inferred Hypotheses**: Designer intuition, single anecdotes, or unvalidated
  guesses.
- **Scoring Formula**:
  `Opportunity Score = Severity (1–5) × Frequency (1–5) × Leverage (1–3)`, tagged
  with `Confidence (High | Medium | Low)`.
- **Problem Triage**: Distinguish usability friction from missing capabilities and
  reliability/latency bugs.
- **Simplicity Q1 (Wedge Ablation)**: Identify the capability delivering `>= 80%` of
  core value inside `<= 20%` of requested scope.
- **Simplicity Q2 (Surface Discipline)**: Limit primary surface framing to **1 hero
  use case, 1 primary action, and `<= 2` supporting areas**.
- **Simplicity Q3 (Evidence Filter)**: Defer `Low`-confidence or `Frequency = 1`
  items to `Fix Next Quarter` or `Non-Goals`.
- **Simplicity Q4 (Token Economy)**: Record discovery answers once in `prd.md`
  Section 1; reference `OPP-NN` and `JTBD-NN` IDs downstream instead of duplicating
  prose.

---

## 2. Step-by-Step Workflow

1. **Restate Scope & Inspect Repo Reality**
   - *Inputs*: Raw prompt, workspace files.
   - *Output*: Greenfield/brownfield baseline note.
   - *Owner*: Product Lead | *Tool*: Directory & text search.
   - Restate the product boundary, target audience, and Spiral time horizon in three
     crisp lines.
   - Scan workspace files (`< 3` source files = greenfield; `>= 3` = brownfield) to
     extract existing routes, schemas, and copy silently.
   - Never ask stakeholders for framework, database, or route facts already visible
     in the repository.

2. **Conduct Frontier Design-Tree Grilling in Bounded Rounds**
   - *Inputs*: Baseline note, `spiral-charter.md`.
   - *Output*: Settled decision tree.
   - *Owner*: Product Lead | *Tool*: Frontier round prompt.
   - Map open choices as a dependency tree and ask at most `5–7` frontier questions
     per round (`<= 1` validator question on `minimal` tier).
   - Provide an **Option A** recommendation on every question so a single
     confirmation locks the simplest path.
   - Stop grilling immediately once the frontier is empty and zero `P0` scope
     ambiguities remain.

3. **Synthesize Behavioral Personas, JTBD & Ranked OST**
   - *Inputs*: Settled answers, telemetry/support notes.
   - *Output*: Sections `1.1–1.4` of `docs/product/prd.md`.
   - *Owner*: Product Strategist | *Tool*: [prd-spec.md](../templates/prd-spec.md).
   - Limit behavioral personas to `<= 2` operational archetypes defined by triggers,
     constraints, and failure costs.
   - Write `<= 3` JTBD statements:
     `When [situation], I want to [motivation], so I can [expected measurable outcome].`
   - Group scored opportunities into three horizons: `Fix This Week` (Spiral 1
     Wedge), `Fix Next Quarter` (`SP-<N+1>`), and `Needs Deeper Research`.

4. **Run Simplicity & Scope-Condensation Pass**
   - *Inputs*: Draft OST and candidate approaches.
   - *Output*: Option A Wedge + `>= 3` Non-Goals + binary validator.
   - *Owner*: Product Lead + Architect | *Tool*: Wedge ablation check.
   - Present **Option A (Simplest High-Craft Narrowest Wedge)** first, backed by
     effort estimate and capability summary.
   - Execute the **Scope-Cut & Condensation Pass**: move at least `3` speculative
     capabilities (admin portals, custom themes, secondary dashboards) into
     `Non-Goals`.
   - Lock one binary success validator (`metric + threshold + verification command`)
     and flush finalized sections directly to `docs/product/prd.md` incrementally.
   - Keep context compact by emitting at most a `<= 25`-line checkpoint summary at
     Spiral Q1 exit.

5. **Deliver a Single-Use Reflection Nudge (When Warranted)**
   - *Inputs*: Finalized Discovery Brief.
   - *Output*: `2–3` concise follow-up prompts.
   - *Owner*: Product Lead | *Tool*: Inline brief note.
   - Before major build spend on an unverified brief, surface `2–3` brief prompts
     (`<= 120` chars each) probing:
     - one unverified market or baseline claim;
     - one core causal assumption linking the wedge to the target metric;
     - one missing operational constraint (budget, compliance, or distribution
       channel).
   - Emit this prompt **at most once** per session; skip when the user requested
     speed, supplied verified telemetry, or asked for a formal review.

### Worked Example: Turning a Bloated Pitch into an Option A Wedge

- **Raw Pitch**: *"Build an AI accounting platform with multi-currency ledgers,
  custom role builders, Slack bots, and PDF/CSV OCR."*
- **Observed Evidence**: Operations manager spends `45 min/week` manually matching
  `80` USD CSV bank lines against Stripe exports.
- **Option A (Narrowest Wedge)**: Single-currency USD CSV import matching Stripe
  payouts with deterministic row diffing (`3` days, `0` new external queues).
- **Cut to `Non-Goals`**: Multi-currency FX, custom role builder, Slack bot, and
  scanned PDF OCR (`SP-02`+).

---

## 3. Reusable Artifact & Template

Discovery outputs write directly into Section 1 of
[prd-spec.md](../templates/prd-spec.md) (`docs/product/prd.md`), eliminating
disconnected pitch documents. Apply these authoring rules when populating each
field:
- Flush finalized subsections directly to `docs/product/prd.md` incrementally
  instead of drafting twice in chat.
- Cross-reference `JTBD-NN` and `OPP-NN` IDs in downstream sections rather than
  copying narrative prose.
- Tag every factual claim explicitly as `Observed` or `Inferred` so Q2 risk review
  spots unverified hypotheses immediately.

| Field Name | Cardinality | Mandatory Content & Constraint |
|---|---|---|
| `Problem Statement` | `1` sentence | Actor, measurable friction, trigger workflow, and concrete time/cost impact |
| `Observed vs. Inferred Log` | `>= 2` bullets | Explicitly separates verified repo/user/telemetry facts from hypotheses |
| `Target Persona(s)` | `1–2` rows | Behavioral archetype, operational constraint, measurable outcome (no demographics) |
| `JTBD Statements` | `1–3` items | `When [situation], I want to [motivation], so I can [expected outcome]` |
| `Ranked OST Table` | `>= 2` rows | `Opportunity ID`, `Pain`, `Evidence Type`, `Severity`, `Frequency`, `Confidence`, `Leverage`, `Horizon` |
| `Candidate Approaches` | `3` options | `Option A (Narrowest Wedge)` first with effort estimate; Option B requires cited evidence |
| `Binary Success Validator` | `1` metric | Numeric target threshold + window + exact verification command or query |
| `Non-Goals Seed` | `>= 3` items | Excluded capabilities deferred out of Spiral 1 with Simplicity/YAGNI rationale |

---

## 4. Verification Checklist

- [ ] Read-only codebase inspection completed before interviewing so zero questions asked for inspectable repo facts.
- [ ] Every pain statement separates observed evidence from inferred hypotheses without relying on hypothetical future scenarios.
- [ ] Behavioral personas are capped at `<= 2` archetypes and omit irrelevant demographic details.
- [ ] Frontier grilling left zero unsettled prerequisite branches and avoided asking blocked downstream questions.
- [ ] Opportunity Solution Tree scores severity, frequency, confidence, and leverage across `Fix This Week`, `Fix Next Quarter`, and `Needs Deeper Research`.
- [ ] Option A (Simplest High-Craft Narrowest Wedge) was surfaced first with `>= 3` concrete capabilities cut to Non-Goals.
- [ ] Success validator names a falsifiable numeric target and verification method instead of an activity-only slogan.

---

## 5. Hard Quality Gate

Discovery exits Spiral Q1 **ONLY** when binary conditions evaluate to `PASS`
(`FAIL > CONCERNS > NOT ASSESSED > PASS`):

- **PASS**: `docs/product/prd.md` Section 1 exists on disk with zero stub markers
  (`TODO`, `TBD`, `FIXME`, `[placeholder]` equivalents):
  - defines `<= 2` behavioral personas and `<= 3` JTBD statements;
  - separates observed evidence from inferred hypotheses;
  - places `Option A` Narrowest Wedge first and seeds `>= 3` Non-Goals;
  - includes a numeric target threshold and verification method.
- **CONCERNS**: Minor wording refinement needed on `Fix Next Quarter` items while
  `Option A` Wedge, `P0` evidence, and numeric target remain unambiguous.
- **NOT ASSESSED**: Any required Section 1 table remains empty or omits explicit
  evidence vs. inference tagging.
- **FAIL**: Zero concrete pain evidence cited, `> 2` personas or bloated
  feature-inventory framing, missing `Option A` Wedge, missing numeric validator, or
  unresolved frontier prerequisites.

```bash
python3 - <<'PY'
from pathlib import Path
import re, sys

prd = Path("docs/product/prd.md")
if not prd.is_file():
    print("FAIL: missing docs/product/prd.md"); sys.exit(1)
text = prd.read_text(encoding="utf-8")
for pat in (r"\bTODO\b", r"\bTBD\b", r"\bFIXME\b", r"\[placeholder\]", r"\bLorem ipsum\b"):
    if re.search(pat, text):
        print(f"FAIL: unresolved stub marker {pat!r}"); sys.exit(1)
required = ("## 1. Discovery Brief", "Option A", "JTBD", "Non-Goals")
missing = [r for r in required if r not in text]
val_block = re.search(
    r"(?ims)^#{2,4}\s+[^\n]*Binary[^\n]*Success Validator[^\n]*\n(.*?)(?=^\s*#{1,4}\s|^\s*---\s*$|\Z)",
    text,
) or re.search(
    r"(?ims)^\s*(?:-\s*)?\*\*[^*\n]*Binary[^*\n]*Success Validator[^*\n]*\*\*\s*:(.*?)(?=^\s*(?:-\s*\*\*|#{1,4}\s|---\s*$)|\Z)",
    text,
)
val_text = val_block.group(1) if val_block else ""
has_metric = bool(
    re.search(r"(?:\$\d[\d,.]*|\d+(?:\.\d+)?\s*(?:%|ms|s|min|hours?|days?))", val_text)
)
if missing or not has_metric:
    print(f"FAIL: missing discovery sections {missing} or numeric Binary Success Validator"); sys.exit(1)
print("PASS: Discovery Brief & Narrowest Wedge gate satisfied.")
PY
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Hypothetical Pain Invention** | Builds elaborate software for imaginary needs nobody actively struggles with today | Pitch says `"users might want"` with zero cited incidents | Demand a real, dated workaround example (`Observed`) or cut from Spiral 1 |
| **Feature-Inventory Framing** | Dilutes engineering focus and clutters primary screens with competing widgets | Discovery brief lists 6+ equal-priority widgets with no hero flow | Enforce `1` hero use case, `1` primary action, and `<= 2` supporting areas |
| **Premature Multi-Round Grilling** | Burns tokens and fatigues users by asking questions invalidated by earlier choices | Questionnaire asks about exports and billing before core actor settles | Map a dependency tree and ask strictly `<= 5–7` **frontier** questions |
| **Demographic Persona Fluff** | Fictional bios, ages, and hobbies contribute zero architectural or UX constraints | Persona section describes lifestyle traits instead of workflow bottlenecks | Cap at `<= 2` behavioral archetypes detailing triggers and failure costs |
| **Over-Scoped Wedge (No Non-Goals)** | Expands Spiral 1 into a bloated monolith before validating core value | Zero items in `Fix Next Quarter` or `Non-Goals`; everything marked `P0` | Apply Wedge Ablation (`>= 80%` value in `<= 20%` scope) and cut `>= 3` items |
| **Loud-Anecdote Extrapolation** | One vocal request overrides frequent friction experienced by core users | Single comment triggers major scope expansion without frequency metrics | Score `Severity × Frequency × Leverage` and tag evidence confidence |
