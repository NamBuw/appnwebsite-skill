# Typography, Spatial Grids & Cognitive Ergonomics

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

---

## 1. Decision Framework

Typography carries `85–90%` of visual hierarchy on modern apps and websites. Before writing CSS, lock font selection, modular scale ratio, fluid `clamp()` bounds, grid geometry, density mode, and ergonomic target minimums.

### Font Selection & Pairing Policy (Strict Anti-AI-Slop Defaults)

- **Default Banned Fonts:** `Inter`, `Roboto`, `Arial`, `Open Sans`, and `Helvetica` are banned by default across greenfield and standard redesign work (unless an explicit dated brownfield ADR passes `--allow-font`).
- **Preferred High-Craft Families:**
  - *Single-Family UI & SaaS:* `Geist`, `Plus Jakarta Sans`, `Manrope`, `Instrument Sans`, `IBM Plex Sans`, `DM Sans`.
  - *High-Legibility Civic / Accessibility:* `Atkinson Hyperlegible`, `IBM Plex Sans`.
  - *Editorial / Display + Sans Pairings:* `Newsreader` + `IBM Plex Sans`, `Playfair Display` + `Geist`, `Fraunces` + `Plus Jakarta Sans`, `Instrument Serif` + `Instrument Sans`.
  - *Monospace (strictly for code, hashes, telemetry, tabular IDs):* `Geist Mono`, `JetBrains Mono`, `IBM Plex Mono`.
- **Pairing Mechanics:** Match x-height (`0.48–0.54` of em-square for body legibility), aperture openness (`c, e, s` distinct at `13–14px`), and pair only across distinct structural classifications (e.g., high-contrast serif display + humanist sans body). Never pair two visually similar geometric sans fonts.
- **Weight & Style Discipline:** Restrict active weights to `400`, `500`, `600`, `700` (and `800` only for deliberate poster/brutalist display); avoid `900` ultra-black bloat and avoid italics in UI controls/cards.

### Modular Type Scale & Fluid `clamp()` Selector

| Surface Archetype | Modular Ratio | Base Body Size | Max Line Measure | Hero / Display Range |
|---|---|---|---|---|
| **Dense SaaS / Telemetry Dashboard** | `1.125` (Major Second) | `14px`–`15px` | `55ch–68ch` (`13–14px` table cells) | `28px–36px` (`H1`) |
| **Balanced Web / Mobile App** | `1.200` (Minor Third) | `16px` (`1rem`) | `60ch–70ch` | `32px–44px` (`H1`) |
| **Editorial / Product Marketing** | `1.250` (Major Third) | `16px`–`18px` | `60ch–65ch` (`<= 680px` hero prose) | `40px–60px` (`H1`) |
| **Flagship / Poster Landing Page** | `1.333`–`1.414` | `17px`–`18px` | `55ch–65ch` (`<= 680px` hero prose) | `48px–72px` (`H1`) |

Exact CSS `clamp()` formula (always mix `rem` + `vw` so browser zoom scales accessibly—never pure `vw`):

```text
slope     = ((maxPx - minPx) / (maxVw - minVw)) * 100        [unit: vw]
intercept = (minPx - (slope / 100) * minVw) / 16             [unit: rem]
clamp     = clamp(minRem, calc(interceptRem + slopeVw), maxRem)
```

Example (`32px -> 56px` across `390px -> 1280px`): `slope = (24 / 890) * 100 = 2.697vw`, `intercept = (32 - 0.02697 * 390) / 16 = 1.343rem` -> `clamp(2rem, calc(1.343rem + 2.697vw), 3.5rem)`.

### Grid Geometry & Density Mode Selector

| Viewport Class | Columns | Margin | Gutter | Max Container | Density Multipliers |
|---|---|---|---|---|---|
| **Mobile (`< 640px`)** | `4` cols | `16px` | `16px` | `100%` (safe-area aware) | `compact: 0.75x`, `comfortable: 1.0x`, `spacious: 1.25x` |
| **Tablet (`640px–1023px`)** | `8` cols | `24px` | `20px` | `100%` | Applied cleanly across `--space-0..900` (`4px/8px` grid) |
| **Desktop (`>= 1024px`)** | `12` cols | `32px` | `24px–32px` | `1200px–1440px` (`1280px` default) | Asymmetric splits (`5:7`, `4:8`, `1.618:1`) over 3-equal-card rows |

### 26-Style Semantic Typography Token Contract

```css
/* Representative fluid + structural scale mapped to Spacing-0..900 rhythm */
:root {
  --font-sans: "Geist", system-ui, -apple-system, sans-serif;
  --font-mono: "Geist Mono", ui-monospace, monospace;
  --type-heading-1: clamp(2rem, calc(1.343rem + 2.697vw), 3.5rem);
  --type-heading-2: clamp(1.625rem, calc(1.2rem + 1.7vw), 2.5rem);
  --type-heading-3: clamp(1.375rem, calc(1.1rem + 1.1vw), 1.875rem);
  --type-title-1: 1.5rem;
  --type-body-1: 1.125rem;
  --type-body-3: 1rem;
  --type-button-md: 0.875rem;
  --type-caption-1: 0.8125rem;
}

.metric-cell {
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
}

.nested-card {
  --outer-r: 16px;
  --gap: 8px;
  border-radius: var(--outer-r);
  padding: var(--gap);
}
.nested-card > .nested-inner {
  border-radius: calc(var(--outer-r) - var(--gap)); /* 8px concentric */
}
```

### Token Economy & Simplest High-Craft Option (Anti-Overengineering Check)

- **Token Economy Rule:** Query `python3 skills/ui-design-craft/scripts/core_search.py "<mood>" --domain typography --json` before picking pairings manually.
- **Simplest High-Craft Option:** Before loading 3 font families across 9 weights or writing JavaScript `ResizeObserver` / `useMediaQuery` layout engines, ask:
  - *"Can a single variable font (`Geist` or `Plus Jakarta Sans`, 4 weights) paired with native CSS `clamp()`, CSS Grid, Subgrid, and `@container` queries achieve cleaner visual rhythm with zero runtime JS?"*
  - *"Can native HTML `<dialog>` and `popover` replace custom z-index portal managers?"*
  Native CSS layout primitives eliminate hydration flicker, bundle bloat, and resize lag.

---

## 2. Step-by-Step Workflow

1. **Select Font Family & Internationalization Fallbacks**
   - **Input:** `design-brief.md` (`site_kind`), target locales (Latin, CJK, Arabic/RTL).
   - **Output:** Verified non-banned font stack and `dir="rtl"` logical CSS rules in `design-master.md`.
   - **Owner:** Design System Lead.
   - **Tool / Script:** `python3 scripts/core_search.py "<site_kind> <mood>" --domain typography --json`.
   - **Execution:** Choose `1` primary font family (or `1` display + `1` body pair across distinct classes) plus `1` monospace family for code/telemetry. Include CJK/RTL fallback stacks (`"Noto Sans CJK SC/JP/KR"`, `"IBM Plex Sans Arabic"`) where internationalized, and author spacing using CSS logical properties (`margin-inline`, `padding-inline`, `inset-inline-start`) so RTL mirroring requires zero duplicated stylesheets.

2. **Build Fluid Type Ramp & 26 Named Text Styles**
   - **Input:** Modular ratio from Section 1 (`1.125`–`1.414`) and viewport bounds (`390px`–`1280px`).
   - **Output:** CSS custom properties for `heading-1..6`, `title-1..5`, `body-1..6`, `button-lg..xsm`, `caption-1..5`.
   - **Owner:** UI Engineer.
   - **Tool / Script:** `python3 scripts/validate_tokens.py tokens.json --strict --json`.
   - **Execution:** Compute `clamp()` expressions for display and heading tiers, keep body at `>= 16px` on content surfaces (`>= 14px` in dense tables), apply `font-variant-numeric: tabular-nums` to all numeric columns, prices, and timers, set `text-wrap: balance` on headings (`<= 3` lines) and `text-wrap: pretty` on long-form paragraphs, and snap micro-adjustments to whole 4px/8px vertical rhythm.

3. **Configure 4/8/12-Col Grid, Container Queries & Nested Radius Geometry**
   - **Input:** Breakpoints, density mode (`compact | comfortable | spacious`), and `Spacing-0..900` tokens (`0, 2, 4, 8, 12, 16, 24, 32, 40, 48, 64, 80, 96px`).
   - **Output:** Root layout stylesheet + component container rules.
   - **Owner:** Frontend Engineer.
   - **Tool / Script:** `python3 scripts/core_search.py "grid layout" --stack html-tailwind --json`.
   - **Execution:** Define reusable components with `container-type: inline-size` and `@container` queries rather than viewport-only media queries so cards adapt seamlessly in sidebars or full-bleed rows. Enforce the **Nested Radius Law**: whenever a child surface sits inside a padded parent with `gap < 32px`, compute `r_inner = max(2px, r_outer - gap)` (when `r_outer - gap > 2px`) so corners stay concentric rather than pinched. Use `100dvh` instead of `100vh` for full-viewport mobile sections to prevent iOS Safari toolbar clipping.

4. **Lock Z-Index Layer Spec & Structural Rhythm**
   - **Input:** Overlay, sticky header, popover, modal, and toast requirements.
   - **Output:** Strict 8-step Z-Index token ladder.
   - **Owner:** Frontend Architect.
   - **Tool / Script:** `python3 scripts/check_anti_slop.py src/ --json`.
   - **Execution:** Lock CSS variables: `--z-base: 0`, `--z-raised: 10`, `--z-sticky: 20`, `--z-overlay: 30`, `--z-modal: 40`, `--z-popover: 50`, `--z-toast: 60`, `--z-tooltip: 70`. Any `z-index >= 999` (such as `9999`) or negative ad-hoc index fails the anti-slop gate. Use native `<dialog>` and HTML `popover` attributes so browser top-layer promotion handles stacking automatically without z-index wars.

5. **Enforce Cognitive Ergonomics (Gestalt, Fitts, Hick, Miller)**
   - **Input:** Interactive controls, forms, toolbars, and card grids.
   - **Output:** Ergonomically compliant component geometry.
   - **Owner:** UX Engineer.
   - **Tool / Script:** `python3 scripts/core_search.py "touch target spacing" --domain ux --json`.
   - **Execution:**
     - **Gestalt Proximity & Common Region:** Keep internal card/field padding `<= 0.5 * outer_gap` so related items visually bind without heavy nested boxes; eliminate single-sided `.card` accent borders.
     - **Fitts' Law:** Enforce `>= 44x44pt` on iOS, `>= 48x48dp` on Android, and `>= 24x24px` minimum (with `>= 8px` inter-target gap) for WCAG 2.2 AA `2.5.8` on desktop; anchor primary mobile actions in the bottom thumb zone.
     - **Hick's Law:** Cap primary toolbar and nav choices at `5 ± 2` visible actions; move secondary/destructive controls into menus or progressive disclosure.
     - **Miller's Law:** Chunk multi-field forms into `3–5` logically grouped `<fieldset>` sections with clear headings.

6. **Complexity Budget & Deletion / Condensation Pass**
   - **Input:** Authored CSS, layout components, and token definitions.
   - **Output:** Condensed stylesheet verified across `320px`, `390px`, `768px`, and `1440px` viewports.
   - **Owner:** Frontend Lead.
   - **Execution:** Snap off-scale sizes (`19px`, `22px`) to the modular ramp, replace nested `<div className="flex ...">` wrappers with direct CSS Grid areas or `gap`, remove JS viewport resize listeners replaced by `@container` / `clamp()`, and verify zero horizontal overflow (`scrollWidth <= clientWidth`) at `320px` and `390px`.

---

## 3. Reusable Artifact & Template

All typography, grid, spacing, radius, and z-index rules lock into Sections 3 and 4 of [../templates/design-master.md](../templates/design-master.md) during Spiral Phase 3A.

| Section / Field | Type | Contract & Allowed Values | Verified By |
|---|---|---|---|
| `heading_font` / `body_font` | String | Non-banned families (`Geist`, `Plus Jakarta Sans`, `Manrope`, `Instrument Sans`, etc.) | `check_anti_slop.py`, `validate_tokens.py` |
| `type_ramp_26` | Token Map | Fluid `clamp()` + `heading-1..6`, `title-1..5`, `body-1..6`, `button-lg..xsm`, `caption-1..5` | `validate_tokens.py` |
| `grid_breakpoints` | Matrix | `4`-col mobile (`16px`), `8`-col tablet (`20px`), `12`-col desktop (`24–32px`, `<= 1440px`) | Viewport overflow audit |
| `spacing_tokens` | Scale | 13 tokens `--space-0..900` (`0, 2, 4, 8, 12, 16, 24, 32, 40, 48, 64, 80, 96px`) | `tokens-dtcg.schema.json` |
| `nested_radius_rule` | Formula | `inner = max(2px, outer - gap)` when `gap < 32px` | Design QA review |
| `z_index_ladder` | Enum Map | `0, 10, 20, 30, 40, 50, 60, 70` (strictly `< 999`) | `check_anti_slop.py` |
| `ergonomic_minimums` | Thresholds | `>= 44x44px` mobile, `>= 24x24px` WCAG 2.2 AA, `<= 65ch` prose (`<= 680px` hero) | `ux-guidelines.csv` audit |

---

## 4. Verification Checklist

- [ ] Heading and body typography exclude `Inter`, `Roboto`, `Arial`, `Open Sans`, and `Helvetica` (or carry an explicit brownfield ADR override).
- [ ] Active font weights stay within `400–700` (`800` only for approved display), avoiding `900` weight and card/UI italics.
- [ ] All fluid `clamp()` scales combine `rem + vw` so `200%` browser text zoom scales cleanly without clipping.
- [ ] Body prose measure is constrained to `45ch–75ch` (`<= 680px` for hero copy) and numeric metrics use `tabular-nums`.
- [ ] Nested interactive surfaces obey `inner_radius = outer_radius - gap` when `gap < 32px` and result `> 2px`.
- [ ] Z-index values strictly follow the `0..70` semantic scale with zero `999`/`9999` spikes, preferring native `<dialog>` / `popover`.
- [ ] Mobile touch targets meet `>= 44x44px` (`>= 48dp` Android) with `>= 8px` separation, and desktop controls meet WCAG 2.2 AA `>= 24x24px`.
- [ ] Zero horizontal overflow (`scrollWidth <= innerWidth`) occurs at `320px`, `390px`, `768px`, and `1440px` viewports.

---

## 5. Hard Quality Gate

| Verdict | Criteria |
|---|---|
| **PASS** | Non-banned typography scale locked in `design-master.md` + `tokens.json`, zero `z-index >= 999`, valid `clamp()` `rem+vw` syntax, `<= 65ch`/`680px` prose measure, touch target minimums met, and `check_anti_slop.py` + `validate_tokens.py` return exit `0`. |
| **CONCERNS** | Minor nested radius or `tabular-nums` polish item logged with target fix before release gate. |
| **NOT ASSESSED** | Non-visual backend/API-only service without rendered UI surfaces. |
| **FAIL** | Banned default font imported without ADR, pure `vw` font sizing blocking browser zoom, `z-index >= 999`, `100vh` mobile overflow/clipping, or horizontal overflow at `390px`. |

Executable gate check command:

```bash
python3 skills/ui-design-craft/scripts/validate_tokens.py tokens.json --strict --json
python3 skills/ui-design-craft/scripts/check_anti_slop.py src/ --strict --json
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Defaulting to `Inter` / `Roboto` / `Arial` / `Open Sans` / `Helvetica`** | Signals unedited AI template output and strips product identity | `font-family` or `next/font/google` importing banned family | Choose `Geist`, `Plus Jakarta Sans`, `Manrope`, `Instrument Sans`, or `IBM Plex Sans` |
| **Pure `vw` Fluid Sizing (`font-size: 4vw`)** | Breaks WCAG 1.4.4 `200%` browser text zoom because `vw` ignores root font scaling | `clamp(..., 4vw, ...)` lacking a `rem` intercept term | Always use `clamp(minRem, calc(interceptRem + slopeVw), maxRem)` |
| **Arbitrary `z-index: 9999` Escalation** | Triggers stacking-context wars where tooltips vanish behind modals | `z-index` values `999`, `9999`, or `99999` in CSS/JSX | Use semantic `--z-base..--z-tooltip` (`0..70`) and native `<dialog>`/`popover` |
| **JavaScript Resize Layout Listeners** | Causes layout thrashing, hydration mismatch, and unnecessary event overhead | `window.addEventListener('resize')` toggling layout classes | Use CSS Grid, Subgrid, and `@container` inline-size queries |
| **3-Equal-Card Symmetry Default** | Produces repetitive, low-hierarchy AI SaaS grids with weak focal rhythm | Uniform `grid-cols-3` identical cards across every section | Use asymmetric splits (`5:7`, `4:8`, bento) aligned to content priority |
| **`100vh` Mobile Hero Trap** | Clips bottom CTAs under iOS Safari / Android Chrome dynamic address bars | `min-height: 100vh` on mobile full-bleed hero/drawers | Use `100dvh` (`min-height: 100dvh`) with `env(safe-area-inset-bottom)` |
| **Unbounded `> 75ch` Prose & Tiny Touch Targets** | Drops reading speed sharply and causes mis-taps on mobile screens | Paragraph containers `> 850px` wide or `< 36px` mobile buttons | Cap prose at `<= 65ch` (`<= 680px` hero) and enforce `>= 44x44px` mobile targets |
