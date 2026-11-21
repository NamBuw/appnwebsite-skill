# Perceptual Color, Contrast Science, W3C DTCG Tokens, 13 Interaction States & Motion Choreography

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

---

## 1. Decision Framework

Color, state completeness, and motion physics separate resilient production interfaces from fragile prototypes. Author palettes in perceptual **OKLCH** space (`oklch(L C H)`), enforce **dual-gate WCAG 2.1 + APCA (`W3`)** contrast plus **Color Vision Deficiency (CVD)** checks, structure tokens in the **3-tier W3C DTCG** standard, implement all **13 interaction/UI states**, and drive motion with **interruptible GPU-only physics**.

### Perceptual Color & Contrast Dual-Gate Matrix

| Metric / Rule | Body Text (`< 18px`) | Large Text (`>= 18pt` / `14pt` bold) | UI Controls, Borders & Focus Rings | Non-Text / Disabled |
|---|---|---|---|---|
| **WCAG 2.1 AA (Floor)** | `>= 4.5:1` | `>= 3.0:1` | `>= 3.0:1` (`1.4.11`) | Exempt if clearly disabled |
| **WCAG 2.1 AAA (Target)** | `>= 7.0:1` | `>= 4.5:1` | `>= 4.5:1` | `>= 2.0:1` recommended |
| **APCA (`W3` Perceptual)** | `|Lc| >= 75` (`>= 60` min) | `|Lc| >= 45` | `|Lc| >= 45` | `|Lc| >= 30` placeholder/subtle |
| **CVD Simulation Check** | `>= 3.0:1` under Protan/Deutan/Tritan | `>= 3.0:1` under CVD | Paired with icon, label, or pattern | Never hue-only state encoding |

### Dark-Mode Surface & 60-30-10 Allocation Rules

- **Ratio Discipline:** Allocate `60%` neutral background/canvas, `30%` secondary structural surfaces (`card`, `muted`, `border`), and `10%` primary accent/CTA (strictly `1` primary accent hue; keep accent chroma `< 80%` max saturation to prevent halation). Keep neutral gray temperature consistent across all steps (cool zinc/slate OR warm stone—never mix warm and cool grays).
- **Dark-Mode Luminance Ladder:** Elevate dark surfaces via flat luminance steps (`#000000`, `#09090B`, `#131209`, `#181818`, `#18181B`, `#1F1F1F`, `#272727`, `#313131`) rather than heavy black drop shadows or muddy `#0a0a0a`/`#121212` defaults.

### Motion Physics & Complexity Selector

| Surface / Interaction Type | Timing / Physics Spec | Duration Cap | Reduced Motion Behavior |
|---|---|---|---|
| **Hover / Color / Border** | `cubic-bezier(0.22, 1, 0.36, 1)` (`--ease-out-expo`) | `200ms–300ms` (never `< 200ms`) | Keep subtle color change (`0ms`) |
| **Enter (Drawers / Panels / Lists)** | Weighted decel `cubic-bezier(0.22, 1, 0.36, 1)` | `250ms–450ms` (`60ms` stagger cap `400ms`) | Instant opacity fade (`<= 100ms`) |
| **Exit / Dismiss** | `60%–70%` of enter duration | `150ms–260ms` | Instant unmount / opacity `0` |
| **Tactile Press / Spring** | `scale(0.98)` / `snappy` (`stiffness: 400, damping: 30`) | `<= 180ms` settle, interruptible mid-flight | Disable transform; focus/outline feedback only |
| **Scroll Reveal (`B11` / Sections)** | `IntersectionObserver` (`threshold: 0.15`) or CSS `animation-timeline: view()` | `32px` max rise, once-only | Render visible immediately (`opacity: 1; transform: none`) |

### Token Economy & Simplest High-Craft Option (Anti-Overengineering Check)

- **Token Economy Rule:** Query `python3 skills/ui-design-craft/scripts/core_search.py "<product>" --domain color --json` instead of inventing hex codes from memory.
- **Simplest High-Craft Option:** Before installing runtime CSS-in-JS theme providers or multi-megabyte JavaScript animation runtimes, ask:
  - *"Can static W3C DTCG JSON compiled into CSS custom properties (`:root` / `[data-theme="dark"]`) and native CSS `transition` / `@keyframes` deliver identical theme switching and `60fps` GPU motion with zero runtime overhead?"*
  - *"Do our components reference semantic aliases exclusively so dark mode swaps cleanly without rewriting component rules?"*
  Static CSS variables avoid React re-renders on theme toggle and run entirely on the compositor thread.

### Reference CSS Token & Reduced-Motion Skeleton

```css
:root {
  --ease-out-expo: cubic-bezier(0.22, 1, 0.36, 1);
  --dur-hover: 200ms;
  --dur-enter: 320ms;
  --dur-exit: 200ms; /* 62.5% of enter */
}

.interactive-panel {
  transition: transform var(--dur-enter) var(--ease-out-expo),
              opacity var(--dur-enter) var(--ease-out-expo);
}

.interactive-control:focus-visible {
  outline: 2px solid var(--color-ring);
  outline-offset: 2px;
}

@media (prefers-reduced-motion: reduce) {
  .interactive-panel,
  .interactive-control {
    transition: opacity 100ms linear;
    transform: none !important;
  }
}
```

---

## 2. Step-by-Step Workflow

1. **Generate OKLCH Tonal Ramp (`50–950`) & 3-Tier W3C DTCG Tokens**
   - **Input:** Brand seed hue/chroma from `design-brief.md` and `colors.csv` lookup.
   - **Output:** Complete 3-tier `tokens.json` (`primitive -> semantic -> component`) conforming to W3C DTCG (`$schema`, `$value`, `$type`, `{alias}`) plus light/dark mode mappings.
   - **Owner:** Design System Engineer.
   - **Tool / Script:** `python3 scripts/validate_tokens.py tokens.json --strict --json`.
   - **Execution:** Generate calibrated OKLCH ramps (`L = 0.985` at `50` down to `L = 0.21` at `950`, bell-curve `C` peaking at `500–600`) and emit sRGB `#RRGGBB` fallbacks. Enforce strict tier isolation: components ONLY reference `semantic.*` aliases, never raw `primitive.*` hex codes. Validate structure, alias existence, and 3-color DFS acyclicity immediately.

2. **Run Dual-Gate Contrast & CVD Verification**
   - **Input:** `tokens.json` or compiled CSS custom properties.
   - **Output:** Contrast & CVD pass report verifying every semantic foreground/background pair.
   - **Owner:** Accessibility & UI Engineer.
   - **Tool / Script:** `python3 scripts/check_contrast.py --file tokens.json --apca --cvd --json`.
   - **Execution:** Test every text/surface pair (`text.primary` on `surface.canvas`/`elevated`, `text.muted` on `surface.canvas`, `on-primary` on `accent.primary`, `destructive` on `surface`). Require `>= 4.5:1` WCAG 2.1 AA (`>= 3.0:1` large/UI), `|Lc| >= 60` (`>= 45` large), and `>= 3.0:1` under Protanopia, Deuteranopia, and Tritanopia simulation. Pair every status color (`success`, `warning`, `error`) with a semantic Phosphor/Solar/Iconamoon icon and explicit text label.

3. **Author the 13-State Interaction Matrix & WCAG 2.2 AA Compliance**
   - **Input:** Component inventory (`button`, `input`, `select`, `card`, `table`, `dialog`, `toast`).
   - **Output:** Deterministic CSS/component state rules documented in `design-master.md` Section 5.
   - **Owner:** UI Engineer.
   - **Tool / Script:** `python3 scripts/core_search.py "focus keyboard aria" --domain web --json`.
   - **Execution:** Specify and implement all 13 states cleanly (`disabled > loading > active > focus-visible > hover > default` precedence):
     1. `default` — calm resting surface and explicit border.
     2. `hover` — perceptible shift (`200–300ms`), `cursor: pointer` on clickable controls.
     3. `focus-visible` — high-contrast `>= 2px` ring with `2px` offset (`WCAG 2.4.11` Focus Not Obscured & `2.4.13` Focus Appearance).
     4. `active` — tactile `scale(0.98)` or `translateY(1px)` press confirmation.
     5. `selected` — `aria-selected="true"` / `aria-pressed="true"` + distinct surface + border/check indicator.
     6. `visited` — distinguishable visited state on long-form navigation/docs links.
     7. `disabled` — prefer `aria-disabled="true"` with explanatory tooltip when actionability matters, else native `disabled`.
     8. `read-only` — non-editable borderless/tinted field preserving copyability (`readonly`).
     9. `loading / optimistic` — layout-matched skeleton reserving exact height/width (zero CLS) + `aria-busy="true"`.
     10. `empty` — helpful explanation + primary next action CTA.
     11. `partial / degraded` — non-blocking banner indicating stale/partial data + manual retry.
     12. `error` — inline `aria-invalid="true"` + `aria-describedby` message + `role="alert"` summary.
     13. `offline` — persistent status indicator + queued-mutation notice.
     Also satisfy WCAG 2.2 AA `3.3.7` (no redundant entry in multi-step flows) and `3.3.8` (accessible authentication supporting password managers/passkeys without cognitive puzzles).

4. **Implement Interruptible GPU-Only Motion Choreography**
   - **Input:** Motion specs from `design-master.md` Section 5.
   - **Output:** Compositor-safe CSS transitions and `@media (prefers-reduced-motion: reduce)` rules.
   - **Owner:** Motion / Frontend Engineer.
   - **Tool / Script:** `python3 scripts/check_anti_slop.py src/ --strict --json`.
   - **Execution:** Animate ONLY `transform` and `opacity` (never `width`, `height`, `top`, `left`, `margin`, or `padding`). Ensure every open/close or tab animation is interruptible mid-flight (clicking a second tab cancels the first transition cleanly via CSS transitions or Web Animations API `cancel()`). Use `IntersectionObserver` (disconnect after first reveal) or CSS `animation-timeline: view()`, and wrap all motion in `@media (prefers-reduced-motion: reduce)` collapsing transforms to instant state transitions.

5. **Complexity Budget & Deletion / Condensation Pass**
   - **Input:** `tokens.json` and component CSS files.
   - **Output:** Minimal, non-redundant token graph and compositor-clean stylesheet.
   - **Owner:** Design System Lead.
   - **Execution:** Prune unused primitive shade steps (`50–950` shades with zero semantic references), collapse duplicate component-level tokens that alias the exact same semantic token, delete `window.addEventListener('scroll')` animations, and confirm `validate_tokens.py --contrast` passes cleanly.

---

## 3. Reusable Artifact & Template

Tokens validate against [../templates/tokens-dtcg.schema.json](../templates/tokens-dtcg.schema.json) and color/state/motion specs lock into Sections 2 and 5 of [../templates/design-master.md](../templates/design-master.md).

| Token Tier / Field | Type | Contract & Validation Rule | Verified By |
|---|---|---|---|
| `primitive.*` | Group | Raw OKLCH / hex colors, spacing (`0..96px`), durations, cubic-beziers; never referenced directly in components | `tokens-dtcg.schema.json` |
| `semantic.*` | Group | Purpose roles (`surface.canvas`, `text.primary`, `accent.primary`, `border.subtle`, `status.*`) aliasing `primitive.*` | `validate_tokens.py` |
| `component.*` | Group | Scoped overrides (`button.primary-bg`, `input.border-focus`) aliasing `semantic.*` only | `validate_tokens.py` |
| `$value` / `$type` | Required | Every leaf token MUST define `$value` and resolve `$type` from the 13 supported DTCG types | `validate_tokens.py` |
| `{alias.path}` | Reference | Must resolve to an existing leaf and form a strict acyclic DAG (3-color DFS verified) | `validate_tokens.py` |
| `contrast_pairs` | Matrix | Every `text.*` / `on-*` pair passes WCAG 2.1 (`>= 4.5:1` / `3.0:1`), APCA (`|Lc| >= 60`), and CVD (`>= 3.0:1`) | `check_contrast.py` |
| `interaction_states_13` | Matrix | All 13 states (`default` through `offline`) + `prefers-reduced-motion` implemented | `check_anti_slop.py` |

---

## 4. Verification Checklist

- [ ] Palette authored in perceptual OKLCH with sRGB hex fallbacks, `60-30-10` allocation, single primary accent, and consistent neutral temperature.
- [ ] All foreground/background pairs pass WCAG 2.1 AA (`>= 4.5:1` text, `>= 3.0:1` large/UI) and APCA (`|Lc| >= 60` text, `>= 45` large).
- [ ] Color Vision Deficiency simulation (`--cvd`) confirms zero status or chart information relies on red/green hue alone.
- [ ] Design tokens follow 3-tier W3C DTCG (`primitive -> semantic -> component`) with zero missing `$value`, zero dangling aliases, and zero circular aliases.
- [ ] All 13 interaction and UI states (`default`, `hover`, `focus-visible`, `active`, `selected`, `visited`, `disabled`, `read-only`, `loading`, `empty`, `partial`, `error`, `offline`) are explicitly handled.
- [ ] Focus rings meet WCAG 2.4.11 (`not obscured`) and 2.4.13 (`>= 2px` offset contrast `>= 3.0:1`).
- [ ] Motion animates only GPU properties (`transform`, `opacity`), uses `cubic-bezier(0.22, 1, 0.36, 1)` (`>= 200ms` hover, exit `60–70%` of enter), and is mid-flight interruptible.
- [ ] Every animated CSS file includes `@media (prefers-reduced-motion: reduce)` removing motion safely.
- [ ] Dark mode elevates surfaces via calibrated luminance steps (`#09090B` -> `#18181B` -> `#27272A`) rather than heavy black shadows or `#0a0a0a` defaults.
- [ ] Multi-step forms comply with WCAG 2.2 `3.3.7` (no redundant re-entry) and authentication complies with `3.3.8` (password manager and passkey friendly).

### Complete 13-State Precedence Reference

| Priority | State | Required Visual & ARIA Signal |
|---|---|---|
| `1` | `disabled` | Reduced contrast (`|Lc| >= 30`), `cursor: not-allowed`, `aria-disabled="true"` + tooltip if actionable |
| `2` | `loading` | Exact layout-matched skeleton reserving dimensions (`aria-busy="true"`) |
| `3` | `error` | Destructive border + inline message + `aria-invalid="true"` + `role="alert"` |
| `4` | `active` | Tactile `scale(0.98)` or `translateY(1px)` press confirmation |
| `5` | `focus-visible` | `2px` high-contrast ring with `2px` offset (`>= 3.0:1` vs adjacent surface) |
| `6` | `selected` | Accent tint + crisp border + `aria-selected="true"` / `aria-pressed="true"` |
| `7` | `hover` | Subtle surface/border shift (`200–300ms` `--ease-out-expo`), `cursor: pointer` |
| `8` | `read-only` | Borderless/tinted non-editable field preserving text selection |
| `9` | `visited` | Distinct visited link tone on long-form documentation and indexes |
| `10` | `empty` / `partial` / `offline` | Actionable empty invitation, stale-data banner, or queued-sync notice |
| `11` | `default` | Calm baseline surface and `1px` structural hairline border |

---

## 5. Hard Quality Gate

| Verdict | Criteria |
|---|---|
| **PASS** | `validate_tokens.py --strict --contrast` exits `0`, `check_contrast.py --apca --cvd` exits `0` for all semantic pairs, all 13 UI states + reduced motion verified, and `check_anti_slop.py` exits `0`. |
| **CONCERNS** | Decorative non-critical chart label achieves WCAG AA (`>= 4.5:1`) while slightly below AAA (`7.0:1`), logged for next sprint. |
| **NOT ASSESSED** | CLI-only text output without color tokens or interactive DOM states. |
| **FAIL** | Missing `$value`, dangling or circular token alias, any text contrast `< 4.5:1` (`< 3.0:1` large/UI), hue-only error/status state, layout-thrashing animation (`width`/`top`/`left`), or missing `prefers-reduced-motion`. |

Executable gate check command:

```bash
python3 skills/ui-design-craft/scripts/validate_tokens.py tokens.json --strict --contrast --json
python3 skills/ui-design-craft/scripts/check_contrast.py --file tokens.json --apca --cvd --json
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Unverified Hex Guessing / Low-Contrast Muted Text** | Leaves `#777777` on `#FFFFFF` (`4.48:1`) failing WCAG AA right below the `4.5:1` boundary | Hardcoded gray hexes without contrast telemetry | Author OKLCH ramps and gate every pair with `check_contrast.py --apca --cvd` |
| **Hue-Only Status Indicators** | Unreadable to `~8%` of male users with red-green CVD (Protanopia/Deuteranopia) | Green/red dot without icon, text label, or stroke pattern | Pair every status color with a Phosphor/Solar/Iconamoon icon and explicit label |
| **Animating Layout Properties (`width`/`height`/`top`/`left`)** | Forces browser layout recalculation every frame, dropping below `60fps` | `@keyframes` or `transition` mutating box-model dimensions | Animate GPU compositor properties (`transform`, `opacity`) exclusively |
| **Unthrottled `scroll` Event Listeners** | Stutters main thread and causes jank on mobile browsers | `window.addEventListener('scroll', ...)` mutating styles | Use `IntersectionObserver` (once-only) or CSS `animation-timeline: view()` |
| **Missing `prefers-reduced-motion` Fallback** | Triggers vestibular discomfort for motion-sensitive users and fails `SLOP-A11Y-01` | CSS files with `transition`/`animation` lacking `prefers-reduced-motion` | Include `@media (prefers-reduced-motion: reduce)` disabling transforms |
| **Runtime CSS-in-JS Theme Provider Bloat** | Serializes styles at runtime, inflates JS bundle, and forces full-tree re-renders | Heavy runtime `ThemeProvider` JS wrapping static token sheets | Emit static W3C DTCG JSON -> CSS custom properties toggled via `data-theme` |
