---
name: figma-design-to-code
description: Translates Figma files, variables, Auto Layout, components, Code Connect mappings, and motion into pixel-faithful, token-synced production UI code with visual parity QA. Use when implementing Figma URLs or nodes, auditing Figma handoff architecture, syncing W3C DTCG tokens with Style Dictionary, Tailwind, or native targets, or running Figma visual parity reviews.
license: MIT
metadata:
  suite: appnwebsite-skill
  version: "1.0.0"
  spiral_stages: "3A, 3B, 3C"
---

# Figma Design-to-Code

Bridge Figma design systems and production UI code bidirectionally around three strict invariants: **Reuse Tokens & Existing Components First**, **Least Code, Highest Craft**, and **DPI-Normalized Visual Parity**.

---

## 1. Pre-Flight & Spiral Gate Check

- **Orchestrated Mode**: Confirm Phase 3A `system-foundation-gate.md` is `UNLOCKED` and load `design-master.md` plus `tokens.json` before authoring Phase 3B UI code.
- **Standalone Mode** (invoked directly without Parent Orchestrator): Run this 3-step pre-flight before generating components:
  1. Scan the target repository for existing UI primitives, styling frameworks, and CSS/DTCG token files.
  2. Apply Simplicity Q1/Q2 below to verify whether existing repo components and native CSS primitives eliminate custom wrappers or token build steps.
  3. Require fresh build/typecheck and side-by-side visual capture evidence before reporting completion.

---

## 2. Progressive Disclosure Router (Load ONLY 1 Reference Per Task)

Never bulk-load both reference files simultaneously. Load only the active reference module and companion template for your current task:

| Active Task / Trigger | Load On Demand (1 File Max) | Companion Template |
|---|---|---|
| Structuring or auditing Figma pages, Variables/Modes/22 Scopes, Auto Layout, Variants (`<= 30`) vs `TEXT`/`BOOLEAN`/`INSTANCE_SWAP`/`SLOT`, Dev Mode redlines, asset exports, or Code Connect | [Figma Architecture & Handoff](references/figma-architecture-and-handoff.md) | [Figma Component Spec](templates/figma-component-spec.md) |
| Extracting via Figma MCP / REST API / Offline, W3C DTCG -> Style Dictionary v4 / Tailwind v4 `@theme` / RN / SwiftUI / Compose sync, Auto Layout -> Flexbox/Grid/Native translation, Figma motion -> code, or `@2x` Visual Parity QA | [Figma-to-Code Engineering](references/figma-to-code-engineering.md) | [Design-to-Code Parity Report](templates/design-to-code-parity-report.md) |

---

## 3. Mandatory Extraction Sequence, Hint Priority & Fallbacks

### URL & Node ID Parsing
- Parse `:fileKey` from `figma.com/design/:fileKey/:name?node-id=X-Y` (or `:branchKey` on `/branch/:branchKey/`).
- Convert hyphen IDs (`42-15`) to colon IDs (`42:15`) for Code Connect, REST API, and `use_figma` calls.
- On local `figma-desktop`, omit `fileKey` to read the active canvas selection.

### Channel A — Figma MCP Execution Order
1. Call `get_design_context(clientLanguages, clientFrameworks)` first; never substitute `get_metadata` or `get_screenshot` for it.
2. Call `get_metadata` only if `get_design_context` truncates or hits a page-node limit, then re-fetch child section nodes.
3. Always call `get_screenshot` for visual ground truth, alongside `get_variable_defs` and `get_code_connect_map`.
4. Call `get_motion_context(recursive: true)` whenever nodes animate or carry motion markers.
5. Download and commit `/api/mcp/asset/...` files locally immediately (`~7`-day expiry window).

### 5-Tier Hint Precedence
Resolve conflicting implementation signals from highest to lowest authority:
`1. Code Connect snippets` -> `2. Component documentation links` -> `3. Dev Mode annotations` -> `4. Design tokens (CSS variables)` -> `5. Raw hex / absolute coordinates (defer to screenshot + Auto Layout intent)`.

### Channels B & C — Non-MCP Fallbacks
- **REST API (`FIGMA_TOKEN`)**: `GET /v1/files/:key/nodes?ids=X:Y`, `GET /v1/images/:key?ids=X:Y&format=png&scale=2`, and `GET /v1/files/:key/variables/local` (Enterprise).
- **Offline Export**: Dev Mode CSS/token JSON + `@2x` PNG captures + exported SVGs; never guess missing SF Symbols, hex tokens, or font metrics from low-resolution rasters.

---

## 4. Anti-Overengineering & Radical Simplicity Gate ("Least Code, Highest Craft")

Interrogate every design-system or implementation step before adding layers, packages, or wrappers:

1. *Can existing repo UI primitives and native HTML/CSS replace raw MCP React+Tailwind boilerplate?*
2. *Can nested Figma `Frame` groups collapse into semantic HTML (`<header>`, `<nav>`, `<button>`, `<dialog>`) + CSS Grid/Flexbox?*
3. *Are we introducing Style Dictionary v4 or Code Connect templates where project scale does not justify them?*
4. *Are static artboard widths (`1440px`/`393px`) being replaced by fluid `clamp()`, `minmax()`, and `@container` rules?*

| Scenario Detected | Overengineered Trap | Simplest High-Craft Choice |
|---|---|---|
| `< 50` tokens on `1` web codebase | Multi-package Style Dictionary v4 build | Direct `tokens.css` (`:root`/`.dark`) or Tailwind v4 `@theme` |
| Starter/Pro plan or `< 10` components | `.figma.ts` Code Connect pipeline | Exact naming + [Figma Component Spec](templates/figma-component-spec.md) |
| `> 30` Figma component variants | Combinatorial variant matrix (`60+`) | Cap variants `<= 30`; use `BOOLEAN`, `INSTANCE_SWAP`, `SLOT` |
| Nested Auto Layout groups | `1:1` `<div>` wrapper pyramid | Single semantic element + CSS Grid/Flexbox (`min-width: 0`) |

---

## 5. Token-Economy Discipline

- Load only the single `references/*.md` file matching your active sub-task.
- On oversized Figma frames, run `get_metadata` first to extract target child section IDs before invoking `get_design_context`.
- Never pass downloaded `.svg` assets to multimodal image-read tools; inspect SVG source text or verify via rendered browser screenshots.
- Batch parallel `use_figma` read calls across pages (`1` `setCurrentPageAsync` per call in one turn); never parallelize conflicting `use_figma` writes.

---

## 6. Negative Triggers (When NOT to Use This Skill)

- **Greenfield visual direction without a Figma source**: Creating OKLCH palettes, font pairings, and brand craft from scratch -> use `ui-design-craft`.
- **Full-surface authoring or codebase redesign without Figma parity scope**: Writing conversion copy, complex app workflows, charts, or UI audits -> use `frontend-surfaces-and-redesign`.
- **Non-UI Figma files**: FigJam whiteboards/diagrams (`figma.com/board/...`) or Figma Slides (`figma.com/slides/...`) -> out of scope.

---

## 7. Cross-Skill Conflict Rules & Hard Exit Gate

- **Typography**: `design-master.md` and product CSS fonts take precedence over Figma's sandbox `Inter` fallback. Reject `Inter`, `Roboto`, `Arial`, `Open Sans`, and `Helvetica` unless an approved brownfield ADR mandates them.
- **Icons & Artwork**: Commit Figma-exported SVG bytes for bespoke icons, logos, and illustrations; use the suite's approved icon system (`Phosphor`, `Solar`, or `Iconamoon`) only when standard UI glyphs match `1:1`. Never hand-draw fake `<svg>`/`<path>` substitutes for real raster or vector art.
- **Surfaces & Tokens**: Preserve intentional Figma token surfaces and contrast; flag unbound raw hex values rather than inventing ad-hoc gradients.
- **Hard Exit Gate**: Produce [Design-to-Code Parity Report](templates/design-to-code-parity-report.md) (`visual-parity-report.md`) and `figma-token-sync.json` with `@2x` DPI normalization logged, `0` `/api/mcp/asset/` URLs remaining, `0` horizontal overflow across `320/390/768/1440`, `prefers-reduced-motion` enforced, and `0` unresolved `P0/P1/P2` defects (`Final Result: passed`).
