# UI Audit and Redesign

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This module defines the end-to-end process for auditing and upgrading existing websites and applications (`Scan -> Diagnose -> Fix`) without breaking live user journeys. It integrates 9-domain design inspection, 3-tier severity triage (`Floor | Reflex | Finish`), `--before` / `--kept` functional preservation verification, `@2x` DPI-normalized visual comparison (`P0-P3`), the 9-step Fix Priority order, and Radical Simplicity ("Least Code, Highest Craft").

---

## 1. Decision Framework

### 1.1 Three-Tier Severity & Triage Matrix (`Floor | Reflex | Finish`)

Classify every audit finding into an unambiguous severity tier before proposing edits:

| Severity Tier | Definition & User Impact | Examples | Fix Mandate |
|---|---|---|---|
| **Tier 1: `Floor` (Hard Blocker)** | Broken usability, accessibility failure, functional regression, or raw placeholder leak | Dropped link/handler/form field, WCAG AA contrast failure (`< 4.5:1` / `< 3:1`), missing `focus-visible`, `390px` horizontal overflow, `100vh` iOS clipping, raw `Lorem ipsum` or console errors | **Mandatory fix before release** — blocks `PASS` |
| **Tier 2: `Reflex` (Structural & Anti-Slop Hygiene)** | Generic AI defaults or interactive debt eroding trust and responsiveness | Banned fonts (`Inter`/`Roboto`/`Arial`/`Open Sans`/`Helvetica`), banned icons (`Lucide`/`Feather`/`Heroicons`/`Material Icons`/`Material Symbols`), AI purple/blue gradient washes, missing hover/active/loading/empty/error states, sticky hover on touch, unthrottled scroll listeners | **Fix in Steps 1-7** of the 9-Step Priority Order |
| **Tier 3: `Finish` (Craft & Editorial Polish)** | Typographic precision, optical alignment, and conversion clarity | `> 75ch` wide body prose, missing `tabular-nums`, uneven card button baselines, unnested corners (`inner != outer - gap`), 3-equal-card stereotypes, generic microcopy | **Polish in Steps 4, 6, 8, 9** after Floor/Reflex clear |

### 1.2 Migration Strategy Matrix (In-Place vs. Strangler-Fig)

| Scope & Risk Profile | Recommended Strategy | Execution Mechanism | Rollback Safety |
|---|---|---|---|
| **Small / Contained UI (`<= 5` screens or isolated surface)** | **Direct In-Place 9-Step Fix** | Edit existing CSS/Tailwind/component files directly while preserving routes, props, and handlers | Single branch/PR revert |
| **Large Multi-Route Live App (`> 5` screens, active traffic)** | **Incremental Strangler-Fig Migration** | Isolate new tokens inside CSS `@layer redesign` or scoped `.ui-v2` wrapper -> upgrade route-by-route behind feature flag -> delete legacy CSS once 100% migrated | Instant per-route flag toggle |

### 1.3 Simplest High-Craft Option

**Anti-Overengineering Self-Interrogation ("Least Code, Highest Craft")**: Never rewrite a working application from scratch or migrate CSS frameworks (e.g., CSS Modules -> Tailwind or Bootstrap -> custom CSS-in-JS) when visual craft can be transformed **in-place**:
- Keep existing framework, router, and working business/form handlers untouched.
- Swap banned fonts/icons and flatten noisy surfaces via existing stylesheet or `@layer` tokens.
- Apply the strict **9-Step Fix Priority** so structural typography, color, states, and layout land before micro-copy polish.
- Run a final Deletion Pass to strip superseded legacy CSS and uninstalled icon packages.

Preserving working business logic, routes, and state cuts regression risk to near zero and ships `5-10x` faster.

---

## 2. Step-by-Step Workflow

### Token Economy Protocol
- Capture structured DOM counts (`--before` / `--kept`), Lighthouse JSON, and targeted flow screenshots (`01-*.png`) first.
- Run deterministic `check_anti_slop.py`, `axe-core`, and `pa11y` checks before reading large component trees into context.
- Edit only components flagged in the 9-domain diagnosis rather than touching clean files.

1. **Scan Environment & Capture Quantitative Baseline (`Owner: UI Auditor`)**
   - **Inputs**: Existing repository, running local/staging URL, `tokens.json` (if present).
   - **Action**:
     - Inspect `package.json`, CSS setup (detect Tailwind v3 `tailwind.config.*` vs Tailwind v4 `@theme` vs CSS Modules/vanilla CSS), and existing font/icon imports.
     - Capture **4 Mandatory Baseline Artifacts**:
       1. *Lighthouse Scores*: Performance, Accessibility, SEO baselines.
       2. *Dual-Engine Accessibility Audit*: Run both `axe-core` and `pa11y` on primary routes so engine blind spots cancel out.
       3. *Normalized `@2x` Flow Screenshots*: Capture `01-*.png` across primary user flows at desktop (`1440x900`) and mobile (`390x844`), normalizing `@2x` retina captures to logical CSS pixels before side-by-side comparison.
       4. *`--before` Functional Preservation Manifest*: Record exact counts and identifiers of all `<a href>` routes, `<button>` / `onClick` / `onSubmit` handlers, and `<form>` / `input[name]` fields.
   - **Outputs**: Populated Baseline & `--before` Preservation sections in [UI Redesign Audit & Preservation Template](../templates/ui-redesign-audit.md).

2. **Diagnose Across All 9 Domains (Zero Edits Yet) (`Owner: UI Auditor`)**
   - **Inputs**: Baseline screenshots, DOM audit, source code scan.
   - **Action**: Audit every domain systematically and tag each issue `Floor`, `Reflex`, or `Finish`:
     1. *Typography*: Banned fonts, mixed families, italics/weight-`900` overuse, missing `clamp()`/`65ch`/`tabular-nums`/`text-wrap`.
     2. *Color & Surfaces*: Unrequested purple/blue gradients, 1-sided accent borders, mixed cool/warm gray temperatures, harsh black shadows, glare/contrast failures.
     3. *Layout & Rhythm*: `100vh` mobile clipping (`100dvh` needed), broken grids (`> 1440px` uncontained or `< 320px` overflow), 3-equal-card monotony, uneven card CTA baselines, uneven optical bottom padding.
     4. *Interactivity & States*: Missing `hover`, `active:scale(0.98)`, `focus-visible`, `loading` skeleton, `empty`, or inline `error` states; sticky hover on touch; paste-blocking; `window.alert()`.
     5. *Content & Microcopy*: AI buzzwords (`delve`, `unleash`, `seamless`, `elevate`), hyphen-heavy copy, vague CTAs, unanchored `Lorem ipsum` or invented metrics.
     6. *Component Patterns*: `border + shadow + white` card overuse, accordion FAQ hiding answers, taller middle pricing tower, intrusive modals where inline/slide-over `<Sheet>` fits, pill/eyebrow clutter.
     7. *Iconography & Imagery*: `Lucide`/`Feather`/`Heroicons`/`Material Icons`/`Material Symbols` imports (swap to `Phosphor`/`Solar`/`Iconamoon`), stretched/CSS-faked brand illustrations, unrequested dark/color tints over hero photos.
     8. *Code Quality & Tokens*: Hardcoded `#hex` soup, inconsistent `z-index` wars, unthrottled scroll listeners, non-GPU animations (`top`/`left`/`width`).
     9. *Strategic Omissions*: Missing skip-link, custom 404, privacy/terms, `prefers-reduced-motion`, `theme-color` meta, or dark/light switcher polish.
     - Present the completed `ui-redesign-audit.md` diagnosis to the stakeholder for explicit **veto / exclusion confirmation** before mutating source files.
   - **Outputs**: User-approved Redesign Audit Plan.

### 2.2.1 Normalized `@2x` Visual QA & Fidelity Surfaces

Before editing or signing off, capture desktop (`1440x900`) and mobile (`390x844`) flow frames (`01-landing.png`, `02-workspace.png`, `03-checkout.png`), normalize Retina `@2x` PNGs down to `1x` CSS pixel dimensions so side-by-side comparisons stay faithful, and verify all **5 Fidelity Surfaces**:
1. **Typography & Scale**: Non-banned font loaded, crisp hierarchy, zero italics/weight-`900`, `~65ch` measure.
2. **Spacing & Rhythm**: Consistent vertical cadence, aligned card footer CTAs, optical bottom padding.
3. **Color & Tokens**: Flat intentional surfaces, unified gray temperature, verified `4.5:1` / `3:1` contrast.
4. **Image & Brand Asset Fidelity**: Real raster/SVG brand assets intact (never replaced by fake CSS boxes or clumsy hand-coded SVGs); zero unrequested dark tints over photos.
5. **Copy & Microcopy**: Active voice, zero AI buzzwords, specific calm error/empty messages.

3. **Execute Fixes in Strict 9-Step Priority Order (`Owner: Frontend Engineer`)**
   - **Inputs**: Approved `ui-redesign-audit.md`, `tokens.json`.
   - **Action**: Execute sequentially so structural typography and surface foundations stabilize before copy or micro-polish:
     1. *Font swap*: Replace banned fonts with `Geist`, `Manrope`, `Poppins`, or approved non-banned pairing; enforce 1 typeface where clean, remove italics and `800/900` weights, add `500/600` clarity.
     2. *Color & surface cleanup*: Flatten noisy cards/gradients, unify gray temperature, apply single `< 80%`-saturation accent, tune background-tinted shadows.
     3. *Interactive states*: Add `hover` inside `@media (hover: hover) and (pointer: fine)`, `active:scale(0.98)`, `2px` `focus-visible` ring + offset, and remove any `onPaste` blocking.
     4. *Layout & spacing*: Apply CSS Grid/`minmax(0, 1fr)`, `1200-1440px` container, `680px` hero cap, `min-height: 100dvh`, nested radius `inner = outer - gap`, break 3-col symmetry, align card CTAs along bottom.
     5. *Motion pass*: Switch to `cubic-bezier(0.22, 1, 0.36, 1)`, GPU-only `transform`/`opacity`, `IntersectionObserver` reveals, and `prefers-reduced-motion` instant fallback.
     6. *Replace generic components*: Convert accordion FAQs to plain side-by-side/searchable Q&A where marketing context fits, remove border+shadow card boxes, replace taller pricing tower with weight/border emphasis, move minor edits out of modals.
     7. *Loading, empty & error states*: Add dimension-matched skeletons, helpful empty states with reset/create CTAs, and calm inline error alerts (`0` `window.alert()`).
     8. *Copy pass*: Strip AI buzzwords, enforce sentence case, remove copy hyphens, sharpen verb+outcome CTAs, use specific confirmation copy.
     9. *Type scale polish*: Snap headings/body to scale, enforce `65ch` prose measure, `tabular-nums` on metrics/tables, and `text-wrap: balance`/`pretty`.
   - **Outputs**: Upgraded UI implementation with every live route and handler preserved.

4. **Verify `--kept` Preservation, Side-by-Side Visual Delta (`P0-P3`) & Deletion Pass (`Owner: QA / Frontend Lead`)**
   - **Inputs**: Upgraded staging/dev build, `--before` manifest, baseline screenshots.
   - **Action**:
     - Run **`--kept` Preservation Diff**: verify `100%` of `--before` links, click/submit handlers, and form field names remain intact (any intentional removal requires explicit ADR/user sign-off).
     - Re-capture normalized `@2x` screenshots at `1440x900` and `390x844`, inspect side-by-side across the 5 fidelity surfaces (typography, spacing/rhythm, colors/tokens, raster/brand image integrity, copy), and iterate `P0-P3` until zero `Floor` or `Reflex` defects remain.
     - Re-run Lighthouse, `axe-core`, and `pa11y` to confirm strictly improved or equal scores.
     - **Deletion / Condensation Pass**: Remove legacy `.old-*` stylesheets, dead CSS overrides, unused icon packages (`lucide-react`, `@heroicons/react`), and orphaned wrapper divs. Re-run full test suite afterward.
   - **Outputs**: Finalized `ui-redesign-audit.md` with before/after receipts.

### 2.4.1 Nine-Step Fix Sequence Quick Reference

| Step | Target Surface | Primary Transformation |
|---|---|---|
| `1` | Typography Foundation | Swap banned fonts -> `Geist`/`Manrope`/`Poppins`; remove italics/`900` |
| `2` | Color & Surfaces | Flatten noisy washes; unify gray temp; single `< 80%`-sat accent |
| `3` | Interactive States | Add `@media (hover: hover)`, `active:scale(0.98)`, `2px` `focus-visible` |
| `4` | Layout & Safe Geometry | Enforce `min-height: 100dvh`, `680px` hero cap, nested radius, `0 px` `390px` overflow |
| `5` | Motion Choreography | Use `cubic-bezier(0.22, 1, 0.36, 1)`, GPU-only `transform`/`opacity`, reduced-motion |
| `6` | Generic Component Swap | Replace `border+shadow` 3-card stereotypes, accordion-only marketing FAQs, taller pricing tower |
| `7` | Feedback & Resilience | Wire matched skeletons, resettable empty states, inline error alerts |
| `8` | Microcopy Cleanup | Remove AI buzzwords, sentence case, verb+outcome CTAs |
| `9` | Type Scale Polish | Apply scale steps, `65ch` measure, `tabular-nums`, `text-wrap: balance/pretty` |

### 2.5 Minimal `--before` / `--kept` Manifest & Strangler-Fig Guard Snippet

```js
// Playwright DOM extraction for --before / --kept functional parity manifest
const manifest = await page.evaluate(() => ({
  links: [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')).sort(),
  buttons: [...document.querySelectorAll('button, [role="button"]')].map(b => b.textContent?.trim()),
  inputs: [...document.querySelectorAll('input[name], select[name], textarea[name]')].map(i => i.name).sort(),
}));
```

```css
/* Incremental Strangler-Fig isolation when migrating > 5 live routes */
@layer redesign {
  .ui-v2 {
    min-height: 100dvh;
    font-family: var(--font-sans);
    background-color: var(--color-bg-canvas);
    color: var(--color-fg-primary);
  }
}
```

---

## 3. Reusable Artifact & Template

Every audit and redesign MUST populate [UI Redesign Audit & Preservation Template](../templates/ui-redesign-audit.md) prior to applying code changes.

| Template Section | Required Contents | Gate Enforcement |
|---|---|---|
| **Scan Metadata** | `Audit ID`, `Stack & CSS Method`, `Migration Mode (In-Place | Strangler-Fig)`, `User Veto Status` | Coding blocked until user reviews diagnosis |
| **Quantitative Delta** | `Lighthouse Perf/A11y/SEO`, `axe-core` + `pa11y` counts, `390px` overflow, `@2x` screenshot paths | Post-fix metrics must equal or beat baseline with `0` Floor issues |
| **`--before` / `--kept` Ledger** | Exact counts & lists of `<a href>`, handlers (`onClick`/`onSubmit`), `input[name]` fields | `100%` parity required unless user explicitly approved removal |
| **9-Domain Findings Table** | `ID`, `Domain (1-9)`, `Tier (Floor/Reflex/Finish)`, `Selector/File`, `Evidence`, `Fix Step (1-9)` | All 9 domains explicitly checked (mark `"No issues"` if clean) |
| **9-Step & Deletion Log** | `User Vetoed Items`, `Step 1-9 Check`, `Deleted Dead CSS/Deps`, `Final Verdict` | Verifies cleanup of superseded styles and unused icon packages |

---

## 4. Verification Checklist

- [ ] Quantitative baseline (Lighthouse, `axe-core`, `pa11y`, normalized `@2x` screenshots, and `--before` DOM manifest) captured before editing code.
- [ ] All 9 audit domains inspected, findings tagged `Floor`, `Reflex`, or `Finish`, and diagnosis presented for user veto before implementation.
- [ ] Redesign executed in strict 9-Step Fix Priority order (`Font -> Color -> States -> Layout -> Motion -> Components -> Loading/Empty/Error -> Copy -> Type Scale`).
- [ ] `--kept` manifest confirms `100%` preservation of all `--before` navigation links, interactive handlers, and form control names.
- [ ] Banned web fonts (`Inter`, `Roboto`, `Arial`, `Open Sans`, `Helvetica`) and banned web icons (`Lucide`, `Feather`, `Heroicons`, `Material Icons`, `Material Symbols`) completely replaced with approved fonts and `Phosphor`/`Solar`/`Iconamoon`.
- [ ] Mobile viewport (`390x844`) uses `min-height: 100dvh`, `@media (hover: hover)`, and exhibits `0 px` horizontal overflow.
- [ ] Normalized `@2x` before/after visual comparison confirms zero `Floor` or `Reflex` regressions across typography, spacing, tokens, assets, and copy.
- [ ] Superseded legacy CSS, dead wrapper components, and uninstalled old icon dependencies deleted and verified with fresh build and test execution.

---

## 5. Hard Quality Gate

- **`PASS`**:
  - `ui-redesign-audit.md` shows `0` `Floor` blockers, `0` `Reflex` anti-slop defects, `100%` `--before == --kept` functional preservation, and `0` critical/serious `axe-core` + `pa11y` errors.
  - Lighthouse Accessibility `>= 95`, Performance non-regressing (`>= 90` target), `0 px` overflow at `390x844`, and clean build/Playwright receipts after deleting dead legacy CSS/deps.
- **`FAIL`**:
  - Any dropped route link, broken form input, missing click handler, unapproved framework rewrite, banned font/icon left in bundle, or unnormalized before/after screenshot claim.
  - Coding started prior to capturing `--before` baseline and presenting the 9-domain diagnosis.

```bash
# Anti-slop check, dual-engine accessibility audit, and Playwright preservation test
python3 skills/ui-design-craft/scripts/check_anti_slop.py --path src/
npx @axe-core/cli http://127.0.0.1:3000 --exit
npx pa11y http://127.0.0.1:3000
npx playwright test --grep "before-kept-preservation|visual-redesign"
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Scratch Rewrite of Working App** | Reintroduces solved edge cases, breaks auth/routing, and wastes weeks for purely visual gains | Rebuilding working React/Next/HTML pages from zero instead of incremental CSS/component upgrades | Upgrade in-place via 9-Step Priority or Strangler-Fig `@layer`/`.ui-v2` isolation |
| **Dropping Links, Handlers, or Form Fields** | Visual refresh silently deletes navigation routes, analytics hooks, or checkout inputs | `--kept` count lower than `--before` manifest | Run `--before` / `--kept` DOM parity assertion in Playwright on every PR |
| **Tweaking Copy Before Fonts & Surfaces** | Micro-polishing spacing or headlines on top of `Inter` + noisy gradients wastes iterations | Editing Step 8 copy/type scale while Step 1-2 banned fonts/surfaces remain | Follow strict 9-Step Priority: Font -> Color -> States -> Layout -> Motion -> Components -> States -> Copy -> Scale |
| **Unnormalized `@2x` vs `1x` Screenshots** | Comparing mismatched DPI captures creates false-positive diffs and hides blurry raster icons | Raw unscaled Retina PNG compared side-by-side against `1x` target frame | Normalize `@2x` captures to logical CSS pixels before `P0-P3` visual review |
| **Leaving Dead Legacy CSS & Old Icon Deps** | Doubles stylesheet specificity conflicts and ships unused kilobytes to production | Both `lucide-react` and `@phosphor-icons/react` remaining in `package.json` | Execute mandatory Deletion Pass removing superseded CSS and old icon libraries |
| **Mixing Gray Temperatures & Light Sources** | Pairing warm ivory cards with cool slate borders and upward shadows breaks visual cohesion | `#F5F5F4` stone ground mixed with `#64748B` cool slate text and random drop-shadows | Lock 1 gray temperature and 1 top-down background-tinted shadow scale in Tier 2 tokens |
