# Design System Master Specification (`design-master.md`)

> **Precedence Rule:** When building a specific page, inspect `design-system/pages/[page-name].md` first.
> If a page override exists, its deviations take precedence; otherwise strictly follow this Master specification.

---

## 1. Brand Identity, Site-Kind & Constraints

| Attribute | Value |
|---|---|
| **Project** | `<Project Name>` |
| **Site-Kind** | `<software \| gaming \| tech \| product \| service \| place>` |
| **Aesthetic Direction** | `<Selected style from design_search.py>` |
| **Default Surface Policy** | `Flat intentional surfaces (hero text-only directional gradient allowed if dark/editorial)` |
| **Icon Library Standard** | `Phosphor (@phosphor-icons/react), Solar, or Iconamoon` |
| **Explicit Bans** | `No Inter, Roboto, Arial, Open Sans, Helvetica; no Lucide, Feather, Heroicons, Material Icons/Symbols; no z-index >= 999` |

---

## 2. Perceptual Color System (OKLCH + Hex + WCAG/APCA)

| Semantic Role | OKLCH | Hex Fallback | CSS Variable | Paired Against | WCAG 2.1 / APCA Lc |
|---|---|---|---|---|---|
| `surface.canvas` | `oklch(0.141 0.005 285.8)` | `#09090B` | `--color-bg-canvas` | — | Base surface |
| `surface.elevated` | `oklch(0.210 0.006 285.9)` | `#18181B` | `--color-bg-elevated` | — | Step +1 surface |
| `text.primary` | `oklch(0.985 0.000 0)` | `#FAFAFA` | `--color-text-primary` | `surface.canvas` | `19.3:1 / Lc 103` |
| `text.muted` | `oklch(0.705 0.015 286.1)` | `#A1A1AA` | `--color-text-muted` | `surface.canvas` | `7.9:1 / Lc 54` |
| `accent.primary` | `oklch(0.696 0.170 162.5)` | `#10B981` | `--color-accent-primary` | `surface.canvas` | `8.5:1 / Lc 56` |
| `accent.on-primary` | `oklch(0.141 0.005 285.8)` | `#09090B` | `--color-on-primary` | `accent.primary` | `8.5:1 / Lc 56` |
| `border.subtle` | `oklch(0.274 0.006 286.0)` | `#27272A` | `--color-border-subtle` | `surface.canvas` | Structural hairline |
| `status.destructive` | `oklch(0.637 0.237 25.3)` | `#EF4444` | `--color-destructive` | `surface.canvas` | Paired with icon + label |

- **CVD Verification:** Status and chart categories pair color with Phosphor icons, pattern strokes, and direct labels (verified under Protanopia, Deuteranopia, Tritanopia).

---

## 3. Typography Ramp & 26 Named Text Styles

- **Heading Family:** `<e.g., Geist / Plus Jakarta Sans / Instrument Sans>` (`400`, `500`, `600`, `700`; zero `900`, zero italics)
- **Body Family:** `<Same single family or crisp pair>` (`tabular-nums` for metrics/tables; `text-wrap: balance` on headings, `pretty` on body)
- **Fluid Formula:** `clamp(minRem, calc(interceptRem + slopeVw), maxRem)` where `slope = (maxPx - minPx) / (maxVw - minVw) * 100`

| Style Group | Named Styles | Size / Clamp Range | Line Height | Weight |
|---|---|---|---|---|
| **Headings (1–6)** | `heading-1` .. `heading-6` | `clamp(2rem, 1.4rem + 2.5vw, 3.5rem)` .. `1.25rem` | `1.10–1.25` | `600–700` |
| **Titles (1–5)** | `title-1` .. `title-5` | `1.5rem` .. `0.9375rem` | `1.25–1.35` | `600` |
| **Body (1–6)** | `body-1` .. `body-6` | `1.125rem` .. `0.8125rem` | `1.50–1.60` | `400–500` |
| **Buttons (4)** | `button-lg`, `button-md`, `button-sm`, `button-xsm` | `1rem` .. `0.75rem` | `1.00–1.20` | `500–600` |
| **Captions (1–5)** | `caption-1` .. `caption-5` | `0.8125rem` .. `0.6875rem` | `1.30–1.40` | `400–500` |

---

## 4. Spatial Grid, Spacing Tokens (`Spacing-0..900`), Nested Radius & Z-Index

- **Grid:** Mobile `4`-col (`16px` margin/gutter) -> Tablet `8`-col (`24px`/`20px`) -> Desktop `12`-col (`1280px` max, `24px` gutter); hero prose `<= 680px` / `65ch`.
- **Spacing Scale:** `--space-0: 0`, `--space-50: 2px`, `--space-100: 4px`, `--space-200: 8px`, `--space-300: 12px`, `--space-400: 16px`, `--space-500: 24px`, `--space-600: 32px`, `--space-700: 48px`, `--space-800: 64px`, `--space-900: 96px`.
- **Nested Radius:** `r_inner = r_outer - gap` when `gap < 32px` and `r_outer - gap > 2px`.
- **Z-Index Scale:** `base: 0`, `raised: 10`, `sticky: 20`, `overlay: 30`, `modal: 40`, `popover: 50`, `toast: 60`, `tooltip: 70`.

---

## 5. 13-State Interaction Matrix & Motion Choreography

- **States Covered:** `default`, `hover`, `focus-visible` (`>= 2px` offset ring), `active` (`scale(0.98)`), `selected`, `visited`, `disabled`, `read-only`, `loading`, `empty`, `partial`, `error`, `offline`.
- **Motion Curve:** `--ease-out-expo: cubic-bezier(0.22, 1, 0.36, 1)`; enter `250–400ms`, exit `150–250ms` (`60–70%` of enter), GPU-only (`transform`, `opacity`), `@media (prefers-reduced-motion: reduce)` mandatory fallback.

---

## 6. UX Copywriting & Anti-AI-Slop Rules

- **Tone:** Calm, concrete, sentence-case, zero exclamation marks, zero apologies, zero AI buzzwords.
- **Verb Consistency:** Button label verb matches confirmation toast (`Publish` -> `Published`).
- **Waiver Ledger (`<= 5` entries max):** `<None — or dated ADR reference>`

---

## 7. Pre-Delivery Verification Commands

```bash
python3 skills/ui-design-craft/scripts/check_contrast.py --file tokens.json --apca --cvd --json
python3 skills/ui-design-craft/scripts/validate_tokens.py tokens.json --strict --json
python3 skills/ui-design-craft/scripts/check_anti_slop.py src/ --strict --json
```
