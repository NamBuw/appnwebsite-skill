# Design-to-Code Visual & Structural Parity Report

> Populate this report after rendering implemented UI against Figma ground truth (`get_design_context` + `get_screenshot` or verified REST/Offline export). Output status MUST remain `blocked` whenever any capture is missing, DPI is un-normalized, or any `P0`, `P1`, or `P2` mismatch remains open.

## Metadata

| Field | Value |
|---|---|
| **Report ID** | `<PARITY-001>` |
| **Target Component / Screen** | `<PricingSection / CheckoutPage>` |
| **Figma URL & Node ID** | `<https://www.figma.com/design/...?node-id=12-34>` (`<12:34>`) |
| **Extraction Channel** | `<MCP | REST API | Offline Export>` |
| **Rendered Preview URL / Route** | `<http://localhost:3000/pricing>` |
| **Theme & States Tested** | `<Light + Dark / Default, Hover, Focus-Visible, Error>` |
| **Token Sync Manifest** | `<figma-token-sync.json>` |
| **Final Result** | `<passed | blocked>` |

---

## 1. Viewport & `@2x` DPI Normalization Record

Always normalize `@2x`/`@3x` Retina exports against `1:1` CSS viewports before judging spacing, font sizes, or border widths.

| Viewport Name | Figma Source Pixels | Impl Capture Pixels | CSS Target Viewport | `deviceScaleFactor` | Normalization Method |
|---|---:|---:|---:|---:|---|
| `Desktop` | `<2880 x 1800 (@2x)>` | `<1440 x 900>` | `1440 x 900` | `<1>` | `<Scaled Figma @2x by 0.5x to match 1:1 CSS px>` |
| `Mobile` | `<786 x 1704 (@2x)>` | `<393 x 852>` | `393 x 852` | `<1>` | `<Scaled Figma @2x by 0.5x to match 1:1 CSS px>` |

---

## 2. Token Sync & Asset Integrity Verification

- **Token Linter Command & Output**: `<npx style-dictionary build && python3 skills/ui-design-craft/scripts/validate_tokens.py --file tokens.json --strict --contrast --json -> 0 violations>`
- **Hardcoded Value Scan**: `<0 hardcoded hex colors or arbitrary 2-digit px values outside token definitions>`
- **Asset Persistence Check**:
  - Zero ephemeral `/api/mcp/asset/...` URLs remaining in source or build output: `<Verified | Failed>`
  - Zero hand-coded fake `<svg>`/`<path>` approximations replacing real Figma raster/logo/illustration art: `<Verified | Failed>`
  - Inline animated SVG paths (`pathLength="1"`) and `opacity` checks (no baked `t=0` `opacity="0"`): `<Verified | N/A>`

---

## 3. Five-Surface Fidelity & Computed Telemetry Matrix

| Fidelity Surface | Inspection Evidence (Figma vs Rendered Code) | Computed Telemetry (`getComputedStyle` / `getBoundingClientRect`) | Status |
|---|---|---|---|
| **1. Typography** | `<Font family, weight, size, line-height, letter-spacing, tabular-nums>` | `<font-family: ..., font-size: 32px, line-height: 1.2>` | `<PASS | FAIL>` |
| **2. Spacing & Layout** | `<Padding, gap, grid alignment, zero clipping, scrollWidth <= clientWidth>` | `<320/390/768/1440 overflow = 0px; card rect 361x248>` | `<PASS | FAIL>` |
| **3. Colors & Tokens** | `<Light/Dark surfaces, borders, focus rings, contrast >= 4.5:1 / 3:1>` | `<bg: var(--color-surface-card), contrast 12.4:1>` | `<PASS | FAIL>` |
| **4. Imagery & Icons** | `<Crisp @2x/SVG rendering, aspect ratio, viewBox, zero distortion>` | `<img naturalWidth 640x480; explicit w/h>` | `<PASS | FAIL>` |
| **5. Copy, States & Motion** | `<Exact copy, interactive states, timelineCohorts, prefers-reduced-motion>` | `<reduced-motion disables transform transitions>` | `<PASS | FAIL>` |

---

## 4. Intentional Deviations Ledger

Record every intentional improvement over the static Figma frame (accessibility, fluid responsiveness, or native platform HIG) so reviewers never mistake deliberate craft for drift.

| Element | Figma Spec | Code Implementation | Rationale (`A11y` / `Responsive` / `Platform HIG`) | Approved By |
|---|---|---|---|---|
| `<CloseIconButton>` | `<28x28px hit box>` | `<44x44px hit box with 20px icon>` | `<WCAG 2.2 AA touch target minimum>` | `<Design + Eng>` |
| `<PricingGrid>` | `<Fixed 1440px 3-col>` | `<grid-cols-[repeat(auto-fit,minmax(280px,1fr))]>` | `<Fluid 320px-1440px reflow without overflow>` | `<Design + Eng>` |

---

## 5. `P0`–`P3` Findings & Iteration History

Severity policy: `P0` (unusable/broken layout, missing content, severe contrast failure), `P1` (major visual/layout/token mismatch or broken responsive breakpoint), `P2` (noticeable spacing, typography, or state alignment defect), `P3` (minor sub-pixel polish).

| Finding ID | Severity | Location | Side-by-Side Evidence (Figma vs Impl) | Impact | Concrete Fix Applied | Status |
|---|---|---|---|---|---|---|
| `<F-001>` | `<P1>` | `<Hero CTA row @390px>` | `<Figma stacks vertically; Impl clipped secondary button>` | `<Horizontal overflow 24px>` | `<Added flex-wrap + min-w-0 on CTA container>` | `<Fixed | Open>` |

### Iteration Log

| Pass # | Capture Paths (Figma + Impl Side-by-Side) | Findings Fixed | Remaining `P0/P1/P2` Count | Pass Verdict |
|---|---|---|---:|---|
| `Pass 1` | `<artifacts/qa/pass1-390.png, artifacts/qa/pass1-1440.png>` | `<Initial baseline capture>` | `<2>` | `<blocked>` |
| `Pass 2` | `<artifacts/qa/pass2-390.png, artifacts/qa/pass2-1440.png>` | `<F-001, F-002>` | `<0>` | `<passed>` |

---

## 6. Final Gate Sign-Off

- **Build / Typecheck / Test Command**: `<npm run typecheck && npm run build>` -> `<Exit 0>`
- **Open `P0 / P1 / P2` Count**: `<0>` (`P3` deferred count: `<0>`)
- **Final Gate Verdict**: `<passed | blocked>`
