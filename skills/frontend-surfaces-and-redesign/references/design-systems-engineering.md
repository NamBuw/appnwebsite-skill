# Design Systems Engineering

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This module governs multi-tier W3C DTCG design token architecture, accessible headless and compound component APIs, cross-mode theming (light, dark, and spatial density), component-level WCAG 2.2 documentation, visual regression testing, SemVer deprecation governance, and Radical Simplicity ("Least Code, Highest Craft").

---

## 1. Decision Framework

### 1.1 Three-Tier W3C DTCG Token Architecture

Separate raw design values from intent and component bindings using strict three-tier inheritance (`Primitive -> Semantic -> Component`):

| Token Tier | Naming Pattern | Allowed Values | Edit Trigger & Governance Rule |
|---|---|---|---|
| **Tier 1: Primitive** | `--{category}-{scale}` (e.g., `--color-cobalt-600`, `--space-4`, `--radius-lg`) | Raw OKLCH/hex colors, `0..96px` spacing steps, type scale, radii, z-index steps | Edit ONLY when expanding foundational brand palette or scale; **never reference directly in feature CSS/JSX** |
| **Tier 2: Semantic** | `--{role}-{surface\|text\|border}-{emphasis}-{state}` (e.g., `--color-bg-surface`, `--color-fg-muted`) | References Tier 1 Primitives exclusively (`{color.cobalt.600}`) | **Primary theming layer**: `.dark` mode, high-contrast mode, and density overrides swap ONLY Tier 2 aliases |
| **Tier 3: Component** | `--{component}-{slot}-{property}-{state}` (e.g., `--btn-primary-bg-hover`, `--card-padding`) | References Tier 2 Semantic tokens (`{color.action.primary}`) | Bounded overrides (`<= 4` overrides per component); avoid creating Tier 3 tokens unless a component diverges across surfaces |

### 1.2 Component API Pattern Selection Matrix

Choose the minimal API abstraction level that preserves accessibility, composability, and prop clarity:

| Component Complexity | Preferred Pattern | Implementation Stack | Prop-Explosion Ceiling |
|---|---|---|---|
| **Atomic Trigger / Display** (`Button`, `Badge`, `Input`, `Tag`) | Native HTML element + `cva` variants + `cn()` | `<button>`, `<input>`, `class-variance-authority`, `clsx` + `tailwind-merge` | `<= 6` style/variant props (`variant`, `size`, `disabled`, `loading`) |
| **Stateful Overlay / Navigation** (`Dialog`, `Popover`, `Tabs`, `Command`, `Select`) | Headless Accessible Primitive + Styled Skin | Radix UI, React Aria, or Base UI wrapping `<dialog>` / ARIA patterns | Delegate open/close, focus trap, and keyboard traversal to primitive |
| **Multi-Region Container** (`Card`, `Sheet`, `Alert`, `DataTable`) | Compound / Slot Composition (`asChild`) | `<Card><CardHeader><CardTitle><CardContent><CardFooter>` | **Forbid monolith props** (`title`, `subtitle`, `leftIcon`, `footerCta`) on 1 tag |
| **Native Mobile Primitives** | Platform-Native Components + Shared Token JSON | SwiftUI `View` / Compose `Modifier` / Expo `NativeTabs` | Compile shared `tokens.json` into Swift/Kotlin/TS constants |

### 1.3 Simplest High-Craft Option

**Anti-Overengineering Self-Interrogation ("Least Code, Highest Craft")**: Before installing runtime CSS-in-JS theme providers (`styled-components`, `Emotion`), building a custom multi-package workspace monorepo, or hand-rolling focus traps, evaluate the simplest high-craft baseline:
- One W3C DTCG `tokens.json` file compiled once at build time to CSS custom properties and Tailwind `@theme`.
- Native HTML (`<button>`, `<dialog>`, `<details>`) + thin Radix/React Aria headless primitives for composite menus/comboboxes.
- Compound subcomponents with `cva` variants (`<= 6` style props) and `asChild` slot forwarding.
- Spatial density (`compact 0.85x`, `comfortable 1.0x`, `spacious 1.2x`) and `.dark` theme handled purely via Tier 2 CSS variable swaps.

Build-time CSS variables deliver zero-JS runtime theming, instant `.dark` switching without hydration flashes, and deterministic token linting.

---

## 2. Step-by-Step Workflow

### Token Economy Protocol
- Validate `tokens.json` schema and WCAG contrast pairs via deterministic Python scripts (`validate_tokens.py`, `check_contrast.py`) instead of inspecting giant JSON trees in LLM context.
- Generate CSS/Tailwind/mobile constants from one source file rather than maintaining duplicated platform theme files by hand.

1. **Author 3-Tier W3C DTCG Tokens (`tokens.json`) (`Owner: Design Systems Lead`)**
   - **Inputs**: `design-master.md` (from `ui-design-craft`), color/typography scales, dark/light requirements.
   - **Action**:
     - Structure `tokens.json` using W3C DTCG `$value` and `$type` fields (`color`, `dimension`, `fontFamily`, `fontWeight`, `duration`, `cubicBezier`).
     - Lock Cross-Skill Conflict defaults at Tier 1: exclude `Inter`, `Roboto`, `Arial`, `Open Sans`, and `Helvetica` from font stacks (`Geist`, `Manrope`, `Poppins`, or bespoke approved pairings only); standardize icon stroke weight metadata (`1.5px` / `2px`) around `Phosphor`, `Solar`, or `Iconamoon` (`Lucide`, `Feather`, `Heroicons`, `Material Icons`, `Material Symbols` banned on web).
     - Define Tier 2 semantic overrides for `.dark` (preserving background-tinted shadows and light-source consistency) and spatial density modes (`compact: 0.85x`, `comfortable: 1.0x`, `spacious: 1.2x` spacing/control-height tokens).
   - **Outputs**: Validated `tokens.json` single source of truth.

2. **Compile Targets & Lint Zero Hardcoded Values (`Owner: Frontend Tooling Engineer`)**
   - **Inputs**: `tokens.json`, build pipeline.
   - **Action**:
     - Compile `tokens.json` (via Style Dictionary or a `< 80`-line deterministic Python/Node build script) into `tokens.css` (`:root` + `.dark` + `[data-density="compact"]`), Tailwind `@theme` mappings, and optional native Swift/Kotlin/TS constants.
     - Enforce a lint rule forbidding raw `#hex`, `rgb()`, or arbitrary `px` spacing/radii inside component stylesheets (`src/components/**`). Apply nested radius math (`inner = outer - gap` when `gap < 32px` and result `> 2px`) in semantic component tokens.
   - **Outputs**: Generated token outputs + zero-raw-hex lint check.

3. **Build Headless & Compound Component Kit (`Owner: Design Systems Engineer`)**
   - **Inputs**: Generated CSS tokens, component inventory, state requirements.
   - **Action**:
     - Author every interactive component with explicit **6-state priority order**: `disabled > loading > active (scale(0.98)) > focus-visible (2px ring + 2px offset) > hover > default`.
     - Use `cva` for bounded variants (`<= 4` variants per dimension, e.g., `primary | secondary | ghost | destructive`) and compound subcomponents with `asChild` slot forwarding so consumers compose icons, badges, or links cleanly without prop explosion.
     - Standardize table primitives with strict column alignment (`Text` left, `Numbers` right + `tabular-nums`, `Status` center, `Actions` right) and `40 / 48 / 56px` row heights.
   - **Outputs**: Composable, token-bound UI kit.

4. **Publish Component-Level WCAG 2.2 Accessibility Docs (`Owner: Accessibility / DS Engineer`)**
   - **Inputs**: Component primitives, interactive state machine.
   - **Action**: Document and enforce per component:
     - *Semantic Element & ARIA*: Native `<button>`/`<dialog>` first; exact `aria-disabled`, `aria-busy`, `aria-invalid`, `aria-describedby`, and `role="alert"` wiring.
     - *Full Keyboard Map*: `Tab`/`Shift+Tab`, `Enter`/`Space` activation, `Escape` dismissal restoring focus to trigger, and roving `ArrowUp`/`ArrowDown`/`Home`/`End` inside composite widgets (`Tabs`, `Menu`, `Command`).
     - *WCAG 2.2 Quantitative Criteria*: `4.5:1` text contrast, `3:1` UI border/icon/focus contrast, `2.4.11 Focus Not Obscured` (`scroll-margin-top` under sticky headers), and `2.5.8 Target Size >= 24x24px` minimum (`44px` comfortable default).
   - **Outputs**: Co-located component accessibility contracts.

### 2.4.1 Spatial Density & Icon Token Multipliers

| Mode / Element | Scale / Value | CSS Custom Property | Enforcement Rule |
|---|---|---|---|
| **Compact Density** | `0.85x` spacing / `40px` table row | `[data-density="compact"]` | Dense ops/telemetry tables and IDE rails |
| **Comfortable Density** | `1.0x` spacing / `48px` table row | `:root` default | Standard SaaS forms, cards, and workspaces |
| **Spacious Density** | `1.2x` spacing / `56px` table row | `[data-density="spacious"]` | Consumer onboarding and editorial flows |
| **Icon Standardization** | `16px` inline, `20px` UI, `24px` nav (`1.5px`/`2px` stroke) | `--icon-stroke-width` | `Phosphor`, `Solar`, or `Iconamoon` only on web |

5. **Automate Storybook Matrix, Visual Regression & SemVer Deprecation (`Owner: DS / QA Lead`)**
   - **Inputs**: Component stories, CI visual pipeline.
   - **Action**:
     - Render matrix stories covering **all variants x 6 states x light/dark x compact/comfortable x `320px`/desktop**; run automated `axe-core` and visual snapshot diffing on every PR.
     - Enforce strict SemVer governance: breaking token or prop changes require `@deprecated` JSDoc + dev-only console warning + automated codemod/alias overlapping for **at least `1` minor/major release cycle** before deletion.
   - **Outputs**: CI-verified Storybook & SemVer deprecation policy.

### 2.5.1 SemVer Token & Prop Deprecation Contract

```ts
/** @deprecated Use `tone="destructive"` instead; removal scheduled in v2.0.0. */
if (process.env.NODE_ENV !== "production" && props.danger) {
  console.warn("[DS-DEPRECATION] `danger` prop is deprecated; migrate to `tone=\"destructive\"`.");
}
```

6. **Execute Deletion & Condensation Pass (`Owner: Design Systems Lead`)**
   - **Inputs**: Component library source, CSS bundle, token usage report.
   - **Action**: Delete unused Tier 3 component tokens, single-use prop aliases, redundant CSS overrides, and wrapper components duplicating native HTML (`<details>`, `<dialog>`). Verify zero hardcoded colors/spacings remain and re-run full validation.
   - **Outputs**: Lean, high-craft `design-system-kit`.

### 2.7 Minimal W3C DTCG Token & Six-State CSS Reference

```json
{
  "color": {
    "primitive": {
      "cobalt": { "600": { "$value": "oklch(0.55 0.21 260)", "$type": "color" } },
      "zinc": { "950": { "$value": "#09090B", "$type": "color" } }
    },
    "semantic": {
      "action-primary": { "$value": "{color.primitive.cobalt.600}", "$type": "color" },
      "bg-canvas": { "$value": "{color.primitive.zinc.950}", "$type": "color" }
    }
  }
}
```

```css
/* Strict 6-state priority: disabled > loading > active > focus-visible > hover > default */
.ds-btn { transition: transform 150ms cubic-bezier(0.22, 1, 0.36, 1); }
@media (hover: hover) and (pointer: fine) {
  .ds-btn:hover:not(:disabled, [aria-busy="true"]) { filter: brightness(1.06); }
}
.ds-btn:focus-visible { outline: 2px solid var(--color-ring-focus); outline-offset: 2px; }
.ds-btn:active:not(:disabled) { transform: scale(0.98); }
.ds-btn[aria-busy="true"] { pointer-events: none; opacity: 0.75; }
.ds-btn:disabled { pointer-events: none; opacity: 0.45; }
```

---

## 3. Reusable Artifact & Template

Design system compliance and token audits attach to the token/component compliance section of [UI Redesign Audit & Preservation Template](../templates/ui-redesign-audit.md) and maintain a **Component Specification & Token Matrix**:

| Matrix Column | Required Specification | Example Entry |
|---|---|---|
| `component_name` | Exported primitive & compound subcomponents | `Dialog` (`DialogTrigger`, `DialogContent`, `DialogHeader`, `DialogFooter`) |
| `primitives_and_semantic_tokens` | Exact Tier 2/3 CSS custom properties bound | `--color-bg-surface`, `--color-border-subtle`, `--color-ring-focus`, `--radius-card` |
| `bounded_variants` | Allowed `cva` axes (`<= 4` per axis, `<= 6` props total) | `size: sm \| md \| lg`, `tone: default \| destructive` |
| `six_state_contract` | Priority rules (`disabled > loading > active > focus > hover > default`) | `focus-visible`: `2px solid var(--color-ring-focus)` + `2px` offset |
| `wcag_2_2_aria_keyboard` | Native/ARIA role, keyboard bindings, `2.4.11` & `2.5.8` verification | `role="dialog"`, `Esc` closes & restores focus, `44px` close button |
| `semver_deprecation_status` | Version introduced, alias/codemod status | `v1.2.0 ACTIVE` (replaces legacy `Modal` deprecated with dev warning) |

---

## 4. Verification Checklist

- [ ] `tokens.json` strictly separates Tier 1 Primitives, Tier 2 Semantic aliases, and bounded Tier 3 Component tokens using W3C DTCG `$value`/`$type` fields.
- [ ] Zero raw `#hex`, `rgb()`, or arbitrary `px` values appear inside component stylesheets (`src/components/**`).
- [ ] `.dark` theme and `compact`/`comfortable`/`spacious` density modes swap cleanly by overriding Tier 2 semantic variables alone (`0` component code forks).
- [ ] Font and icon tokens exclude `Inter`, `Roboto`, `Arial`, `Open Sans`, `Helvetica`, `Lucide`, `Feather`, `Heroicons`, `Material Icons`, and `Material Symbols`, using `Phosphor`, `Solar`, or `Iconamoon`.
- [ ] Components use compound/slot (`asChild`) composition with `<= 6` style props and zero monolith prop-explosion wrappers.
- [ ] Every interactive control implements `disabled > loading > active > focus-visible > hover > default` priority with a `2px` focus ring and `2px` offset.
- [ ] Component documentation specifies exact WCAG 2.2 keyboard bindings, ARIA attributes, `4.5:1`/`3:1` contrast, and `>= 24x24px` (`44px` target) hit areas.
- [ ] Automated Storybook/Playwright `axe-core` tests pass across light, dark, and `320px` viewports, and breaking APIs follow the SemVer deprecation policy.

---

## 5. Hard Quality Gate

- **`PASS`**:
  - `validate_tokens.py` and `check_contrast.py` (from `ui-design-craft`) exit `0` across light and `.dark` semantic token sets with zero WCAG AA/3:1 violations.
  - Zero raw `#hex` literals in component code, `<= 6` style props per component, `0` `axe-core` story failures, and deletion pass verified with clean build/test receipts.
- **`FAIL`**:
  - Flat un-tiered tokens, runtime CSS-in-JS theme provider overhead where CSS variables suffice, prop-explosion monoliths (`> 6` layout/style props), or broken focus traps/missing `focus-visible` rings.
  - Undocumented breaking token renames or components failing `320px` / `.dark` visual regression.

```bash
# Token validation, contrast verification, and Storybook/component accessibility gate
python3 skills/ui-design-craft/scripts/validate_tokens.py --file tokens.json --strict
python3 skills/ui-design-craft/scripts/check_contrast.py --file tokens.json --level AA --apca --cvd --json
npx test-storybook --url http://127.0.0.1:6006
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Flat Hardcoded Token Soup** | Forces manual find-and-replace for dark mode and lets components leak inconsistent grays | Components importing `--gray-800` or raw `#18181B` directly | Enforce 3-tier `Primitive -> Semantic -> Component` inheritance; swap `.dark` at Tier 2 |
| **Prop-Explosion Monolith Components** | Creates fragile 20-prop APIs (`leftIcon`, `subtitle`, `badgeText`, `footerAlign`) that resist composition | Component interfaces exceeding `6` visual/slot props | Switch to Compound subcomponents + Radix `asChild` slot forwarding |
| **Runtime CSS-in-JS Theme Bloat** | Injects style recalculation cost on every render and breaks zero-JS RSC streaming | `ThemeProvider` context re-rendering trees for static CSS values | Compile `tokens.json` to static CSS custom properties + Tailwind `@theme` |
| **Div-Soup Custom Overlays** | Lacks keyboard Escape, screen-reader announcements, inert backdrop, and focus restoration | `<div onClick={...}>` acting as dropdown, modal, or tab button | Use native `<button>`/`<dialog>`/`<details>` or headless Radix/React Aria primitives |
| **Unannounced Breaking Token Renames** | Silently breaks downstream product screens during design-system upgrades | Removing/renaming `--color-brand` without deprecation overlap | Follow SemVer: keep alias + `@deprecated` JSDoc + dev warning + codemod for `>= 1` cycle |
| **Light-Only Primitives & Mixed Shadows** | Produces harsh white glare or invisible borders when `.dark` mode is enabled | Hardcoded `box-shadow: rgba(0,0,0,0.1)` and missing `.dark` surface tokens | Derive `.dark` surfaces and background-tinted shadows strictly via Tier 2 aliases |
