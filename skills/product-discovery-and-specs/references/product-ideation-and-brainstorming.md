# Product Ideation, Brainstorming, and Wedge Validation

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

Strong engineering cannot rescue a weak or undifferentiated app/web concept. Random open-ended brainstorming collapses into either AI-wrapper clones ("chat over a PDF") or sprawling multi-persona platforms with no distribution wedge.

This module provides a structured, market-leading pre-PRD ideation engine combining the **Double Diamond**, **How Might We (HMW)** reframing, **Crazy 8s**, **SCAMPER**, **First-Principles Inversion**, **Value Proposition Canvas**, **Competitive White-Space Mapping**, and **48-Hour Riskiest Assumption Tests (RAT)**.

---

## 1. Decision Framework

### 1.1 Double Diamond Divergence & Convergence Posture

Every app or web product ideation sprint separates **divergent option generation** (quantity and non-obvious breadth without premature judgment) from **convergent pruning** (ruthless elimination using falsifiable user-value, distribution, and complexity criteria):

| Diamond Stage | Objective | Cognitive Mode | Mandatory Output | Rigor Floor (`minimal` / `standard` / `full`) |
|---|---|---|---|---|
| **Discover (Diverge)** | Expose unmet workflow friction, manual workarounds, and willingness-to-pay triggers | Exploratory | Constraint Box + `>= 3` HMW prompts | `2` / `4` / `6` real workaround signals |
| **Define (Converge)** | Lock the exact user pain, non-negotiable constraints, and value thesis | Analytical | `1` locked Value Proposition thesis | Single-sentence ICP + pain + outcome |
| **Develop (Diverge)** | Break first-thought anchoring via Crazy 8s, SCAMPER, and inversion | Generative | `>= 8` distinct concepts + Killed Log | `8` / `12` / `16` distinct product angles |
| **Deliver (Converge)** | Rank white-space fit, test riskiest assumptions, and isolate Option A wedge | Decisive | Weighted Matrix + `1` RAT + Wedge lock | `1` falsifiable 48h pre-build experiment |

### 1.2 Ideation Technique Selector

Choose the right generative lens based on where the product idea currently feels blocked:

| Ideation Method | When to Trigger | Execution Mechanics | Expected Yield |
|---|---|---|---|
| **How Might We (HMW)** | Problem feels too narrow or solution-biased ("build an AI app for X") | Reframe friction into open outcome questions (*"How might we cut X from 40 min to 30 sec with zero setup?"*) | `3–5` non-prescriptive problem frames |
| **Crazy 8s (Timeboxed Sprint)** | Team anchors on the first obvious competitor clone | Generate `8` distinct workflow/UX/wedge concepts (`1` concept per slot); slots `1–3` drain obvious ideas, slots `5–8` force radical angles | `>= 8` non-overlapping concepts |
| **SCAMPER (7 Lenses)** | Idea feels stale, crowded, or incremental | Apply **S**ubstitute, **C**ombine, **A**dapt, **M**agnify/Minimize, **P**ut to other use, **E**liminate, **R**everse to the core loop | `>= 7` concrete product mutations |
| **First-Principles & Inversion** | High technical or UX friction assumed "unavoidable" | Strip legacy industry steps down to physics/data essentials; invert (*"What makes users fail today? Guarantee its opposite"*) | Zero-step or inverted onboarding/pricing models |
| **Cross-Industry Analogy** | Domain UX conventions are stagnant | Borrow proven mechanics from unrelated verticals (e.g., multiplayer presence, Git diff reviews, airline check-in passes) | `2–3` structural UX differentiators |
| **Distribution-First Wedge** | Great tool idea with zero organic acquisition loop | Co-design one free utility, embeddable widget, SEO programmatic asset, or shareable artifact inside the core loop | Built-in loop costing `$0` paid ads |

### 1.3 Competitive White-Space & Value Proposition Framing

Map the top `3–5` incumbent workarounds (including spreadsheets, WhatsApp/email, and manual ops) across two decisive axes before committing:

- **Axis 1 (Buyer Constraint)**: Speed-to-value (`< 5 min` self-serve vs. multi-week setup) or price floor (`free`/`$19` vs. `$500+` enterprise).
- **Axis 2 (Capability Axis)**: Automated outcome vs. human-in-the-loop control, single-player utility vs. multiplayer workflow.
- **Value Proposition Lock**: Must satisfy without hand-waving:
  `Our [app/web product] helps [specific ICP] achieve [quantified outcome] in [time window] without [primary friction/workaround], unlike [top incumbent] because [defensible wedge].`

### 1.4 Ideation Radical Simplicity Gate ("Least Code, Highest Craft")

- **Anti-Platform Rule**: An ideation sprint MUST reject `"all-in-one super-app"` pitches. Every surviving concept must prove it works as a **1-job, 1-surface, 1-metric** product first.
- **Killed Ideas Requirement**: A brainstorm with zero rejected ideas signals zero convergent rigor. Explicitly archive `>= 5` rejected concepts in the **Killed Ideas Log** with concrete kill reasons.
- **Option A Wedge First**: Surface the narrowest buildable workflow that proves real user pull in `<= 2` weeks before designing multi-role dashboards or marketplace network effects.

---

## 2. Step-by-Step Workflow

1. **Lock the Constraint Box & HMW Prompts (Discover)**
   - **Input:** Raw founder/team spark, domain context, budget/timeline ceiling.
   - **Output:** Filled Section 1 (`Constraint Box` + `3–5` HMW prompts) in [../templates/ideation-workshop-brief.md](../templates/ideation-workshop-brief.md).
   - **Owner:** Product Lead / Founder.
   - **Execution:** Fix hard boundaries upfront (target platform: web/mobile/hybrid, build horizon `<= 14d` for V1, ICP budget ceiling, zero-paid-ads or regulatory constraints) and convert raw feature wishes into `3–5` outcome-oriented HMW questions.

2. **Run Divergent Generation Sprint — Crazy 8s + SCAMPER (Develop)**
   - **Input:** HMW prompts, observed workaround inventory.
   - **Output:** `>= 8` numbered, mutually distinct concept rows (`IDEA-01..IDEA-NN`).
   - **Owner:** Cross-functional trio (Product, Design, Engineering).
   - **Execution:** Generate `8` distinct concepts covering at least `3` different mechanism families (workflow elimination, data-native automation, embedded distribution utility, inverted pricing/flow). Then apply all `7` **SCAMPER** lenses to the strongest `2` seeds—explicitly targeting **Eliminate** (steps removed) and **Reverse** (zero-config value before signup).

3. **Run Competitive White-Space & Anti-Me-Too Filter**
   - **Input:** `>= 8` candidate concepts + `3–5` real alternatives users use today.
   - **Output:** `2x2` White-Space Position Table + initial kills in `Killed Ideas Log`.
   - **Owner:** Product Strategist.
   - **Execution:** Compare each concept against the incumbent workflow (including `"do nothing / Excel"`). Immediately kill thin AI wrappers that merely forward a prompt to a third-party LLM with zero proprietary workflow state, verification loop, or distribution moat.

4. **Convergent Scoring & Complexity Budget / Deletion Pass**
   - **Input:** Surviving candidates (`>= 4`).
   - **Output:** Weighted Scoring Matrix (`Pain Severity`, `Speed to First Value`, `Distribution Wedge`, `Build Simplicity`) + `>= 5` entries in `Killed Ideas Log`.
   - **Owner:** Product Lead + Engineering Lead.
   - **Execution:** Score each candidate `1–5` on `Score = (Severity × 2) + SpeedToValue + DistributionWedge + BuildSimplicity` (max `25`). Enforce the **Complexity Budget** via a mandatory **Deletion / Condensation Pass** on the top winner: strip secondary roles, admin settings, and AI bells until only the **Option A Wedge** remains.

5. **Lock Value Proposition Canvas & Map Riskiest Assumptions**
   - **Input:** Top-scoring Option A Wedge.
   - **Output:** Filled Value Proposition Canvas + ranked Top-3 Assumptions (`Desirability`, `Feasibility`, `Viability`).
   - **Owner:** Product Lead.
   - **Execution:** Map ICP jobs, top `3` pains, and exact pain relievers. Rank every hidden assumption by `(Impact if Wrong × Uncertainty)` to isolate the single **Riskiest Assumption** (`RA-01`).

6. **Execute 48-Hour Riskiest Assumption Test (RAT) & Hand Off to JTBD Discovery**
   - **Input:** `RA-01` hypothesis and falsifiable pass/fail threshold.
   - **Output:** Logged RAT result (`GO` / `PIVOT` / `KILL`) + locked seed for [product-discovery-and-jtbd.md](product-discovery-and-jtbd.md).
   - **Owner:** Product & Design Leads.
   - **Execution:** Validate `RA-01` before writing production code using the cheapest truthful test (concierge manual run, clickable Figma/HTML smoke prototype, or 5 customer commitment calls). Only `GO` wedges advance into `prd.md` and Spiral Q1 discovery.

---

## 3. Reusable Artifact & Template

Record every ideation sprint in `docs/product/ideation-brief.md` using [../templates/ideation-workshop-brief.md](../templates/ideation-workshop-brief.md).

| Section | Mandatory Content | Verification Rule |
|---|---|---|
| `1. Constraint Box & HMW` | Target ICP, hard timeline/platform bounds, `>= 3` HMW prompts | Zero solution names embedded in HMW prompts |
| `2. Divergent Concept Log` | `>= 8` distinct ideas (Crazy 8s + SCAMPER tags) | Concepts span `>= 3` mechanism families |
| `3. White-Space & Scoring Matrix` | Incumbent comparison + weighted `1–5` scoring (`max 25`) | Clear numeric winner + Simplicity Ablation notes |
| `4. Killed Ideas Log` | `>= 5` explicitly rejected concepts with concrete kill rationale | Proves convergent pruning occurred |
| `5. Value Proposition & RAT` | Completed VPC thesis + `RA-01` 48h test + `GO/PIVOT/KILL` | Numeric pass/fail metric defined before build |

---

## 4. Verification Checklist

- [ ] Constraint Box fixes target platform, build horizon, and distribution/budget limits before ideation begins.
- [ ] At least `3` How Might We (HMW) prompts frame measurable user outcomes rather than pre-baked UI features.
- [ ] Divergent Log contains `>= 8` genuinely distinct concepts with SCAMPER **Eliminate** and **Reverse** variations explored.
- [ ] Incumbent comparison explicitly benchmarks against real non-software workarounds (spreadsheets, chat, manual steps).
- [ ] At least `5` ideas appear in the `Killed Ideas Log` with concrete market, distribution, or complexity kill reasons.
- [ ] Selected winner completes the full Value Proposition thesis sentence without buzzwords or vague claims.
- [ ] Simplicity Ablation strips secondary personas, premature admin panels, and decorative AI features into an Option A Wedge.
- [ ] Top Riskiest Assumption (`RA-01`) carries a falsifiable numeric pass threshold and `<= 48h` validation plan.

---

## 5. Hard Quality Gate

Ideation closes and hands off to `product-discovery-and-jtbd.md` **ONLY** when `docs/product/ideation-brief.md` evaluates to `PASS` (`FAIL > CONCERNS > NOT ASSESSED > PASS`):

- **PASS**: `docs/product/ideation-brief.md` contains `>= 3` HMW prompts, `>= 8` distinct concepts in the Divergent Log, a scored matrix (`max 25`), `>= 5` logged kills in `Killed Ideas Log`, a complete Value Proposition thesis, and a quantified `RA-01` validation test (`GO` or scheduled `<= 48h` check) with zero stub markers (`TODO`/`TBD`/`FIXME`).
- **CONCERNS**: `8+` ideas and `5+` kills logged, but RAT relies on indirect proxy metrics pending direct user test.
- **NOT ASSESSED**: Ideation sprint skipped (brownfield maintenance bugfix) or RAT evidence field blank.
- **FAIL**: `< 8` concepts generated, zero killed ideas, unvalidated AI-wrapper clone with no white-space edge, missing Value Proposition thesis, or `"build everything"` platform scope without Option A Wedge ablation.

```bash
python3 - <<'PY'
from pathlib import Path
import re, sys

brief = Path("docs/product/ideation-brief.md")
if not brief.is_file():
    print("FAIL: missing docs/product/ideation-brief.md"); sys.exit(1)
text = brief.read_text(encoding="utf-8")
for pat in (r"\bTODO\b", r"\bTBD\b", r"\bFIXME\b", r"\[placeholder\]", r"\bLorem ipsum\b"):
    if re.search(pat, text):
        print(f"FAIL: unresolved stub marker {pat!r}"); sys.exit(1)
ideas = re.findall(r"\bIDEA-\d{2,3}\b", text)
kills = re.findall(r"\bKILL-\d{2,3}\b", text)
hmws = re.findall(r"\bHMW-\d{2,3}\b", text)
if len(set(hmws)) < 3 or len(set(ideas)) < 8 or len(set(kills)) < 5 or "RA-01" not in text:
    print(f"FAIL: ideation thresholds unmet (hmws={len(set(hmws))}/3, ideas={len(set(ideas))}/8, kills={len(set(kills))}/5)")
    sys.exit(1)
print("PASS: Product Ideation & Brainstorming gate satisfied.")
PY
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **First-Idea Anchoring** | Locks onto the initial brainstorm spark (usually identical to every competitor) | Only `1–3` ideas explored before jumping to wireframes or schema | Force `>= 8` Crazy 8s + SCAMPER concepts; exhaust obvious ideas in slots `1–3` |
| **Solution-Led HMW Framing** | Pre-judges UI or model choice inside problem statements and blocks divergent leaps | Prompts read `"How might we build an AI chatbot..."` | Frame pure outcome & constraint gaps (`"cut step X from 30m to 30s"`) |
| **Thin AI-Wrapper Cloning** | Zero defensibility; incumbents or base LLM UIs absorb the product overnight | Pitch equals *"ChatGPT for X"* with no proprietary workflow state or loop | Design closed-loop deterministic state, verification, or proprietary data flywheels |
| **Zero-Kill Brainstorming** | Treats every cool suggestion as MVP scope, producing bloated V1 builds | Empty `Killed Ideas Log`; every concept merged into one giant feature list | Kill `>= 5` concepts explicitly and isolate `1` Option A Wedge |
| **Ignoring Distribution Mechanics** | Builds a polished product in isolation with no built-in channel to reach ICPs | Ideation brief omits how the first `100` users discover the wedge without paid ads | Co-design an embedded utility, shareable artifact, or SEO wedge inside SCAMPER |
| **Premature Code Before RAT** | Spends weeks building architecture for an unvalidated switching assumption | Coding starts with zero `RA-01` experiment or customer commitment check | Run a `48h` concierge, clickable smoke test, or pre-order check first |
| **Opinion-as-Validation** | Confuses team excitement or generic AI praise for real customer willingness to switch | Zero falsifiable `RA-01` metric; `"people will love this"` rationale | Define a binary `48h` RAT threshold (`GO/PIVOT/KILL`) before locking `prd.md` |
