# Figma-to-Code Engineering: Extraction, Token Sync, Layout, Motion & Visual Parity QA

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

This module translates Figma components, variables, Auto Layout frames, and motion timelines into concise, accessible, token-synchronized production code across Web, React Native, SwiftUI, and Jetpack Compose, verified through a DPI-normalized `P0–P3` visual parity loop.

---

## 1. Decision Framework

### 1.1 Figma Extraction Channel & 5-Tier Hint Hierarchy

Select the richest verified extraction channel without fabricating missing design details:

| Channel | When to Use | Exact Endpoints / Tools | Hard Constraint |
|---|---|---|---|
| **Channel A — Figma MCP (Default)** | Remote `https://mcp.figma.com/mcp` (`FIGMA_OAUTH_TOKEN`, `X-Figma-Region`, `rmcp_client = true`) or local `figma-desktop` | `get_design_context`, `get_metadata`, `get_screenshot`, `get_variable_defs`, `get_code_connect_map`, `get_motion_context` | Never substitute `get_metadata` or `get_screenshot` for `get_design_context`; `figma-desktop` reads open selection |
| **Channel B — Figma REST API Fallback** | Headless CI or environments lacking MCP server access (`FIGMA_TOKEN`) | `GET /v1/files/:key/nodes?ids=X:Y`, `GET /v1/images/:key?ids=X:Y&format=png&scale=2`, `GET /v1/files/:key/variables/local` | `/variables/local` requires Org/Enterprise plan; convert `-` to `:` in `ids` |
| **Channel C — Offline Handoff Fallback** | Restricted environments without API or MCP access | Dev Mode CSS/token export + `@2x` PNG captures + local SVG/WebP bundle | Never guess SF Symbol names, exact hex tokens, or font metrics from low-res rasters; mark gaps `NOT ASSESSED` |

Apply signals strictly according to the **5-Tier Hint Precedence Hierarchy** (highest authority wins):
1. Code Connect snippets (`CodeConnectSnippet`)
2. Component documentation links (`documentationLinks`)
3. Dev Mode annotations
4. Design tokens (CSS custom properties)
5. Raw hex colors and absolute coordinates (defer to `get_screenshot` + Auto Layout intent)

### 1.2 Bidirectional Token Sync Pipeline Selector (Simplicity First)

| Sync Tier | Threshold Condition | Toolchain & Outputs | When to Reject |
|---|---|---|---|
| **Option A — Direct CSS / Tailwind v4 `@theme` (Simplest High-Craft)** | `< 50` tokens AND `1` web codebase | Direct W3C DTCG `tokens.json` (optional) + `tokens.css` (`:root`/`.dark`) or Tailwind v4 `@theme inline` | Zero build scripts, zero extra packages; reject Style Dictionary below `50` tokens |
| **Option B — Style Dictionary v4 Pipeline** | `>= 50` tokens OR `>= 2` target platforms (Web + RN + SwiftUI + Compose) | W3C DTCG 2025.10 (`$value`, `$type`, `$description`, `{alias}`) + `style-dictionary` v4 (`usesDtcg: true`) | Reject custom ad-hoc Python/Bash token compilers on multi-platform teams |

### 1.3 Motion Implementation Selector

| Target Platform | Primary Motion Stack | Fallback / Escalation Rule |
|---|---|---|
| **React Web** | `motion/react` (`motion.dev` snippets verbatim from `get_motion_context`), or adapt to existing Framer Motion / GSAP | Never add a second animation package when one already exists in `package.json` |
| **Vanilla / Non-React Web** | CSS `@keyframes` + Web Animations API (WAAPI) | Inline `<svg>` `<path pathLength="1">` for path-trim animations |
| **SwiftUI / iOS** | `.animation(...)`, `.timingCurve(...)`, `.spring(duration:bounce:)`, `KeyframeAnimator` mapped from CSS snippets | Never invent non-existent SwiftUI modifiers; map easing curves explicitly |
| **Unsupported Figma Effects** | Static start/end CSS transitions or Lottie / MP4 export | Surface verbatim MCP lint errors for Smart Animate transitions and GIF/animated SVG layers |

### 1.4 Anti-Overengineering Self-Interrogation & Token Economy

Answer all four checks before authoring UI code:
1. **Simplicity Q1**: Can an existing repository component (`Button`, `Input`, `Card`, `Dialog`) be reused instead of pasting Figma MCP's raw JSX + Tailwind output?
2. **Simplicity Q2**: Can `3–5` nested Figma Auto Layout `Frame` groups collapse into one semantic HTML landmark (`<header>`, `<nav>`, `<main>`, `<button>`, `<dialog>`) with CSS Grid/Flexbox?
3. **Simplicity Q3**: Are we introducing Style Dictionary v4 or a motion runtime for `< 50` tokens or static screens?
4. **Simplicity Q4**: Are fixed `1440px` / `393px` artboard dimensions being replaced with fluid `clamp()`, `minmax()`, and `@container` rules?

**Token Economy**: Load ONLY this reference module during implementation and parity QA.
On oversized frames, call `get_metadata` first to select child frame IDs (`<= 2` screens per pass) before invoking `get_design_context`.
Never feed downloaded `.svg` files to multimodal image-read tools; inspect SVG markup as text or verify visually in rendered browser screenshots.

---

## 2. Step-by-Step Workflow

1. **Step 1 — Context & Asset Extraction with 7-Day Persistence** *(Owner: Frontend/Mobile Engineer; Inputs: Figma URL/Node ID; Outputs: design context, screenshot, committed assets)*:
   - Parse `fileKey` (or `branchKey`) from `figma.com/design/:fileKey/:name?node-id=X-Y` and invoke `get_design_context(fileKey, nodeId, clientLanguages, clientFrameworks)`.
   - If `get_design_context` truncates or hits a page-node error, call `get_metadata` to pick section node IDs and re-run `get_design_context` per section.
   - Always call `get_screenshot`, `get_variable_defs`, and `get_code_connect_map`.
   - **7-Day Ephemeral Asset Persistence Rule**:
     - `/api/mcp/asset/...` URLs expire in `~7` days—download every SVG/PNG/WebP immediately and commit exact bytes in `src/assets/` or `public/assets/`.
     - Inspect exported SVGs for baked `opacity="0"` attributes left over from `t=0` animation frames.
   - **Icon & Artwork Sizing Discipline**:
     - Render icons inside explicit sized boxes (`size-6` / `24px x 24px`) with `width: 100%; height: 100%` (never `auto`).
     - Use Figma-exported SVG bytes for bespoke vectors, brand marks, and illustrations.
     - Use the approved icon library (`Phosphor`, `Solar`, or `Iconamoon`) only when standard UI glyphs match `1:1`; never hand-draw fake `<svg>`/`<path>` substitutes for real raster or brand art.

2. **Step 2 — Bidirectional W3C DTCG Token Synchronization** *(Inputs: `get_variable_defs` / REST variables + `tokens.json`; Outputs: `figma-token-sync.json` + platform tokens)*:
   - Normalize tokens to W3C DTCG format (`$schema`, `$value`, `$type` among `color`, `dimension`, `fontFamily`, `fontWeight`, `duration`, `cubicBezier`, `shadow`, and `{primitive.*}` aliases).
   - Under **Option A**, map directly into `:root` / `.dark` CSS custom properties and Tailwind v4 `@theme inline { --color-bg-primary: var(--color-bg-primary); }`.
   - Under **Option B**, configure Style Dictionary v4 (`usesDtcg: true` in `sd.config.mjs`) to emit:
     - **Web**: `tokens.css` + Tailwind v4 `@theme`
     - **React Native**: typed `tokens.ts` (`dp` numeric scale, hex/rgba strings)
     - **SwiftUI**: `Tokens.swift` + `Assets.xcassets` colorsets + Dynamic Type (`.font(.body)`)
     - **Jetpack Compose**: `Tokens.kt` (`Color(0xFF...)`, `.dp`, `.sp`, `TextStyle`)
   - **Bidirectional Conflict Rule**:
     - Production code wins for shipped hexes and CSS variable names.
     - Figma wins for newly reviewed semantic token additions.
     - Log reconciled mappings in `figma-token-sync.json` and lint for `0` hardcoded hex or 2-digit pixel literals outside token files.
   - **Font Governance**: Enforce `design-master.md` and codebase fonts; strip accidental Figma `Inter` fallbacks unless a brownfield ADR authorizes them.

```json
// Minimal W3C DTCG token excerpt (Option A direct CSS or Option B Style Dictionary v4)
{
  "primitive": { "color": { "ink": { "900": { "$type": "color", "$value": "#111318" } } } },
  "semantic": { "text": { "primary": { "$type": "color", "$value": "{primitive.color.ink.900}" } } }
}
```

```js
// Option B Style Dictionary v4 (sd.config.mjs) for >= 50 tokens or >= 2 platforms
export default {
  source: ["tokens/**/*.tokens.json"],
  usesDtcg: true,
  platforms: {
    css: { transformGroup: "css", buildPath: "src/styles/", files: [{ destination: "tokens.css", format: "css/variables" }] },
    rn: { transformGroup: "react-native", buildPath: "src/theme/", files: [{ destination: "tokens.ts", format: "javascript/es6" }] },
    swift: { transformGroup: "ios-swift", buildPath: "ios/Tokens/", files: [{ destination: "Tokens.swift", format: "ios-swift/class.swift" }] },
    compose: { transformGroup: "compose", buildPath: "android/tokens/", files: [{ destination: "Tokens.kt", format: "compose/object" }] }
  }
};
```

3. **Step 3 — Auto Layout to Flexbox, Grid, `@container` & Native Translation** *(Inputs: `get_design_context` + component specs; Outputs: responsive UI components)*:
   - Translate Figma Auto Layout into semantic HTML landmarks and logical CSS properties (RTL-ready) instead of cloning Figma wrapper nesting:

| Figma Auto Layout Property | Web CSS / Tailwind v4 Translation | Native Translation (SwiftUI / RN / Compose) |
|---|---|---|
| `layoutMode: HORIZONTAL \| VERTICAL` | `display: flex; flex-direction: row \| column` (`flex-row` / `flex-col`) | SwiftUI `HStack` / `VStack`; RN `flexDirection`; Compose `Row` / `Column` |
| `layoutWrap: WRAP` + gaps | `display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: <row> <col>` | SwiftUI `LazyVGrid`; RN `flexWrap: 'wrap'`; Compose `FlowRow` |
| `primaryAxisAlignItems: SPACE_BETWEEN` | `justify-content: space-between` | SwiftUI `Spacer()`; RN `justifyContent: 'space-between'`; Compose `Arrangement.SpaceBetween` |
| `layoutSizing*: FIXED` | Token size or `flex: 0 0 <N>px`; convert large widths to `width: 100%; max-width: <N>px` | `.frame(width:)` / fixed `dp` (bounded by container width) |
| `layoutSizing*: HUG` | `width: fit-content; flex: 0 0 auto` | Intrinsic sizing in SwiftUI/Compose; `alignSelf: 'flex-start'` in RN |
| `layoutSizing*: FILL` | `flex: 1 1 0%; min-width: 0` (prevents flex text overflow) or `width: 100%` | `.frame(maxWidth: .infinity)` / `flex: 1` / `Modifier.weight(1f)` |
| `minWidth` / `maxWidth` | `min-width` / `max-width` or `clamp(min, preferred, max)` | `.frame(minWidth:maxWidth:)` / `minWidth`/`maxWidth` |
| `layoutPositioning: ABSOLUTE` + `constraints` | `position: absolute` with `inset-block-start` / `inset-inline-end` inside `position: relative` | SwiftUI `.overlay(alignment:)`; RN `position: 'absolute'`; Compose `Box(Modifier.align(...))` |

   - **Fluid Responsiveness & Optical Craft**:
     - Support `320px`, `390px`, `768px`, `1024px`, and `1440px` using `@container` queries on reusable cards.
     - Use `min-height: 100dvh` (never `100vh`) to prevent mobile browser URL-bar clipping.
     - Apply `font-variant-numeric: tabular-nums` to metrics, `text-wrap: balance` to headings, and `text-wrap: pretty` to body copy.
   - **Mobile Native HIG Rules (SwiftUI / RN)**:
     - Build multi-screen navigation scaffolds first (`NavigationStack`, `TabView`, `.sheet`).
     - Strip Figma device chrome (`StatusBar`, `Bezel`, `HomeIndicator`) before writing native views.
     - Map HIG colors (`Color(.systemBackground)`), use `Image(systemName:)` for SF Symbols (never codepoints), prefer `List`/`Form`, and replace rotated-rectangle fake charts with Swift Charts.
   - **Intentional Deviation Ledger**: Log every accessibility or responsive improvement (`44x44px` touch target, `>= 4.5:1` contrast, native `<select>`/`<dialog>`) in the parity report so reviewers distinguish deliberate craft from drift.

4. **Step 4 — Figma Motion-to-Code Choreography** *(Inputs: `get_design_context` + `get_motion_context(recursive: true)`; Outputs: reduced-motion-safe animation code)*:
   - Call `get_motion_context(fileKey, nodeId, recursive: true)` (cap `500` nodes).
   - Join every returned node back to `get_design_context` via `data-node-id`; exact `nodeId` always overrides `fallbackNodeId`.
   - Drive coordinated nodes in `timelineCohorts` from one shared lifecycle using `durationMs / 1000` and `loopMode` (`once | loop | boomerang`).
   - Preserve verbatim `codeSnippets` values (`duration`, easing, per-element `transformOrigin`), factoring repeated animations into shared `variants` or constants.
   - Enforce **six non-negotiable Figma motion rules**:
     - **Interleaved 3-Layer Transforms**: Keep `motion.div[data-motion-wrapper-for] > static-transform div > inner` nesting and subtract static base offsets from absolute keyframes (`[45, 125, 125]` over `rotate-45` -> `[0, 80, 80]`) to avoid double rotation; re-apply `data-motion-transform-template` via `transformTemplate`.
     - **Animated `display: contents` Trap**: Keep `display: contents` on static groups; when a group itself animates, replace `display: contents` with a real positioned box carrying explicit dimensions.
     - **Layout vs. Motion Transform Split**: Separate Tailwind centering (`-translate-x-1/2`) from Motion inline transforms (`rotate`/`scale`), or encode `x: "-50%"` in every keyframe.
     - **Easing & SVG Path-Trim**: Map `HOLD` to `steps(1, jump-end)`, `duration: 0` to static style, `CUSTOM_SPRING` to real springs, rotation pivot to `(y - 1) * 100%`, distant hues to OKLCH, and `PATH_TRIM` vectors to inline `<svg>` `<path pathLength="1">`.
     - **`prefers-reduced-motion` Mandate**: Wrap CSS animations in `@media (prefers-reduced-motion: reduce)` and React animations in `useReducedMotion()` / `<MotionConfig reducedMotion="user">`.
     - **Verbatim Motion Lint Surfacing**: Surface unsupported Smart Animate transitions, GIF/animated SVG exports, and `display: contents` warnings explicitly rather than inventing fake keyframes.

```tsx
// Interleaved 3-layer transform: static rotate-45 base subtracted from absolute [45, 125] -> [0, 80]
<motion.div data-motion-wrapper-for="12:34" animate={{ rotate: [0, 80, 80] }} transition={{ duration: 0.6 }}>
  <div className="rotate-45">
    <div data-node-id="12:34" className="origin-[50%_0%]">Badge</div>
  </div>
</motion.div>
```

5. **Step 5 — Complexity Budget & Pre-Parity Deletion/Condensation Pass** *(Inputs: working components; Outputs: lean, build-clean UI code)*:
   - Delete redundant single-child `<div>` wrappers left from Figma frame nesting.
   - Deduplicate repeated `variants` objects or Tailwind class strings into shared primitives.
   - Prune unused downloaded MCP assets, then re-run typecheck and production build.

6. **Step 6 — `@2x` DPI-Normalized `P0–P3` Visual & Structural Parity QA Loop** *(Inputs: Figma `get_screenshot` + live rendered captures; Outputs: `visual-parity-report.md`)*:
   - Capture live rendered UI (Playwright or simulator) at matching routes, themes (`Light`/`Dark`), and interactive states (`deviceScaleFactor: 1` or explicitly normalized `@2x` dimensions, e.g. `786x1704 @2x` -> `393x852` CSS px).
   - Inspect **combined side-by-side comparisons** (full-page + zoomed detail crops on typography, icons, and dense controls)—never review code alone or view captures separately.
   - Measure runtime DOM telemetry via `getBoundingClientRect()`, `getComputedStyle()`, and `scrollWidth <= clientWidth` across `320px`, `390px`, `768px`, and `1440px`.
   - Audit all **5 Fidelity Surfaces** (`Typography`, `Spacing & Layout`, `Colors & Tokens`, `Imagery & Icons`, `Copy, States & Motion`).
   - Loop `Fix -> Re-capture -> Re-compare` until `0` open `P0`, `P1`, or `P2` defects remain.

---

## 3. Reusable Artifact & Template

Record every verification cycle in [Design-to-Code Visual & Structural Parity Report](../templates/design-to-code-parity-report.md) (`visual-parity-report.md`) paired with `figma-token-sync.json`.

| Artifact / Section | Required Fields & Contract |
|---|---|
| **`figma-token-sync.json`** | `schema_version`, `source_file_key`, `pipeline_tier` (`direct-css` \| `style-dictionary-v4`), `token_count`, `platforms` (`web`, `rn`, `swiftui`, `compose`), `sync_timestamp`, `conflicts_resolved[]` |
| **Metadata & DPI Record** | `Report ID`, `Figma URL & Node ID`, `Extraction Channel`, `Viewport Name`, `Figma Source Px`, `Impl Capture Px`, `CSS Target Size`, `deviceScaleFactor`, `Normalization Method` |
| **Token & Asset Verification** | Token linter command + `0` violations, confirmation of `0` `/api/mcp/asset/` URLs, `0` fake inline SVGs for real artwork, `0` baked `opacity="0"` SVGs |
| **5-Surface Telemetry Matrix** | Typography, Spacing/Layout (`getBoundingClientRect()`, `320/390/768/1440` overflow = `0`), Colors/Tokens contrast, Imagery/Icons, Copy/States/`prefers-reduced-motion` |
| **Deviations & `P0–P3` Log** | A11y/responsive/HIG deviations approved by Design+Eng; ordered findings (`P0–P3`), iteration passes, and binary `passed` \| `blocked` verdict |

---

## 4. Verification Checklist

- [ ] Extracted design context via `get_design_context` + `get_screenshot` (or documented REST/Offline fallback gaps).
- [ ] Downloaded and committed every `/api/mcp/asset/...` asset locally before `7`-day URL expiry.
- [ ] Reused existing repository UI components (`Button`, `Input`, `Card`, `Dialog`) instead of pasting raw MCP output.
- [ ] Synchronized W3C DTCG tokens to CSS/Tailwind v4 `@theme` (or Style Dictionary v4) with zero hardcoded hexes or pixels.
- [ ] Translated Auto Layout to semantic HTML + Flexbox/Grid/`@container` with `min-width: 0` and logical RTL properties.
- [ ] Verified zero horizontal overflow (`scrollWidth <= clientWidth`) at `320px`, `390px`, `768px`, and `1440px`.
- [ ] Preserved 3-layer motion offset subtraction, replaced animated `display: contents` boxes, and enforced `prefers-reduced-motion`.
- [ ] Normalized `@2x` Retina captures against `1:1` CSS viewports and reviewed combined side-by-side screenshots.
- [ ] Verified `getComputedStyle()` font families/sizes/weights, WCAG contrast ratios, and `getBoundingClientRect()` bounds.
- [ ] Resolved all `P0`, `P1`, and `P2` parity defects and recorded intentional deviations before marking `passed`.

---

## 5. Hard Quality Gate

Run automated asset/token scans and build checks after the Pre-Parity Deletion/Condensation Pass:

```bash
# 1. Fail on leftover 7-day ephemeral Figma MCP asset URLs
grep -rnE "/api/mcp/asset/" src/ public/ app/ && exit 1 || true

# 2. Build tokens (when Option B Style Dictionary v4 is active), typecheck, and bundle
npx style-dictionary build --config sd.config.mjs && npm run typecheck && npm run build
```

- **PASS**: `templates/design-to-code-parity-report.md` completed with side-by-side captures, `@2x` DPI normalization logged, `0` horizontal overflow at `320/390/768/1440`, `0` ephemeral `/api/mcp/asset/` URLs or hardcoded token leaks, `0` open `P0/P1/P2` defects, `prefers-reduced-motion` verified, and `typecheck`/`build` green.
- **CONCERNS**: Only minor `P3` sub-pixel polish items remain with tracked follow-up IDs.
- **NOT ASSESSED**: Missing Figma `get_screenshot`, missing live screenshot, un-normalized `@2x` comparison, or unfilled `<...>` fields -> status MUST stay `blocked`.
- **FAIL**: Committed `/api/mcp/asset/...` URLs; real brand logo/photo replaced with hand-coded fake `<svg>`/`<path>`; raw Figma MCP JSX+Tailwind pasted over repo components/tokens; horizontal overflow at `390px`; missing `prefers-reduced-motion`; or unresolved `P0/P1/P2` drift.

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **Verbatim MCP JSX+Tailwind Paste** | Duplicates buttons/cards, hardcodes raw hexes, and bypasses repository a11y primitives | Inline `bg-[#...]` classes and duplicate modal/button markup outside `components/ui/` | Map `Code Connect` hints and tokens onto existing repo components and CSS/DTCG variables |
| **7-Day Ephemeral Asset & Fake SVG Substitution** | `/api/mcp/asset/...` URLs expire in `7` days; AI-drawn SVGs distort real brand marks/artwork | `localhost` or `/api/mcp/asset/` URLs in source, or hand-coded `<circle>`/`<path>` replacing art | Download and commit exact SVG/WebP/PNG bytes locally with explicit box sizing |
| **`<div>` Pyramid & Pixel-Locked Artboard Cloning** | Cloning Figma frames 1:1 produces deep `div` nesting and fixed `1440px` layouts that break mobile | `width: 1440px` or `scrollWidth > clientWidth` at `390px` inside nested `<div>` wrappers | Collapse into semantic HTML + CSS Grid/Flexbox (`min-width: 0`) + `clamp()` + `@container` |
| **Un-Normalized `@2x` or Code-Only QA** | Misjudges spacing/type by `2x` or misses font fallbacks, clipped labels, and dark-mode drift | Review claims `passed` without side-by-side DPI-normalized captures or `getComputedStyle()` | Normalize `@2x` captures to `1:1` CSS viewports and audit 5 surfaces side-by-side |
| **Motion Double-Rotation & Animated `display: contents`** | Absolute keyframes over `rotate-45` double rest angle; `display: contents` drops group motion | Element rests at `90deg` or freezes; missing `prefers-reduced-motion` guard | Subtract static base offsets in 3-layer wrappers, promote animated `contents` boxes, add reduced motion |
| **Premature Style Dictionary Monolith** | Adds multi-package build complexity for a single web app with `30` CSS tokens | `style-dictionary` pipeline and custom transforms built for `< 50` tokens on `1` web surface | Use direct `tokens.css` / Tailwind v4 `@theme` until `>= 50` tokens or `>= 2` platforms exist |
