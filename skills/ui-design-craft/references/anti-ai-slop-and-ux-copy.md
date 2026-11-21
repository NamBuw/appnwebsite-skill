# Anti-AI-Slop Craft, UX Copywriting & Design Critique

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

---

## 1. Decision Framework

Generic AI-generated interfaces fail immediately because they converge on identical clichés—default fonts, generic icon packs, gratuitous purple-blue gradients, inflated marketing copy, and missing failure states. This module enforces non-negotiable visual and verbal baselines balanced with **Site-Kind** visual vernacular and a governed **Brownfield ADR Override** path.

### Strict Default Visual Policy (Banned vs. Preferred)

| Surface / Asset | Strictly Banned by Default | Approved Standard | Governed Exception Rule |
|---|---|---|---|
| **Fonts** | `Inter`, `Roboto`, `Arial`, `Open Sans`, `Helvetica` | `Geist`, `Plus Jakarta Sans`, `Manrope`, `Instrument Sans`, `IBM Plex Sans`, `Newsreader`, `Geist Mono` | Dated brownfield ADR + `--allow-font <name>` |
| **Icons** | `Lucide`, `Feather`, `Heroicons`, `Material Icons`, `Material Symbols` | `Phosphor` (`@phosphor-icons/react`), `Solar`, `Iconamoon` (`@iconify/react`) | Dated brownfield ADR + `--allow-icon <pkg>` |
| **Surfaces & Gradients** | Background gradients (`linear-gradient`/`radial-gradient` cards, AI purple/blue washes), 1-sided `.card` borders, `#0a0a0a` / `#121212` cliché darks | Flat intentional surfaces (`#09090B` / `#18181B` dark; `#FAFAFA` / `#FFFFFF` light); hero text-only directional gradient (`#FFFFFF -> #9B9B9B` or `#000000 -> #666666`) with `background-clip: text` | Explicit brand visual ADR in `design-master.md` |
| **Stacking & Weights** | `z-index: 9999` (`>= 999`), `font-weight: 900`, italic UI labels, sun/moon theme toggles on fixed single-mode marketing pages | Semantic `--z-base..--z-tooltip` (`0..70`), weights `400–700`, native `<dialog>`/`popover` | `800` display only in `Kinetic`/`Bauhaus` site-kind |

### Site-Kind Taxonomy & AI-Convergence Trap Filter

Select the visual vernacular matching the product's real **Site-Kind** (`software`, `gaming`, `tech`, `product`, `service`, `place`) while actively avoiding the **5 AI-Convergence Traps**:
1. Warm cream canvas paired exclusively with `#D97757` terracotta accents.
2. Near-black backgrounds paired with acid-green or vermilion highlights without domain rationale.
3. Broadsheet 1px hairline grids applied indiscriminately to casual consumer tools.
4. Cookie-cutter 3-equal-card SaaS pricing/feature grids topped with pill badges and generic gradient blobs.
5. Tracked `ALL-CAPS` eyebrow labels paired with `·` mid-dot metadata, `—` em-dashes, and `→` link arrows everywhere.

### 3-Tier Anti-Slop Severity Model

- **FLOOR (Hard Blockers):** Contrast `< 4.5:1` / `< 3.0:1`, horizontal overflow at `390px`, missing `prefers-reduced-motion`, placeholder copy (`Lorem ipsum`, `coming soon`, `Your headline here`), AI hype buzzwords, dropped links/handlers during redesign (`SLOP-STRUCT-01`).
- **REFLEX (Default Craft Violations):** Banned fonts (`Inter`, `Roboto`, `Arial`, `Open Sans`, `Helvetica`), banned icon libraries (`Lucide`, `Feather`, `Heroicons`, `Material Icons`, `Material Symbols`), background gradients lacking `background-clip: text`, `z-index >= 999`.
- **FINISH (Editorial Polish):** Single-sided card borders, generic `ease`/`linear` transitions instead of `cubic-bezier(0.22, 1, 0.36, 1)`, raw `scroll` listeners, unaligned microcopy verbs, off-scale spacing.

### Token Economy & Simplest High-Craft Option (Anti-Overengineering Check)

- **Token Economy Rule:** Query `python3 skills/ui-design-craft/scripts/design_search.py "<product>" --domain icons --json` and run `check_anti_slop.py` deterministically instead of burning LLM context manually inspecting files line by line.
- **Simplest High-Craft Option:** Spend visual boldness in **one** deliberate focal point (for example, crisp hero display scale, real interactive product telemetry, or bespoke hardware photography). Delete decorative pill badges, icons inside every subheading, ambient gradient blobs, and 4-column footer link farms before adding any secondary ornament.

### Before / After UX Copy & Visual Remediation Examples

```text
SLOPPY HERO COPY : "Unlock Next-Gen Synergy — Effortlessly revolutionize your workflow today!"
HIGH-CRAFT COPY  : "Measure every production query. Deterministic SQL telemetry with sub-50ms rollup."

SLOPPY CTA/TOAST : Button "Submit" -> Toast "Success! Action completed!"
HIGH-CRAFT CTA   : Button "Publish release" -> Toast "Release v2.4.1 published."

SLOPPY ERROR     : "Oops! Something went wrong! Please try again later!"
HIGH-CRAFT ERROR : "Upload failed. The archive exceeds the 20 MB limit. Split files or compress below 20 MB."

SLOPPY HERO TEXT : background: linear-gradient(135deg, #6366f1, #a855f7); /* full card gradient */
HIGH-CRAFT HERO  : color: transparent; background: linear-gradient(180deg, #FFFFFF 0%, #9B9B9B 100%);
                   -webkit-background-clip: text; background-clip: text;
```

### B11 Word-by-Word Tagline & Icon Migration Reference

- **Word-by-Word Reveal (`B11`):** Stagger words cleanly at `50ms` per word (`cubic-bezier(0.22, 1, 0.36, 1)`) inside an `IntersectionObserver` once-only trigger, collapsing immediately to `opacity: 1` under `@media (prefers-reduced-motion: reduce)`.
- **Icon Replacement Map:**
  - Replace `@heroicons/react`, `lucide-react`, `react-feather`, and `material-icons` imports with `@phosphor-icons/react` (`import { ArrowRight, CheckCircle, WarningCircle } from "@phosphor-icons/react"`) or `@iconify/react` (`solar:*`, `iconamoon:*`).
  - Always set `aria-hidden="true"` on icons paired with visible text labels, and provide explicit `aria-label` on icon-only controls.

---

## 2. Step-by-Step Workflow

1. **Classify Site-Kind & Lock Icon / Font Standard**
   - **Input:** `design-brief.md` (`site_kind`), product domain.
   - **Output:** Locked font/icon baseline and `<= 5` waiver ledger in `design-master.md`.
   - **Owner:** Design Lead.
   - **Tool / Script:** `python3 scripts/core_search.py "<category>" --domain icons --json`.
   - **Execution:** Choose `1` primary icon family (`Phosphor` via `@phosphor-icons/react`, `Solar`, or `Iconamoon`) and keep stroke weight and corner geometry uniform across all icons (`size={18}`–`20`, `aria-hidden="true"` when paired with visible label, explicit `aria-label` on icon-only buttons). Never mix `Lucide`, `Feather`, `Heroicons`, `Material Icons`, or `Material Symbols` with `Phosphor` unless a brownfield ADR documents the migration boundary.

2. **De-Slop UI & Marketing Copy (26-Pattern Humanizer Pass)**
   - **Input:** Draft headlines, CTAs, empty states, error alerts, and demo datasets.
   - **Output:** Calm, concrete, sentence-case UX copy across all 5 surfaces.
   - **Owner:** UX Writer / Product Designer.
   - **Tool / Script:** `python3 scripts/check_anti_slop.py src/ --json`.
   - **Execution:** Apply targeted pattern elimination across all 5 UX copy surfaces:
     - **Marketing & Hero Copy:** Strip inflated AI stock words (`revolutionize`, `supercharge`, `cutting-edge`, `effortless`, `synergy`, `next-gen`, `world-class`, `harness the power`, `transform your workflow`). Eliminate *"Not X, but Y"* antithesis staging, forced rule-of-three adjective triads, em-dash (`—`) pause padding, and shallow `-ing` participial fluff (*"empowering teams to..."*). Lead with concrete numbers or observable product mechanics (*"Deterministic SQL telemetry with sub-50ms rollup latency"*).
     - **CTAs & Navigation Labels:** Use **Verb + Concrete Outcome** (`Inspect Architecture`, `Create workspace`, `Export tokens`) in sentence case. Enforce **exact button-to-toast verb consistency** (`Publish` button triggers `"Project published"`, `Archive` triggers `"Record archived"`). Ban generic `Submit`, `Click here`, and `Learn more`.
     - **Empty States:** State what belongs here and offer the exact single primary action (`"No webhooks configured. Add an endpoint to start receiving events."`). Never render blank voids or anthropomorphic chatbot greetings.
     - **Error & Confirmation Messages:** Use calm, active voice stating what failed and the immediate corrective step (`"Upload failed. The file exceeds the 20 MB limit."` / `"Invoice sent to Dana."`). Zero exclamation marks, zero *"Oops!"* or *"Sorry!"* apologies, and zero `window.alert()`.
     - **Realistic Demo Data:** Populate prototypes with non-round numbers (`$47/mo`, `99.94%`, `14.2ms`), realistic dates, and domain-authentic names. Use explicit template tokens like `{{price}}` for unverified commercial facts—never `Lorem ipsum`, `TBD`, or `coming soon` placeholders.

3. **Run the `impeccable` Design Critique Pass**
   - **Input:** Rendered prototype or staging screenshots (`390px` mobile + `1440px` desktop).
   - **Output:** Prioritized critique notes resolved before release.
   - **Owner:** Peer Designer / QA Reviewer.
   - **Execution:** Evaluate screens across 7 concrete studio lenses rather than vague taste adjectives:
     1. *Visual Rhythm* — deliberate focal point and alternating dense/breathing bands.
     2. *Optical Weight* — balanced icon-to-text sizing (`16–20px` icon alongside `14–16px` text).
     3. *Figure-Ground Separation* — crisp surface contrast without murky gray-on-gray cards.
     4. *Typographic Hierarchy* — unmistakable H1 -> H2 -> Body -> Caption step ratio.
     5. *Density Balance* — zero cramped sidebars or half-empty decorative padding voids.
     6. *Affordance Clarity* — interactive vs static elements visually distinct without hover guessing.
     7. *State Completeness* — empty, loading, error, and focus states verified visually.

4. **Execute Static Anti-Slop Scan & Redesign Retention Check**
   - **Input:** Source tree `src/` (plus `--before` directory when performing an existing-UI redesign).
   - **Output:** Zero-violation `anti-slop-audit.json` report.
   - **Owner:** Frontend Engineer / CI Pipeline.
   - **Tool / Script:**
     ```bash
     python3 scripts/check_anti_slop.py src/ --strict --json
     python3 scripts/check_anti_slop.py --before legacy_src/ --kept new_src/ --json
     ```
   - **Execution:** On brownfield redesigns, run `--before ... --kept ...` to prove zero live `<a href>`, `<Link>`, `<form>`, `onClick`/`onSubmit` handlers, or `data-testid` hooks were silently dropped.

5. **Complexity Budget & Deletion / Condensation Pass**
   - **Input:** Audited components, stylesheets, and landing sections.
   - **Output:** Lean, high-signal UI implementation.
   - **Owner:** Frontend Lead.
   - **Execution:** Delete decorative eyebrow pills above every heading, cut redundant subtitle sentences that repeat the headline, collapse multi-column generic link footers into essential legal/product links, and remove unused CSS utility overrides.

---

## 3. Reusable Artifact & Template

Anti-slop policy, icon/font rules, UX copy voice rules, and the `<= 5` waiver ledger live in Sections 1 and 6 of [../templates/design-master.md](../templates/design-master.md).

| Field / Ledger Entry | Type | Validation Constraint | Verified By |
|---|---|---|---|
| `banned_fonts_policy` | Rule | Rejects `Inter`, `Roboto`, `Arial`, `Open Sans`, `Helvetica` unless ADR waived | `check_anti_slop.py` (`SLOP-FONT-01`) |
| `icon_standard` | Enum | `Phosphor` (`@phosphor-icons/react`), `Solar`, or `Iconamoon`; bans `Lucide`/`Feather`/`Heroicons`/`Material Icons`/`Material Symbols` | `check_anti_slop.py` (`SLOP-ICON-01`) |
| `surface_gradient_rule` | Rule | Flat surfaces; gradients allowed only on hero display text with `background-clip: text` | `check_anti_slop.py` (`SLOP-GRAD-01`) |
| `copy_voice_contract` | Matrix | Sentence case, button-to-toast verb parity, zero buzzwords, zero `Lorem ipsum` | `check_anti_slop.py` (`SLOP-COPY-01`) |
| `redesign_retention_diff` | Diff Check | Zero dropped routes, forms, or handlers across `--before` and `--kept` | `check_anti_slop.py --before --kept` |
| `waiver_ledger` | Table (`<= 5`) | Dated ADR ID, rule waived, rationale, expiration/review date | Design Lead sign-off |

---

## 4. Verification Checklist

- [ ] Font declarations exclude `Inter`, `Roboto`, `Arial`, `Open Sans`, and `Helvetica` (or cite a valid `--allow-font` brownfield ADR).
- [ ] All icons originate from `Phosphor`, `Solar`, or `Iconamoon` with zero `Lucide`, `Feather`, `Heroicons`, `Material Icons`, or `Material Symbols` imports.
- [ ] Background gradients are absent from cards/sections; any hero text gradient explicitly declares `background-clip: text`.
- [ ] Zero `z-index >= 999` values exist anywhere in CSS or inline JSX styles.
- [ ] Hero, feature, empty, and error copy contain zero AI hype buzzwords, zero em-dash fluff, and zero exclamation marks or apologies.
- [ ] Action button labels match confirmation toast verbs (`Publish` -> `Published`, `Delete` -> `Deleted`) in sentence case.
- [ ] Demo data uses realistic non-round values (`$47/mo`, `99.94%`, `14.2ms`) with zero placeholder text (`Lorem ipsum`, `coming soon`).
- [ ] Redesigns pass `--before ... --kept ...` with zero unapproved dropped links, forms, or event handlers.
- [ ] Legal links (privacy/terms where required), custom `404` recovery, and a keyboard skip-to-content link exist on web surfaces.
- [ ] Heading levels follow strict semantic order (`h1` -> `h2` -> `h3` without skipped levels) and icon-only buttons carry explicit `aria-label` attributes.
- [ ] Zero sun/moon theme toggle clutter appears on fixed single-theme marketing pages, and zero `window.alert()`/`confirm()` dialogs appear in production flows.

### Site-Kind Aesthetic Calibration Matrix

| Site-Kind | Primary Vernacular | Focal Boldness Budget | Forbidden Cliché |
|---|---|---|---|
| `software` | Crisp Bento / High-contrast workspace | Interactive product frame or live SQL/code preview | 3 identical feature cards + purple gradient hero |
| `gaming` | High-contrast dark HUD / kinetic display | Atmospheric key art or custom geometric frame | Muddy neon glow obscuring HUD readability |
| `tech` | Precision hardware / schematic grid | Macro hardware render or telemetry specification table | Generic floating abstract spheres |
| `product` | Studio photography + calm tactile UI | Single full-bleed product detail or material close-up | Cluttered multi-badge discount ribbons |
| `service` | Editorial typography + verified proof | Client outcome metrics + clear consultation booking | Stock handshake photos + `"world-class"` prose |
| `place` | Warm archival serif + spatial photography | Atmospheric venue photography + direct hours/map | Tiny low-contrast captions over unmasked photos |

### Deterministic Rule Catalog (`check_anti_slop.py`)

- `SLOP-FONT-01` (`REFLEX`): Detects banned font families (`Inter`, `Roboto`, `Arial`, `Open Sans`, `Helvetica`) in CSS, JSX, or font loaders.
- `SLOP-ICON-01` (`REFLEX`): Detects banned icon libraries (`Lucide`, `Feather`, `Heroicons`, `Material Icons`, `Material Symbols`).
- `SLOP-GRAD-01` (`REFLEX`): Detects background gradients lacking hero `background-clip: text`.
- `SLOP-ZIDX-01` (`REFLEX`): Detects out-of-scale `z-index >= 999` or negative stacking hacks.
- `SLOP-COPY-01` (`FLOOR`): Detects `Lorem ipsum`, `coming soon`, and AI buzzword copy.
- `SLOP-A11Y-01` (`FLOOR`): Detects CSS transitions/animations without `prefers-reduced-motion`.
- `SLOP-STRUCT-01` (`FLOOR`): Detects dropped links, forms, handlers, or test IDs during redesign (`--before --kept`).

---

## 5. Hard Quality Gate

| Verdict | Criteria |
|---|---|
| **PASS** | `check_anti_slop.py --strict` exits `0` (`0` FLOOR/REFLEX/FINISH violations), `design_search.py` emits zero banned fonts/icons, all 5 UX copy surfaces verified clean, and redesign retention diff (when applicable) drops zero live routes/handlers. |
| **CONCERNS** | Up to `<= 5` documented brownfield ADR waivers (`--allow-font` / `--allow-icon`) tracked with sunset milestone. |
| **NOT ASSESSED** | Non-UI backend library with zero user-facing screens or copy templates. |
| **FAIL** | Any FLOOR or REFLEX violation: banned font/icon without ADR, unclipped background gradient, `z-index: 9999`, `Lorem ipsum` / AI buzzword copy, missing `prefers-reduced-motion`, or dropped live links/forms during redesign. |

Executable gate check command:

```bash
python3 skills/ui-design-craft/scripts/check_anti_slop.py src/ --strict --json
python3 skills/ui-design-craft/scripts/design_search.py "B2B SaaS analytics" --design-system -p "VerifyApp" -f markdown --json
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **AI Purple-Blue Gradient Wash** | Immediately flags template-generated landing pages and obscures text contrast | `linear-gradient(135deg, #6366f1, #a855f7)` on cards/sections | Use flat intentional surfaces (`#09090B`/`#18181B` or `#FAFAFA`) and `1` crisp accent |
| **Silent Fallback to `Inter` / `Lucide` / `Heroicons`** | Overrides brand differentiation and violates cross-skill visual defaults | Imports of `Inter`, `Roboto`, `lucide-react`, `heroicons`, `material-icons` | Use `Geist`/`Plus Jakarta Sans`/`Manrope` and `Phosphor`/`Solar`/`Iconamoon` |
| **3-Equal-Card SaaS Row + Pill Badges** | Uniform generic bento/pricing cliché with weak scannability and fake visual density | Identical 3-col cards with `ALL-CAPS` pill badges above every title | Use asymmetric content-driven grids (`5:7`, `4:8`) and spend boldness in `1` focal point |
| **Chatbot-Tainted Microcopy & Apologies** | *"Unlock Next-Gen Synergy!"* or *"Oops! Something went wrong!"* erodes user trust | AI buzzwords, `"Oops"`, `"Sorry"`, `"Learn more"`, `"Submit"`, `"—"` padding | Use concrete numbers, Verb + Outcome CTAs, and calm active error recovery |
| **Unilateral Link/Handler Deletion During Redesign** | Breaks user bookmarks, checkout flows, and automated QA selectors silently | Missing `<a href>`, `<form>`, `onClick`, or `data-testid` vs `--before` | Run `check_anti_slop.py --before <old> --kept <new>` before merging redesigns |
| **Over-Decorated Eyebrow & Chrome Bloat** | Stacking icons on every heading, decorative status dots, and 4-col footer farms dilutes signal | Repeated `eyebrow · meta — desc →` patterns on every card | Delete decorative chrome; preserve only elements that drive comprehension or action |
