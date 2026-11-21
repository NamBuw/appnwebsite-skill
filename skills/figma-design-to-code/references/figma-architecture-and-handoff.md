# Figma Architecture, Variables, Components & Handoff

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This module governs how Figma files, variables, Auto Layout frames, component sets, Dev Mode annotations, asset exports, and Code Connect mappings are structured and audited prior to Phase 3B UI implementation.
It unifies local Figma engineering conventions with **Least Code, Highest Craft** simplicity and **Maximum Signal, Minimum Tokens** discipline.

---

## 1. Decision Framework

### 1.1 Variable & Collection Architecture Tier Selector

Match collection complexity strictly to token count, theme requirements, and Figma plan mode limits (Starter = `1` mode/collection, Professional = `4` modes/collection, Organization/Enterprise = `40` modes/collection):

| Architecture Tier | Token & Platform Threshold | Collection Topology | Mode Strategy | When to Reject Higher Tiers |
|---|---|---|---|---|
| **Tier 1 — Simple (Simplest High-Craft Option)** | `< 50` tokens, `1` product surface, `1–2` themes | Single `Tokens` collection + Text/Effect styles | `Light` and `Dark` (or `Value` only if light-only) | Default for MVPs, marketing sites, and small apps; avoids premature alias indirection |
| **Tier 2 — Standard** | `50–200` tokens, reusable product UI system | `Primitives` -> `Color`, `Spacing`, `Typography` semantic collections | `Primitives` (`Value`), `Color` (`Light` / `Dark` aliases), `Spacing` & `Typography` (`Value`) | Reject component-tier collections unless `>= 3` overrides per component justify aliasing |
| **Tier 3 — Multi-Brand / Density** | `200+` tokens, multi-brand or strict contrast/density NFRs | `Primitives` + `Semantic` + `Density/Brand` extended collections | `Light`, `Dark`, `High Contrast`, `Brand A/B`, `Compact/Comfortable` | Requires Org/Enterprise plan (`> 4` modes) and verified multi-brand NFRs |

### 1.2 Component Architecture Selector: Variants vs. Properties vs. Slots

Cap every `ComponentSetNode` at **`<= 30` variant combinations**.
Reserve `VARIANT` axes for permutations that alter layout geometry or structural surface tokens, and delegate labels, icons, toggles, and freeform children to native Component Properties:

| Modeling Mechanism | Use When | Hard Cap / Constraint | Maps in Production Code To |
|---|---|---|---|
| `VARIANT` | Style, size, or state alters padding, border, height, or surface tokens | `<= 30` total product (`Axes` multiplied); split by `Style` or `.Building Blocks/` if `> 30` | Enum props (`variant`, `size`) + CSS `:hover`/`:focus-visible`/`:active` |
| `TEXT` | Label, helper text, placeholder, or badge copy varies per instance | Override via `setProperties()` on instances, not raw `node.characters` | `children` or string props (`label`, `placeholder`) |
| `BOOLEAN` | Optional leading/trailing icons, dividers, or captions toggle visibility | Wire `visible` through `componentPropertyReferences` | Conditional rendering (or inferred from prop presence) |
| `INSTANCE_SWAP` | Swappable fixed icon, avatar, or status indicator in a constrained slot | Attach `preferredValues`; map in `.figma.ts` via `getInstanceSwap()` | Typed component/element prop (`leadingIcon?: ReactNode`) |
| `SLOT` | Arbitrary freeform child composition (card body, modal footer, toolbar) | Create via `createSlot()` / `slotContentId`; never `GRID` inside slot | Composition `children` or named slots (`footer`) via `getSlot()` |

Model web pseudo-states (`:hover`, `:focus-visible`, `:active`, `:disabled`) only on reusable interactive primitives (`Button`, `Input`, `Checkbox`), never across duplicated page screens.

### 1.3 Code Connect Strategy Tier Selector

| Tier | Plan & Scale Prerequisite | Authoring Mechanism | Output Artifact |
|---|---|---|---|
| **Tier 0 — Skip** | Starter/Professional plan OR `< 10` custom components | Exact component naming + [Figma Component Spec](../templates/figma-component-spec.md) | Markdown spec only (zero CLI/build overhead) |
| **Tier 1 — Simple Map (Default)** | Org/Enterprise plan + published library components | MCP `get_code_connect_suggestions` -> `send_code_connect_mappings` (`source`, `componentName`, `label`) | Live MCP mapping + `WEB` `var(--...)` syntax |
| **Tier 2 — Parserless `.figma.ts`** | Org/Enterprise + complex prop transforms, `INSTANCE_SWAP`, or `SLOT` | `ComponentName.figma.ts` exporting `` figma.code`...` `` (`isParserless: true`, `nestable: true`) | `*.figma.ts` template (reject `.figma.tsx` unless legacy) |
| **Tier 3 — Legacy `.figma.tsx`** | Existing brownfield repo already enforcing parser-based `figma.connect()` | Leave existing `.figma.tsx` untouched; add `.figma.ts` alongside when migrating | Preserved legacy mapping |

### 1.4 Anti-Overengineering Self-Interrogation ("Least Code, Highest Craft") & Token Economy

Answer four questions before building Figma libraries or Code Connect files:
1. **Simplicity Q1**: Can `BOOLEAN` + `INSTANCE_SWAP` + `SLOT` replace a `36–60` variant explosion?
2. **Simplicity Q2**: Does a Tier 1 single collection or Tier 2 semantic split solve every active theme without component-tier token collections?
3. **Simplicity Q3**: Are we writing `.figma.ts` templates for unpublished drafts or Free/Pro plans where Code Connect cannot publish?
4. **Simplicity Q4**: Can nested Figma `Frame` wrappers be flattened now so downstream codegen produces clean semantic HTML?

**Token Economy**: Read ONLY this module when auditing or structuring Figma files.
When automating Figma via `use_figma`, run read-only discovery once, then fan out multi-page reads or writes in parallel (`1` `setCurrentPageAsync` per call in one turn) instead of looping across pages inside a single script.

---

## 2. Step-by-Step Workflow

1. **Step 1 — File, Page & Breakpoint Taxonomy Audit** *(Owner: Design Systems Engineer; Inputs: Figma URL / fileKey; Tools: `get_metadata`, `search_design_system`, `use_figma` read-only)*:
   - Parse `fileKey` (or `branchKey` under `/branch/:branchKey/`) from `figma.com/design/:fileKey/:name?node-id=X-Y`.
   - Convert hyphenated node IDs (`42-15`) to colon format (`42:15`) for Plugin API, REST API, and Code Connect calls.
   - Verify canonical page order with `---` separators:
     - `Cover` -> `---` -> `Foundations` / `Icons` -> `---` -> `Components (Atoms -> Molecules -> Organisms)` -> `---` -> `Screens (Desktop 1440 / Tablet 768 / Mobile 390)` -> `Utilities`.
   - Enforce layout grids without duplicating identical screens across minor breakpoints:
     - Desktop `1440px`: `12` columns, `72px` margins, `24px` gutter.
     - Tablet `768px`: `8` columns, `32px` margins, `20px` gutter.
     - Mobile `390px`: `4` columns, `16px` margins, `16px` gutter.
   - **Remote Library Variable Trap**: `figma.variables.getLocalVariableCollectionsAsync()` misses linked team-library variables; always pair it with `search_design_system(includeVariables: true)`.
   - **Font Conflict Rule**: Read `design-master.md` and codebase CSS fonts first. `Inter` is preloaded in Figma sandboxes and appears on unstyled text; never carry `Inter`, `Roboto`, `Arial`, `Open Sans`, or `Helvetica` into new specs unless an approved brownfield ADR overrides the ban.

2. **Step 2 — Variable Creation, Aliasing, 22 Scopes & Code Syntax Discipline** *(Inputs: `tokens.json` / brand palette; Outputs: scoped variables + styles)*:
   - Use lowercase slash-separated names (`color/bg/primary`, `spacing/md`, `radius/md`, `font/size/body`). Keep CSS/platform prefixes (`--ds-`, `--md-sys-`) inside `codeSyntax`, not the Figma variable name.
   - Bind every semantic variable to its primitive via `figma.variables.createVariableAlias(primitiveVar)` (`resolvedType` must match); never duplicate raw hex values inside semantic collections.
   - Assign explicit scopes from the 22-role contract below and **ban `ALL_SCOPES`**:

| Variable Role | Required `scopes` Array | `resolvedType` |
|---|---|---|
| Raw color primitives | `[]` (hidden from pickers) | `COLOR` |
| Semi-transparent shadow/overlay primitives | `["EFFECT_COLOR"]` | `COLOR` |
| Background / surface fills | `["FRAME_FILL", "SHAPE_FILL"]` | `COLOR` |
| Text fill | `["TEXT_FILL"]` | `COLOR` |
| Icon / vector fill + stroke | `["SHAPE_FILL", "STROKE_COLOR"]` | `COLOR` |
| Border / divider stroke | `["STROKE_COLOR"]` | `COLOR` |
| Shared background + border | `["FRAME_FILL", "SHAPE_FILL", "STROKE_COLOR"]` | `COLOR` |
| Shadow / elevation tint | `["EFFECT_COLOR"]` | `COLOR` |
| Gap spacing & container padding | `["GAP"]` | `FLOAT` |
| Corner radius | `["CORNER_RADIUS"]` | `FLOAT` |
| Width / height dimensions | `["WIDTH_HEIGHT"]` | `FLOAT` |
| Font size / line height / letter spacing / weight | `["FONT_SIZE"]`, `["LINE_HEIGHT"]`, `["LETTER_SPACING"]`, `["FONT_WEIGHT"]` | `FLOAT` |
| Stroke width / effect blur / opacity | `["STROKE_FLOAT"]`, `["EFFECT_FLOAT"]`, `["OPACITY"]` | `FLOAT` |
| Font family / font style name | `["FONT_FAMILY"]`, `["FONT_STYLE"]` | `STRING` |
| Feature/state toggle | *(scopes unsupported on BOOLEAN)* | `BOOLEAN` |

   - Note that `ALL_FILLS` is mutually exclusive with individual fill scopes (`FRAME_FILL`, `SHAPE_FILL`, `TEXT_FILL`); prefer individual scopes for precision.
   - Set `setVariableCodeSyntax` on every semantic variable:
     - `WEB`: MUST wrap in `var(...)` — bare `--color-bg-primary` fails in CSS output.
     - `ANDROID`: camelCase (`colorBgPrimary`).
     - `iOS`: dot notation (`Color.bgPrimary`).
   - Author composite Effect Styles (`Shadow/Subtle`, `Elevation/1..5` with umbra + penumbra) and Text Styles (`Display/Hero`, `Heading/H1..H4`, `Body/Lg..Sm`, `Label/*`, `Code/*`) bound to variables where supported.

```javascript
// Canonical variable aliasing, explicit scopes, and WEB var() syntax in use_figma
const semantic = figma.variables.createVariable("color/bg/primary", colorCollection, "COLOR");
semantic.scopes = ["FRAME_FILL", "SHAPE_FILL"]; // Never ALL_SCOPES
semantic.setValueForMode(lightModeId, figma.variables.createVariableAlias(whitePrimitive));
semantic.setVariableCodeSyntax("WEB", "var(--color-bg-primary)");
semantic.setVariableCodeSyntax("iOS", "Color.bgPrimary");
semantic.setVariableCodeSyntax("ANDROID", "colorBgPrimary");
```

3. **Step 3 — Auto Layout Mechanics & Constraint Invariants** *(Inputs: component frames; Outputs: responsive Auto Layout trees)*:
   - Configure `layoutMode` (`HORIZONTAL` | `VERTICAL` | `WRAP`), frame `primaryAxisSizingMode` / `counterAxisSizingMode` (`FIXED` | `AUTO`), child `layoutSizingHorizontal` / `layoutSizingVertical` (`FIXED` | `HUG` | `FILL` AFTER `appendChild`), `itemSpacing` / `counterAxisSpacing` (or `primaryAxisAlignItems = 'SPACE_BETWEEN'`), `padding*` bound to `GAP` variables, and `minWidth`/`maxWidth`/`minHeight`/`maxHeight`.
   - Use `layoutPositioning = 'ABSOLUTE'` + `constraints` (`MIN`, `CENTER`, `MAX`, `STRETCH`, `SCALE`) strictly for floating badges, close buttons, and overlays inside an Auto Layout parent.
   - **Prevent Three Classic Layout Bugs**:
     - Never mix `*AxisSizingMode` (`FIXED | AUTO`) with `layoutSizing*` (`FIXED | HUG | FILL`).
     - Never nest a `FILL` child inside a `HUG` parent on the same axis without `minWidth`, which collapses containers to `0px`.
     - Never leave multi-line `TEXT` nodes on `textAutoResize = 'WIDTH_AND_HEIGHT'` inside `FILL` containers; set `textAutoResize = 'HEIGHT'` with `layoutSizingHorizontal = 'FILL'` to prevent 1-character vertical thread wrapping.

4. **Step 4 — Component Build Order, Properties & `use_figma` Plugin Hygiene** *(Inputs: scoped variables + Auto Layout primitives; Outputs: published ComponentSets)*:
   - Build strictly bottom-up: Tier 0 Atoms (`Icon`, `Avatar`, `Badge`) -> Tier 1 Molecules (`Button`, `Input`, `Toggle`) -> Tier 2 Organisms (`Card`, `Dialog`, `Nav`).
   - Clone one variable-bound base -> call `figma.combineAsVariants(variants, page)` -> arrange in a clean matrix (`State` columns, `Size x Variant` rows) -> size container with `resizeWithoutConstraints`.
   - Attach `addComponentProperty` (`TEXT`, `BOOLEAN`, `INSTANCE_SWAP`, `SLOT`) wired via `componentPropertyReferences`; use `createSlot()` rather than manual `slotContentId`.
   - **Mandatory `use_figma` Plugin API Rules**:
     - Write plain top-level `await` + `return { createdNodeIds, mutatedNodeIds }` (never `figma.closePlugin()`, `figma.notify()`, or `console.log()`).
     - Use `0–1` RGB floats; clone read-only `fills`/`strokes`; reassign the paint returned by `setBoundVariableForPaint(paint, 'color', varObj)`.
     - Load current fonts via `getStyledTextSegments(['fontName'])` + `await figma.loadFontAsync(font)` before any text or text-variable mutation.
     - Narrow `componentPropertyDefinitions` owner first: promote any variant `COMPONENT` inside a `COMPONENT_SET` to `node.parent` (optional chaining `?.` still throws).
     - Call `await figma.setCurrentPageAsync(page)` at most once per call; fan multi-page reads across parallel tool calls in one turn; never parallelize conflicting writes; stop and inspect errors on atomic script failures.

5. **Step 5 — Dev Mode Handoff, Annotations, Asset Export & Code Connect** *(Inputs: ComponentSets & Screens; Outputs: Dev-ready annotations, local assets, Code Connect mappings)*:
   - Mark verified frames `Ready for Dev` and add Dev Mode annotations for interactive semantics (`<button>` vs `<a>`, `Escape` dismiss, focus order, `aria-live`, truncation, and responsive `clamp()` bounds).
   - **Asset Export Discipline**:
     - Icons: `16/20/24px` integer pixel grid, flattened paths, `viewBox`, `currentColor`, clean SVGO output without baked `t=0` `opacity="0"`.
     - Rasters/Brand Art: Export `@1x`/`@2x` (`@3x` native) WebP/AVIF + PNG fallback with explicit `width`/`height`; never approximate photos or brand logos with hand-drawn inline SVGs.
   - **Code Connect Execution**:
     - Confirm Org/Enterprise plan, published library component, and `node-id`.
     - Run `get_code_connect_suggestions(fileKey, nodeId, excludeMappingPrompt: true)` -> resolve `mainComponentNodeId`.
     - Call `get_context_for_code_connect` -> inspect target code `Props`.
     - For **Tier 1**, call `send_code_connect_mappings` with a valid `label` enum (`React`, `Web Components`, `Vue`, `Svelte`, `Storybook`, `Javascript`, `Swift UIKit`, `Objective-C UIKit`, `SwiftUI`, `Compose`, `Java`, `Kotlin`, `Android XML Layout`, `Flutter`, `Markdown`).
     - For **Tier 2**, create `ComponentName.figma.ts` using parserless `` figma.code`...` `` (`isParserless: true`):
       - Map every `VARIANT` option in `getEnum` so none resolves to `undefined`.
       - Guard `INSTANCE_SWAP` with `if (swap && swap.type === 'INSTANCE')` before `executeTemplate()`.
       - Interpolate `getSlot()` directly as `${content}` without `.map().join()`.
       - Set `nestable: true` in both `metadata` and `templateDataJson` for inline nested components.
       - Omit Figma properties that lack a matching prop in the code component interface.

```ts
// Tier 2 parserless Code Connect template (ComponentName.figma.ts — never .figma.tsx)
import figma from "figma";
const instance = figma.selectedInstance;
const variant = instance.getEnum("Variant", { Primary: "primary", Secondary: "secondary" });
const icon = instance.getInstanceSwap("Icon");
const iconCode = icon && icon.type === "INSTANCE" ? icon.executeTemplate().example : undefined;
const slotContent = instance.getSlot("Content");

export default {
  id: "action-card",
  example: figma.code`<ActionCard variant="${variant}" icon={${iconCode}}>${slotContent}</ActionCard>`,
  metadata: { nestable: true },
};
```

6. **Step 6 — Complexity Budget & Pre-Handoff Condensation Pass** *(Inputs: draft library + spec; Outputs: lean handoff)*:
   - Delete scratch frames, detached copies, and unused variables; collapse nested Figma frame groups (`Frame > Frame > Text` -> single padded Auto Layout frame).
   - Complete `templates/figma-component-spec.md` with zero `[...]` stubs remaining.

---

## 3. Reusable Artifact & Template

Instantiate [Figma Component & Handoff Specification](../templates/figma-component-spec.md) for every shared component before Phase 3B implementation.

| Spec Section | Required Fields & Contract |
|---|---|
| **Metadata** | `Component Name`, `Figma File Key & URL`, colon `Node ID`, `Library Publish Status`, `Code Connect Tier (0-3)`, `Target Code Path`, `Owner / Last Verified` |
| **1. Variant Matrix** | Axis list, per-axis counts, code prop/pseudo-state mapping, explicit product `<= 30` (or split/`.Building Blocks/` rationale) |
| **2. Component Properties** | Exact-case property name, type (`TEXT`/`BOOLEAN`/`INSTANCE_SWAP`/`SLOT`), default value, wired `componentPropertyReferences`, mapped code prop (`omit` list) |
| **3. Auto Layout & Responsive** | `layoutMode`, `FIXED`/`AUTO` vs `HUG`/`FILL`, gap/padding bindings, min/max constraints, target CSS Flexbox/Grid/`@container`/Native stack |
| **4. Variable Bindings** | Visual property, variable path, non-`ALL_SCOPES` scope, `WEB` `var(--...)` / `iOS` / `ANDROID` syntax, Light & Dark check |
| **5. States, A11y & Assets** | Interactive/error/empty states, semantic tag, ARIA/keyboard contract, touch target (`>= 44x44` or `>= 24x24`), local asset paths |
| **6. Simplicity & Gate Sign-Off** | Simplicity Q1/Q2 check, Code Connect status, binary `PASS / CONCERNS / NOT ASSESSED / FAIL` verdict |

---

## 4. Verification Checklist

- [ ] Converted Figma URL `node-id` hyphens to colons (`12-34` to `12:34`) for API and Code Connect calls.
- [ ] Canonical page hierarchy (`Cover`, `Foundations`, `Components`, `Screens`, `Utilities`) avoids duplicate static screen clones.
- [ ] Semantic variables reference primitives via `VARIABLE_ALIAS` with zero raw hex values in semantic modes.
- [ ] Every variable uses explicit role scopes (primitives use `[]`; zero `ALL_SCOPES` usages).
- [ ] Every `WEB` `codeSyntax` entry includes the `var(--...)` wrapper matching production CSS variable names.
- [ ] Every `ComponentSetNode` stays `<= 30` variants via `TEXT`, `BOOLEAN`, `INSTANCE_SWAP`, and `SLOT` properties.
- [ ] Auto Layout frames avoid `HUG` parent + `FILL` child collapse and `WIDTH_AND_HEIGHT` 1-character text threads.
- [ ] Published library components carry zero unbound fills, strokes, radii, spacing, or accidental `Inter` fallbacks.
- [ ] Exported SVG icons sit on integer grids with `viewBox`, `currentColor`, clean SVGO paths, and zero `t=0` `opacity="0"`.
- [ ] Code Connect tier fits plan/scale (Tier 0–2), and `.figma.ts` templates use parserless `figma.code` with exhaustive `getEnum` coverage.

---

## 5. Hard Quality Gate

Run automated checks on the component spec, token bindings, and any `.figma.ts` files before unlocking Phase 3B UI implementation:

```bash
# 1. Fail on unresolved spec stubs or forbidden ALL_SCOPES declarations
grep -rnE "TODO|TBD|FIXME|\[placeholder\]|ALL_SCOPES" docs/ figma-component-spec.md && exit 1 || true

# 2. Verify TypeScript compilation for parserless .figma.ts Code Connect files (when Tier 2 active)
npx tsc --noEmit
```

- **PASS**: `templates/figma-component-spec.md` complete with zero unresolved fields; `<= 30` variants per set; zero `ALL_SCOPES` or missing `var()` `WEB` syntax; zero unbound fills/radii/spacing on published components; clean assets committed; Code Connect verified via `get_code_connect_map` and `tsc --noEmit` (if Tier 1/2).
- **CONCERNS**: Minor non-blocking annotation omissions on secondary variants with an assigned owner.
- **NOT ASSESSED**: `get_design_context` or `get_variable_defs` not yet run, or spec retains unfilled `<...>` fields.
- **FAIL**: Variant explosion `> 30`; `ALL_SCOPES` on variables; missing `var()` in `WEB` `codeSyntax`; raw hexes on published components; `HUG` parent collapsing `FILL` child; or `.figma.tsx` emitted when parserless `.figma.ts` was targeted.

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Combinatorial Variant Explosion** | Multiplying size x theme x icon x state creates `60–200+` variants, slowing Figma and bloating Code Connect | `ComponentSetNode` has `> 30` variants or axes named `ShowIcon` / `IconType` | Cap variants `<= 30`; use `BOOLEAN`, `INSTANCE_SWAP`, `TEXT`, `SLOT`, and `.Building Blocks/` |
| **`ALL_SCOPES` & Un-Aliased Semantics** | Pollutes every picker with irrelevant tokens and breaks Light/Dark mode aliasing | `scopes: ["ALL_SCOPES"]` or raw RGBA hexes stored inside semantic `Color` modes | Set `scopes: []` on primitives, role-specific scopes on semantics, and bind via `createVariableAlias()` |
| **Missing `var()` Wrapper in `WEB` Syntax** | Dev Mode emits invalid CSS (`color: --color-bg-primary;`) instead of `var(...)` | `codeSyntax.WEB` starts with `--` without `var(...)` | Format every `WEB` syntax entry as `var(--token-name)` matching production CSS |
| **`HUG` Parent + `FILL` Child Collapse** | Collapses inputs or text rows to `0px` or `1`-char vertical threads | `layoutSizingHorizontal = 'FILL'` inside `counterAxisSizingMode = 'AUTO'` without `minWidth` | Set parent axis `FIXED` or supply `minWidth`, and set `textAutoResize = 'HEIGHT'` |
| **Redundant Frame Pyramids & Detached Instances** | Deep `Frame > Frame > Group` nesting causes bloated `<div>` trees in codegen | Layer depth > 4 for a simple card/button, or detached library instances | Flatten decorative wrappers in Figma and retain live component instances |
| **Premature Enterprise Library Overengineering** | Spending 50+ `use_figma` calls, 7 collections, and `.figma.ts` files for an 8-component MVP | `> 3` collections or `.figma.ts` templates on a Free/Pro plan or `< 10` component app | Apply Simplest High-Craft Tier 1 single collection + Tier 0 naming & `figma-component-spec.md` |
