# Curated `DESIGN.md` Design-Language Blueprints

> **Contents**: [1. Decision Framework](#1-decision-framework) | [2. Step-by-Step Workflow](#2-step-by-step-workflow) | [3. Reusable Artifact & Template](#3-reusable-artifact--template) | [4. Verification Checklist](#4-verification-checklist) | [5. Hard Quality Gate](#5-hard-quality-gate) | [6. Anti-Patterns](#6-anti-patterns)

---

## 1. Decision Framework

Generic interfaces happen when styling is improvised property-by-property without an aesthetic thesis. Inspired by Google Stitch `DESIGN.md`, `VoltAgent/awesome-design-md`, and Anthropic `frontend-design`, commit to **one explicit Design-Language Blueprint** upfront before authoring HTML, JSX, or CSS.

### Blueprint Selection Matrix (Domain -> Design Language)

| Domain / Surface | Blueprint ID | Signature Stage & Elevation | Typography Pairing |
|---|---|---|---|
| Food, Culinary, Hospitality, Recipes | `culinary-editorial` (**Airbnb x Kinfolk**) | `#FFFFFF` luminous canvas + `#FAF7F2` tonal resting bands, borderless photos, warm diffused shadows | `Newsreader` (serif display) + `Manrope` (UI/body) |
| Developer Tools, AI Infra, SaaS CLI | `linear-dark` (**Linear Precision Dark**) | `#09090B` / `#111113` deep obsidian, `1px` crisp zinc dividers, interactive telemetry preview | `Geist` + `Geist Mono` (`tabular-nums`) |
| Fintech, Payments, API Platforms | `stripe-clarity` (**Stripe Trust & Editorial**) | `#FFFFFF` + `#F6F9FC` porcelain, interactive sandbox cards, calm settlement metrics | `Plus Jakarta Sans` + `Geist Mono` |
| Physical Goods, Botanical, Craft Studio | `aesop-tactile` (**Aesop Tactile Minimalism**) | `#F6F2EB` unbleached linen, macro studio photography, asymmetrical `5:7` editorial columns | `Newsreader` + `Manrope` |
| Hardware, Consumer Flagship Launch | `product-monumental` (**Apple Product Showcase**) | Pure clean stage (`#FAFAFA` / `#0A0A0A`), monumental viewport imagery, single CTA | `Geist` / `Instrument Sans` (`text-6xl`+) |

- **Cover & Surface Grammar Rule:** Culinary and lifestyle products showcase warm, cohesive real photography inside borderless rounded frames (`18px–28px` radius) rather than boxing visuals in `1px` wireframe cards.
- **Simplest High-Craft Blueprint Principle:** Applying `1` named `DESIGN.md` blueprint backed by authentic web/client photography is the simplest high-craft path—never generate synthetic AI lifestyle photos (`SLOP-AI-IMAGE-01`) or layer redundant CSS chrome when `1`–`2` focal visual bands carry the page.
- **Domain-Specificity Test:** If replacing product copy with enterprise invoicing leaves the visual structure intact, the blueprint choice was too generic and must be re-anchored.

---

## 2. Step-by-Step Workflow

1. **Select Blueprint & Lock `DESIGN.md` Design Direction**
   - **Input:** `design-brief.md`, Site-Kind, and real product/food photography library.
   - **Output:** Locked blueprint ID and token palette inside [../templates/design-master.md](../templates/design-master.md).
   - **Owner / Tool:** Design Lead using `python3 scripts/design_search.py "<domain>" --design-system`.
   - **Execution:** Choose the single matching blueprint (`culinary-editorial`, `linear-dark`, `stripe-clarity`, `aesop-tactile`, or `product-monumental`) before writing stylesheets.
2. **Apply Cover Hero & Borderless Photographic Surface Grammar**
   - **Input:** Locked cover photo (Pexels / Unsplash / Wikimedia Commons / Foodiesfeed CC0, never AI-generated) and verified headline copy.
   - **Output:** Above-the-fold full-bleed cover hero (`border-radius: 28px`, neutral dark readability scrim `rgba(18, 14, 11, 0.84)` -> `0.14`, white serif `<h1>`, single pill CTA) plus borderless multi-ratio photo galleries.
   - **Owner / Tool:** Frontend Engineer using native CSS Grid and `object-fit: cover`.
   - **Execution:** Separate sections through crisp `#FFFFFF` <-> `#FAF7F2` background shifts and warm diffused shadow (`0 12px 34px rgba(26, 20, 16, 0.07)`) instead of rigid `1px` borders around food photos.
3. **Bind Interactive Controls to Authentic Photography & Natural Human Copy**
   - **Input:** Interactive preview states (such as ingredient filters or meal trays) and plain everyday UI copy.
   - **Output:** Dynamic dish photo swaps paired with localized natural wording free of AI marketing clichés (`SLOP-COPY-01`).
   - **Owner / Tool:** UX Writer & Frontend Engineer verified with `scripts/check_anti_slop.py --strict`.
   - **Execution:** Map each interactive option to a distinct verified photograph so grid rows never repeat identical images side by side.
4. **Execute Complexity Budget & Deletion / Condensation Pass**
   - **Input:** Assembled header, CTA bar, and section stylesheets.
   - **Output:** Streamlined layout free of redundant buttons, boxed switches, or visual noise.
   - **Owner / Tool:** Frontend Lead running Playwright desktop (`1440px`) + mobile (`390px`) captures.
   - **Execution:** Delete redundant navbar links pointing to immediately visible page bands, remove heavy `1px` boxes around light/dark theme toggles, replace broken `border-bottom` link underlines with `text-underline-offset: 5px`, and strip synthetic image marks before deployment.

---

## 3. Reusable Artifact & Template

Blueprint tokens, cover scrim rules, and photography source governance are persisted directly into [../templates/design-master.md](../templates/design-master.md):

| Field / Token | Culinary Editorial Default | Linear Precision Dark Default | Enforcement Check |
|---|---|---|---|
| `paper_canvas` | `#FFFFFF` / `#FAF7F2` (Dark: `#141210`) | `#09090B` / `#111113` | `check_anti_slop.py` (`SLOP-COLOR-HARMONY-01`) |
| `accent_primary` | `#B84225` (`#9E381E` link ink) | `#FAFAFA` (`#A1A1AA` muted ink) | `check_contrast.py --apca` |
| `typography_pair` | `Newsreader` (`500–600`) + `Manrope` (`400–700`) | `Geist` + `Geist Mono` | `check_anti_slop.py` (`SLOP-FONT-01`) |
| `photo_scrim` | Neutral dark `rgba(18, 14, 11, 0.84 -> 0.14)` | None (`1px` subtle hairline border) | `check_anti_slop.py` (`SLOP-GRAD-01`) |
| `photography_source` | Real web/client photos + `CREDITS.md` | Interactive code/CLI product frame | `check_anti_slop.py` (`SLOP-AI-IMAGE-01`) |
| `wordmark_treatment` | Clean typographic serif wordmark (`Newsreader` 600) | Monochrome crisp wordmark | `check_anti_slop.py` (`SLOP-SVG-LOGO-01`) |
| `card_separation` | Borderless photos separated by canvas shift & soft shadow | Crisp `1px` dark hairline dividers | Visual Playwright audit |
| `header_nav_budget` | Max `3` nav links + borderless theme label + `1` pill CTA | Max `4` nav links + command trigger | Deletion/condensation review |

```css
:root {
  --paper: #FFFFFF;
  --surface-soft: #FAF7F2;
  --ink: #1C1917;
  --ink-muted: #645D56;
  --accent: #B84225;
  --accent-ink: #9E381E;
  --shadow-soft: 0 12px 34px rgba(26, 20, 16, 0.07), 0 1px 3px rgba(26, 20, 16, 0.04);
  --font-serif: 'Newsreader', Georgia, serif;
  --font-sans: 'Manrope', system-ui, sans-serif;
}
.hero-scrim { background: linear-gradient(90deg, rgba(18, 14, 11, 0.84) 0%, rgba(18, 14, 11, 0.14) 100%); }

/* Blueprint 2: Linear Precision Dark */
:root[data-blueprint="linear-dark"] {
  --paper: #09090B;
  --surface: #111113;
  --surface-elevated: #18181B;
  --ink: #FAFAFA;
  --ink-muted: #A1A1AA;
  --border-hairline: rgba(255, 255, 255, 0.08);
  --accent: #FAFAFA;
  --font-sans: 'Geist', system-ui, sans-serif;
  --font-mono: 'Geist Mono', ui-monospace, monospace;
}

/* Blueprint 3: Stripe Trust & Editorial */
:root[data-blueprint="stripe-clarity"] {
  --paper: #FFFFFF;
  --surface-soft: #F6F9FC;
  --ink: #0A2540;
  --ink-muted: #425466;
  --accent: #0073E6;
  --font-sans: 'Plus Jakarta Sans', system-ui, sans-serif;
}

/* Blueprint 4 & 5: Aesop Tactile & Apple Product Showcase */
:root[data-blueprint="aesop-tactile"] {
  --paper: #F6F2EB;
  --surface: #EFECE6;
  --ink: #252422;
  --ink-muted: #5E5B55;
  --accent: #3F4A3C;
  --font-serif: 'Newsreader', Georgia, serif;
}

:root[data-blueprint="product-monumental"] {
  --paper: #FAFAFA;
  --surface: #FFFFFF;
  --ink: #111113;
  --ink-muted: #52525B;
  --accent: #18181B;
  --font-sans: 'Geist', system-ui, sans-serif;
}
```

### Concrete Cross-Blueprint Component & Deletion Rules
- **No Redundant Control Framing:** Never wrap quiet mode toggles or secondary utility controls in heavy `1px` button borders when clean borderless typography communicates clearly.
- **Underline & Affordance Hygiene:** Use `text-decoration: underline; text-underline-offset: 5px` on inline editorial links instead of bottom borders below `44px` buttons.
- **Photographic Rhythm Baseline:** Culinary, retail, and hospitality pages must carry consistent lighting across hero, showcase spread, interactive preview, and catalog cards without synthetic smoothing or adjacent photo duplication.
- **Mobile Adaptation (`390px`):** Stack cover scrim overlays cleanly at the bottom edge (`180deg`), collapse 4-column strips to single or 2-column stacks with zero horizontal overflow, and preserve `>= 44px` tap targets.

---

## 4. Verification Checklist

- [ ] Explicit `DESIGN.md` blueprint recorded in `design-master.md` before styling begins.
- [ ] Zero AI-generated photos exist for real food, produce, venues, or people (`CREDITS.md` documents real sources).
- [ ] Cover hero, showcase spreads, interactive preview, and catalog tiles load distinct verified photographs.
- [ ] Card and section separation relies on canvas shifts and diffused elevation rather than `1px` boxes.
- [ ] Streamlined header contains at most 3 primary nav links, borderless theme switch, and 1 pill CTA.
- [ ] WCAG AA (`>= 4.5:1`) and APCA (`|Lc| >= 60`) contrast pass across Light and Dark modes.
- [ ] Playwright `1440px` and `390px` screenshots inspected visually with zero horizontal overflow or broken crops.

---

## 5. Hard Quality Gate

| Verdict | Criteria |
|---|---|
| **PASS** | Named blueprint applied consistently, `check_anti_slop.py --strict` exits `0`, zero AI-generated food/lifestyle assets (`SLOP-AI-IMAGE-01`), WCAG + APCA pass, and Playwright screenshots verified clean. |
| **CONCERNS** | Minor progressive font-swap timing verified acceptable without CLS layout shift. |
| **NOT ASSESSED** | Headless CLI or non-visual backend service with zero UI templates. |
| **FAIL** | Bare boxy template on editorial domain, AI-generated dish/product imagery, scrimless unreadable hero text, or AI-cliché button/nav copy. |

```bash
python3 skills/ui-design-craft/scripts/check_anti_slop.py src/ --strict --json
python3 skills/ui-design-craft/scripts/check_contrast.py --fg "#FFFFFF" --bg "#B84225" --apca --json
```

---

## 6. Anti-Patterns

| Pattern | Why It Fails | Detection Signal | Correct Replacement |
|---|---|---|---|
| **AI-Generated Food or People Photos** | Synthetic waxy lighting destroys authenticity on real culinary/lifestyle sites | AI filenames/credits or synthetic smoothing artifacts (`SLOP-AI-IMAGE-01`) | Real photography from Pexels, Unsplash, Foodiesfeed CC0, or Wikimedia Commons |
| **Bare Typographic SaaS Split on Food Sites** | Makes culinary products read like generic B2B accounting tools | Small cramped collage boxes with minimal authentic imagery | Full-bleed rounded cover hero + asymmetric 2-col and 4-col photo spreads |
| **1px Wireframe Cage Around Photographs** | Visually flattens photography and looks like an admin spreadsheet | `border: 1px solid ...` around every dish image card | Borderless `18px–24px` rounded photos with tonal `#FFFFFF`/`#FAF7F2` separation |
| **Redundant Nav Chrome & Floating Underlines** | Competing header links, boxed switches, and `border-bottom` lines add clutter | 4+ header pills/boxes or `.text-link` underline floating `14px` below text | At most 3 nav links + borderless theme switch + 1 pill CTA + `text-underline-offset` |
| **Adjacent Duplicate Grid Photos & Robotic Copy** | Repeating identical thumbnails and syrupy AI verbs signal generated slop | Identical `<img>` src across neighbors or AI buzzwords (`SLOP-COPY-01`) | Map each slot/slug to distinct photos; use plain human everyday phrasing |
| **Low-Resolution Wiki Snapshots in Editorial Heroes** | Harsh flash snapshots erode appetite appeal and visual warmth | Unbalanced cellphone flash or signage backgrounds in key showcase slots | Source color-graded culinary studio sets (`Pexels`, `Foodiesfeed CC0`, `Unsplash`) |
| **Mismatched Lighting Across Catalog Rows** | Mixing clinical blue cutouts beside warm tabletop shots breaks harmony | Cold cool-gray marbles next to candlelight wood in adjacent tiles | Curate lighting-consistent warm or cool editorial photography sets |
