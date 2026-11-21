---
name: ui-design-craft
description: First-principles UI/UX research, information architecture, typography and grid geometry, OKLCH/APCA/CVD color systems, W3C DTCG 3-tier tokens, 13-state accessibility, motion choreography, strict anti-AI-slop craft, UX microcopy humanization, and deterministic UI verification scripts.
license: MIT
metadata:
  suite: appnwebsite-skill
  version: "1.0.0"
  milestone: M3
  spiral_stages: "3A,3B,3C"
---

# UI Design Craft

Standalone first-principles UI/UX design craft skill covering research, information architecture, typography, spatial grids, perceptual color science, 3-tier W3C DTCG tokens, 13-state interaction accessibility, GPU motion choreography, UX copy humanization, and deterministic UI validation.

---

## 1. Spiral Role & Gate Responsibility

- **Phase 3A (System-First Visual Foundation Gate):** Lock [design-brief.md](templates/design-brief.md), [design-master.md](templates/design-master.md), and `tokens.json` (validated against [tokens-dtcg.schema.json](templates/tokens-dtcg.schema.json)) **before** authoring feature screens or component libraries.
- **Phase 3B / 3C (Build & Hard Verification):** Enforce dual-gate WCAG 2.1 + APCA contrast, CVD legibility, strict anti-AI-slop rules, and token schema parity across every UI diff.

---

## 2. Progressive Disclosure Routing Table

Load **only** the reference module required for your active subtask; never bulk-load all four modules into context when a targeted CLI query suffices.

| Active Task / Concern | Reference Module (Read On Demand) | Target Template / Schema | Primary CLI Script |
|---|---|---|---|
| UX research tiers, JTBD, personas, card sort, tree test, IA sitemap, heuristics | [references/ux-research-and-ia.md](references/ux-research-and-ia.md) | [templates/design-brief.md](templates/design-brief.md) | `scripts/core_search.py` |
| Type pairings, `clamp()` math, `4/8/12`-col grids, `@container`, nested radius, Gestalt/Fitts/Hick/Miller | [references/typography-grids-and-ergonomics.md](references/typography-grids-and-ergonomics.md) | [templates/design-master.md](templates/design-master.md) | `scripts/design_search.py` |
| OKLCH ramps, WCAG/APCA/CVD contrast, 3-tier DTCG tokens, 13 UI states, GPU motion | [references/color-contrast-tokens-motion.md](references/color-contrast-tokens-motion.md) | [templates/tokens-dtcg.schema.json](templates/tokens-dtcg.schema.json) | `scripts/check_contrast.py`, `scripts/validate_tokens.py` |
| Anti-AI-slop policy, Site-Kind taxonomy, 26-pattern UX microcopy, design critique | [references/anti-ai-slop-and-ux-copy.md](references/anti-ai-slop-and-ux-copy.md) | [templates/design-master.md](templates/design-master.md) | `scripts/check_anti_slop.py` |
| Curated `DESIGN.md` design-language blueprints (Editorial Culinary, Precision Dark, Tactile) | [references/design-languages.md](references/design-languages.md) | [templates/design-master.md](templates/design-master.md) | `scripts/design_search.py` |

---

## 3. Token-Economy CLI Workflow (Query Before Reading)

Run deterministic BM25 queries across the reconciled `data/` catalog (`192` aligned products/colors/reasoning rules, `73` clean font pairings, `115` Phosphor/Solar/Iconamoon entries, `17` aesthetic DNA blocks, `22` framework stacks) before opening large docs:

```bash
# 1. Generate project MASTER.md + page overrides from reconciled reasoning rules
python3 skills/ui-design-craft/scripts/design_search.py "B2B SaaS analytics" --design-system -p "MyApp" -f markdown --persist --page pricing -o ./docs

# 2. Query targeted domain rules (style, color, typography, icons, ux, landing, chart, design, google-fonts)
python3 skills/ui-design-craft/scripts/core_search.py "modern developer saas" --domain typography --json

# 3. Query stack-specific best practices across 22 stacks (nextjs, react, shadcn, html-tailwind, flutter, swiftui, etc.)
python3 skills/ui-design-craft/scripts/design_search.py "accessibility performance" --stack nextjs --json
```

---

## 4. Radical Simplicity ("Least Code, Highest Craft") Gate

Before introducing any styling framework, animation engine, or JS widget library, answer:
1. Can native HTML (`<dialog>`, `<details>`, `popover`) and native CSS (`clamp()`, Grid/Subgrid, `@container`, `:has()`, CSS custom properties) replace JS layout/modal/theme dependencies?
2. Can `1` variable font family (`Geist` or `Plus Jakarta Sans`, weights `400–700`) and `1` focal boldness zone achieve stronger visual authority than multi-font decoration and gradient cards?
3. Are every route, card chrome element, and primitive shade genuinely used by an active flow?

---

## 5. Non-Negotiable Visual Defaults & Verification Gates

- **Fonts:** Default ban on `Inter`, `Roboto`, `Arial`, `Open Sans`, and `Helvetica` (governed brownfield exception requires dated ADR + `--allow-font`).
- **Icons:** Standardize on `Phosphor` (`@phosphor-icons/react`), `Solar`, or `Iconamoon`; ban `Lucide`, `Feather`, `Heroicons`, `Material Icons`, and `Material Symbols` by default (`--allow-icon` only with ADR).
- **Surfaces & Stacking:** Flat intentional surfaces by default (hero text-only gradient with `background-clip: text` allowed); semantic z-index ladder `0..70` (`>= 999` banned); mandatory `@media (prefers-reduced-motion: reduce)`.
- **Imagery, Brand Marks & Color Harmony:** Require real web/client photography (`<img>`/`<picture>`) in consumer/product heroes (`SLOP-HERO-NO-PHOTO`), ban AI-generated food/lifestyle photos (`SLOP-AI-IMAGE-01`) and hand-coded inline `<svg>` logos (`SLOP-SVG-LOGO-01`), strip AI copy clichés in EN/VI (`SLOP-COPY-01`), enforce 60-30-10 color harmony (`SLOP-COLOR-HARMONY-01`), and inspect `1440px` + `390px` Playwright screenshots visually before release.
- **Mandatory Gate Commands:**

```bash
python3 skills/ui-design-craft/scripts/check_contrast.py --file tokens.json --apca --cvd --json
python3 skills/ui-design-craft/scripts/validate_tokens.py tokens.json --strict --contrast --json
python3 skills/ui-design-craft/scripts/check_anti_slop.py src/ --strict --json
```

---

## 6. Negative Triggers (Scope Boundaries)

Do **NOT** use this skill for:
- Extracting Figma Variables, Auto Layout, Code Connect, or MCP visual parity specs (route to `figma-design-to-code`).
- Writing framework routing, SSR/RSC data fetching, mobile store builds, or chart engine code (route to `frontend-surfaces-and-redesign` or `fullstack-api-engineering`).
- Threat modeling, API auth, or backend database architecture (route to `security-engineering` or `system-data-architecture`).
